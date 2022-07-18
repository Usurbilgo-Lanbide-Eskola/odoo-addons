# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    @api.depends('user_input_line_ids.answer_score',
                 'user_input_line_ids.question_id',
                 'predefined_question_ids.answer_score')
    def _compute_scoring_values(self):
        super()._compute_scoring_values()
        for user_input in self:
            rating_questions = user_input.predefined_question_ids.filtered(
                lambda x: x.is_rating_question)
            if rating_questions:
                answered_ratings = user_input.user_input_line_ids.mapped(
                    'question_id').filtered(lambda x: x.is_rating_question)
                unanswered_ratings = rating_questions - answered_ratings
                answers_to_compute = user_input.predefined_question_ids - \
                    unanswered_ratings
                total_possible_score = 0
                for question in answers_to_compute:
                    if question.question_type in [
                        'simple_choice', 'multiple_choice'] and not \
                            question.is_rating_question:
                        total_possible_score += sum(
                            score for score in
                            question.mapped(
                                'suggested_answer_ids.answer_score')
                            if score > 0)
                    elif question.question_type == 'simple_choice':
                        total_possible_score += max(
                            score for score in
                            question.mapped(
                                'suggested_answer_ids.answer_score')
                            if score > 0)
                    elif question.is_scored_question:
                        total_possible_score += question.answer_score

                if total_possible_score == 0:
                    user_input.scoring_percentage = 0
                    user_input.scoring_total = 0
                else:
                    score_percentage = (
                        user_input.scoring_total / total_possible_score) * 100
                    user_input.scoring_percentage = round(
                        score_percentage, 2) if score_percentage > 0 else 0
