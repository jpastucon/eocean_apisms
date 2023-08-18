# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, timedelta, time
from odoo.exceptions import UserError
import requests, logging, random, re

_logger = logging.getLogger(__name__)


class SMSCampaign(models.Model):
    _name = "eoceansms.sms_campaign"
    _description = "Entel Touch Ocean SMS Campaign"

    connection_id = fields.Many2one("eoceansms.sms_connection", "Conexión")

    campaign_id = fields.Char(string="ID Campaña", invisible=True)
    name = fields.Char(string="Nombre Campaña", required=True)
    status = fields.Char(string="Estado", readonly=True)

    type_action = fields.Selection(
        [("1", "Campaña Inmediata"), ("2", "Campaña Programada")],
        string="Tipo",
        default="Campaña Inmediata",
        required=True,
    )
    message = fields.Char(string="Mensaje")
    datetime = fields.Datetime(
        string="Seleccione la fecha y hora",
        store=True,
        default=lambda self: fields.Datetime.now(),
    )

    date = fields.Char(string="Fecha", store=True, readonly=True)
    time = fields.Char(string="Hora", store=True, readonly=True)

    contacts = fields.Many2many(
        "res.partner",
        string="Contactos",
        relation="eoceansms_sms_campaign_contacts_rel",
        column1="campaign_id",
        column2="contact_id",
        domain=[("phone", "!=", False)],
    )

    @api.onchange("datetime")
    def _onchange_datetime(self):
        if self.datetime:
            # Ajuste manual del desfase de -6 horas
            utc_datetime = fields.Datetime.from_string(self.datetime)
            utc_datetime += timedelta(hours=-6)
            local_datetime = fields.Datetime.context_timestamp(self, utc_datetime)

            self.date = (
                local_datetime.strftime("%d-%m-%Y") if local_datetime.date() else ""
            )
            self.time = (local_datetime + timedelta(hours=1)).strftime("%H:%M")

    def _sanitize_phone_number(self, number):
        if number:
            # Eliminar "+56" y luego eliminar espacios en blanco
            sanitized_number = number.replace("+56", "").replace(" ", "")
            if len(sanitized_number) >= 9:
                return sanitized_number[-9:]
        return False

    def send_campaign(self):
        url = "https://api.touch.entelocean.io/125/api/sms-channel/send-sms"

        connection = self.connection_id

        if not connection:
            raise UserError("Debe seleccionar una conexión antes de enviar la campaña.")

        connection.authenticate_gateway()

        headers = {"Authorization": f"Bearer {connection.access_token}"}
        payload = {
            "campaign": {
                "name": self.name,
                "type_campaign_id": "2803",  # PLANTILLA PREDEFINIDA
                "type_action": self.type_action,
                "registers": [],
            }
        }

        if self.contacts:
            phone_set = set()  # Conjunto para rastrear números de teléfono únicos
            for contact in self.contacts:
                phone_numbers = [
                    self._sanitize_phone_number(contact.phone),
                    self._sanitize_phone_number(contact.mobile),
                    self._sanitize_phone_number(contact.x_studio_telefono_01),
                    self._sanitize_phone_number(contact.x_studio_telefono_02),
                    self._sanitize_phone_number(contact.x_studio_telefono_03),
                ]

                for number in phone_numbers:
                    if number and number not in phone_set:  # Evitar duplicados
                        phone_set.add(number)
                        payload["campaign"]["registers"].append(
                            {
                                "id": contact.id,
                                "name": contact.name,
                                "phone": number,
                                "message": self.message,
                            }
                        )

        if self.datetime:
            utc_datetime = fields.Datetime.from_string(self.datetime)
            utc_datetime += timedelta(hours=-6)
            local_datetime = fields.Datetime.context_timestamp(self, utc_datetime)

            self.date = (
                local_datetime.strftime("%d-%m-%Y") if local_datetime.date() else ""
            )
            self.time = (local_datetime + timedelta(hours=1)).strftime("%H:%M")

            payload["campaign"]["date"] = self.date
            payload["campaign"]["hour"] = self.time

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            campaign_id = response_data.get("campaign")
            campaign_status = response_data.get("status")

            existing_campaign = self.env["eoceansms.sms_campaign"].search(
                [("id", "=", self.id)], limit=1
            )

            if existing_campaign:
                existing_campaign.connection_id = self.connection_id.id
                existing_campaign.campaign_id = campaign_id
                existing_campaign.name = self.name
                existing_campaign.status = campaign_status
                existing_campaign.type_action = self.type_action
                existing_campaign.datetime = self.datetime
                existing_campaign.date = self.date
                existing_campaign.time = self.time
                existing_campaign.contacts = [(6, 0, self.contacts.ids)]
                existing_campaign.message = self.message
            else:
                campaign_to_create = {
                    "connection_id": self.connection_id.id,
                    "campaign_id": campaign_id,
                    "name": self.name,
                    "status": campaign_status,
                    "type_action": self.type_action,
                    "datetime": self.datetime,
                    "date": self.date,
                    "time": self.time if self.time else "",
                    "contacts": [(6, 0, self.contacts.ids)],
                    "message": self.message,
                }

                existing_campaign = self.env["eoceansms.sms_campaign"].create(
                    campaign_to_create
                )

            registers_to_create = []
            if self.contacts:
                phone_set_1 = set()  # Conjunto para rastrear números de teléfono únicos
                for contact in self.contacts:
                    phone_numbers = [
                        self._sanitize_phone_number(contact.phone),
                        self._sanitize_phone_number(contact.mobile),
                        self._sanitize_phone_number(contact.x_studio_telefono_01),
                        self._sanitize_phone_number(contact.x_studio_telefono_02),
                        self._sanitize_phone_number(contact.x_studio_telefono_03),
                    ]

                    for number in phone_numbers:
                        if number and number not in phone_set_1:  # Evitar duplicados
                            register_values = {
                                "id": contact.id,
                                "register_id": contact.id,
                                "name": contact.name,
                                "phone": number,
                                "message": self.message,
                                "campaign_ids": [(4, existing_campaign.id)],
                            }

                            registers_to_create.append(register_values)
                registers = self.env["eoceansms.sms_register"].create(
                    registers_to_create
                )

            return self.env.ref("eocean_apisms.sms_campaign_action_tree").read()[0]
        else:
            raise UserError(f"Error en la carga útil: {response.text}")

    def update_campaign_status(self):
        url = "https://api.touch.entelocean.io/125/api/sms-channel/campaign"

        connection = self.env["eoceansms.sms_connection"].search([], limit=1)

        if not connection:
            raise UserError("Debe seleccionar una conexión antes de enviar la campaña.")

        connection.authenticate_gateway()

        headers = {"Authorization": f"Bearer {connection.access_token}"}

        campaigns = self.env["eoceansms.sms_campaign"].search([])

        if not campaigns:
            raise UserError("No se encontraron campañas para actualizar el estado.")

        for campaign in campaigns:
            campaign_id = campaign.campaign_id
            if not campaign_id:
                raise UserError("La campaña no tiene un ID asignado.")

            payload = {"id": campaign_id}

            response = requests.get(url, headers=headers, params=payload)

            if response.status_code == 200:
                response_data = response.json()
                campaign_status = response_data.get("status")

                campaign.status = campaign_status

                sms_registers = self.env["eoceansms.sms_register"].search(
                    [("campaign_ids", "=", campaign.id)]
                )

                campaign_data = response_data.get("campaign", [])

                if campaign_data:
                    sms_register_data = campaign_data[0].get("sms_records", [])
                else:
                    sms_register_data = []

                for sms_register in sms_registers:
                    for record_data in sms_register_data:
                        record_external_id = record_data.get("id")
                        record_phone = record_data.get("fono")
                        # _logger.info("record_external_id: %s", record_external_id)
                        if str(record_phone) == str(sms_register.phone):
                            status_value = record_data.get("estado")
                            if str(status_value) in dict(
                                sms_register._fields["status"].selection
                            ):
                                sms_register.status = str(status_value)
                                sms_register.register_id = record_external_id
                                fecha_envio = record_data.get("fecha envio")
                                sms_register.fecha_envio = (
                                    fields.Datetime.to_datetime(fecha_envio)
                                    if fecha_envio
                                    else False
                                )

                                fecha_entrega = record_data.get("fecha entrega")
                                sms_register.fecha_entrega = (
                                    fields.Datetime.to_datetime(fecha_entrega)
                                    if fecha_entrega
                                    else False
                                )

                            else:
                                raise UserError(
                                    f"Error al obtener el estado del registro: {record_data}"
                                )
            else:
                raise UserError(
                    f"Error al obtener el estado de la campaña: {response.text}"
                )

    def action_view_registers(self):
        action = self.env.ref("eocean_apisms.sms_register_action_tree").read()[0]
        action["domain"] = [("campaign_ids", "in", self.ids)]
        action["context"] = {
            "default_campaign_ids": [(6, 0, self.ids)],
            "search_default_campaign_ids": [self.id],
        }
        return action
