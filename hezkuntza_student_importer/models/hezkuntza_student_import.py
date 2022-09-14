# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import pathlib
import zipfile
import tempfile
from io import BytesIO
import xlrd
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HezkuntzaStudentImport(models.Model):
    _name = "hezkuntza.student.import"

    name = fields.Char("Importation Name", copy=False)
    file = fields.Binary("Enrollment File", copy=False)
    school_year = fields.Many2one(comodel_name="school.year")
    image_path = fields.Char("Image Path")
    image_zip = fields.Binary("Image Zip", copy=False,
                              help="Upload student images in a zip file")
    mapped_lines = fields.One2many(
        comodel_name="hezkuntza.student.import.line",
        inverse_name="import_id")
    error_mapped_lines = fields.One2many(
        comodel_name="hezkuntza.student.import.line",
        compute="_compute_error_lines", inverse="_inverse_changes")
    error_lines = fields.Boolean("Error Lines", copy=False)
    overwrite = fields.Boolean("Overwrite", copy=False)

    @api.depends('mapped_lines')
    def _compute_error_lines(self):
        for importer in self:
            self.error_mapped_lines = [(6, 0,
                                        importer.mapped_lines.filtered(
                                            lambda x: x.errors).ids)]

    def _inverse_changes(self):
        pass

    @api.onchange('name')
    def onchange_name(self):
        school_year_obj = self.env['school.year']
        for school_year in self:
            active_school_year = school_year_obj.get_current_school_year()
            if active_school_year:
                school_year.school_year = active_school_year

    def unzip_images_in_path(self):
        if self.image_zip and self.image_path:
            zip_file = BytesIO(base64.b64decode(self.image_zip))
            with zipfile.ZipFile(zip_file) as zf:
                zf.extractall(self.image_path)

    def _get_image_path(self, student_id):
        path = pathlib.Path(self.image_path)
        file = list(path.glob(student_id.upper() + ".*"))
        if not file:
            file = list(path.glob(student_id.lower() + ".*"))
        if not file:
            return False
        return path.joinpath(file[0])

    def _get_image(self, student_id):
        file_path = self._get_image_path(student_id)
        if file_path and file_path.is_file():
            with file_path.open('br') as f:
                image = base64.b64encode(f.read())
            return image
        return None

    def _row_is_importable(self, sheet, row, headers):
        # TODO to config page
        index = headers.index('DIE_ALU')
        return sheet.row(row)[index].value and True or False

    def _get_row_values(self, sheet, row):
        line_values = []
        for col in range(sheet.ncols):
            line_values.append(sheet.row(row)[col].value)
        return line_values

    def _get_country_by_hezkuntza_code(self, country_code):
        if country_code:
            return self.env['hezkuntza.country.code'].search([(
                'hezkuntza_code', '=', country_code)], limit=1).odoo_code
        return self.env['res.country']

    def _get_state_by_hezkuntza_code(self, state_code):
        if state_code:
            return self.env['hezkuntza.state.code'].search([(
                'hezkuntza_code', '=', state_code)], limit=1).odoo_code
        return self.env['res.country.state']

    def _get_gender_by_hezkuntza_code(self, gender_code):
        if gender_code:
            return self.env['hezkuntza.gender'].search([(
                'hezkuntza_code', '=', gender_code)], limit=1).odoo_code
        return None

    def _get_language_by_hezkuntza_code(self, language_code):
        if language_code:
            return self.env['hezkuntza.language'].search([(
                'hezkuntza_code', '=', language_code)], limit=1).odoo_code
        return None

    def _get_student_line(self, raw_dict):
        return {
            'id_hezkuntza': raw_dict['DIE_ALU'],
            'personal_id': raw_dict['DOCU_IDENTI_ALU'] or
            raw_dict['PASAPORTE_ALU'],
            'name': raw_dict['NOMBRE_ALU'],
            'lastname': raw_dict['APELLIDO_1_ALU'],
            'lastname2': raw_dict['APELLIDO_2_ALU'],
            'birthdate_date': raw_dict['FECHA_NACI_ALU'],
            'gender': self._get_gender_by_hezkuntza_code(
                raw_dict['COD_SEXO_ALU']),
            'country_id': self._get_country_by_hezkuntza_code(
                raw_dict['COD_PAIS_RESI_ALU']).id,
            'state_id': self._get_state_by_hezkuntza_code(
                raw_dict['COD_PROV_RESI_ALU']).id,
            'city': raw_dict['DES_MUNI_RESI_ALU'],
            'location': raw_dict['DES_LOCA_RESI_ALU'],
            'street': raw_dict['DIRECCION_ALU'],
            'zip': raw_dict['COD_POSTAL_ALU'],
            'phone': raw_dict['TELEFONO_1_ALU'],
            'phone2': raw_dict['TELEFONO_2_ALU'],
            'personal_email': raw_dict['EMAIL_ALU'],
            'hezkuntza_language': self._get_language_by_hezkuntza_code(
                raw_dict['COD_IDIOMA_CORRES']),
        }

    def _get_lines_dict(self):
        if self.file:
            book = xlrd.open_workbook(
                file_contents=base64.b64decode(self.file))
            # TODO get sheet name from odoo configuration page
            sheet = book.sheet_by_name('Des_Alumnos')
            headers = [header.value for header in sheet.row(0)]
            res_lines = []
            for row in range(1, sheet.nrows):
                if self._row_is_importable(sheet, row, headers):
                    row_values = self._get_row_values(sheet, row)
                    row_dict = dict(zip(headers, row_values))
                    student_dict = self._get_student_line(row_dict)
                    if self.image_path:
                        student_dict.update({'image': self._get_image(
                            student_dict.get('id_hezkuntza'))})
                    res_lines.append(student_dict)
            return res_lines

    def import_lines(self):
        if not self.file:
            raise UserError(_("Add a enrollment file"))
        if self.image_zip:
            with tempfile.TemporaryDirectory() as working_dir:
                old_path = self.image_path
                self.image_path = working_dir
                self.unzip_images_in_path()
                lines_dict = self._get_lines_dict()
                self.image_path = old_path
        else:
            lines_dict = self._get_lines_dict()
        res_lines = []
        for line in lines_dict:
            line_name = line.get('id_hezkuntza')
            partner_obj = self.with_context(active_test=False
                                            ).env['res.partner']
            partner_map = partner_obj.search([('id_hezkuntza', '=ilike',
                                               line_name)], limit=1)
            line.update(imported_partner_id=partner_map.id)
            already_mapped = self.mapped_lines.filtered(
                lambda x: x.id_hezkuntza == line_name)
            if already_mapped:
                res_lines.append((1, already_mapped[0].id, line))
            else:
                res_lines.append((0, 0, line))
        self.write({'mapped_lines': res_lines})
        self.test_lines()

    def test_lines(self):
        for line in self.mapped_lines:
            errors = line.test_line()
            if errors:
                line.errors = errors
            else:
                line.errors = ""

    def create_partners(self):
        created_partners = self.env['res.partner']
        lines = self.error_mapped_lines if self.error_lines else \
            self.mapped_lines
        for line in lines:
            if self.overwrite:
                created_partners |= line.overwrite_partner()
            created_partners |= line.create_partner()
        return created_partners


class HezkuntzaStudentImportLine(models.Model):
    _name = "hezkuntza.student.import.line"
    _rec_name = "id_hezkuntza"

    import_id = fields.Many2one(comodel_name='hezkuntza.student.import',
                                ondelete="cascade")
    id_hezkuntza = fields.Char("Hezkuntza ID")
    school_year = fields.Many2one(comodel_name="school.year",
                                  related='import_id.school_year')
    personal_id = fields.Char("Student ID")
    name = fields.Char("Name")
    lastname = fields.Char("Lastname")
    lastname2 = fields.Char("Second Lastname")
    birthdate_date = fields.Date("Birth Date")
    gender = fields.Char("Gender")
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    state_id = fields.Many2one(comodel_name="res.country.state",
                               string="State")
    city = fields.Char("City")
    location = fields.Char("Location")
    street = fields.Char("Street")
    zip = fields.Char("ZIP")
    phone = fields.Char("Telephone1")
    phone2 = fields.Char("Telephone2")
    personal_email = fields.Char("Email")
    hezkuntza_language = fields.Char("Language")
    image = fields.Image("Student Photo")
    imported_partner_id = fields.Many2one(comodel_name='res.partner',
                                          string='Imported Partner')
    errors = fields.Text("Errors")

    def test_line(self):
        # check country and state
        errors = ""
        if not self.country_id:
            errors += _("Doesn't has country\n")
        if not self.state_id:
            errors += _("Doesn't has state\n")
        # student ID
        if not self.personal_id:
            errors += _("Not ID or Passport supplied\n")
        # student image
        if not self.image:
            errors += _("No image found\n")
        return errors and errors[:-1] or ""

    def _select_odoo_language(self, hezkuntza_language):
        if hezkuntza_language:
            lang = self.env['hezkuntza.language'].search([(
                'odoo_code', '=', hezkuntza_language)], limit=1)
            if lang:
                return lang.odoo_lang.code
        return None

    def _get_partner_dict(self):
        return {
            'company_type': 'person',
            'id_hezkuntza': self.id_hezkuntza,
            'personal_id': self.personal_id,
            'firstname': self.name,
            'lastname': self.lastname,
            'lastname2': self.lastname2,
            'birthdate_date': self.birthdate_date,
            'gender': self.gender,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'city': self.city,
            'location': self.location,
            'street': self.street,
            'zip': self.zip,
            'phone': self.phone,
            'phone2': self.phone2,
            'personal_email': self.personal_email,
            'hezkuntza_language': self.hezkuntza_language,
            'image_1920': self.image,
            'lang': self._select_odoo_language(self.hezkuntza_language)
        }

    def _get_partner_by_hezkuntza_id(self, hezkuntza_id):
        return self.env['res.partner'].search([('id_hezkuntza', '=ilike',
                                               hezkuntza_id)], limit=1)

    def _already_imported(self):
        return self.imported_partner_id or self.with_context(
            active_test=False)._get_partner_by_hezkuntza_id(self.id_hezkuntza)

    def _overwrite_partner(self):
        if self.imported_partner_id:
            partner_dict = self._get_partner_dict()
            overwrite_fields = {k: v for k, v in partner_dict.items() if v}
            self.imported_partner_id.write(overwrite_fields)
            return self.imported_partner_id
        return self.env['res.partner']

    def overwrite_partner(self):
        if self.imported_partner_id:
            return self._overwrite_partner()
        already_imported = self._already_imported()
        if already_imported:
            self.imported_partner_id = already_imported
            return self._overwrite_partner()
        return self.env['res.partner']

    def enroll_in_school_year(self, student):
        student.active = True

    def create_partner(self):
        already_imported = self._already_imported()
        if already_imported:
            if self.school_year.is_active:
                self.enroll_in_school_year(already_imported)
            self.imported_partner_id = already_imported
        else:
            errors = self.test_line()
            # TODO block partner creation if errors?
            if errors:
                pass
            partner_dict = self._get_partner_dict()
            partner_id = self.env['res.partner'].create(partner_dict)
            self.imported_partner_id = partner_id.id
            return partner_id
        return self.env['res.partner']
