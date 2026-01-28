# Copyright 2026 Mikel Arregi Etxaniz - Zubieta Lanbide Eskola
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class InternshipPredictionLine(models.Model):
    _name = "internship.prediction.line"
    _description = "Internship Prediction Line"
    _rec_name = "school_year_historical_id"

    school_year_historical_id = fields.Many2one(
        comodel_name="school.year.historical", required=True)
    notes = fields.Text(string="Notes")
    student_id = fields.Many2one("res.partner", string="Student",
                                 related="school_year_historical_id.student_id",
                                 store=True)
    age = fields.Integer(string="Age", related="student_id.age")
    driving_license = fields.Boolean(
        string="Driving License", related="student_id.driving_license")
    car_owned = fields.Boolean(
        string="Car Owned", related="student_id.car_owned")
    city = fields.Char(string="City", related="student_id.city")
    company_city = fields.Char(string="Company City",
                               relared="student_company_id.city")
    delivery_address_id = fields.Many2one(
        comodel_name="res.partner", string="Delivery Address")
    delivery_city = fields.Char(
        string="Delivery City", relared="delivery_address_id.city")
    student_small_image = fields.Image(
        related="student_id.image_128", string="Student Image")
    group_id = fields.Many2one(comodel_name="product.template",
                               related='school_year_historical_id.group_id', store=True)
    school_year_id = fields.Many2one(
        related="school_year_historical_id.school_year_id", store=True)
    student_company_id = fields.Many2one(comodel_name="res.partner")
    group_possible_company_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="school_year_historical_company_rel",
        compute="_compute_group_possible_companies")
    record_company_id = fields.Many2one(
        related="school_year_historical_id.student_company_id",
        store=True)

    @api.depends("group_id")
    def _compute_group_possible_companies(self):
        for internship in self:
            lost_lead = self.env["crm.lead"].search(
                [("probability", ">", 0)])
            internship_lines = self.env["internship.line"].search([
                ('lead_id', 'in', lost_lead.ids),
                ('school_year_id', '=', internship.school_year_id.id),
                ('student_group_id', '=', internship.group_id.id)])
            partners = internship_lines.mapped('lead_id.partner_id')

            # Get companies: direct companies or parent company if it's a person
            company_ids = []
            for partner in partners:
                if partner.is_company:
                    company_ids.append(partner.id)
                elif partner.parent_id:
                    company_ids.append(partner.parent_id.id)
            internship.group_possible_company_ids = [(6, 0, company_ids)]
