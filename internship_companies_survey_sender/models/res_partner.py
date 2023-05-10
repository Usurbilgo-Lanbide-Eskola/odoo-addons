# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _

AVAILABLE_SCORES = [
    ('0', 'No Score'),
    ('1', 'Very Low'),
    ('2', 'Low'),
    ('3', 'Medium'),
    ('4', 'High'),
    ('5', 'Very High'),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    reputation = fields.Selection(selection=AVAILABLE_SCORES,
                                  string="Reputation",
                                  compute="compute_partner_reputation",
                                  store=True)
    raw_reputation = fields.Float(string="Numerical Reputation",
                                  compute="compute_partner_reputation",
                                  store=True)
    review_qty = fields.Integer(string="Number of Reviews",
                                compute="compute_partner_reputation",
                                compute_sudo=True)
    student_reputation = fields.Selection(
        selection=AVAILABLE_SCORES, string="Reputation",
        compute="compute_student_partner_reputation", store=True)
    student_raw_reputation = fields.Float(
        string="Numerical Reputation",
        compute="compute_student_partner_reputation", store=True)
    student_review_qty = fields.Integer(
        string="Number of Reviews",
        compute="compute_student_partner_reputation", compute_sudo=True)

    def _search_tutor_tutored_students(self, school_year=False):
        self.ensure_one()
        if not self.is_tutor:
            raise UserWarning(_(f"{self.name} is not a tutor"))
        if not school_year:
            school_year = self.env['school.year'].get_school_year()
        search_domain = [
            ('school_year_id', '=', school_year.id),
            ('student_tutor_id', '=', self.id)]
        tutor_students = self.env["school.year.historical"].search(
            search_domain)
        return tutor_students.mapped("active_student_record_ids").mapped(
            "student_instructor_id.parent_id")

    def _get_partner_surveys(self):
        self.ensure_one()
        partner_model_id = self.env['ir.model'].search(
            [('model', '=', 'res.partner')], limit=1)
        survey_type = self.env['survey.type'].search(
            [('model_id', '=', partner_model_id.id)], limit=1)
        return self.env['survey.survey'].search(
            [('survey_type', '=', survey_type.id),
             ('instance_id', '=', self.id)])

    def compute_partner_reputation(self):
        for partner in self:
            partner_surveys = partner._get_partner_surveys()
            answers = self.env['survey.user_input'].search(
                [('survey_id', 'in', partner_surveys.ids),
                 ('scoring_percentage', '!=', 0),
                 ('partner_id.is_student', '=', False)])
            avg_percentage = 0
            answers_qty = len(answers)
            partner.review_qty = answers_qty
            if answers:
                avg_percentage = sum(x.scoring_percentage for x in answers) / \
                                 answers_qty
            max_score = int(max(x[0] for x in AVAILABLE_SCORES))
            raw_reputation = avg_percentage * max_score / 100
            partner.raw_reputation = raw_reputation
            partner.reputation = str(round(raw_reputation))

    def compute_student_partner_reputation(self):
        for partner in self:
            student_partner_surveys = partner._get_partner_surveys()
            answers = self.env['survey.user_input'].search(
                [('survey_id', 'in', student_partner_surveys.ids),
                 ('scoring_percentage', '!=', 0),
                 ('partner_id.is_student', '=', True)])
            avg_percentage = 0
            answers_qty = len(answers)
            partner.student_review_qty = answers_qty
            if answers:
                avg_percentage = sum(x.scoring_percentage for x in answers) / \
                                 answers_qty
            max_score = int(max(x[0] for x in AVAILABLE_SCORES))
            raw_reputation = avg_percentage * max_score / 100
            partner.student_raw_reputation = raw_reputation
            partner.student_reputation = str(round(raw_reputation))
