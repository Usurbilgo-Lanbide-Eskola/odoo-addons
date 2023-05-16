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

    # TODO add constrains all lines has same school_year_id lines.map(
    #  "school_year_id") < 2

    # TODO if one line is internship all lines need to be internships


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    internship_record_id = fields.Many2one(
        comodel_name="school.year.historical", copy=False)
    instructor_id = fields.Many2one(
        comodel_name='res.partner',
        related="internship_record_id.student_instructor_id",
        domain="[('company_instructor', '=', True),"
               "('parent_id', '=', order_id.partner_id)]",
        inverse="set_internship_instructor")
    tutor_id = fields.Many2one(
        comodel_name='res.partner',
        related="internship_record_id.student_tutor_id",
        domain=[('is_tutor', '=', True)],
        inverse="set_internship_tutor")
    internship_type_id = fields.Many2one(
        comodel_name='internship.type',
        string="Internship Type",
        related="internship_record_id.internship_type",
        inverse="set_internship_type")
    internship_line = fields.Boolean(related="product_id."
                                             "product_tmpl_id.is_student_group"
                                     )
    school_year_id = fields.Many2one(comodel_name="school.year",
                                     related="product_id.product_tmpl_id."
                                     "school_year_id")

    def set_internship_type(self):
        if self.instructor_id:
            type_id = self.internship_type_id.id
            self.internship_record_id.internship_type = type_id

    def set_internship_tutor(self):
        if self.instructor_id:
            tutor_id = self.tutor_id.id
            self.internship_record_id.student_tutor_id = tutor_id

    def set_internship_instructor(self):
        if self.instructor_id:
            instructor = self.instructor_id
            self.internship_record_id.student_instructor_id = instructor.id
            company_id = instructor.id if instructor.is_company else \
                instructor.parent_id.id
            self.internship_record_id.student_company_id = company_id

    @api.constrains('product_id', 'internship_record_id')
    def check_internship_students(self):
        for line in self:
            is_internship = line.product_id.product_tmpl_id.is_student_group
            if line.internship_record_id and not is_internship:
                raise ValidationError(_("At least in one line there are "
                                        "students with a product that is not "
                                        "a internship"))

    @api.constrains('product_uom_qty', 'state', 'students_ids')
    def check_all_students_are_assign(self):
        for line in self:
            if line.internship_line and line.product_uom_qty != 1 \
                    and line.state == 'sale':
                raise ValidationError(_("Internship line qty must be 1"))
