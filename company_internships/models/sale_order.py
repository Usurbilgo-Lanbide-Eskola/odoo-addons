# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_internship_line = fields.Boolean(
        compute="_compute_has_internship_line")

    @api.depends("order_line.internship_line")
    def _compute_has_internship_line(self):
        for sale in self:
            sale.has_internship_line = any(
                sale.order_line.mapped("internship_line"))

    def action_confirm(self):
        for order in self:
            for line in order.order_line:
                already_has_internship = line.student_ids.filtered(
                    lambda x: x.internship_of_group_year)
                if already_has_internship:
                    raise ValidationError(_(
                        f"Those students already has an "
                        f"assigned internship:\n "
                        f"{';'.join(already_has_internship.mapped('name'))}"))
        return super().action_confirm()

    # TODO add constrains all lines has same school_year_id lines.map(
    #  "school_year_id") < 2

    # TODO if one line is internship all lines need to be internships


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    student_ids = fields.Many2many(comodel_name="res.partner",
                                   domain="[('is_student', '=', True)]",
                                   copy=False)
    internship_line = fields.Boolean(related="product_id."
                                             "product_tmpl_id.is_student_group"
                                     )
    internship_type = fields.Many2one(comodel_name="internship.type",
                                      string="Internship Type")
    school_year_id = fields.Many2one(comodel_name="school.year",
                                     related="product_id.product_tmpl_id."
                                     "school_year_id")

    @api.constrains('product_id', 'student_ids')
    def check_internship_students(self):
        for line in self:
            is_internship = line.product_id.product_tmpl_id.is_student_group
            if line.student_ids and not is_internship:
                raise ValidationError(_("At least in one line there are "
                                        "students with a product that is not "
                                        "a internship"))

    @api.constrains('product_uom_qty', 'state', 'students_ids')
    def check_all_students_are_assign(self):
        for line in self:
            if line.internship_line and len(line.student_ids) > \
                    line.product_uom_qty and line.state == 'sale':
                raise ValidationError(_("To many students assigned in a line"))