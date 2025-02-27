# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class CreateInternshipDocument(models.TransientModel):
    _name = "create.internship.document"

    partner_id = fields.Many2one(
        comodel_name="res.partner", domain=[('is_student', '=', False),
                                            ('is_tutor', '=', False)])
    document_type_id = fields.Many2one(comodel_name="internship.document.type")
    no_duplicate = fields.Boolean("Don't duplicate", default=True, 
                                  help="If a document of the same type exists," 
                                  "it will not be created.")

    @api.model
    def default_get(self, fields):
        res = super(CreateInternshipDocument, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            res['partner_id'] = active_id
        return res
    
    def has_same_document(self):
        
        if self.no_duplicate:
            active_id = self.env.context.get('active_id')
            partner = self.env['res.partner'].browse(active_id)
            if self.env['internship.document'].search([
                ('partner_id', '=', partner.id),
                ('documents_ids', '=', self.document_type_id.id)
            ]):
                return True
        return False


    def button_create_document(self):
        for record in self.filter(lambda x: x.has_same_document()):
            partner = self.partner_id
            document_type = self.document_type_id
            self.env["internship.document"].create({
                "document_type_id": document_type.id,
                "res_model": partner.model,
                "res_id": partner.id,
                "code": document_type.code,
                "state_line_ids": [[0,0,({
                    "sequence": stage.sequence,
                    "name": stage.name,
                    "everyone_sign": stage.everyone_sign,
                    "to_sign_by": [(6,0, stage.stage_signer_ids.ids)],
                    })] for stage in document_type.stage_ids],

            })
        