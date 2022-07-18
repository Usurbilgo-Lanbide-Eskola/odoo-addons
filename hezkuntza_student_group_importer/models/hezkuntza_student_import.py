# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import xlrd
from odoo import fields, models


class HezkuntzaStudentImport(models.Model):
    _inherit = "hezkuntza.student.import"

    def get_student_group(self, values):
        course = values['CURSO']
        linguistic_model = values['DES_MODELO_LINGUIS']
        degree = values['COD_CICLO_MODALIDAD']
        degree_desc = values['DES_CICLO_MODALIDAD']
        educational_level = values['COD_NIVEL_EDUCATIVO']
        educational_level_desc = values['DES_NIVEL_EDUCATIVO']
        degree_mode = values['COD_MOD_IMPARTICION']
        degree_mode_desc = values['DES_MOD_IMPARTICION']
        course_obj = self.env['hezkuntza.course']
        linguistic_model_obj = self.env['hezkuntza.linguistic.model']
        degree_obj = self.env['hezkuntza.degree']
        educational_level_obj = self.env['hezkuntza.educational.level']
        degree_mode_obj = self.env['hezkuntza.degree.mode']
        course_id = course_obj.search([('hezkuntza_code', '=', course)])
        if not course_id:
            course_id = course_obj.create({'hezkuntza_code': course})
        linguistic_model_id = self.env['hezkuntza.linguistic.model'].search(
            [('hezkuntza_code', '=', linguistic_model)])
        if not linguistic_model_id:
            linguistic_model_id = linguistic_model_obj.create({
                'hezkuntza_code': linguistic_model})
        degree_id = self.env['hezkuntza.degree'].search(
            [('hezkuntza_code', '=', degree)])
        if not degree_id:
            degree_id = degree_obj.create({'hezkuntza_code': degree,
                                           'description': degree_desc})
        educational_level_id = self.env['hezkuntza.educational.level'].search(
            [('hezkuntza_code', '=', educational_level)])
        if not educational_level_id:
            educational_level_id = educational_level_obj.create(
                {'hezkuntza_code': educational_level,
                 'description': educational_level_desc})
        degree_mode_id = self.env['hezkuntza.degree.mode'].search(
            [('hezkuntza_code', '=', degree_mode)])
        if not degree_mode_id:
            degree_mode_id = degree_mode_obj.create(
                {'hezkuntza_code': degree_mode,
                 'description': degree_mode_desc})
        student_group_obj = self.env['hezkuntza.student.group']
        student_group_id = student_group_obj.search([
            ('course_id', '=', course_id.id),
            ('linguistic_model_id', '=', linguistic_model_id.id),
            ('degree_id', '=', degree_id.id),
            ('educational_level_id', '=', educational_level_id.id),
            ('degree_mode_id', '=', degree_mode_id.id)
        ])
        if not student_group_id:
            student_group_id = student_group_obj.create({
                'course_id': course_id.id,
                'linguistic_model_id': linguistic_model_id.id,
                'degree_id': degree_id.id,
                'educational_level_id': educational_level_id.id,
                'degree_mode_id': degree_mode_id.id,
            })
        return student_group_id

    def _get_student_group_lines(self):
        if self.file:
            book = xlrd.open_workbook(
                file_contents=base64.b64decode(self.file))
            sheet = book.sheet_by_name('Des_Sol_Mat')
            headers = [header.value for header in sheet.row(0)]
            student_group = {}
            index_id_hezkuntza = headers.index('DIE_ALU')
            for row in range(1, sheet.nrows):
                id_student = sheet.cell_value(row, index_id_hezkuntza)
                if id_student in student_group:
                    continue
                line_values = []
                for col in range(sheet.ncols):
                    line_values.append(sheet.cell_value(row, col))
                line_dict = dict(zip(headers, line_values))
                student_group[id_student] = line_dict
            return student_group

    def import_lines(self):
        res = super().import_lines()
        student_group_lines = self._get_student_group_lines()
        for line in self.mapped_lines:
            group_values = student_group_lines.get(line.id_hezkuntza)
            if group_values:
                line.group_id = self.get_student_group(group_values)
        return res


class HezkuntzaStudentImportLine(models.Model):
    _inherit = "hezkuntza.student.import.line"

    group_id = fields.Many2one(comodel_name="hezkuntza.student.group")

    def _get_partner_dict(self):
        res = super()._get_partner_dict()
        res.update(hezkuntza_group_id=self.group_id.id)
        return res
