# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError


class SurveyType(models.Model):
    _name = "survey.type"

    name = fields.Char(string="Name")
    model_id = fields.Many2one(comodel_name="ir.model")
    action_id = fields.Many2one(comodel_name="ir.actions.act_window")

    @api.constrains("model_id")
    def unique_model_id(self):
        for type in self.filtered(lambda x: x.model_id):
            existing_type = self.env['survey.type'].search([
                ('model_id', '=', type.model_id.id), ('id', '!=', self.id)
            ])
            if existing_type:
                raise ValidationError(_("Already exist another type with "
                                        "the same model"))

    @api.onchange("model_id")
    def _onchange_model(self):
        if self.model_id:
            self.name = self.model_id.name

    def create_action(self):
        for type in self:
            wizard_view_id = self.env.ref(
                "survey_model_instance_link.create_surveys_from_template_form"
            ).id
            type.action_id = self.env["ir.actions.act_window"].with_user(
                SUPERUSER_ID).create({
                'name': 'survey template wizard',
                'res_model': "create.surveys.from.template",
                'view_mode': 'form',
                'view_id': wizard_view_id,
                'target': 'new',
                'binding_model_id': type.model_id.id,
                'binding_view_types': 'list,form'})
        return True

    def delete_action(self):
        for type in self:
            if type.action_id:
                type.action_id.unlink()
        return True


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    survey_type = fields.Many2one(comodel_name="survey.type", copy=True)
    instance_id = fields.Integer(string="Instance ID")
    survey_template = fields.Boolean(string="Survey Template")
    parent_template_id = fields.Many2one(comodel_name="survey.survey")

    def see_related_instance(self):
        self.ensure_one()
        model = self.survey_type.model_id.model
        view = self.env["ir.ui.view"].search([('model', '=', model),
                                              ('type', '=', 'form'),
                                              ('mode', '=', 'primary')],
                                             limit=1)
        if view:
            return {
                "type": "ir.actions.act_window",
                "res_model": model,
                "view_type": "form",
                "view_mode": "form",
                "views": [(view.id, "form")],
                "res_id": self.instance_id,
            }

    def get_related_instance(self):
        self.ensure_one()
        if self.instance_id:
            model = self.survey_type.model_id.model
            return self.env[model].browse(self.instance_id)

    def create_child_surveys(self, instances, template_survey, survey_type,
                             duplicate=False):
        new_surveys = self.env['survey.survey']
        for instance in instances:
            if not duplicate:
                domain = [
                    ('survey_template', '=', False),
                    ('instance_id', '=', instance.id),
                    ('survey_type', '=', survey_type.id),
                    ('parent_template_id', '=', template_survey.id),
                ]
                if self.env['survey.survey'].search(domain):
                    continue
            survey_dict = {
                'survey_template': False,
                'instance_id': instance.id,
                'survey_type': survey_type.id,
                'title': f"{template_survey.title} {instance.name}",
                'parent_template_id': template_survey.id,
            }
            new_survey = template_survey.sudo().copy(survey_dict)
            new_survey.title = f"{template_survey.title} {instance.name}"
            new_surveys |= new_survey
        return new_surveys
