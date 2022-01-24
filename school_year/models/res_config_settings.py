# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    school_year_months_duration = fields.Integer("School Year Duration")
    school_year_start_month = fields.Integer("School Year Start Month")
    school_year_start_day = fields.Integer("School Year Start Day")

    @api.constrains("school_year_start_month")
    def _check_month_number(self):
        if not 0 < self.school_year_start_month < 13:
            raise ValidationError(_("Month number must be between 1 and 12"))

    @api.constrains("school_year_start_day")
    def _check_day_number(self):
        if not 0 < self.school_year_start_day < 32:
            raise ValidationError(_("Day number must be between 1 and 31"))

    @api.constrains("school_year_months_duration")
    def _check_duration_number(self):
        if not 0 < self.school_year_months_duration < 13:
            raise ValidationError(_("Duration must be between 1 and 12"))

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            school_year_months_duration=self.env[
                'ir.config_parameter'].sudo().get_param(
                'school_year.school_year_months_duration', default=10),
            school_year_start_month=self.env[
                'ir.config_parameter'].sudo().get_param(
                'school_year.school_year_start_month', default=9),
            school_year_start_day=self.env[
                'ir.config_parameter'].sudo().get_param(
                'school_year.school_year_start_day', default=1),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('school_year.school_year_months_duration',
                        self.school_year_months_duration)
        param.set_param('school_year.school_year_start_month',
                        self.school_year_start_month)
        param.set_param('school_year.school_year_start_day',
                        self.school_year_start_day)
