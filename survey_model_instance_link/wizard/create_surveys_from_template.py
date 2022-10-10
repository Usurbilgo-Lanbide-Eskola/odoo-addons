# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CreateSurveysFromTemplate(models.TransientModel):
    _name = "create.surveys.from.template"

    survey_id = fields.Many2one(comodel_name="survey.survey", string="Survey")
    survey_template_ids = fields.Many2many(
        comodel_name="survey.survey")

    @api.model
    def default_get(self, fields_list):
        model = self._context.get('active_model')
        survey_type = self.env['survey.type'].search([('model_id', '=',
                                                       model)])
        if survey_type:
            surveys = self.env["survey.survey"].search([
                ('survey_template', '=', True),
                ('survey_type', '=', survey_type.id)])
            survey_template_ids = [(6, 0, surveys.ids)]
            return {
                'survey_template_ids': survey_template_ids
            }

    @api.depends('survey_template_ids')
    def _compute_model_template_surveys(self):
        for wizard in self:
            model = self._context.get('active_model')
            survey_type = self.env['survey.type'].search([('model_id', '=',
                                                           model)])
            if survey_type:
                surveys = self.env["survey.survey"].search([
                    ('survey_template', '=', True),
                    ('survey_type', '=', survey_type.id)])
                self.survey_template_ids = [(6, 0, surveys.ids)]

    def create_surveys(self):
        for wizard in self:
            model = self._context.get('active_model')
            survey_type = self.env['survey.type'].search([('model_id', '=',
                                                           model)])
            if not survey_type:
                raise UserError(_("There is not an survey type with model {}."
                                  " Create one".format(model)))
            ids = wizard._context.get('active_ids')
            model = wizard._context.get('active_model')
            instances = self.env[model].browse(ids)
            parent_survey = wizard.survey_id
            new_surveys = self.env['survey.survey'].create_child_surveys(
                instances, parent_survey, survey_type)
            survey_kanban_view_id = self.env.ref("survey.survey_kanban").id
            survey_form_view_id = self.env.ref("survey.survey_form").id
            survey_tree_view_id = self.env.ref("survey.survey_tree").id
            views = [(survey_kanban_view_id, "kanban"),
                     (survey_tree_view_id, "tree"),
                     (survey_form_view_id, "form"), ]

            return {
                "type": "ir.actions.act_window",
                "res_model": "survey.survey",
                "view_mode": "kanban, tree, form",
                "views": views,
                "context": {
                    "search_default_parent_template_id": parent_survey.id,
                    "search_default_groupby_state": 1},
            }
