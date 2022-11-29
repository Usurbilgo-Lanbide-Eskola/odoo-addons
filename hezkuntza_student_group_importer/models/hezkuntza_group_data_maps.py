# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


@api.depends("code", "name", "payment_type")
def calculate_name(instances):
    result = []
    for hezkuntza_map in instances:
        result.append(
            (
                hezkuntza_map.id,
                "{} ({})".format(
                    hezkuntza_map.odoo_code, hezkuntza_map.hezkuntza_code,
                ),
            )
        )
    return result


class HezkuntzaCourse(models.Model):
    _name = "hezkuntza.course"
    _rec_name = "odoo_code"

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

    @api.depends("hezkuntza_code", "odoo_code")
    def name_get(self):
        return calculate_name(self)


class HezkutzaLinguisticModel(models.Model):
    _name = "hezkuntza.linguistic.model"
    _rec_name = "odoo_code"

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

    @api.depends("hezkuntza_code", "odoo_code")
    def name_get(self):
        return calculate_name(self)


class HezkuntzaDegree(models.Model):
    _name = "hezkuntza.degree"
    _rec_name = "odoo_code"

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

    @api.depends("hezkuntza_code", "odoo_code")
    def name_get(self):
        return calculate_name(self)


class HezkuntzaEducationalLevel(models.Model):
    _name = "hezkuntza.educational.level"
    _rec_name = "odoo_code"

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

    @api.depends("hezkuntza_code", "odoo_code")
    def name_get(self):
        return calculate_name(self)


class HezkuntzaDegreeMode(models.Model):
    _name = "hezkuntza.degree.mode"
    _rec_name = "odoo_code"

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

    @api.depends("hezkuntza_code", "odoo_code")
    def name_get(self):
        return calculate_name(self)
