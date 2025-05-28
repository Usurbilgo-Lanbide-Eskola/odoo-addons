# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class GenerateNewGroup(models.TransientModel):
    _name = 'generate.new.group'
    _description = 'generate.new.group'

    school_year_id = fields.Many2one("school.year")

    def generate_new_school_year_group(self):
        product_obj = self.env['product.template']
        hezkuntza_group_obj = self.env["hezkuntza.student.group"]
        active_ids = self.env.context.get("active_ids", [])
        for record in hezkuntza_group_obj.browse(active_ids):
            if not record.product_ids.filtered(lambda x: x.school_year_id.id == self.school_year_id.id):
                record.product_ids = [(4, product_obj.create(
                    {'name': record.code, 'is_student_group': True,
                    'list_price': 0, 'type': 'consu', 'school_year_id':
                        self.school_year_id.id}).id)]
