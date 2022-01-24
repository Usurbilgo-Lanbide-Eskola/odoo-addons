# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_internship_line = fields.Boolean(
        compute="_compute_has_internship_line")

    @api.depends("order_line.internship_line")
    def _compute_has_internship_line(self):
        for sale in self:
            sale.has_internship_line = any(
                sale.order_line.mapped("internship_line"))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    student_ids = fields.Many2many(comodel_name="res.partner",
                                   domain="[('is_student', '=', True)]")
    internship_line = fields.Boolean(related="product_id."
                                             "product_tmpl_id.is_internship")
