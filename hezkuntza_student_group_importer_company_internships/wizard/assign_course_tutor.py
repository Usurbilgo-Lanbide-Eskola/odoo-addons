# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class AssignCourseTutor(models.TransientModel):
    _name = "assign.course.tutor"
    _description = "Assign Course Tutor Wizard"

    course_tutor_line = fields.One2many("assign.course.tutor.line", "assign_id")
    school_year_id = fields.Many2one("school.year", readonly=True)

    def default_get(self, fields):
        res = super().default_get(fields)
        school_year = self.env["school.year"].get_school_year()
        self.school_year_id = school_year.id if school_year else False

        tutors = self.env["res.partner"].search([("is_tutor", "=", True)])
        line_ids = []
        for tutor in tutors:
            course_ids = False
            already = self.env["product.template"].search([
                ("school_year_id", "=", school_year.id),
                ("tutor_ids", "=", tutor.id),
            ])
            if already:
                course_ids = already
            elif tutor.tutor_speciality_id:
                course_ids = self.env["product.template"].search([
                    ("speciality_id", "=", tutor.tutor_speciality_id.id),
                    ("school_year_id", "=", school_year.id),
                ])
            line_vals = {
                "tutor_id": tutor.id,
            }
            if course_ids:
                line_vals["course_ids"] = [(6, 0, course_ids.ids)]
            line_ids.append((0, 0, line_vals))
        res["school_year_id"] = school_year.id
        res["course_tutor_line"] = line_ids

        return res

    def assign_courses(self):
        for wiz in self:
            course_tutor = {}
            for line in wiz.course_tutor_line:
                tutor_id = line.tutor_id.id
                for course in line.course_ids:
                    if not course_tutor.get(course):
                        course_tutor[course] = [tutor_id]
                    else:
                        course_tutor[course].append(tutor_id)
            for course, tutor_ids in course_tutor.items():
                course.tutor_ids = [(6, 0, tutor_ids)]
        return {'type': 'ir.actions.act_window_close'}


class AssignCourseTutorLine(models.TransientModel):
    _name = "assign.course.tutor.line"
    _description = "Assign Course Tutor Line"

    assign_id = fields.Many2one(
        comodel_name="assign.course.tutor", ondelete="cascade")
    tutor_id = fields.Many2one(comodel_name="res.partner")
    course_ids = fields.Many2many(comodel_name="product.template")
    assign_all = fields.Boolean("Assign All")
    unassign_all = fields.Boolean("Unassign All")

    @api.onchange("assign_all")
    def assign_all_courses(self):
        self.ensure_one()
        school_year = self.assign_id.school_year_id
        all_courses = self.env["product.template"].search(
            [("school_year_id", "=", school_year.id)])
        self.course_ids = [(6, 0, all_courses.ids)]
        self.assign_all = False

        # self.ensure_one()
        # school_year = self.assign_id.school_year_id
        # all_courses = self.env["product.template"].search(
        #     [("school_year_id", "=", school_year.id)])
        # self.write({'course_ids': [(6, 0, all_courses.ids)]})
        # return True

    @api.onchange("unassign_all")
    def unassign_all_courses(self):
        self.ensure_one()
        self.course_ids = [(5, 0, 0)]
        self.unassign_all = False
