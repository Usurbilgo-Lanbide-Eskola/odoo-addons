# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolYearHistorical(models.Model):
    _name = "school.year.historical"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "student_id"

    student_id = fields.Many2one(comodel_name="res.partner",
                                 ondelete='cascade')
    school_year_id = fields.Many2one(comodel_name="school.year")
    group_id = fields.Many2one(comodel_name="product.template")
    student_tutor_id = fields.Many2one(comodel_name="res.partner",
                                       tracking=True)
    student_instructor_id = fields.Many2one(
        comodel_name="res.partner", domain="[('id', 'in', "
                                           "allowed_instructors)]",
        tracking=True)
    allowed_instructors = fields.Many2many(
        comodel_name="res.partner", compute="_compute_allowed_instructors")
    internship_type = fields.Many2one(comodel_name="internship.type",
                                      string="Internship Type",
                                      tracking=True)
    student_company_id = fields.Many2one(comodel_name="res.partner",
                                         tracking=True)
    is_active = fields.Boolean(related="school_year_id.is_active", store=True)
    user_id = fields.Many2one(comodel_name="res.users",
                              compute="_compute_user_id", store=True)
    student_without_internship = fields.Boolean("Student Without "
                                                "Internship", tracking=True)
    resignation_line_ids = fields.One2many(
        comodel_name="resigned.internship.line", inverse_name="record_id",
        string="Resignation Lines")
    record_sale_line_id = fields.Many2one(comodel_name="sale.order.line")
    unsubscribed = fields.Boolean("Unsubscribed")
    turn = fields.Selection(selection=[("0", "No Turn"),
                                       ("1", "First Turn"),
                                       ("2", "Second Turn")], default="0",
                            tracking=True)
    student_delivery_id = fields.Many2one(
        comodel_name="res.partner", domain="[('id', 'in', "
                                           "allowed_deliveries)]",
        tracking=True)
    allowed_deliveries = fields.Many2many(
        comodel_name="res.partner", compute="_compute_allowed_deliveries")


    @api.constrains("student_company_id", "student_instructor_id")
    def instructor_is_companies_child(self):
        if self.student_company_id and self.student_instructor_id and \
                self.student_instructor_id.parent_id != \
                self.student_company_id:
            raise ValidationError(_("Instructor must belong to the company"))

    @api.depends("student_company_id")
    def _compute_allowed_instructors(self):
        partner_obj = self.env['res.partner']
        for record in self:
            domain = [('company_instructor', '=', True)]
            if record.student_company_id:
                domain.append(('parent_id', '=', record.student_company_id.id))
            allowed = partner_obj.search(domain)
            record.allowed_instructors = [(6, 0, allowed.ids)]

    @api.depends("student_company_id")
    def _compute_allowed_deliveries(self):
        partner_obj = self.env['res.partner']
        for record in self:
            domain = [('type', '=', 'delivery')]
            if record.student_company_id:
                domain.append(('parent_id', '=', record.student_company_id.id))
            allowed = partner_obj.search(domain)
            record.allowed_deliveries = [(6, 0, allowed.ids)]

    @api.onchange('group_id')
    def onchange_student_group(self):
        for record in self.filtered(lambda x: x.group_id):
            record.school_year_id = record.group_id.school_year_id

    @api.onchange('student_company_id')
    def onchange_company(self):
        for record in self:
            company = record.student_company_id
            instructor = record.student_instructor_id
            if company:
                if instructor.parent_id != company:
                    record.student_instructor_id = False
            else:
                record.student_instructor_id = False

    @api.onchange('student_instructor_id')
    def onchange_instructor(self):
        for record in self.filtered(lambda x: x.student_instructor_id):
            company = record.student_company_id
            instructor = record.student_instructor_id
            if instructor.parent_id and instructor.parent_id != company:
                record.student_company_id = instructor.parent_id.id

    def unarchive_year_data(self):
        students = self.env['res.partner']
        for record in self:
            record.student_id.write({
                'student_group_id': record.group_id.id,
                #'student_tutor': record.student_tutor_id.id,
                #'student_instructor': record.student_instructor_id.id,
            })
            students |= record.student_id
        return students

    @api.depends("student_tutor_id")
    def _compute_user_id(self):
        for record in self:
            user = self.env['res.users'].search(
                [('partner_id', '=', record.student_tutor_id.id)])
            record.user_id = user[0].id if len(user) > 0 else False

    def get_active_historical_lines(self, student_id):
        active_year = self.env['school.year'].get_school_year()
        if not isinstance(student_id, int):
            student_id = student_id.id
        if active_year:
            return self.search([
                ('student_id', '=', student_id),
                ('school_year_id', '=', active_year.id)])

    def get_student_company(self, student_id, school_year):
        internship_line = self.env["school.year.historical"].search(
            [("student_id", "=", student_id),
             ("school_year_id", "=", school_year.id)])
        if len(internship_line) != 1:
            raise ValidationError(_(f"Multiple internship lines for student: "
                                    f"{internship_line[0].student_id.name}"))
        return internship_line.student_company_id

    def name_get(self):
        return [(record.id,
                 f"{record.student_id.display_name} "
                 f"({record.school_year_id.name})") for record in self]

    def action_open_form(self):
        return {
            'name': _('Record Form'),
            'view_mode': 'form',
            'view_id': self.env.ref(
                'company_internships.view_school_year_historical_form').id,
            'res_model': 'school.year.historical',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
        }


class ResignedInternshipLine(models.Model):
    _name = "resigned.internship.line"

    record_id = fields.Many2one(comodel_name="school.year.historical",
                                string="Record")
    student_company_id = fields.Many2one(comodel_name="res.partner")
    resignation_date = fields.Date("Resignation Date",
                                   default=fields.Date.context_today)
    description = fields.Text("Internal None")

