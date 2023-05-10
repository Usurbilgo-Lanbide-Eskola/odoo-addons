# Copyright 2023 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    @api.model
    def _get_active_year(self):
        school_year = self.env['school.year'].get_current_school_year()
        if school_year:
            return school_year.id

    school_year_id = fields.Many2one(comodel_name="school.year",
                                     default=_get_active_year)
    current_school_year = fields.Boolean("In Current School Year")

    @api.depends("school_year_id")
    def _compute_in_active_school_year(self):
        for survey in self:
            active_year = survey.env['school.year'].get_current_school_year()
            if active_year == survey.school_year:
                survey.current_school_year = True
            survey.current_school_year = False

    @api.onchange("school_year_id", "survey_template")
    def onchange_school_year_id(self):
        for survey in self:
            if survey.survey_template:
                survey.school_year_id = False

    def search_child_survey(self, instance, template_survey, survey_type):
        res = super().search_child_survey(
            instance, template_survey, survey_type)
        school_year = self._context.get("school_year_id")
        if school_year:
            res = res.filtered(lambda x: x.school_year_id == school_year)
        return res


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    school_year_id = fields.Many2one(comodel_name="school.year",
                                     related="survey_id.school_year_id",
                                     store=True)
    current_school_year = fields.Boolean(
        related="survey_id.current_school_year", store=True)
    is_student = fields.Boolean(related="partner_id.is_student")
    is_tutor = fields.Boolean(related="partner_id.is_tutor")
    speciality_id = fields.Many2one(
        comodel_name="hezkuntza.speciality",
        compute="_compute_partner_speciality", store=True)

    def _compute_partner_speciality(self):
        for answer in self:
            partner = answer.partner_id
            speciality = partner.tutor_speciality_id if partner.is_tutor \
                else partner.speciality_id
            partner.speciality_id = speciality


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

    school_year_id = fields.Many2one(comodel_name="school.year",
                                     related="survey_id.school_year_id",
                                     store=True)
    current_school_year = fields.Boolean(
        related="survey_id.current_school_year", store=True)
    is_student = fields.Boolean(related="user_input_id.is_student")
    is_tutor = fields.Boolean(related="user_input_id.is_tutor")
    speciality_id = fields.Many2one(
        comodel_name="hezkuntza.speciality",
        related="user_input_id.speciality_id", store=True)
