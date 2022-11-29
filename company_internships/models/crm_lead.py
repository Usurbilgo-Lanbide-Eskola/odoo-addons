# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _

OPPORTUNITY_TYPE = [
    ('opportunity', 'Opportunity'),
    ('internship', 'Internship'),
]


class CrmLead(models.Model):
    _inherit = "crm.lead"

    opportunity_type = fields.Selection(string="Service Type",
                                        selection=OPPORTUNITY_TYPE)
    internship_line_ids = fields.One2many(comodel_name="internship.line",
                                          inverse_name="lead_id",
                                          string="Internship Lines")

    def action_sale_quotations_new(self):
        action = super().action_new_quotation()
        if self.internship_line_ids:
            sale_lines = []
            for line in self.internship_line_ids:
                sale_lines.append((0, 0,
                                   {'name': line.student_group_id.name,
                                    'product_id': line.student_group_id.id,
                                    'product_uom_qty': line.student_qty,
                                    'product_uom':
                                        line.student_group_id.uom_id.id,
                                    'price_unit': 0}))
            action['context'].update(default_order_line=sale_lines)
        return action


class InternshipLines(models.Model):
    _name = "internship.line"

    lead_id = fields.Many2one(comodel_name="crm.lead")
    student_group_id = fields.Many2one(comodel_name="product.product",
                                       string="Student Group")
    student_qty = fields.Integer()
