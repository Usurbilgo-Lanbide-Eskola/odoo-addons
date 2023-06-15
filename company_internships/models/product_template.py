# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_current_school_year(self):
        return self.env['school.year'].get_current_school_year()

    is_student_group = fields.Boolean("Is Student Group")
    school_year_id = fields.Many2one(
        comodel_name="school.year", default=get_current_school_year,
        string="School Year")
    internship_ids = fields.One2many(comodel_name="school.year.historical",
                                     inverse_name="group_id",
                                     string="Internships", readonly=True)
    lead_line_ids = fields.One2many(comodel_name="internship.line",
                                    inverse_name="student_group_id",
                                    readonly=True)
    students_count = fields.Integer(compute="_compute_students_count",
                                    store=True)
    internship_excluded_count = fields.Integer(
        compute="_compute_students_count"
    )
    internship_students_count = fields.Integer(
        compute="_compute_students_count")
    no_internship_students_count = fields.Integer(
        compute="_compute_students_count")
    accepted_internships = fields.Integer(
        compute="_compute_internship_count")
    pending_qty = fields.Integer(compute="_compute_student_group_leads",
                                 store=True)

    def get_enabled_internship_lines(self):
        self.ensure_one()
        return self.internship_ids.filtered(
                lambda x: x.student_without_internship == False)

    @api.depends("lead_line_ids")
    def _compute_student_group_leads(self):
        for group in self:
            pending_qty = 0
            for lead_line in group.lead_line_ids:
                if not lead_line.lead_id.order_ids:
                    pending_qty += lead_line.student_qty
            group.pending_qty = pending_qty

    @api.depends('internship_ids')
    def _compute_students_count(self):
        for product in self:
            lines = product.get_enabled_internship_lines()
            students_count = self.env["res.partner"].search_count([
                ("student_group_id", "=", product.id),
                ("is_student", "=", True)
            ])
            product.students_count = students_count
            product.internship_excluded_count = len(
                product.internship_ids) - len(lines)
            product.internship_students_count = len(lines.filtered(
                lambda x: x.student_company_id))
            product.no_internship_students_count = len(lines.filtered(
                lambda x: not x.student_company_id))

    def _compute_internship_count(self):
        r = {}
        self.sales_count = 0
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return r
        domain = [
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

    def action_historical_records_lines(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "company_internships.action_school_year_historical")
        return action

    def action_no_assigned_internship_lines(self):
        action = self.action_historical_records_lines()
        action["context"] = {
            'search_default_students_no_assigned_internship': 1,
            'search_default_group_id': self.id,
        }
        return action

    def action_assigned_internship_lines(self):
        action = self.action_historical_records_lines()
        action["context"] = {'search_default_students_assigned_internship': 1,
                             'search_default_group_id': self.id}
        return action

    def action_get_opportunities(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            "crm.crm_lead_action_pipeline")
        products = self.env['product.product'].search([('product_tmpl_id',
                                                        '=', self.id)])
        lead_ids = self.env['internship.line'].search(
            [('student_group_id', 'in', products.ids)]).mapped("lead_id")
        domain = [('id', 'in', lead_ids.ids)]
        action['domain'] = domain
        action['context'] = {
            'search_default_current_school_year': 1,
            'search_default_allowed_group_ids': self.name,
            'search_default_no_order_leads': 1,
        }
        return action

    def action_student_group_sale_lines(self):
        action = self.env['ir.actions.act_window']._for_xml_id(
            "company_internships.action_editable_sale_line")
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
