# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hezkuntza_student_group_id = fields.Many2one(
        comodel_name="hezkuntza.student.group")
    course_id = fields.Many2one(comodel_name="hezkuntza.course",
                                related="hezkuntza_student_group_id.course_id",
                                store=True)
    linguistic_model_id = fields.Many2one(
        comodel_name="hezkuntza.linguistic.model",
        related="hezkuntza_student_group_id.linguistic_model_id", store=True)
    degree_id = fields.Many2one(comodel_name="hezkuntza.degree",
                                related="hezkuntza_student_group_id.degree_id",
                                store=True)
    educational_level_id = fields.Many2one(
        comodel_name="hezkuntza.educational.level",
        related="hezkuntza_student_group_id.educational_level_id", store=True)
    degree_mode_id = fields.Many2one(
        comodel_name="hezkuntza.degree.mode",
        related="hezkuntza_student_group_id.degree_mode_id", store=True)
