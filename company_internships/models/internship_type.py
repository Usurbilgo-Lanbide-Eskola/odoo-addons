# Copyright 2023 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class InternshipType(models.Model):
    _name = "internship.type"
    _description = "Internship Type"

    name = fields.Char("Internship Type")
    description = fields.Char("Description")
    agreement_type_ids = fields.Many2many("agreement.type")


class AgreementType(models.Model):
    _name = "agreement.type"
    _description = "Agreement Type"

    name = fields.Char("Name")
    description = fields.Char("Description")