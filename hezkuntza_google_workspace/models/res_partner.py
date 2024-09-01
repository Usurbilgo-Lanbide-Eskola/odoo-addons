# Copyright 2024 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    workspace_id = fields.Char("Workspace ID")

    def add_hna_workspace(self, user, hna):
        service = self.env["res.config.settings"].get_google_service()
        if not user.get('externalIds'):
            user.update(externalIds=[])
        user['externalIds'].append({'type': "organization", 'value': hna})
        try:
            service.users().update(userKey=user["primaryEmail"],
                                   body=user).execute()
        except:
            raise ValidationError(_(f"Error on updating workspace user"))

    def sync_partner_workspace(self):
        if self.id_hezkuntza and self.email:
            service = self.env["res.config.settings"].get_google_service()
            query = f"email={self.email}"
            request = service.users().list(customer='my_customer',
                                           maxResults=1, query=query)
            response = request.execute()
            user = response.get('users', [])
            if user:
                user = user[0]
                hna = list(filter(lambda x: x["type"] == "organization",
                                  user.get('externalIds', [])))
                if len(hna) == 1 and hna[0]["value"] == self.id_hezkuntza:
                    self.workspace_id = user["id"]
                    return True
                elif len(hna) == 1 and hna[0]["value"] != self.id_hezkuntza:
                    raise ValidationError(_(f"{self.email}"))
                if not hna:
                    self.add_hna_workspace(user, self.id_hezkuntza)
                    self.workspace_id = user["id"]
                    return True
                return False
        elif self.id_hezkuntza:
            service = self.env["res.config.settings"].get_google_service()
            query = f"externalId={self.id_hezkuntza}"
            request = service.users().list(customer='my_customer',
                                           maxResults=2, query=query)
            response = request.execute()
            user = response.get('users', [])
            if user and len(user) == 1:
                user = user[0]
                self.email = user["primaryEmail"]
                self.workspace_id = user["id"]
                return True
            return False

    def get_google_user(self, hna=None, email=None):
        service = self.env["res.config.settings"].get_google_service()
        # XOR
        if bool(hna) != bool(email):
            if email:
                query = f"email={email}"
            else:
                query = f"externalId={hna}"

            request = service.users().list(customer='my_customer',
                                           maxResults=2, query=query)
            response = request.execute()
            users = response.get('users', [])

            # if not users:
            #     self.google_create_user()
            if users:
                if len(users) > 1:
                    _logger.info(ValidationError(_(f'Multiple users with'
                                                   f' {hna or email}')))
                    return []
                return users[0]
            return []
        ValidationError(_("At least one parameter is required hna or "
                          "email"))
        return []

    def get_google_data(self):
        service = self.env["res.config.settings"].get_google_service()
        if self.workspace_id:
            request = service.users().get(userKey=self.workspace_id)
            user = request.execute()
            # try:
            #     self.google_create_user()
            # except:
            #     ValidationError(
            #         _(f'Not found {self.id_hezkuntza}'))
            #     return False
            return user
        return False

    def create_hezkuntza_email(self):
        def to_lower_ascii(email):
            email = email.lower()
            my_dict = {225: 97,  # á
                233: 101,  # é
                237: 105,  # í
                243: 111,  # ó
                250: 117,  # ú
                241: 110,  # ñ
                252: 117,  # ü
            }
            return email.translate(my_dict)

        # TODO password creation template
        school_year = str(self.env["school.year"].get_current_school_year(

        ).start_date.year)[2:]
        try:
            email = (f"ik{''.join(x[0] for x in self.firstname.split())}"
                     f"{self.lastname.replace(' ', '')}{school_year}@lhusurbil.eus")
            email = to_lower_ascii(email)
            user = self.get_google_user(email=email)
            if user:
                email = (f"ik{''.join(x[0] for x in self.firstname.split())}"
                         f"{''.join(x[0] for x in self.lastname.split())}"
                         f"{self.lastname2.replace(' ', '')}"
                         f"{school_year}@lhusurbil.eus")
                email = to_lower_ascii(email)
                user = self.get_google_user(email=email)
                if user:
                    return False
        except Exception as e:
            return False
        return email

    def google_create_user(self):
        def create_user(service, email, password):
            user_body = {"primaryEmail": email,
                         "name": {"givenName": self.firstname,
                                  "familyName": f"{self.lastname} "
                                                f"{self.lastname2}"},
                         "password": password,
                         "changePasswordAtNextLogin": True,
                         "orgUnitPath": self.hezkuntza_group_id.workspace_organisation_path or "/",
                         "externalIds": [{"type": "organization",
                                          "value": self.id_hezkuntza}]}
            try:
                user = service.users().insert(body=user_body).execute()
                return user
            except HttpError as err:
                _logger.error(ValidationError(_(f'Failed to create user. '
                                                f'Error: {err}')))
                return None

        if not self.workspace_id:
            self.sync_partner_workspace()
            if self.workspace_id:
                Warning("Already created")
                return False
        settings_obj = self.env["res.config.settings"]
        service = self.env["res.config.settings"].get_google_service()
        email = self.email if self.email else self.create_hezkuntza_email()
        if email:
            user = create_user(service, email,
                               settings_obj.get_default_password())
            if user:
                self.email = user["primaryEmail"]
                self.workspace_id = user["id"]
            else:
                return False

    def delete_workspace_user(self):
        service = self.env["res.config.settings"].get_google_service()
        try:
            service.users().delete(userKey=self.workspace_id).execute()
            self.email = ""
            self.workspace_id = ""
            return True
        except:
            return False
