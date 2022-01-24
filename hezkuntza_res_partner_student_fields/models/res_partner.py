# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models

HEZKUNTZA_LANGUAGES = [('none', 'None'), ('spanish', 'Spanish'),
                       ('basque', 'Basque'), ('bilingual', 'Bilingual')]


class ResPartner(models.Model):
    _inherit = "res.partner"

    id_hezkuntza = fields.Char("Hezkuntza ID")
    location = fields.Char("Location")
    personal_id = fields.Char("Personal ID")
    personal_email = fields.Char("Personal Email")
    hezkuntza_language = fields.Selection(HEZKUNTZA_LANGUAGES,
                                          "Hezkuntza Language")
