# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    student_group_id = fields.Many2one(
        inverse="_set_student_group_historical_record")
    hezkuntza_group_id = fields.Many2one(
        related='student_group_id.hezkuntza_student_group_id')
    tutor_speciality_id = fields.Many2one(
        comodel_name="hezkuntza.speciality")

    def _set_student_group_historical_record(self):
        for student in self:
            if student.student_group_id:
                student.active_student_record_ids.write({
                    'group_id': student.student_group_id}
                )

    def next_group(self):
        groups = super().next_group()
        try:
            next_course = chr(ord(
                self.hezkuntza_group_id.course_id.odoo_code[0]) + 1)
            return groups.filtered(
                lambda x: x.hezkuntza_student_group_id.course_id.odoo_code == next_course and
                  all(
                    getattr(x.hezkuntza_student_group_id, attr).id == getattr(self.hezkuntza_group_id, attr).id
                    for attr in ['linguistic_model_id', 'degree_id', 'educational_level_id', 'degree_mode_id']
                )
            )

        except Exception as e:
            return groups
