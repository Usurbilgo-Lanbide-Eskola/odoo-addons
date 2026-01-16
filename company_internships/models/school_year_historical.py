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
        comodel_name="res.partner", tracking=True)
    allowed_instructors = fields.Many2many(
        comodel_name="res.partner",
        compute="_compute_group_possible_companies")
    internship_type = fields.Many2one(comodel_name="internship.type",
                                      string="Internship Type",
                                      tracking=True)
    agreement_type_ids = fields.Many2many(
        related="internship_type.agreement_type_ids")
    agreement_type_id = fields.Many2one(
        comodel_name="agreement.type",
        domain="[('id', 'in', agreement_type_ids)]"
    )
    student_company_id = fields.Many2one(comodel_name="res.partner",
                                         tracking=True)
    group_possible_company_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="school_year_historical_company_rel",
        compute="_compute_group_possible_companies")
    is_active = fields.Boolean(related="school_year_id.is_active", store=True)
    user_id = fields.Many2one(comodel_name="res.users",
                              compute="_compute_user_id", store=True)
    student_without_internship = fields.Boolean("Student Without "
                                                "Internship", tracking=True)
    student_without_internship_reason = fields.Selection(selection=[('exempt', 'Exempt'),
                                                                    ('sick_leave',
                                                                     'Sick Leave'),
                                                                    ('absenteeism',
                                                                     'Absenteeism'),
                                                                    ('other', 'Other')])
    special_internship = fields.Boolean("Special Internship",
                                        tracking=True,
                                        help="This option is selected when the company is for a student who "
                                        "requires an alternative training experience "
                                        "instead of a company")
    special_internship_reason_id = fields.Many2one("special.internship.reason",
                                                   "Reason")
    notes = fields.Text("Notes")
    resignation_line_ids = fields.One2many(
        comodel_name="resigned.internship.line", inverse_name="record_id",
        string="Resignation Lines", tracking=True)
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
    state = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Waitting Documentation'),
        ('not_started', 'Accepted'),
        # ('in_internship', 'In Internship'),
        ('pause', 'Paused'),
        ('done', 'Done')],
        'State', default='draft', store=True, tracking=True)

    @api.depends("group_id")
    def _compute_group_possible_companies(self):
        for internship in self:
            won_stage = self.env["crm.stage"].search(
                [("is_won", "=", True)], limit=1)
            internship_lines = self.env["internship.line"].search([
                ('stage_id', '=', won_stage.id), 
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
            instructor_domain = [("company_instructor", "=", True),
                                 ("parent_id", "in", company_ids)]
            instructor_ids = self.env["res.partner"].search(
                instructor_domain).ids
            internship.allowed_instructors = [(6, 0, instructor_ids)]

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
            allowed = []
            if record.student_company_id:
                domain = [('type', '=', 'delivery')]
                domain.append(('parent_id', '=', record.student_company_id.id))
                allowed = partner_obj.search(domain).ids
            record.allowed_deliveries = [(6, 0, allowed)]

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
                record.special_internship = company.special_internship
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
                # 'student_tutor': record.student_tutor_id.id,
                # 'student_instructor': record.student_instructor_id.id,
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

    @api.onchange("student_without_internship")
    def onchange_student_without_internship(self):
        for record in self:
            if not record.student_without_internship:
                record.student_without_internship_reason = False

    @api.constrains("student_without_internship", "special_internship")
    def _check_internship_flags(self):
        for record in self:
            if record.student_without_internship and record.special_internship:
                raise ValidationError(
                    _("A student cannot be marked as both without "
                      "internship and having a special internship"))

    def action_internship_confirmed(self):
        for record in self:
            if (record.state == 'draft' and record.student_tutor_id and
                record.student_company_id and record.student_instructor_id and
                    record.internship_type):
                record.state = 'documentation'
            else:
                raise ValidationError(_('Ensure all fields are filled out'))

    def action_documentation_finished(self):
        for record in self:
            if record.state == 'documentation':
                record.state = 'not_started'

    def action_pause_internship(self):
        for record in self:
            if record.state == 'not_started':
                record.state == 'pause'

    def action_resume_internship(self):
        for record in self:
            if record.state == 'pause':
                record.state = 'not_started'

    def action_done(self):
        for record in self:
            if record.state not in ['draft', 'documentation']:
                record.state = 'done'

    def action_resignation(self):
        for record in self:
            if record.state not in ['pause']:
                # TODO wizard to add a resignation line
                record.state = 'draft'

    def action_open_resignation_wizard(self):
        return {
            'name': _('Resignation Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'resignation.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('company_internships.view_resignation_wizard_form').id,
            'target': 'new',
            'context': {'active_id': self.id},
        }


class ResignedInternshipLine(models.Model):
    _name = "resigned.internship.line"

    record_id = fields.Many2one(comodel_name="school.year.historical",
                                string="Record")
    student_company_id = fields.Many2one(comodel_name="res.partner")
    resignation_date = fields.Date("Resignation Date",
                                   default=fields.Date.context_today)
    description = fields.Text("Internal None")


    student_id = fields.Many2one(comodel_name="res.partner", related='record_id.student_id')
    school_year_id = fields.Many2one(comodel_name="school.year", related='record_id.school_year_id')
    group_id = fields.Many2one(comodel_name="product.template", related='record_id.group_id')
    student_tutor_id = fields.Many2one(comodel_name="res.partner",)
    student_instructor_id = fields.Many2one(
        comodel_name="res.partner")
    internship_type = fields.Many2one(comodel_name="internship.type",
                                      string="Internship Type",
                                      )
    agreement_type_id = fields.Many2one(comodel_name="agreement.type")
    student_company_id = fields.Many2one(comodel_name="res.partner",
                                         )
    is_active = fields.Boolean(related="school_year_id.is_active")
    special_internship = fields.Boolean("Special Internship",
                                        help="This option is selected when the company is for a student who "
                                        "requires an alternative training experience "
                                        "instead of a company")
    special_internship_reason_id = fields.Many2one("special.internship.reason",
                                                   "Reason")
    notes = fields.Text("Notes")
    unsubscribed = fields.Boolean("Unsubscribed")
    turn = fields.Selection(selection=[("0", "No Turn"),
                                       ("1", "First Turn"),
                                       ("2", "Second Turn")], default="0",)
    student_delivery_id = fields.Many2one(comodel_name="res.partner")
    state = fields.Selection(related='record_id.state')    


class SpecialInternshipReason(models.Model):
    _name = "special.internship.reason"

    name = fields.Char()
    description = fields.Char()
