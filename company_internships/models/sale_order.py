# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from itertools import groupby


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_current_school_year(self):
        return self.env['school.year'].get_current_school_year()

    has_internship_line = fields.Boolean(
        compute="_compute_has_internship_line")
    state = fields.Selection(selection_add=[('internship', 'Internship')],
                             default="draft")
    school_year_id = fields.Many2one(comodel_name="school.year",
                                     default=get_current_school_year)

    # @api.onchange("has_internship_line")
    # def change_status(self):
    #     if self.has_internship_line:
    #         self.state = 'internship'

    @api.constrains("opportunity_id")
    def check_lead_has_other_sale(self):
        for sale in self:
            opportunity = sale.opportunity_id
            if opportunity.opportunity_type == 'internship' and (sale.id not in
                    opportunity.internship_sale_ids._ids):
                raise ValidationError(_("Opportunity has already a sale"))

    @api.depends("order_line.internship_line")
    def _compute_has_internship_line(self):
        for sale in self:
            sale.has_internship_line = any(
                sale.order_line.mapped("internship_line"))

    def action_cancel(self):
        res = super().action_cancel()
        if self.has_internship_line:
            self.order_line.write({'internship_record_id': False})
        return res

    @api.constrains("school_year_id", "has_internship_line", "partner_id")
    def unique_sale_per_school_year(self):
        for sale in self.filtered(
                lambda x: x.school_year_id and x.has_internship_line and
                          x.partner_id):
            other_lead = self.env['crm.lead'].search([
                ("opportunity_type", "=", "internship"),
                ("partner_id", "=", sale.partner_id.id),
                ("school_year_id", "=", sale.school_year_id.id)])
            if other_lead:
                raise ValidationError(_("Internship sale must be "
                                        "unique per school year and customer"))

    @api.constrains("school_year_id", "order_line")
    def same_school_year(self):
        for sale in self.filtered(lambda x: x.has_internship_line):
            lines = sale.order_line.filtered(
                lambda x: x.internship_line and x.school_year_id.id !=
                          sale.school_year_id.id)
            if lines:
                raise ValidationError(_("All internship lines must have the "
                                        "same school year of the sale order"))

    @api.constrains("order_line")
    def all_lines_internships(self):
        for sale in self.filtered(lambda x: x.order_line):
            internship_lines = sale.order_line.filtered(
                lambda x: x.display_type == False).mapped("internship_line")
            if any(internship_lines) and not all(internship_lines):
                raise ValidationError(_("if a line has a internship all "
                                        "lines must be internship lines"))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    internship_record_id = fields.Many2one(
        comodel_name="school.year.historical",
        compute="compute_record", inverse="record_inverse",
        copy=False, search="_search_internship")
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
    internship_line = fields.Boolean(
        related="product_id.product_tmpl_id.is_student_group",
        string="Is Internship Line")
    school_year_id = fields.Many2one(comodel_name="school.year",
                                     related="product_id.product_tmpl_id."
                                             "school_year_id")
    record_ids = fields.One2many(comodel_name="school.year.historical",
                                 inverse_name="record_sale_line_id")

    _sql_constraints = [
        ('accountable_required_fields',
         "CHECK(display_type IS NOT NULL OR internship_line IS NOT NULL ("
         "product_id IS NOT NULL AND product_uom IS NOT NULL))",
         "Missing required fields on accountable sale order line.")]

    def _search_internship(self, operator, value):
        records = self.env['school.year.historical'].search([
            ('id', operator, value)])
        return [('id', 'in', records.mapped('record_sale_line_id').ids)]

    def record_inverse(self):
        for line in self:
            if len(line.record_ids) > 0:
                sale = self.env['sale.order'].browse(
                    line.record_ids[0].id)
                sale.record_sale_line_id = False
            line.internship_record_id.record_sale_line_id = line

    @api.depends("record_ids")
    def compute_record(self):
        for line in self:
            if len(line.record_ids) > 0:
                line.internship_record_id = line.record_ids[0]
            else:
                line.internship_record_id = False

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
