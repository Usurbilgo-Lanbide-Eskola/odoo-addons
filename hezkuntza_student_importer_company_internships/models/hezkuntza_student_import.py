# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class HezkuntzaStudentImportLine(models.Model):
    _inherit = "hezkuntza.student.import"

    def _get_partner_dict(self):
        res = super()._get_partner_dict()
        res.update({'is_student': True})
        return res

    def enroll_in_school_year(self, student):
        super().enroll_in_school_year(student)
        historical_obj = self.env['school.year.historical']
        if not historical_obj.get_active_historical_lines(student):
            student_group = student.student_group_id
            if student_group:
                if isinstance(student_group, int):
                    student_group = self.env['product.template'].browse(
                        student_group)
                school_year = student_group.school_year_id
            else:
                school_year = self.env['school.year'].get_school_year()
            student.write({'student_record_ids': [(0, 0, {
                'school_year_id': school_year.id,
                'group_id': student_group.id})]})

    def delete_rejected_students(self):
        self.mapped_lines.filtered(lambda x: x.reject).delete_related_student()


class HezkuntzaStudentImportLine(models.Model):
    _inherit = "hezkuntza.student.import.line"

    def delete_related_student(self):
        for line in self.filtered(lambda x: x.imported_partner_id):
            student = line.imported_partner_id
            student_records = student.student_record_ids
            student.write({"student_record_ids": [(2, student_records.filtered(
                lambda x: x.school_year_id.id == line.school_year.id).id)]})
            student.student_safe_delete()
