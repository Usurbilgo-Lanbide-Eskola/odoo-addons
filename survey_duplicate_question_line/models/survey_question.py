# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, _


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    def duplicate_question_line(self):
        for line in self:
            line.copy({'title': _(f"{line.title} (copy)")})
