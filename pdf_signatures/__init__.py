from . import models
from odoo import api, SUPERUSER_ID

def _generate_signatures_for_existing_pdfs(cr, registry):
    """Generate signatures for all existing PDF attachments."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    attachment_obj = env['ir.attachment']
    pdf_attachments = attachment_obj.search(
        [('mimetype', '=', 'application/pdf'),('signature_line_ids', '=', False),
          '|', ('db_datas', '!=', False), ('store_fname', '!=', False)])
    for attachment in pdf_attachments:
        try:
            attachment.signature_line_ids = attachment_obj._process_pdf_signatures(
                attachment)
        except Exception as e:
            pass
