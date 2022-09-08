# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolYear(models.Model):
    _name = "school.year"
    _rec_name = "start_date"

    name = fields.Char(string="School Year",
                       compute="_compute_school_year_name")
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    is_active = fields.Boolean(string="Is Active", )
    current_active_year = fields.Boolean(
        string="Current School Year", compute="_compute_active_school_year",
        store=True)

    @api.depends("start_date", "end_date")
    def _compute_school_year_name(self):
        for school_year in self:
            if school_year.start_date and school_year.end_date:
                start_year = school_year.start_date.strftime("%y")
                end_year = school_year.end_date.strftime("%y")
                if start_year != end_year:
                    school_year.name = "{}-{}".format(start_year, end_year)
                else:
                    school_year.name = school_year.start_date.strftime("%y")
                return
            school_year.name = ""

    def name_get(self):
        return [(year.id, year.name or year.start_date) for year in self]

    @api.constrains("start_date", "end_date")
    def _check_non_overlap_school_years(self):
        self.env['school.year'].flush()
        query = """
            SELECT other.id FROM school_year this
            JOIN school_year other
              ON this.id = other.id
             AND other.id != this.id
             AND (
                other.start_date <= this.start_date AND this.start_date <= other.end_date
                OR
                other.start_date >= this.start_date AND this.end_date >= other.start_date
            )
            WHERE this.id IN %(ids)s
        """
        self.env.cr.execute(query, {'ids': tuple(self.ids)})
        res = self.env.cr.fetchall()
        if res:
            raise ValidationError(
                _("School years can't overlap"))

    @api.constrains("start_date", "end_date")
    def _check_start_date_older_than_end_date(self):
        for school_year in self:
            if school_year.start_date >= school_year.end_date:
                raise ValidationError(
                    _("Start date cannot be earlier to end date"))

    @api.depends("start_date", "end_date")
    def _compute_active_school_year(self):
        today = fields.Date.today()
        for school_year in self:
            if school_year.start_date and school_year.end_date:
                if school_year.start_date <= today <= school_year.end_date:
                    school_year.current_active_year = True
                    continue
            school_year.current_active_year = False

    def get_school_year(self):
        return self.search([("is_active", "=", True)])

    def get_current_school_year(self):
        return self.search([("current_active_year", "=", True)])

    def get_next_school_year(self):
        today = fields.Date.to_string(fields.Date.today())
        return self.search([('start_date', '>', today)],
                           order="start_date asc", limit=1)

    def get_last_school_year(self):
        return self.search([], order="end_date desc", limit=1)

    @api.model
    def create_school_year(self):
        school_year = self.get_current_school_year()
        if not school_year:
            today = fields.Date.today()
            res_param = self.env['ir.config_parameter'].sudo()
            duration = int(res_param.get_param(
                'school_year.school_year_months_duration', 10))
            start_month = int(res_param.get_param(
                'school_year.school_year_start_month', 9))
            start_day = int(res_param.get_param(
                'school_year.school_year_start_day', 1))
            start_date = today.replace(month=start_month, day=start_day)
            if start_date > today:
                start_date = start_date + relativedelta(years=-1)
                end_date = start_date + relativedelta(months=duration)
                if not today <= end_date:
                    start_date = start_date + relativedelta(years=1)
            end_date = start_date + relativedelta(months=duration)
            school_year = self.create({'start_date': start_date,
                                       'end_date': end_date})
        return school_year

    def school_year_deactivate_process(self):
        pass

    def school_year_activate_process(self):
        pass

    def active_year_change_process(self):
        self.ensure_one()
        active_year = self.get_school_year()
        if active_year != self:
            active_year.school_year_deactivate_process()
            old_active_year = self.get_school_year()
            old_active_year.is_active = False
            self.is_active = True
            self.school_year_activate_process()
