# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class PromoteStudent(models.TransientModel):
    _name = "promote.student"

    school_year_id = fields.Many2one("school.year")
    student_group_id = fields.Many2one(
        comodel_name="product.template",
        string="Student Group",
    )
    change_degree = fields.Boolean()

    def promote_student(self):
        student = self.env["res.partner"].browse(self.env.context.get("active_id"))
        student.write({'student_record_ids': [(0, 0, {
                    'school_year_id': self.school_year_id.id,
                    'group_id': self.student_group_id.id})]})
