# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import base64
import datetime
from ..tools.signature_wrapper import get_pdf_signatures


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    signature_line_ids = fields.One2many(comodel_name="pdf.signature",
                                         inverse_name="file_id")

    def _process_pdf_signatures(self, file):
        """Helper method to process PDF signatures."""
        pdf_file = base64.b64decode(file.datas)
        new_signatures = []
        for signature in get_pdf_signatures(pdf_file):
            certificate = signature.certificate
            subject = signature.certificate.subject
            new_signatures.append((0, 0, {
                'name': signature.signer_name,
                'date': signature.signing_time.astimezone(
                    datetime.timezone.utc).replace(tzinfo=None),
                'cert_issuer': certificate.issuer,
                'cert_not_before': certificate.validity.not_before.astimezone(
                    datetime.timezone.utc).replace(tzinfo=None),
                'cert_not_after': certificate.validity.not_after.astimezone(
                    datetime.timezone.utc).replace(tzinfo=None),
                'cert_common_name': subject.common_name,
                'cert_serial_number': subject.serial_number,

            }))
        return new_signatures

    @api.model
    def create(self, vals):
        attachment = super(IrAttachment, self).create(vals)
        if attachment.mimetype == 'application/pdf' and attachment.datas:
            attachment.signature_line_ids = self._process_pdf_signatures(
                attachment)
        return attachment

    def write(self, vals):
        res = super(IrAttachment, self).write(vals)
        if 'datas' in vals or 'mimetype' in vals:
            for file in self.filtered(
                    lambda x: x.mimetype == 'application/pdf' and x.datas):
                file.signature_line_ids.unlink()
                file.signature_line_ids = self._process_pdf_signatures(file)
        return res


class PDFSignature(models.Model):
    _name = "pdf.signature"

    name = fields.Char()
    date = fields.Datetime()
    cert_issuer = fields.Char()
    cert_not_before = fields.Datetime()
    cert_not_after = fields.Datetime()
    cert_common_name = fields.Char()
    cert_serial_number = fields.Char()
    file_id = fields.Many2one(comodel_name="ir.attachment", ondelete="cascade")
