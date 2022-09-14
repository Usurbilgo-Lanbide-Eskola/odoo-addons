# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class HezkuntzaStudentGroup(models.Model):
    _inherit = "hezkuntza.student.group"

    product_ids = fields.One2many(comodel_name="product.template",
                                  inverse_name="hezkuntza_student_group_id")
