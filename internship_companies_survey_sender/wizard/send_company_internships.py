# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SendCompanyInternships(models.TransientModel):
    _inherit = "survey.invite"
    _name = "send.company.internships"

    @api.model
    def _get_active_year(self):
        school_year = self.env['school.year'].get_school_year()
        if school_year:
            return school_year.id

    tutor_survey_line_ids = fields.One2many(
        comodel_name="send.company.internships.line",
        inverse_name="send_wizard_id")

    school_year = fields.Many2one(comodel_name="school.year",
                                  default=_get_active_year)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'tutor_survey_mail_compose_message_ir_attachments_rel', 'wizard_id',
        'attachment_id',
        string='Attachments')
    partner_ids = fields.Many2many(
        'res.partner', 'tutor_survey_invite_partner_ids', 'invite_id',
        'partner_id', string='Recipients',
        domain="""[
            '|', (survey_users_can_signup, '=', 1),
            '|', (not survey_users_login_required, '=', 1),
                 ('user_ids', '!=', False),
        ]"""
    )
    select_survey_to_send = fields.Boolean("Custom Sending")

    def _create_internship_survey_title(self, student_id, school_year):
        internship_line = self.env["school.year.historical"].search(
            [("student_id", "=", student_id),
             ("school_year_id", "=", school_year.id)])
        if len(internship_line) != 1:
            raise UserError(_(f"Multiple internship lines for student: "
                              f"{internship_line[0].student_id.name}"))
        return (f"{internship_line.student_id.name} - "
                f"{internship_line.student_company_id.display_name}")

    def _add_tutor_surveys(self, generate_new=False):
        survey_type = self.env['survey.type'].search([('model_id', '=',
                                                       'res.partner')])
        if not survey_type:
            raise UserError(_("There is not an survey type of a "
                              "'res.partner' model. Create one"))
        for line in self.tutor_survey_line_ids:
            tutor = line.tutor_id
            if generate_new:
                students = tutor._search_tutor_tutored_students(
                    self.school_year)
                new_surveys = self.env['survey.survey'].create_child_surveys(
                    students, self.survey_id, survey_type)
                new_surveys.write({'school_year_id': self.school_year.id})
                for survey in new_surveys:
                    survey.title = self._create_internship_survey_title(
                        survey.instance_id, self.school_year)
                    survey.company_id = self.env["school.year.historical"
                    ].get_student_company(
                        survey.instance_id, self.school_year)
            surveys = self._get_tutor_survey_lines(
                tutor, self.survey_id, self.school_year)._ids
            line.survey_ids = surveys

    def _get_tutor_survey_lines(self, tutor, survey, school_year=False):
        if isinstance(tutor, int):
            tutor = self.env['res.partner'].browse(tutor)
        students = tutor._search_tutor_tutored_students(school_year)
        return self.env["survey.survey"].search([
            ('parent_template_id', '=', survey.id),
            ('instance_id', 'in', students.ids)])

    def get_not_completed_surveys(self):
        self._add_tutor_surveys(generate_new=True)
        answer_obj = self.env['survey.user_input']
        for line in self.tutor_survey_line_ids:
            tutor = line.tutor_id
            surveys = self._get_tutor_survey_lines(
                tutor, self.survey_id, self.school_year)
            line.survey_ids = surveys.filtered(lambda x: answer_obj.search(
                [('survey_id', '=', x.id),
                 ('partner_id', '=', tutor.id)],
                order='create_date desc', limit=1).state != 'done')
        return {'view_mode': 'form', 'res_model': "send.company.internships",
            'res_id': self.id, 'target': 'new', 'type':
                    'ir.actions.act_window', }

    @api.onchange('survey_id')
    def _onchange_survey_id(self):
        if self.env.context.get('active_model') == 'res.partner':
            lines = []
            for old_line in self.tutor_survey_line_ids:
                lines.append((2, old_line.id))
            if self.survey_id:
                tutors = self._context.get("active_ids")
                for tutor in tutors:
                    line = {'tutor_id': tutor}
                    lines.append((0, 0, line))
            self.update({
                'tutor_survey_line_ids': lines
            })

    def _prepare_answers(self):
        def _update_answers(answers, tutor, answer):
            if answers.get(tutor):
                answers[tutor] |= answer
            else:
                answers[tutor] = answer

        answers = {}
        for surveys_line in self.tutor_survey_line_ids:
            for survey in surveys_line.survey_ids:
                tutor = surveys_line.tutor_id
                existing_answer = self.env['survey.user_input'].search([
                    ('survey_id', '=', survey.id),
                    ('partner_id', '=', tutor.id),
                ], order='create_date desc', limit=1)
                if existing_answer:
                    if self.existing_mode == 'resend':
                        _update_answers(answers, tutor, existing_answer)
                else:
                    _update_answers(answers, tutor, survey._create_answer(
                        partner=tutor, check_attempts=False,
                        **self._get_answers_values()))
        return answers

    def _send_mail(self, bundle):
        """ Create mail specific for recipient containing notably
        its access token """
        subject = self.env['mail.render.mixin'].with_context(
            safe=True)._render_template(self.subject,
                                        'tutor.answer.bundle',
                                        bundle.ids, post_process=True)[
            bundle.id]
        body = self.env['mail.render.mixin']._render_template(
            self.body, 'tutor.answer.bundle', bundle.ids,
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
            'recipient_ids': [(4, bundle.tutor_id.id)]
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

    def action_invite(self):
        if not self.select_survey_to_send:
            self._add_tutor_surveys(generate_new=True)
        answers = self._prepare_answers()
        answer_bundle = self.env['tutor.answer.bundle']
        for tutor, answer_ids in answers.items():
            bundle = answer_bundle.create({
                'tutor_id': tutor.id,
                'answer_ids': [(6, 0, answer_ids.ids)],
                'school_year_id': answer_ids[0].school_year_id.id})
            self._send_mail(bundle)
        return {'type': 'ir.actions.act_window_close'}


class SendCompanyInternshipsLine(models.TransientModel):
    _name = "send.company.internships.line"

    tutor_id = fields.Many2one(comodel_name="res.partner", domain=[(
        'is_tutor', '=', True)])
    survey_ids = fields.Many2many(comodel_name="survey.survey")
    send_wizard_id = fields.Many2one(
        comodel_name="send.company.internships")
    tutor_sent_surveys = fields.Many2many(
        comodel_name="survey.survey",
        relation="sent_surveys_rel",
        compute="_compute_sent_surveys",
        compute_sudo=True,
        store=True,
    )

    @api.depends("send_wizard_id.survey_id", "send_wizard_id.school_year",
                 "tutor_id")
    def _compute_sent_surveys(self):
        for line in self:
            wiz = line.send_wizard_id
            surveys = wiz._get_tutor_survey_lines(
                line.tutor_id, wiz.survey_id, wiz.school_year)
            line.tutor_sent_surveys = surveys


class TutorAnswerBundle(models.TransientModel):
    _name = "tutor.answer.bundle"

    tutor_id = fields.Many2one(comodel_name="res.partner", domain=[(
        'is_tutor', '=', True)])
    answer_ids = fields.Many2many(comodel_name="survey.user_input")
    school_year_id = fields.Many2one(comodel_name="school.year")

