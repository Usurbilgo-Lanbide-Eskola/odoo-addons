# Copyright 2023 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    speciality_id = fields.Many2one(comodel_name="hezkuntza.speciality",
                                    string="Speciality",
                                    compute="_compute_speciality",
                                    store=True)

    @api.depends("partner_id")
    def _compute_speciality(self):
        for answer in self:
            partner = answer.partner_id
            if partner.is_student:
                answer.speciality_id = partner.hezkuntza_group_id.speciality_id
            else:
                answer.speciality_id = partner.tutor_speciality_id


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

    speciality_id = fields.Many2one(comodel_name="hezkuntza.speciality",
                                    string="Speciality",
                                    related="user_input_id.speciality_id",
                                    store=True)
