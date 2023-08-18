# -*- coding: utf-8 -*-
from odoo import models, fields


class SMSRegister(models.Model):
    _name = "eoceansms.sms_register"
    _description = "Entel Touch Ocean SMS Register"

    campaign_ids = fields.Many2many(
        "eoceansms.sms_campaign",
        relation="eoceansms_sms_campaign_sms_register_rel",
        column1="register_id",
        column2="campaign_id",
        string="Campañas",
    )

    register_id = fields.Char(string="ID Registro", invisible=True)
    contact_id = fields.Many2one(
        "res.partner",
        string="Contacto",
        domain=[("phone", "!=", False)],
        ondelete="restrict",
    )

    name = fields.Char(string="Nombre")
    phone = fields.Char(string="Teléfono")
    message = fields.Char(string="Mensaje")

    status = fields.Selection(
        [
            ("1", "Descartado"),
            ("2", "Pendiente"),
            ("3", "Ejecutado"),
            ("4", "Recibido"),
            ("5", "Contestado"),
            ("6", "No recibido"),
            ("7", "Cerrado"),
        ],
        string="Estado",
    )

    fecha_envio = fields.Datetime(string="Fecha de envío", store=True)

    fecha_entrega = fields.Datetime(string="Fecha de entrega", store=True)
