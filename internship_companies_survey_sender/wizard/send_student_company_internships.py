# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SendStudentCompanyInternships(models.TransientModel):
    _inherit = "survey.invite"
    _name = "send.student.company.internships"

    @api.model
    def _get_active_year(self):
        school_year = self.env['school.year'].get_school_year()
        if school_year:
            return school_year.id

    school_year = fields.Many2one(comodel_name="school.year",
                                  default=_get_active_year)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'student_survey_mail_compose_message_ir_attachments_rel', 'wizard_id',
        'attachment_id',
        string='Attachments')
    partner_ids = fields.Many2many(
        'res.partner', 'student_survey_invite_partner_ids', 'invite_id',
        'partner_id', string='Recipients',
        domain="""[
            '|', (survey_users_can_signup, '=', 1),
            '|', (not survey_users_login_required, '=', 1),
                 ('user_ids', '!=', False),
        ]"""
    )

    def _create_student_surveys_answers(self, records):
        survey_type = self.env['survey.type'].search(
            [('model_id', '=', 'res.partner')])
        if not survey_type:
            raise UserError(_("There is not an survey type of a "
                              "'res.partner' model. Create one"))
        surveys = {}
        survey_obj = self.env['survey.survey']
        for record in records:
            student_id = record.student_id
            company_id = record.student_company_id
            new_surveys = survey_obj.with_context(
                    {'school_year_id': self.school_year}).create_child_surveys(
                company_id, self.survey_id, survey_type)
            new_surveys.write({'school_year_id': self.school_year})
            if surveys.get(student_id):
                surveys[student_id] |= survey_obj.with_context(
                    {'school_year_id': self.school_year}).search_child_survey(
                    company_id, self.survey_id, survey_type)
            else:
                surveys[student_id] = survey_obj.with_context(
                    {'school_year_id': self.school_year}).search_child_survey(
                    company_id, self.survey_id, survey_type)

        answers = self._prepare_student_answers(surveys)
        for record in records:
            record.answer_id = record.get_record_last_answer()
        return answers

    def _prepare_student_answers(self, surveys):
        def _update_answers(answers, student, answer):
            if answers.get(student):
                answers[student] |= answer
            else:
                answers[student] = answer
        answers = {}
        for student, surveys in surveys.items():
            for survey in surveys:
                existing_answer = self.env['survey.user_input'].search([
                    ('survey_id', '=', survey.id),
                    ('partner_id', '=', student.id),
                ], order='create_date desc', limit=1)
                if existing_answer:
                    if self.existing_mode == 'resend':
                        _update_answers(answers, student, existing_answer)
                else:
                    _update_answers(answers, student, survey._create_answer(
                        partner=student, check_attempts=False,
                        **self._get_answers_values()))
        return answers

    def _send_students_mail(self, bundle):
        """ Create mail specific for recipient containing notably
        its access token """
        subject = self.env['mail.render.mixin'].with_context(
            safe=True)._render_template(self.subject,
                                        'student.answer.bundle',
                                        bundle.ids, post_process=True)[
            bundle.id]
        body = self.env['mail.render.mixin']._render_template(
            self.body, 'student.answer.bundle', bundle.ids,
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
            'recipient_ids': [(4, bundle.student_id.id)]
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
                template_ctx = {
                    'message': self.env['mail.message'].sudo().new(
                        dict(body=mail_values['body_html'],
                             record_name=self.survey_id.title)),
                    'model_description': self.env['ir.model']._get(
                        'survey.survey').display_name,
                    'company': self.env.company,
                }
                body = template._render(template_ctx, engine='ir.qweb',
                                        minimal_qcontext=True)
                mail_values['body_html'] = self.env[
                    'mail.render.mixin']._replace_local_links(body)

        return self.env['mail.mail'].sudo().create(mail_values)

    def action_invite_students(self):
        record_ids = self._context.get("active_ids")
        records = self.env['school.year.historical'].search([
            ('id', 'in', record_ids),
            ('school_year_id', '=', self.school_year.id)
        ])
        answers = self._create_student_surveys_answers(records)
        answer_bundle = self.env['student.answer.bundle']
        for student, answer_id in answers.items():
            bundle = answer_bundle.create({'student_id': student.id,
                                           'answer_ids': answer_id})
            self._send_students_mail(bundle)
        return {'type': 'ir.actions.act_window_close'}


class StudentAnswerBundle(models.TransientModel):
    _name = "student.answer.bundle"

    student_id = fields.Many2one(comodel_name="res.partner")
    answer_ids = fields.Many2many(comodel_name="survey.user_input")
