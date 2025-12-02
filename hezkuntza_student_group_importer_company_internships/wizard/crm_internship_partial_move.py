# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, _

class CrmInternshipPartialMove(models.TransientModel):
    _inherit = "crm.internship.partial.move"
    
    def generate_line_dict(self, lead=None):
        res = super().generate_line_dict(lead)
        if res is None:
            return 
        res.update({
            "internship_type_id": lead.internship_type_id.id,
            "speciality_id": lead.speciality_id.id
		})
        return res

class CrmInternshipPartialMoveLine(models.TransientModel):
    _inherit = "crm.internship.partial.move.line"
    
    internship_type_id = fields.Many2one(comodel_name="internship.type",
                                         string="Internship Type")
    speciality_id = fields.Many2one(
        comodel_name="hezkuntza.speciality", string="Speciality")

    def get_line_dict(self):
        self.ensure_one()
        res = super().get_line_dict()
        res.update({
            "speciality_id": self.speciality_id.id if self.speciality_id else False,
            "internship_type_id": self.internship_type_id.id if self.internship_type_id else False,
        }
        )
        return res
