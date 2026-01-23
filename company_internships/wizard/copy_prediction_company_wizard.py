# Copyright 2026 Mikel Arregi Etxaniz - Zubieta Lanbide Eskola
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class InternshipPredictionCopyWizard(models.TransientModel):
    _name = "internship.prediction.copy.wizard"
    _description = "Wizard to copy prediction companies to school year historical"

    line_ids = fields.Many2many(comodel_name="internship.prediction.line",
                                string="Lines to Process")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_ids'):
            res['line_ids'] = [(6, 0, self.env.context.get('active_ids'))]
        return res

    def action_copy_companies(self):
        for line in self.line_ids:
            if line.student_company_id:
                line.school_year_historical_id.student_company_id = \
                    line.student_company_id
