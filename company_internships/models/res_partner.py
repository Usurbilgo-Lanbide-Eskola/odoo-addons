# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_student = fields.Boolean("Is Student")
    is_tutor = fields.Boolean("Is Tutor")
    student_group_id = fields.Many2one(comodel_name="product.template",
                                       string="Student Group",
                                       domain=[
                                           ('is_student_group', '=', True)])
    school_year = fields.Many2one(comodel_name="school.year",
                                  related="student_group_id.school_year_id",
                                  string="School Year")
    internship_count = fields.Integer(compute="_compute_internships",
                                      store=True)
    internship_of_group_year = fields.Many2one(
        comodel_name="sale.order.line", compute="_compute_internships")
    # Field to trigger the compute function
    internship_count_dummy = fields.Integer(
        compute="_compute_internships")
    in_active_school_year = fields.Boolean(
        compute="_compute_in_active_school_year", store=True)
    student_tutor = fields.Many2one(comodel_name="res.partner")
    student_instructor = fields.Many2one(comodel_name="res.partner")
    student_record_ids = fields.One2many(
        comodel_name="school.year.historical", inverse_name="student_id")
    company_instructor = fields.Boolean("Instructor")
    tutor_students_qty = fields.Integer("Students Qty",
                                        compute="compute_tutor_students")

    @api.depends('student_tutor')
    def compute_tutor_students(self):
        school_year = self.env['school.year'].get_school_year()
        domain = [('is_student', '=', True),
         ('school_year', '=', school_year.id),
         ('student_tutor', '=', self.id)]
        self.tutor_students_qty = self.search_count(domain)

    @api.depends("school_year", "active")
    def _compute_in_active_school_year(self):
        for partner in self:
            if partner.is_student:
                active_year = partner.env['school.year'].get_school_year()
                if active_year == partner.school_year:
                    partner.in_active_school_year = True
                    continue
            partner.in_active_school_year = False

    @api.depends("school_year", "student_group_id")
    def _compute_internships(self):
        for student_id in self:
            internships = self.env['sale.order.line'].search(
                [("student_ids", "=", student_id.id), ("state", "in",
                                                       ["sale", "done"])])
            student_group_year = student_id.student_group_id.school_year_id
            internship_of_group_year = internships.filtered(
                lambda x: x.school_year_id.id == student_group_year.id)
            if len(internship_of_group_year) > 1:
                raise UserError(_(f"Student: {student_id.name} "
                                  f"has more than one interships assigned"))
            student_id.internship_of_group_year = internship_of_group_year.id
            internship_count = len(internships)
            student_id.internship_count = internship_count
            student_id.internship_count_dummy = internship_count

    def action_view_tutor_students(self):
        school_year = self.env['school.year'].get_school_year()
        domain = [('is_student', '=', True),
                  ('school_year', '=', school_year.id),
                  ('student_tutor', '=', self.id)]
        action = self.env['ir.actions.act_window']._for_xml_id(
            'company_internships.action_internships_students')
        action['domain'] = domain
        return action


    def action_view_sale_lines(self):
        '''
        This function returns an action that displays the sale lines from
        partner.
        '''
        if self.is_student:
            action = self.env['ir.actions.act_window']._for_xml_id(
                'sale_order_line_menu.action_orders_lines')
            action['domain'] = [('student_ids', '=', self.id)]
            return action
        return None


    def archive_year_data(self):
        for student in self.filtered(lambda x: x.is_student):
            student_group = student.student_group_id
            school_year = student_group.school_year_id
            if not school_year:
                school_year = self.env['school.year'].get_school_year()
            if school_year not in self.student_record_ids.mapped(
                    "school_year_id"):
                student.student_record_ids = [(0, 0, {
                    'group_id': student_group.id,
                    'school_year_id': school_year.id,
                    'student_tutor_id': student.student_tutor.id,
                    'student_instructor_id': student.student_instructor.id,
                })]
            student.write({
                'student_group_id': False,
                'student_tutor': False,
                'student_instructor': False,
            })


class SchoolYearHistorical(models.Model):
    _name = "school.year.historical"

    student_id = fields.Many2one(comodel_name="res.partner")
    school_year_id = fields.Many2one(comodel_name="school.year")
    group_id = fields.Many2one(comodel_name="product.template")
    student_tutor_id = fields.Many2one(comodel_name="res.partner")
    student_instructor_id = fields.Many2one(comodel_name="res.partner")

    def unarchive_year_data(self):
        students = self.env['res.partner']
        for record in self:
            record.student_id.write({
                'student_group_id': record.group_id.id,
                'student_tutor': record.student_tutor_id.id,
                'student_instructor': record.student_instructor_id.id,
            })
            students |= record.student_id
        return students
