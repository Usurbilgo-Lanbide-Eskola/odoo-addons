# Copyright 2026 Mikel Arregi Etxaniz - Zubieta Lanbide Eskola
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class InternshipPredictionCopyWizard(models.TransientModel):
    _name = "internship.prediction.copy.wizard"
    _description = "Wizard to copy prediction companies to school year historical"

    line_ids = fields.Many2many(comodel_name="internship.prediction.line",
                                relation="internship_prediction_copy_wizard_line_rel",
                                column1="wizard_id",
                                column2="line_id",
                                string="Lines to Process")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        prediction_lines = self.env["internship.prediction.line"].search([
            ('id', 'in', self.env.context.get('active_ids')),
            ('student_company_id', '!=', False)])

        if prediction_lines:
            res['line_ids'] = [(6, 0, prediction_lines.ids)]
        return res

    def action_copy_companies(self):
        for line in self.line_ids:
            if line.student_company_id:
                line.school_year_historical_id.student_company_id = \
                    line.student_company_id
