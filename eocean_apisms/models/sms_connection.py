# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
import requests


class SMSConnection(models.Model):
    _name = "eoceansms.sms_connection"
    _description = "Entel Touch Ocean Gateway Configuration"

    name = fields.Char(string="Nombre", required=True, size=100)
    client_id = fields.Char(string="Client ID", required=True, help="eocean-client-id")
    client_secret = fields.Char(
        string="Client Secret", required=True, help="eocean-client-secret"
    )
    access_token = fields.Char(
        string="Access Token", readonly=True, help="eocean-access-token"
    )

    def authenticate_gateway(self):
        url = "https://api.touch.entelocean.io/125/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            return self.env.ref('eocean_apisms.sms_connection_action_tree').read()[0]
        else:
            self.access_token = ""
            raise UserError("Failed to authenticate with the gateway")
