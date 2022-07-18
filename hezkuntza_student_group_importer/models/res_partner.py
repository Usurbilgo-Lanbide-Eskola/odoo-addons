# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    hezkuntza_group_id = fields.Many2one(
        comodel_name="hezkuntza.student.group", string="Student Group")
    course_id = fields.Many2one(comodel_name="hezkuntza.course",
                                related="hezkuntza_group_id.course_id",
                                store=True)
    linguistic_model_id = fields.Many2one(
        comodel_name="hezkuntza.linguistic.model",
        related="hezkuntza_group_id.linguistic_model_id", store=True)
    degree_id = fields.Many2one(comodel_name="hezkuntza.degree",
                                related="hezkuntza_group_id.degree_id",
                                store=True)
    educational_level_id = fields.Many2one(
        comodel_name="hezkuntza.educational.level",
        related="hezkuntza_group_id.educational_level_id", store=True)
    degree_mode_id = fields.Many2one(
        comodel_name="hezkuntza.degree.mode",
        related="hezkuntza_group_id.degree_mode_id", store=True)
