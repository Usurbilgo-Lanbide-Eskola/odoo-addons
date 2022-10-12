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
                                  compute="compute_partner_reputation")

    def _search_tutor_tutored_students(self, school_year=False):
        self.ensure_one()
        if not self.is_tutor:
            raise UserWarning(_(f"{self.name} is not a tutor"))
        if not school_year:
            school_year = self.env['school.year'].get_school_year()
        active_year = self.env['school.year'].get_school_year()
        search_domain = [('is_student', '=', True),
                         ('student_tutor', '=', self.id)]
        model = "res.partner"
        field = "student_instructor"
        # if not active school year search in historical data
        if school_year.id != active_year.id:
            field = 'student_instructor_id'
            model = 'school.year.historical'
            search_domain = [
                ('school_year_id', '=', school_year.id),
                ('student_tutor_id', '=', self.id)]
        tutor_students = self.env[model].search(search_domain)
        return tutor_students.mapped(
            f"{field}.parent_id")

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
                 ('scoring_percentage', '!=', 0)])
            avg_percentage = 0
            if answers:
                avg_percentage = sum(x.scoring_percentage for x in answers) / \
                    len(answers)
            max_score = int(max(x[0] for x in AVAILABLE_SCORES))
            partner.reputation = str(round(avg_percentage * max_score / 100))

