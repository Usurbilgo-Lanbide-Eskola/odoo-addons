# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_student = fields.Boolean("Is Student")
    is_tutor = fields.Boolean("Is Tutor")
    school_year = fields.Many2many(comodel_name="school.year",
                                   string="School Year")
    internship_count = fields.Integer(compute="_compute_internship_count",
                                      store=True)
    # Field to trigger the compute function
    internship_count_dummy = fields.Integer(
        compute="_compute_internship_count")
    in_active_school_year = fields.Boolean(
        compute="_compute_in_active_school_year", store=True)

    @api.depends("school_year")
    def _compute_in_active_school_year(self):
        for partner in self:
            if partner.is_student:
                active_year = partner.env['school.year'].get_school_year()
                if active_year in partner.school_year:
                    partner.in_active_school_year = True
                    continue
            partner.in_active_school_year = False

    def _compute_internship_count(self):
        for student_id in self:
            internship_count = self.env[
                'sale.order.line'].search_count([("student_ids", "=",
                                                  student_id.id)])
            student_id.internship_count = internship_count
            student_id.internship_count_dummy = internship_count

    def action_view_sale_lines(self):
        '''
        This function returns an action that displays the sale lines from
        partner.
        '''
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sale_order_line_menu.action_orders_lines')
        if self.is_student:
            action['domain'] = [('student_ids', '=', self.id)]
            return action
        return None
