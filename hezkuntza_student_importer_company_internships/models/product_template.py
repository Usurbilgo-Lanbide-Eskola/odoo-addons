# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    level = fields.Many2one(comodel_name="")