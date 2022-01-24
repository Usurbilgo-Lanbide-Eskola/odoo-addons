from odoo.addons.hezkuntza_res_partner_student_fields.models.res_partner \
    import HEZKUNTZA_LANGUAGES
from odoo import fields, models


class HezkuntzaCountryCode(models.Model):
    _name = "hezkuntza.country.code"
    _rec_name = "hezkuntza_code"

    hezkuntza_code = fields.Char("Hezkuntza Code")
    odoo_code = fields.Many2one(comodel_name="res.country", string="Country")


class HezkuntzaStateCode(models.Model):
    _name = "hezkuntza.state.code"
    _rec_name = "hezkuntza_code"

    hezkuntza_code = fields.Char("Hezkuntza Code")
    odoo_code = fields.Many2one(comodel_name="res.country.state",
                                string="Country State")


class HezkuntzaGender(models.Model):
    _name = "hezkuntza.gender"
    _rec_name = "hezkuntza_code"

    hezkuntza_code = fields.Char("Hezkuntza Code")
    odoo_code = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")]
    )


class HezkuntzaLanguage(models.Model):
    _name = "hezkuntza.language"
    _rec_name = "hezkuntza_code"

    hezkuntza_code = fields.Char("Hezkuntza Code")
    odoo_code = fields.Selection(HEZKUNTZA_LANGUAGES)
