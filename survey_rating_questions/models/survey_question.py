# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    is_rating_question = fields.Boolean("Rating Question")

    @api.constrains('question_type')
    def rating_question_must_be_simple_choice(self):
        for question in self:
            if question.is_rating_question and question.question_type != \
                    'simple_choice':
                raise UserError(_("A rating question must be of type simple "
                                  "choice"))

    @api.onchange('question_type')
    def onchange_question_type(self):
        for question in self:
            if question.is_rating_question:
                question.is_rating_question = False
