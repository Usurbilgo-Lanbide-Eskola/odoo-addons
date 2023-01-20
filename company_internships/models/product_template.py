# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_active_school_year(self):
        return self.env['school.year'].get_school_year()

    is_student_group = fields.Boolean("Is Student Group")
    school_year_id = fields.Many2one(
        comodel_name="school.year", default=get_active_school_year,
        string="School Year")
    students_count = fields.Integer(compute="_compute_students_count",
                                    store=True)
    students_count_dummy = fields.Integer(compute="_compute_students_count")
    internship_quotations_count = fields.Integer(
        compute="_compute_internship_quotations_count")
    internship_students_count = fields.Integer(
        compute="_compute_students_count")
    accepted_internships = fields.Integer(
        compute="_compute_internship_count")
    no_internship_students_count = fields.Integer(
        compute="_compute_students_count")
    lead_qty = fields.Integer(compute="_compute_student_group_leads",
                              store=True)
    pending_qty = fields.Integer(compute="_compute_student_group_leads",
                                 store=True)
    lead_qty_dummy = fields.Integer(compute="_compute_student_group_leads")

    @api.depends("students_count")
    def _compute_student_group_leads(self):
        lead_lines = self.env['internship.line']
        for group in self:
            lead_qty = sum(lead_lines.search(
                [('student_group_id', '=', group.id)]
                                  ).mapped('student_qty'))
            group.lead_qty = lead_qty
            group.lead_qty_dummy = lead_qty
            group.pending_qty = group.students_count - lead_qty


    @api.depends('internship_students_count')
    def _compute_students_count(self):
        for product in self:
            domain = [('is_student', '=', True), ('student_group_id', '=',
                                                  product.id)]
            students = self.env['res.partner'].search(domain)
            students_count = len(students)
            product.students_count = students_count
            product.students_count_dummy = students_count
            assigned_students = len(students.filtered(
                lambda x: x.internship_of_group_year))
            product.internship_students_count = assigned_students
            product.no_internship_students_count = students_count - \
                                                   assigned_students

    def _compute_internship_count(self):
        r = {}
        self.sales_count = 0
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return r

        done_states = self.env['sale.report']._get_done_states()

        domain = [
            ('state', 'in', done_states),
            ('product_id', 'in', self.ids),
        ]
        for group in self.env['sale.report'].read_group(
                domain, ['product_id', 'product_uom_qty'], ['product_id']):
            r[group['product_id'][0]] = group['product_uom_qty']
        for product in self:
            if not product.id:
                product.accepted_internships = 0.0
                continue
            product.accepted_internships = float_round(
                r.get(product.id, 0),
                precision_rounding=product.uom_id.rounding)
        return r

    def _compute_internship_quotations_count(self):
        r = {}
        self.sales_count = 0
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return r

        quotation_states = ['draft', 'sent']

        domain = [
            ('state', 'in', quotation_states),
            ('product_id', 'in', self.ids),
        ]
        for group in self.env['sale.report'].read_group(
                domain, ['product_id', 'product_uom_qty'], ['product_id']):
            r[group['product_id'][0]] = group['product_uom_qty']
        for product in self:
            if not product.id:
                product.internship_quotations_count = 0.0
                continue
            product.internship_quotations_count = float_round(
                r.get(product.id, 0),
                precision_rounding=product.uom_id.rounding)
        return r

    def action_student_group_sale_lines(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            "sale_order_line_menu.action_orders_lines")
        products = self.env['product.product'].search([('product_tmpl_id',
                                                        '=', self.id)])
        sale_lines = self.env['sale.order.line'].search(
            [('product_id', 'in', products.ids)])
        domain = [('id', 'in', sale_lines.ids)]
        action['domain'] = domain
        return action

    def _get_student_action(self, domain):
        action = self.env['ir.actions.act_window']._for_xml_id(
            'company_internships.action_internships_students')
        action['domain'] = domain
        return action

    def action_group_students(self):
        domain = [('is_student', '=', True),
                  ('student_group_id', '=', self.id)]
        return self._get_student_action(domain)

    def action_assigned_students(self):
        sale_lines = self.env['sale.order.line'].search(
            [('state', 'in', ['sale', 'done']), ('product_id', '=', self.id)])
        domain = [('id', 'in', sale_lines.student_ids.ids)]
        return self._get_student_action(domain)

    def action_not_assigned_students(self):
        sale_lines = self.env['sale.order.line'].search(
            [('state', 'in', ['sale', 'done']), ('product_id', '=', self.id)])
        domain = [('is_student', '=', True),
                  ('student_group_id', '=', self.id),
                  ('id', 'not in', sale_lines.student_ids.ids)]
        return self._get_student_action(domain)
