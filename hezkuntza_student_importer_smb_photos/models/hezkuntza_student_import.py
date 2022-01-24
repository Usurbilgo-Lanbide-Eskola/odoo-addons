# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import tempfile

from smb.SMBConnection import SMBConnection, OperationFailure
from odoo import fields, models, _
from odoo.exceptions import UserError


class HezkuntzaStudentImport(models.Model):
    _inherit = "hezkuntza.student.import"

    use_zip_file = fields.Boolean("Use Zip file")
    smb_user = fields.Char("SMB User")
    smb_password = fields.Char("SMB Password")
    smb_host = fields.Char("SMB Host")
    smb_port = fields.Integer("SMB Port", default=139)
    image_path = fields.Char(help="To specify smb path first set shared "
                                  "folder name and then the path joined by a "
                                  "slash. Ex.: sharedfolder/path/to/dest")

    def _search_file(self, conn, shared_folder, folder_path, file_name_part):
        directories = []
        for file in conn.listPath(shared_folder, folder_path):
            if not file.isDirectory:
                find_file = file.filename.lower().find(file_name_part.lower())
                if find_file == 0:
                    return "{}/{}".format(folder_path, file.filename)
            elif file.filename not in ["..", "."]:
                directories.append(file)
        for directory in directories:
            find_file = self._search_file(conn, shared_folder, "{}/{}".format(
                folder_path, directory.filename), file_name_part)
            if find_file:
                return find_file
        return False

    def _get_image(self, student_id):
        if self.use_zip_file:
            return super()._get_image(student_id)
        conn, shared_folder, dest_path = self._context.get(
            'smb_connection', [False, False, False])
        file_path = self._search_file(conn, shared_folder, dest_path,
                                      student_id)
        if file_path:
            with tempfile.TemporaryFile() as temp_file:
                conn.retrieveFile(shared_folder, file_path, temp_file)
                temp_file.seek(0)
                return base64.b64encode(temp_file.read())
        return None

    def import_lines(self):
        if not self.use_zip_file:
            if self.image_zip:
                self.image_zip = False
            conn = SMBConnection(self.smb_user, self.smb_password,
                                 self.smb_host, "", use_ntlm_v2=True)
            if not conn.connect(self.smb_host, self.smb_port):
                raise UserError(_("smb connection fails"))
            if self.image_path[0] == '/':
                raise UserError(_("first character of the images path "
                                  "can't be a slash"))
            path = self.image_path.split('/')
            shared_folder = path[0]
            dest_path = "/".join(path[1:])
            try:
                conn.listPath(shared_folder, dest_path)
            except OperationFailure:
                raise UserError(_("Image path is not correct"))

            return super(HezkuntzaStudentImport, self.with_context(
                smb_connection=[conn, shared_folder, dest_path])
                         ).import_lines()
        return super().import_lines()
