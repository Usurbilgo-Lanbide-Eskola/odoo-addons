# Copyright 2023 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class InternshipType(models.Model):
    _name = "internship.type"

    name = fields.Char("Internship Type")
    description = fields.Char("Description")

    type_ids = fields.One2many(
        comodel_name = "internship.subtype",
        inverse_name= "type_id"
    )

class InternshipSubtype(models.Model):
    _name = "internship.subtype"
    _description = "Internship Subtype"

    name = fields.Char("Internship Subtype")

    type_id = fields.Many2one(
        comodel_name = "internship.type"
    )
