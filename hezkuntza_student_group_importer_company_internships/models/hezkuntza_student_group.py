# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class HezkuntzaStudentGroup(models.Model):
    _inherit = "hezkuntza.student.group"

    product_ids = fields.One2many(comodel_name="product.template",
                                  inverse_name="hezkuntza_student_group_id")


class HezkuntzaStudentImportLine(models.Model):
    _inherit = "hezkuntza.student.import.line"

    group_id = fields.Many2one(comodel_name="hezkuntza.student.group")

    def create_partner(self):
        res = super().create_partner()
        if not self.group_id.product_id:
            product_obj = self.env['product.template']
            self.group_id.product_ids = [(4, product_obj.create(
                {'name': self.group_id.code, 'is_student_group': True,
                 'list_price': 0, 'type': 'consu', 'school_year_id':
                     self.school_year.id}).id)]
        return res
