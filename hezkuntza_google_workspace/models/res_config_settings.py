# Copyright 2024 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from google.oauth2 import service_account
from googleapiclient.discovery import build
import csv
import xmlrpc.client
import pathlib
import base64
import sys

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    credentials_file = fields.Binary("Credentials file")
    scope = fields.Text("Scopes")
    delegated_credentials = fields.Char("Delegated credentials email")
    password_model = fields.Char("Password Model")


    def get_google_service(self):
        res = self.get_values()
        path = f"{pathlib.Path(sys.argv[0]).parent}/google_credentials.json"
        if not pathlib.Path(path).exists():
            with open(path, "bw") as f:
                f.write(base64.b64decode(res["credentials_file"]))
        credentials = service_account.Credentials.from_service_account_file(
            path, scopes=res["scope"].split(","))

        # # Delegated credentials for admin actions
        delegated_credentials = credentials.with_subject(
            res["delegated_credentials"])

        # # Create the service client
        return build('admin', 'directory_v1',
                        credentials=delegated_credentials)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('hezkuntza_google_workspace.credentials_file',
                        self.credentials_file)
        param.set_param('hezkuntza_google_workspace.scope',
                        self.scope)
        param.set_param('hezkuntza_google_workspace.delegated_credentials',
                        self.delegated_credentials)
        param.set_param('hezkuntza_google_workspace.password_model',
                        self.password_model)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(credentials_file=self.env[
            'ir.config_parameter'].sudo().get_param(
            'hezkuntza_google_workspace.credentials_file', default=""),
            scope=self.env[
                'ir.config_parameter'].sudo().get_param(
                'hezkuntza_google_workspace.scope', default=""),
            delegated_credentials=self.env[
                'ir.config_parameter'].sudo().get_param(
                'hezkuntza_google_workspace.delegated_credentials',
                default=""),
            password_model=self.env[
                'ir.config_parameter'].sudo().get_param(
                'hezkuntza_google_workspace.password_model', default=""))
        return res

    def get_default_password(self):
        return self.get_values()["password_model"]