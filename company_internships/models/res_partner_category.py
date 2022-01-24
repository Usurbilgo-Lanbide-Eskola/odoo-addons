# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResPartnerCategory(models.Model):
    _inherit = "res.partner.category"

    is_student_group = fields.Boolean("Student Group")
    student_group_tutor = fields.Many2many("res.partner", "category_tutor_rel",
                                           "category_id", "partner_id",
                                           string="Student Group Tutor")
