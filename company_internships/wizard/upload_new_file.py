# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class UploadNewFile(models.TransientModel):
    _name = 'upload.new.file'
    _description = 'Upload files to internship.document'

    # TODO check if the user is in the signers users.
    # TODO check if the file modification date is older than the actual upload time
    # TODO check if the new file has all signatures
    # TODO if in this stage there are a non internal user add posibility to select
    # it and upload file in the name of those user
    # TODO get the new signature and save it in signed by. Check the older signatures there are in the file

    # TODO in stages not in this file. In signed by save the signature of the user

    document = fields.Binary("Updload Document")
    #no_signed_by_ids = fields.Many2many("internship.document.signer",
    #                              related="active_line_id.to_sign_by")


    def _check_file_validity(self):
        valid = True
        error = False
        return {
            "valid":valid ,
            "error": error,
        }
    
    def button_upload_file(self):
        file_validity = self._check_file_validity()
        if not file_validity.get("valid"):
            raise Warning(file_validity(file_validity.get("error")))
        return True