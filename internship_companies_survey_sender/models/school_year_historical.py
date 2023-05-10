# Copyright 2023 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class SchoolYearHistorical(models.Model):
    _inherit = "school.year.historical"

    answer_id = fields.Many2one(comodel_name="survey.user_input",
                                string="Student Survey")

    def get_record_last_answer(self):
        self.ensure_one()
        survey_type = self.env['survey.type'].search(
            [('model_id', '=', 'res.partner')])
        domain = [
            ('partner_id', '=', self.student_id.id),
            ('school_year_id', '=', self.school_year_id.id),
            ('survey_id.instance_id', '=', self.student_company_id.id),
            ('survey_id.survey_type', '=', survey_type.id),
        ]
        return self.env["survey.user_input"].search(
            domain, order='create_date desc', limit=1)
