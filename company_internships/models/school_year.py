# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class SchoolYear(models.Model):
    _inherit = "school.year"

    def school_year_deactivate_process(self):
        partner_obj = self.env['res.partner']
        for student in partner_obj.search([('is_student', '=', True)]):
            student.archive_year_data()
            student.active = False
        student_groups = self.env['product.template'].search([(
            'school_year_id', '=', self.id)])
        student_groups.write({'active': False})
        return super().school_year_deactivate_process()

    def school_year_activate_process(self):
        student_records_obj = self.env['school.year.historical']
        records = student_records_obj.search(
            [('school_year_id', '=', self.id)])
        for record in records:
            student = record.unarchive_year_data()
            student.active = True
        domain = [
            ('school_year_id', '=', self.id),
            '|', ('active', '=', False), ('active', '=', True)]
        student_groups = self.env['product.template'].search(domain)
        student_groups.write({'active': True})
        return super().school_year_activate_process()
