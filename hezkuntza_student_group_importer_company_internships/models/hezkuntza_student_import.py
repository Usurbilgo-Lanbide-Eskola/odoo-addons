# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, _
from odoo.exceptions import UserError


class HezkuntzaStudentImportLine(models.Model):
    _inherit = "hezkuntza.student.import.line"

    group_id = fields.Many2one(comodel_name="hezkuntza.student.group")

    def _get_group_of_year(self):
        return self.group_id.product_ids.filtered(
            lambda x: x.school_year_id.id == self.school_year.id)

    def _create_group_of_year(self):
        if not self.school_year or not self.group_id:
            raise UserError(_(f"Line with Hezkuntza id:{self.id_hezkuntza} "
                              f"has no group"))
        return self.env['product.template'].create(
                    {'name': self.group_id.code, 'is_student_group': True,
                     'list_price': 0, 'type': 'consu', 'school_year_id':
                         self.school_year.id, 'hezkuntza_student_group_id':
                         self.group_id.id})

    def _get_partner_dict(self):
        res = super()._get_partner_dict()
        if 'hezkuntza_group_id' in res:
            res.pop('hezkuntza_group_id')
            group_of_year = self._get_group_of_year()
            if not group_of_year:
                group_of_year = self._create_group_of_year()
        res.update(student_group_id=group_of_year.id)
        return res

    def create_partner(self):
        res = super().create_partner()
        if not self.group_id.product_ids:
            product_obj = self.env['product.template']
            self.group_id.product_ids = [(4, product_obj.create(
                {'name': self.group_id.code, 'is_student_group': True,
                 'list_price': 0, 'type': 'consu', 'school_year_id':
                     self.school_year.id}).id)]
        return res

    def enroll_in_school_year(self, student):
        res = super().enroll_in_school_year(student)
        group_of_year = self._get_group_of_year()
        if not group_of_year:
            group_of_year = self._create_group_of_year()
        student.student_group_id = group_of_year
        return res
