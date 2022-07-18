# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class HezkuntzaStudentImportLine(models.Model):
    _inherit = "hezkuntza.student.import.line"

    group_id = fields.Many2one(comodel_name="hezkuntza.student.group")

    def _get_partner_dict(self):
        res = super()._get_partner_dict()
        if 'hezkuntza_group_id' in res:
            res.pop('hezkuntza_group_id')
            group_of_year = self.group_id.product_ids.filtered(
                lambda x: x.school_year_id.id == self.school_year.id)
            if not group_of_year:
                group_of_year = self.env['product.template'].create(
                    {'name': self.group_id.code, 'is_student_group': True,
                     'list_price': 0, 'type': 'consu', 'school_year_id':
                         self.school_year.id, 'hezkuntza_student_group_id':
                         self.group_id.id})
        res.update(student_group_id=group_of_year.id)
        return res
