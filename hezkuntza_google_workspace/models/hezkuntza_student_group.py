# Copyright 2024 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from google.oauth2 import service_account
from googleapiclient.discovery import build


class HezkuntzaStudentGroup(models.Model):
    _inherit = "hezkuntza.student.group"

    group_gmail_id = fields.Char("Group Google ID")
    group_gmail = fields.Char("Group gmail")
    workspace_organisation_path = fields.Char("Workspace organisation path")
    deleted_member_organisation_path = fields.Char(
        "inactive member organisation path",
        help="When a member is deleted from organisation by default will be "
             "added to this organisation")
    def delete_all_members(self):
        service = self.env["res.config.settings"].get_google_service()
        try:
            members = service.members().list(
                groupKey=self.group_gmail).execute().get('members', [])
        except Exception as e:
            raise ValidationError(
                _(f'Failed to list members of : {self.group_gmail}. Error: '
                  f'{e}'))
        if members:
            for member in members:
                member_email = member['email']
                try:
                    service.members().delete(groupKey=self.group_gmail,
                                             memberKey=member_email).execute()
                except Exception as e:
                    raise ValidationError(
                        _(f'Failed to delete member: {member_email}. Error: '
                          f'{e}'))

    def insert_member(self, service, email, group_email=None, role="MEMBER"):
        member = {'email': email, 'role': role}
        group_email = group_email or self.group_gmail
        try:
            request = service.members().insert(groupKey=group_email,
                                               body=member)
            request.execute()
            return False
        except:
            return True

    def google_sync_group_members(self):
        service = self.env["res.config.settings"].get_google_service()
        # Add user to Admin SDK group
        group_email = self.group_gmail  # Replace with the email of the group
        self.delete_all_members()
        students = self.get_group_students()

        def get_error_string(name):
            return _(f"User {name} sync fail. "
                     f"check users email is on google "
                     f"workspace")

        for student in students:
            student_name = student.name
            success = self.insert_member(service, student.email)
            if not success:
                try:
                    student.get_google_user(hna=student.id_hezkuntza)
                except:
                    raise ValidationError(get_error_string(student_name))
                success = self.insert_member(service, student.email)
                if not success:
                    raise ValidationError(get_error_string(student_name))
