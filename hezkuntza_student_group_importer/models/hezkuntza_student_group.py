# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class HezkuntzaStudentgroup(models.Model):
    _name = "hezkuntza.student.group"
    _rec_name = "code"

    code = fields.Char("Code")
    description = fields.Char("Description")
    course_id = fields.Many2one(comodel_name="hezkuntza.course")
    linguistic_model_id = fields.Many2one(
        comodel_name="hezkuntza.linguistic.model")
    degree_id = fields.Many2one(comodel_name="hezkuntza.degree")
    educational_level_id = fields.Many2one(
        comodel_name="hezkuntza.educational.level")
    degree_mode_id = fields.Many2one(comodel_name="hezkuntza.degree.mode")
    speciality_id = fields.Many2one(comodel_name="hezkuntza.speciality",
                                    related="degree_id.speciality_id",
                                    store=True)

    def recalculate_code(self):
        for group in self:
            group.code = group.get_code(
                course_id=group.course_id,
                linguistic_model_id=group.linguistic_model_id,
                degree_id=group.degree_id,
                educational_level_id=group.educational_level_id,
                degree_mode_id=group.degree_mode_id,
            )

    def get_code(self, **kwargs):
        def get_instance(model, instance):
            if isinstance(instance, int):
                return self.env[model].browse(instance)
            return instance
        course = kwargs.get('course_id', '')
        course_name = get_instance(
            'hezkuntza.course', course).odoo_code or '' if course else ''
        linguistic_model = kwargs.get('linguistic_model_id', '')
        linguistic_model_name = get_instance(
            'hezkuntza.linguistic.model', linguistic_model).odoo_code or '' \
            if linguistic_model else ''
        degree = kwargs.get('degree_id', '')
        degree_name = get_instance(
            'hezkuntza.degree', degree).odoo_code or '' if degree else ''
        educational_level = kwargs.get('educational_level_id', '')
        educational_level_name = get_instance(
            'hezkuntza.educational.level', educational_level).odoo_code or '' \
            if educational_level else ''
        degree_mode = kwargs.get('degree_mode_id', '')
        degree_mode_name = get_instance(
            'hezkuntza.degree.mode', degree_mode).odoo_code or '' \
            if degree_mode else ''
        return f"{course_name}{linguistic_model_name}{degree_name}" \
               f"{educational_level_name}{degree_mode_name}"

    @api.model
    def create(self, vals=None):
        if not vals.get("code"):
            code = self.get_code(**vals)
            if not code:
                code = self.env["ir.sequence"].next_by_code(
                    "hezkuntza.student.group") or "Group"
            vals.update({'code': code})
        return super().create(vals)
