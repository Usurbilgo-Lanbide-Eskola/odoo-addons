# Copyright 2024 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

DOCUMENT_MODELS = [("internship", "Internship"),
                   ("company", "Company")]


class InternshipDocumentSigner(models.Model):
    _name = "internship.document.signer"

    name = fields.Char("Signer")
    is_internal_user = fields.Boolean("Is internal User")
    res_user = fields.Many2one(comodel_name="res.users")

class InternshipDocumentSignedBy(models.Model):
    _name = "internship.document.signed.by"

    document_signer = fields.Char("Name")
    signature_hash = fields.Char("Signature Hash")


class InternshipDocument(models.Model):
    _name = "internship.document"

    # @api.model
    # def get_type_stages(self):
    #     stages = False#get from type
    #     return [(stage.model,stage.name) for stage in stages]

    original_document = fields.Binary(string="Original Document")
    last_document = fields.Binary(string="Final Document")
    # model_id = fields.Many2one("ir.model", "Model",
    #                            readonly=True)

    document_type_id = fields.Many2one(comodel_name="internship.document.type")
    code = fields.Char("type code", readonly=True)
    res_model = fields.Many2one("ir.model",
                                related="document_type_id.res_model")
    res_id = fields.Integer("ResId")

    #stage = fields.Reference(selection="_get_type_stages")
    stage_line_ids = fields.One2many(
        comodel_name="internship.document.stage.line",
        inverse_name="internship_document_id")
    # Active stage line linked fields
    # active_line_id = fields.Many2one(
    #     comodel_name="internship.document.stage.line", compute="compute_active_line", store=True)
    # stage_signer_ids = fields.Many2many(
    #     "internship.document.signer")
    #     #related="active_line_id.to_sign_by")
    # no_signed_by_ids = fields.Many2many("internship.document.signer",
    #                                  compute="compute_active_line")
    # signed_by_ids = fields.Many2many("internship.document.signer",
    #                               compute="compute_active_line")
    record_ref = fields.Reference(
        string="Record Referenced",
        compute="_compute_record_ref",
        selection=lambda self: self._get_ref_selection(),
    )
    state = fields.Selection(
        [
            ("no_started", "No Started"),
            ("started", "No File"),
            ("to_sign", "To Sign"),
            ("signed", "Signed"),
            ("done", "Done")
        ],
        string="Status",
        default="no_started",
    )

    def upload_file(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Upload File'),
            'res_model': 'upload.new.file',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }
    
    @api.depends("stage_line_ids")
    def compute_active_line(self):
        for record in self:
            active_line = record.stage_line_ids.filtered(lambda line: line.is_active)
            record.active_line_id = active_line and active_line[0] or False
            record.no_signed_by_ids = active_line.no_signed_by_ids if active_line else False
            record.signed_by_ids = active_line.signed_by_ids if active_line else False

    @api.model
    def _get_ref_selection(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    @api.depends("res_model", "res_id")
    def _compute_record_ref(self):
        for record in self:
            record.record_ref = False
            if record.res_model and record.res_id:
                record.record_ref = "{},{}".format(record.res_model, record.res_id)

    def launch_wizard(self, document_types):
        #TODO
        return True

    def create_new_document(self, res_model,res_id):
        res_model = res_model or self._context.get("active_model")
        document_types = self.env["internship.document.type"].search([
            ("res_model", "=", res_model)])
        if not document_types:
            raise Warning(_("No document type found for a model"))
        if len(document_types)>1:
            return self.launch_wizard(document_types)
        return self.create({
            "document_type_id": document_types.id,
            "res_model": document_types.res_model.id,
            "res_id": res_id,
            "stage_line_ids": [[0, 0, {
                "name": record.name,
                "sequence": record.sequence,
                "to_sign_by": [[0,0, {
                    "name": signer.name,
                }] for signer in record.stage_signer_ids]
            }] for record in document_types.stage_ids]
        })
          


    # @api.depends("no_signed", "school_signed", "second_party_signed")
    # def _internship_is_signed(self):
    #     if all([self.no_signed, self.school_signed, self.second_party_signed]):
    #         self.signed = True


class InternshipDocumentStageLine(models.Model):
    _name = "internship.document.stage.line"
    _order = "sequence,id"

    name = fields.Char("Name")
    sequence = fields.Integer(string="Sequence", default=10)
    to_sign_by = fields.Many2many("internship.document.signed.by",
                                  "document_line_internship_document_signer_to_sign_rel")
    signed_by_ids = fields.Many2many("internship.document.signed.by", compute="compute_get_signed_lines")
    no_signed_by_ids = fields.Many2many("internship.document.signed.by", compute="compute_get_signed_lines")
    internship_document_id = fields.Many2one("internship.document")
    everyone_sign = fields.Boolean("Everyone Must Sign", default=True)
    is_active = fields.Boolean("Is active")
    signed = fields.Boolean("Signed", compute="compute_is_signed")

    @api.depends("to_sign_by.signature_hash")
    def compute_is_signed(self):
        for record in self:
            signed_by_ids = record.to_sign_by.filtered(
                lambda signer: signer.signature_hash)
            record.signed_by_ids = signed_by_ids
            record.no_signed_by_ids = record.to_sign_by - signed_by_ids

    @api.depends("to_sign_by")
    def compute_is_signed(self):
        for record in self:
            if record.everyone_sign:
                record.signed = all(signer.signature_hash 
                                    for signer in record.to_sign_by)
            else:
                record.signed = any(signer.signature_hash 
                                    for signer in record.to_sign_by)

    @api.constrains('is_active')
    def unique_active_stage(self):
        checked = self.env["internship.document.type"]
        for record in self:
            final_stages = self.search_count([('document_type_id', '=',
                          record.document_type_id.id), ('is_active', '=',
                                                        True)])
            if final_stages > 1:
                raise ValidationError(_("is_final must be only in one stage"))
            checked |= record.document_type_id



class DocumentStage(models.Model):
    _name = "document.stage"
    _order = "sequence,id"

    
    name = fields.Char("Name")
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Char("Description")
    custom_partners_notification = fields.Boolean("Notify", default=True)
    document_type_id = fields.Many2one(comodel_name="internship.document.type")
    stage_signer_ids = fields.Many2many("internship.document.signer")
    everyone_sign = fields.Boolean("Everyone Must Sign", default=True)



class InternshipDocumentType(models.Model):
    _name = "internship.document.type"

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search(
            [("res_model", "in", True)])
        return [(model.model, model.name) for model in models]

    name = fields.Char("Name")
    code = fields.Char("Code",
                       default=lambda self: self.env['ir.sequence'].next_by_code('seq_internship_document_type'))
    res_model = fields.Many2one(comodel_name="ir.model")
    stage_ids = fields.One2many(comodel_name="document.stage",
                                inverse_name="document_type_id")
    
    
class ResPartnerInternshipDocument(models.Model):
    _inherit = "res.partner"

    documents_ids = fields.Many2many(comodel_name="internship.document",
                                     compute="_compute_internship_documents")

    def _compute_internship_documents(self):
        for partner in self:
            partner.documents_ids = self.env['internship.document'].search([(
                'res_model', '=', partner.model), ('res_id', '=', partner.id)])
            
    def create_document(self):
        self.env["internship.document"].create_new_document("res.partner", 
                                                            self.id)

