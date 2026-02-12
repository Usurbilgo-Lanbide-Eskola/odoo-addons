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
                               related="student_company_id.city")
    delivery_address_id = fields.Many2one(
        comodel_name="res.partner", string="Delivery Address")
    delivery_city = fields.Char(
        string="Delivery City", related="delivery_address_id.city")
    student_small_image = fields.Image(
        related="student_id.image_128", string="Student Image")
    group_id = fields.Many2one(comodel_name="product.template",
                               related='school_year_historical_id.group_id',
                               store=True)
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
    company_assignable_qty = fields.Integer(
        compute="_compute_company_assignable_qty",
        string="Assignable Quantity",
        help="Number of students that can be assigned to the company. "
             "Negative values indicate students must be unassigned"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('student_company_id'):
                partner = self.env['res.partner'].browse(
                    vals['student_company_id'])
                company = self._get_company(partner)
                if company:
                    vals['student_company_id'] = company.id
        return super().create(vals_list)

    def _get_company(self, partner_id):
        if partner_id.ensure_one():
            if partner_id.is_company:
                return partner_id
            elif partner_id.parent_id:
                return partner_id.parent_id
        return False
    
    def _compute_company_assignable_qty(self):
        for internship in self:
            internship.company_assignable_qty = 0
            not_lost_lead = self.env["crm.lead"].search(
                [("probability", ">", 0)])
            if internship.student_company_id:
                company_id = self._get_company(internship.student_company_id)
                if not company_id:
                    continue
                internship_lines = self.env["internship.line"].search([
                    ('lead_id', 'in', not_lost_lead.ids),
                    ('school_year_id', '=', internship.school_year_id.id),
                    ('student_group_id', '=', internship.group_id.id),
                    ('lead_id.partner_id', 'child_of', company_id.id)])
                already_assigned_qty = self.search_count([
                    ("school_year_id", "=", internship.school_year_id.id),
                    ("student_group_id", "=", internship.group_id.id),
                    ("student_company_id", "=", internship.student_company_id.id)])
                internship.company_assignable_qty = sum(
                    line.student_qty for line in internship_lines) - already_assigned_qty


    @api.depends("group_id")
    def _compute_group_possible_companies(self):
        for internship in self:
            not_lost_lead = self.env["crm.lead"].search(
                [("probability", ">", 0)])
            internship_lines = self.env["internship.line"].search([
                ('lead_id', 'in', not_lost_lead.ids),
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

    def button_read_company_internship_lines_info(self):
        internship_line_obj = self.env['internship.line']
        for record in self:
            company = record.student_company_id.parent_id if record.student_company_id.parent_id else record.student_company_id
            company_name = company.name
            results = internship_line_obj.read_group([
                ('partner_id', 'child_of', company.id),
                ('school_year_id', '=', record.school_year_id.id),
                ('student_group_id', '=', record.group_id.id)],
                ['partner_id', 'agreement_type',
                    'internship_type_id', 'student_qty:sum'],
                ['partner_id', 'agreement_type', 'internship_type_id'],
                lazy=False)

            company_groups = {}
            for result in results:
                partner = self.env['res.partner'].browse(
                    result['partner_id'][0])
                company = partner.parent_id if partner.parent_id else partner

                key = (company.id, result.get('agreement_type')[0] if result.get('agreement_type') else False, result.get(
                    'internship_type_id')[0] if result.get('internship_type_id') else False)

                if key not in company_groups:
                    company_groups[key] = {
                        'internship_type_id': str(result.get('internship_type_id')[1]) if result.get('internship_type_id') else False,
                        'agreement_type': str(result.get('agreement_type')[1]) if result.get('agreement_type') else False,
                        'student_qty': 0
                    }
                company_groups[key]['student_qty'] += result.get(
                    'student_qty', 0)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Info',
                    'message': str(f"{company_name}: {[[y for y in x.values()] for x in company_groups.values()]}"),
                    'type': 'info',  # 'warning', 'danger', 'success', 'info'
                    'sticky': False,  
                }
            }
