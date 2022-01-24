# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class HezkuntzaStudentImportLine(models.Model):
    _inherit = "hezkuntza.student.import.line"

    def _get_partner_dict(self):
        res = super()._get_partner_dict()
        res.update({'is_student': True})
        return res
