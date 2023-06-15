# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

OPPORTUNITY_TYPE = [
    ('opportunity', 'Opportunity'),
    ('internship', 'Internship'),
]


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def get_current_school_year(self):
        return self.env['school.year'].get_current_school_year()

    school_year_id = fields.Many2one(comodel_name="school.year",
                                     default=get_current_school_year)
    opportunity_type = fields.Selection(string="Service Type",
                                        selection=OPPORTUNITY_TYPE)
    internship_line_ids = fields.One2many(comodel_name="internship.line",
                                          inverse_name="lead_id",
                                          string="Internship Lines")
    allowed_group_ids = fields.Many2many(comodel_name="product.product",
                                         compute="_get_related_products",
                                         store=True)
    internship_sale_id = fields.Many2one(comodel_name="sale.order",
                                         compute="compute_sale",
                                         inverse="sale_inverse")
    internship_sale_ids = fields.One2many(comodel_name="sale.order",
                                          inverse_name='opportunity_id')

    def sale_inverse(self):
        for lead in self:
            if len(lead.internship_sale_ids) > 0:
                sale = self.env['sale.order'].browse(
                    lead.internship_sale_ids[0].id)
                sale.opportunity_id = False
            lead.internship_sale_id.opportunity_id = lead

    @api.depends("internship_sale_ids")
    def compute_sale(self):
        for lead in self:
            if len(lead.internship_sale_ids) > 0:
                lead.internship_sale_id = lead.internship_sale_ids[0]

    @api.depends("internship_line_ids")
    def _get_related_products(self):
        for lead in self:
            products = lead.internship_line_ids.mapped("student_group_id")
            lead.allowed_group_ids = products

    def action_sale_quotations_new(self):
        action = super().action_new_quotation()
        if self.opportunity_type == 'internship':
            sale_lines = []
            for line in self.internship_line_ids:
                for sale_line_index in range(line.student_qty):
                    sale_line = line._get_sale_line_info()
                    sale_line.update({'product_uom_qty': 1, 'price_unit': 0})
                    sale_lines.append((0, 0, sale_line))
            action['context'].update(default_order_line=sale_lines,
                                     default_state='internship')
        return action

    def open_quotation(self):
        return {
            "name": _("Sale Form"),
            "view_mode": "form",
            "res_id": self.internship_sale_id.id,
            "res_model": "sale.order",
            'view_id': self.env.ref(
                'sale.view_order_form').id,
            "type": "ir.actions.act_window",
        }

    @api.constrains("school_year_id", "opportunity_type", "partner_id")
    def unique_lead_per_school_year(self):
        for lead in self.filtered(
                lambda x: x.school_year_id and
                          x.opportunity_type == 'internship' and x.partner_id):
            other_lead = self.env['crm.lead'].search([
                ("opportunity_type", "=", "internship"),
                ("partner_id", "=", lead.partner_id.id),
                ("school_year_id", "=", lead.school_year_id.id)])
            if other_lead:
                raise ValidationError(_("Internship opportunity must be "
                                        "unique per school year and customer"))


class InternshipLines(models.Model):
    _name = "internship.line"

    lead_id = fields.Many2one(comodel_name="crm.lead")
    school_year_id = fields.Many2one(comodel_name="school.year",
                                     related="student_group_id.school_year_id",
                                     store=True)
    student_group_id = fields.Many2one(comodel_name="product.product",
                                       string="Student Group")
    student_qty = fields.Integer()

    def _get_sale_line_info(self):
        self.ensure_one()
        return {
            'name': self.student_group_id.name,
            'product_id': self.student_group_id.id,
            'product_uom': self.student_group_id.uom_id.id,
            'internship_line': True,
        }
