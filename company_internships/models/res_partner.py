# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_student = fields.Boolean("Is Student")
    is_tutor = fields.Boolean("Is Teacher")
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
    #student_tutor = fields.Many2one(comodel_name="res.partner")
    #student_instructor = fields.Many2one(comodel_name="res.partner")
    student_active_tutor_ids = fields.Many2many(
        "res.partner", 'student_active_tutors', 'student_id', 'tutor_id',
        compute="compute_tutor_students", store=True)
    student_record_ids = fields.One2many(
        comodel_name="school.year.historical", inverse_name="student_id")
    active_student_record_ids = fields.One2many(
        comodel_name="school.year.historical", inverse_name="student_id",
        domain=[('is_active', '=', True)])
    company_instructor = fields.Boolean("Instructor")
    company_legal_agent = fields.Boolean("Legal Agent")
    company_contact_person = fields.Boolean("Contanct Person")
    tutor_students_qty = fields.Integer("Students Qty",
                                        compute="compute_count_tutor_students")
    company_internship_record_groups = fields.Many2many(
        comodel_name="school.year.historical",
        compute="compute_company_records",
        search="_search_historical_records_groups")
    company_internship_record_types = fields.Many2many(
        comodel_name="school.year.historical",
        compute="compute_company_records",
        search="_search_historical_records_types")
    driving_license = fields.Boolean(string="Driving License")
    car_owned = fields.Boolean(string="Car in Property")

    def _search_historical_records_groups(self, operator, value):

        if operator == 'in':
            return [('id', 'in', value)]
        query = f"""
            SELECT h.id
                FROM school_year_historical h
                LEFT JOIN hezkuntza_speciality hs
                ON h.speciality_id = hs.id
                WHERE hs.name ilike '%{value}%'
        """
        self._cr.execute(query)
        res = self._cr.fetchall()
        if not res:
            return [(0, '=', 1)]
        return [('company_internship_record_groups.id', 'in',
                 [r[0] for r in res])]


        # # Assumes operator is '=' or '!=' and value is True or False
        # self._assert_phone_field()
        # if operator != '=':
        #     if operator == '!=' and isinstance(value, bool):
        #         value = not value
        #     else:
        #         raise NotImplementedError()
        #
        # if value:
        #     query = """
        #         SELECT m.id
        #             FROM phone_blacklist bl
        #             JOIN %s m
        #             ON m.phone_sanitized = bl.number AND bl.active
        #     """
        # else:
        #     query = """
        #         SELECT m.id
        #             FROM %s m
        #             LEFT JOIN phone_blacklist bl
        #             ON m.phone_sanitized = bl.number AND bl.active
        #             WHERE bl.id IS NULL
        #     """







        # if operator == 'in':
        #     return [('id', 'in', value)]
        # if operator not in [
        #         '=', '!=', 'like', 'ilike', 'not like', 'not ilike']:
        #     raise UserError(_('Operation not supported'))
        # return [('company_internship_record_groups.group_id.display_name',
        #          operator, value)]

    def _search_historical_records_types(self, operator, value):
        # if operator not in ['=', '!='] or not isinstance(value, bool):
        #     raise UserError(_('Operation not supported'))
        # if operator != '=':
        #     value = not value
        # self._cr.execute("""
        #     SELECT id FROM account_account account
        #     WHERE EXISTS (SELECT * FROM account_move_line aml WHERE aml.account_id = account.id LIMIT 1)
        # """)
        if operator not in [
                '=', '!=', 'like', 'ilike', 'not like', 'not ilike']:
            raise UserError(_('Operation not supported'))
        return [('company_internship_record_groups.internship_type.display_name',
                 operator, value)]

    def compute_company_records(self):
        historical_obj = self.env['school.year.historical']
        for company in self.filtered(lambda x: x.is_company):
            records = historical_obj.search([('student_company_id', '=', company.id)]).ids
            company.company_internship_record_groups = [(6, 0, records)]
            company.company_internship_record_types = [(6, 0, records)]

    # @api.depends('company_internship_records')
    # def compute_company_internship_data(self):
    #     for company in self.filtered(lambda x: x.is_company):
    #         groups = company.company_internship_records.mapped(
    #             'group_id')
    #         internship_types = company.company_internship_records.mapped(
    #             'internship_type')
    #         company.company_internship_groups = [(6, 0, groups.ids)]
    #         company.company_internship_types = [(6, 0, internship_types.ids)]

    @api.depends('active_student_record_ids', 'student_record_ids')
    def compute_count_tutor_students(self):
        for tutor in self:
            school_year = self.env['school.year'].get_school_year()
            domain = [('school_year_id', '=', school_year.id),
                      ('student_tutor_id', '=', tutor.id)]
            tutor.tutor_students_qty = self.env[
                'school.year.historical'].search_count(domain)

    @api.depends('active_student_record_ids', 'student_record_ids')
    def compute_tutor_students(self):
        for tutor in self:
            school_year = self.env['school.year'].get_school_year()
            domain = [('school_year_id', '=', school_year.id),
                      ('student_id', '=', tutor.id)]
            records = self.env['school.year.historical'].search(domain)
            tutor.student_active_tutor_ids = records.mapped("student_tutor_id")

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
            if not student_id.is_student:
                student_id.internship_count_dummy = 0
                student_id.internship_of_group_year = False
                continue
            internships = self.env['sale.order.line'].search(
                [("internship_record_id.student_id.id", "=", student_id.id),
                 ("state", "in", ["sale", "done"])])
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

    def action_view_tutor_internships(self):
        if self.is_tutor:
            action = self.env['ir.actions.act_window']._for_xml_id(
                'company_internships.action_school_year_historical')
            action['domain'] = [('student_tutor_id', '=', self.id)]
            action['context'] = {"search_default_filter_active_year": 1}
            return action
        return None

    def action_view_tutor_students(self):
        school_year = self.env['school.year'].get_school_year()
        domain = [('is_student', '=', True),
                  ('school_year', '=', school_year.id),
                  ('student_active_tutor_ids', '=', self.id)]
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
            action['domain'] = [('internship_record_id.student_id.id', '=', self.id)]
            return action
        return None

    def deactivate_student_group(self):
        for student in self:
            student.write({
                'student_group_id': False,
                # 'student_tutor': False,
                # 'student_instructor': False,
            })

    def archive_year_data(self):
        for student in self.filtered(lambda x: x.is_student):
            student_group = student.student_group_id
            school_year = student_group.school_year_id
            if not school_year:
                school_year = self.env['school.year'].get_school_year()
            record = student.student_record_ids.filtered(
                lambda x: x.school_year_id == school_year)
            if not record:
                student.student_record_ids = [(0, 0, {
                    'group_id': student_group.id,
                    'school_year_id': school_year.id,
                    #'student_tutor_id': student.student_tutor.id,
                    #'student_instructor_id': student.student_instructor.id,
                })]
            student.deactivate_student_group()

    def _search_partners(self, domain):
        query = """
                    SELECT h.student_company_id
                        FROM school_year_historical h
                        LEFT JOIN hezkuntza_speciality hs
                        ON h.speciality_id = hs.id
                        LEFT JOIN internship_type it
                        ON h.internship_type = it.id
        """
        where_cond = """
        WHERE h.student_company_id is not null
        """
        for leaf in domain:
            if 'company_internship_record_groups' in leaf[0]:
                where_cond += f" and hs.name ilike '%{leaf[2] or ''}%'"
            elif 'company_internship_record_types' in leaf[0]:
                where_cond += f" and it.name ilike '%{leaf[2] or ''}%'"
        query += where_cond
        self._cr.execute(query)
        res = self._cr.fetchall()
        ids = [r[0] for r in res]

        return [('id', 'in', ids)]

    def _transform(self, leaf, condition=False, domain=[]):
        if len(leaf) == 0:
            new_domain = self._search_partners(domain)

            domain.clear()
            domain.extend(new_domain)
            return []
        if leaf[0] in ['&', '|']:
            condition = leaf[0]
        else:# is list
            if 'company_internship_record_groups' in leaf[0][0] or \
                    'company_internship_record_types' in leaf[0][0]:
                if condition == '&':
                    domain.append(leaf[0])
                    res = self._transform(leaf[1:], condition=condition,
                                     domain=domain)
                    res.extend(domain)
                    return res
                else:  # condition is or
                    condition = 'x' if condition == '|' else '&'
                    res = self._transform(leaf[1:], condition=condition,
                                    domain=domain)
                    or_leaf = domain + list(leaf[0])
                    new_leaf = or_leaf
                    res.extend(new_leaf)
                    return res
            condition = 'x' if condition == '|' else '&'
        res = self._transform(leaf[1:], condition=condition, domain=domain)
        res.append(leaf[0])
        return res

    def transform(self, args):
        res = self._transform(args)
        res.reverse()
        return res

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        if self.env.context.get('from_search_view'):
            args = expression.normalize_domain(args)
            args = self.transform(args)
        return super().search(args, offset=offset, limit=limit, order=order,
                              count=count)

    @api.model
    def create(self, values):
        if values.get('is_student'):
            if not values.get('student_record_ids'):
                student_group = values.get('student_group_id')
                if student_group:
                    if isinstance(student_group, int):
                        student_group = self.env['product.template'].browse(
                            student_group)
                    school_year = student_group.school_year_id
                else:
                    school_year = self.env['school.year'].get_school_year()
                values.update({
                    'student_record_ids': [(0, 0,
                                            {'school_year_id': school_year.id,
                                             'group_id': student_group.id})]
                })
        return super().create(values)

    def write(self, values):
        if values.get('is_student'):
            historical_obj = self.env['school.year.historical']
            if not historical_obj.get_active_historical_lines(self):
                student_group = values.get('student_group_id') or \
                                self.student_group_id
                if student_group:
                    if isinstance(student_group, int):
                        student_group = self.env['product.template'].browse(
                            student_group)
                    school_year = student_group.school_year_id
                else:
                    school_year = self.env['school.year'].get_school_year()
                values.update({
                    'student_record_ids': [(0, 0,
                                            {'school_year_id': school_year.id,
                                             'group_id': student_group.id})]
                })
        return super().write(values)
