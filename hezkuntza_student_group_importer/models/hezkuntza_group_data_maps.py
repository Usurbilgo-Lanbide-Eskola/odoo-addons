# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class HezkuntzaCourse(models.Model):
    _name = "hezkuntza.course"
    _rec_name = "hezkuntza_code"

    hezkuntza_code = fields.Char("Hezkuntza Code")
    odoo_code = fields.Char("Odoo Code")
    description = fields.Char("Description")

    _sql_constraints = [
        (
            "hezkuntza_code_uniq",
            "unique(hezkuntza_code)",
            "Hezkuntza code must be unique",
        )
    ]


class HezkutzaLinguisticModel(models.Model):
    _name = "hezkuntza.linguistic.model"
    _rec_name = "hezkuntza_code"

    hezkuntza_code = fields.Char("Hezkuntza Code")
    odoo_code = fields.Char("Odoo Code")
    description = fields.Char("Description")

    _sql_constraints = [
        (
            "hezkuntza_code_uniq",
            "unique(hezkuntza_code)",
            "Hezkuntza code must be unique",
        )
    ]


class HezkuntzaDegree(models.Model):
    _name = "hezkuntza.degree"
    _rec_name = "hezkuntza_code"

    hezkuntza_code = fields.Char("Hezkuntza Code")
    odoo_code = fields.Char("Odoo Code")
    description = fields.Char("Description")

    _sql_constraints = [
        (
            "hezkuntza_code_uniq",
            "unique(hezkuntza_code)",
            "Hezkuntza code must be unique",
        )
    ]


class HezkuntzaEducationalLevel(models.Model):
    _name = "hezkuntza.educational.level"
    _rec_name = "hezkuntza_code"

    hezkuntza_code = fields.Char("Hezkuntza Code")
    odoo_code = fields.Char("Odoo Code")
    description = fields.Char("Description")

    _sql_constraints = [
        (
            "hezkuntza_code_uniq",
            "unique(hezkuntza_code)",
            "Hezkuntza code must be unique",
        )
    ]


class HezkuntzaDegreeMode(models.Model):
    _name = "hezkuntza.degree.mode"
    _rec_name = "hezkuntza_code"

    hezkuntza_code = fields.Char("Hezkuntza Code")
    odoo_code = fields.Char("Odoo Code")
    description = fields.Char("Description")

    _sql_constraints = [
        (
            "hezkuntza_code_uniq",
            "unique(hezkuntza_code)",
            "Hezkuntza code must be unique",
        )
    ]
