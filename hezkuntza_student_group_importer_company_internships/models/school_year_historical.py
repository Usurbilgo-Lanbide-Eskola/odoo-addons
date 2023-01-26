# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class SchoolYearHistorical(models.Model):
    _inherit = "school.year.historical"

    speciality_id = fields.Many2one(comodel_name="hezkuntza.speciality",
                                    related="group_id.speciality_id",
                                    store=True)
