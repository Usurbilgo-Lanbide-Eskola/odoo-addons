# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SendCompanySatisfactionSurvey(models.TransientModel):
    _inherit = "survey.invite"
    _name = "send.company.satisfaction.survey"

    @api.model
    def _get_active_year(self):
        school_year = self.env['school.year'].get_school_year()
        if school_year:
            return school_year.id
        
    survey_id = fields.Many2one('survey.survey', required=False)
    school_year = fields.Many2one(comodel_name="school.year",
                                  default=_get_active_year)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'instructor_survey_mail_compose_message_ir_attachments_rel', 
        'wizard_id',
        'attachment_id',
        string='Attachments')
    partner_ids = fields.Many2many(
        'res.partner', 'instructor_survey_invite_partner_ids', 'invite_id',
        'partner_id', string='Recipients',
        domain="""[
            '|', (survey_users_can_signup, '=', 1),
            '|', (not survey_users_login_required, '=', 1),
                 ('user_ids', '!=', False),
        ]"""
    )

    satisfaction_line_ids = fields.One2many(
        comodel_name="send.company.satisfaction.survey.line",
        inverse_name="send_wizard_id")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        record_ids = self._context.get("active_ids")
        if not record_ids:
            return res
        internship_types = self.env['school.year.historical'].browse(record_ids
            ).mapped("internship_type")
        satisfaction_lines = [(0, 0, {
            'internship_type_id': i.id,
        }) for i in internship_types]
        res['satisfaction_line_ids'] = satisfaction_lines
        return res
    
    def _create_instructor_surveys_answers(self, records):
        survey_type = self.env['survey.type'].search(
            [('model_id', '=', 'internship.type')])
        if not survey_type:
            raise UserError(_("There is not an survey type of a "
                              "'internship.type' model. Create one"))
        surveys = {}
        survey_obj = self.env['survey.survey']
        for record in records:
            instructor_id = record.student_instructor_id
            internship_type = record.internship_type
            survey_instance = self.satisfaction_line_ids.filtered(
                lambda x: x.internship_type_id.id == internship_type.id).survey_id
            if not survey_instance:
                raise ValidationError(_(
                    f"No survery for: {record.student_instructor_id}"))
            new_surveys = survey_obj.with_context(
                    {'school_year_id': self.school_year}).create_child_surveys(
                internship_type, survey_instance, survey_type)
            new_surveys.write({'school_year_id': self.school_year})
            if surveys.get(instructor_id):
                surveys[instructor_id] |= survey_obj.with_context(
                    {'school_year_id': self.school_year}).search_child_survey(
                    internship_type, survey_instance, survey_type)
            else:
                surveys[instructor_id] = survey_obj.with_context(
                    {'school_year_id': self.school_year}).search_child_survey(
                    internship_type, survey_instance, survey_type)
        

        return self._prepare_instructor_answers(surveys)
        # TODO link to a internship_type?

    def _prepare_instructor_answers(self, surveys):
        def _update_answers(answers, instructor, answer):
            if answers.get(instructor):
                answers[instructor] |= answer
            else:
                answers[instructor] = answer
        answers = {}
        for instructor, surveys in surveys.items():
            for survey in surveys:
                existing_answer = self.env['survey.user_input'].search([
                    ('survey_id', '=', survey.id),
                    ('partner_id', '=', instructor.id),
                ], order='create_date desc', limit=1)
                if existing_answer:
                    if self.existing_mode == 'resend':
                        _update_answers(answers, instructor, existing_answer)
                else:
                    _update_answers(answers, instructor, survey._create_answer(
                        partner=instructor, check_attempts=False,
                        **self._get_answers_values()))
        return answers

    def _send_instructor_mail(self, bundle):
        """ Create mail specific for recipient containing notably
        its access token """
        subject = self.env['mail.render.mixin'].with_context(
            safe=True)._render_template(self.subject,
                                        'instructor.answer.bundle',
                                        bundle.ids, post_process=True)[
            bundle.id]
        body = self.env['mail.render.mixin']._render_template(
            self.body, 'instructor.answer.bundle', bundle.ids,
            post_process=True)[
            bundle.id]
        # post the message
        mail_values = {
            'email_from': self.email_from,
            'author_id': self.author_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'attachment_ids': [(4, att.id) for att in self.attachment_ids],
            'auto_delete': True,
            'recipient_ids': [(4, bundle.instructor_id.id)]
        }

        # optional support of notif_layout in context
        notif_layout = self.env.context.get('notif_layout',
                                            self.env.context.get(
                                                'custom_layout'))
        if notif_layout:
            try:
                template = self.env.ref(notif_layout,
                                        raise_if_not_found=True)
            except ValueError:
                _logger.warning(
                    'QWeb template %s not found when sending survey mails. '
                    'Sending without layouting.' % (
                        notif_layout))
            else:
                title = ""
                template_ctx = {
                    'message': self.env['mail.message'].sudo().new(
                        dict(body=mail_values['body_html'],
                             record_name=title)),
                    'model_description': self.env['ir.model']._get(
                        'survey.survey').display_name,
                    'company': self.env.company,
                }
                body = template._render(template_ctx, engine='ir.qweb',
                                        minimal_qcontext=True)
                mail_values['body_html'] = self.env[
                    'mail.render.mixin']._replace_local_links(body)

        return self.env['mail.mail'].sudo().create(mail_values)

    def action_invite_instructors(self):
        record_ids = self._context.get("active_ids")
        records = self.env['school.year.historical'].search([
            ('id', 'in', record_ids),
            ('school_year_id', '=', self.school_year.id),
            ('student_without_internship', '=', False)
        ])
        if any(not record.student_instructor_id for record in records):
            raise UserError(_("All the records must have an instructor"))
        answers = self._create_instructor_surveys_answers(records)
        answer_bundle = self.env['instructor.answer.bundle']
        for instructor, answer_id in answers.items():
            bundle = answer_bundle.create({'instructor_id': instructor.id,
                                           'answer_ids': answer_id})
            self._send_instructor_mail(bundle)
        return {'type': 'ir.actions.act_window_close'}


class SendCompanySatisfactionSurveyLine(models.TransientModel)  :
    _name = "send.company.satisfaction.survey.line"


    internship_type_id = fields.Many2one(comodel_name="internship.type")
    survey_id = fields.Many2one(comodel_name="survey.survey")
    send_wizard_id = fields.Many2one(
        comodel_name="send.company.satisfaction.survey")


class InstructorAnswerBundle(models.TransientModel):
    _name = "instructor.answer.bundle"

    instructor_id = fields.Many2one(comodel_name="res.partner")
    answer_ids = fields.Many2many(comodel_name="survey.user_input")
    school_year_id = fields.Many2one(comodel_name="school.year")
