# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    student_group_id = fields.Many2one(
        inverse="_set_student_group_historical_record")
    hezkuntza_group_id = fields.Many2one(
        related='student_group_id.hezkuntza_student_group_id')

    def _set_student_group_historical_record(self):
        for student in self:
            if student.student_group_id:
                student.active_student_record_ids.write({
                    'group_id': student.student_group_id}
                )
