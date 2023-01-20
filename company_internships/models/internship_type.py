# Copyright 2023 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class InternshipType(models.Model):
    _name = "internship.type"

    name = fields.Char("Internship Type")
    description = fields.Char("Description")