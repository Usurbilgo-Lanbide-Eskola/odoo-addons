# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, _


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    repeat_survey = fields.Boolean(string="Repeat Survey")
