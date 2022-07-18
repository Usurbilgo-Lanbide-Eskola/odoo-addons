# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    hezkuntza_group_id = fields.Many2one(
        related='student_group_id.hezkuntza_student_group_id')