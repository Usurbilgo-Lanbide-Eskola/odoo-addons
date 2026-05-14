# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class PromoteStudentGroup(models.TransientModel):
    _name = 'promote.student.group'
    _description = 'Promote Student Group to new School Year'

    school_year_id = fields.Many2one("school.year", required=True)

    def action_promote(self):
        product_obj = self.env['product.template']
        active_ids = self.env.context.get("active_ids", [])
        for product in product_obj.browse(active_ids).filtered('is_student_group'):
            student_group = product.hezkuntza_student_group_id
            new_name = student_group.display_name
            if not new_name:
                continue
            if not student_group.product_ids.filtered(
                    lambda x: x.school_year_id.id == self.school_year_id.id):
                new_product = product_obj.create({
                    'name': new_name,
                    'is_student_group': True,
                    'list_price': 0,
                    'type': 'consu',
                    'school_year_id': self.school_year_id.id,
                    'hezkuntza_student_group_id': student_group.id,
                })
                student_group.product_ids = [(4, new_product.id)]
