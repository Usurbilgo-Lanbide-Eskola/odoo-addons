# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class InternshipLines(models.Model):
    _inherit = "internship.line"

    internship_type_id = fields.Many2one(comodel_name="internship.type",
                                         string="Internship Type")
    speciality_id = fields.Many2one(
        comodel_name="hezkuntza.speciality", string="Speciality")

    @api.onchange("student_group_id")
    def onchange_student_group(self):
        for line in self:
            if line.student_group_id:
                line.speciality_id = line.student_group_id.speciality_id
