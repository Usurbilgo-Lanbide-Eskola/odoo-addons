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

class InternshipDocument(models.Model):
    _name = "internship.document"

    # @api.model
    # def get_type_states(self):
    #     states = False#get from type
    #     return [(state.model,state.name) for state in states]

    original_document = fields.Binary(string="Original Document")
    final_document = fields.Binary(string="Final Document")
    # model_id = fields.Many2one("ir.model", "Model",
    #                            readonly=True)

    document_type = fields.Many2one(comodel_name="internship.document.type")
    res_model = fields.Many2one("res.model",
                                related="document_type_id.res_model")
    res_id = fields.Integer("ResId")

    #state = fields.Reference(selection="_get_type_states")
    state_line_ids = fields.One2many(
        comodel_name="internship.document.state.line")
    # Active state line linked fields
    state_id = fields.Many2one(comodel_name="document.state")
    document = fields.Binary("Document")
    state_signer_ids = fields.Many2many(
        "internship.document.signer",
        related="state_id.state_signer_ids")
    signed_by_ids = fields.Many2many("internship.document.signer")
    to_sign_by = fields.Many2many("internship.document.signer")


    @api.depends("no_signed", "school_signed", "second_party_signed")
    def _internship_is_signed(self):
        if all([self.no_signed, self.school_signed, self.second_party_signed]):
            self.signed = True

class InternshipDocumentStateLine(models.Model):
    _name = "internship.document.state.line"

    document = fields.Binary("Document")
    state_signer_ids = fields.Many2many(
        "internship.document.signer",
        related="state_id.state_signer_ids")
    signed_by_ids = fields.Many2many("internship.document.signer")
    to_sign_by = fields.Many2many("internship.document.signer")
    internship_document_id = fields.Many2one("internship.document")
    state_id = fields.Many2one(comodel_name="document.state")


class DocumentState(models.Model):
    _name = "document.state"

    name = fields.Char("Name")
    description = fields.Char("Description")
    custom_partners_notification = fields.Boolean("Notify", default=True)
    document_type_id = fields.Many2one(comodel_name="internship.document.type")
    state_signer_ids = fields.Many2many("internship.document.signer")
    everyone_sign = fields.Boolean("Everyone Must Sign", default=True)
    is_final = fields.Boolean("Is Final")

    @api.constrains('is_final')
    def unique_final_state(self):
        checked = self.env["internship.document.type"]
        for record in self:
            final_states = self.search_count([('document_type_id', '=',
                          record.document_type_id.id), ('is_final', '=',
                                                        True)])
            if final_states > 1:
                raise ValidationError(_("is_final must be only in one state"))
            checked |= record.document_type_id





class InternshipDocumentType(models.Model):
    _name = "internship.document.type"

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search(
            [("res_model", "in", True)])
        return [(model.model, model.name) for model in models]

    name = fields.Char("Name")
    res_model = fields.Many2one(comodel_name="res.model")
    state_ids = fields.One2many(comodel_name="document.state",
                                inverse_name="document_type_id")


class ResPartnerInternshipDocument(models.Model):
    _inherit = "res.partner"

    documents_ids = fields.Many2many(comodel_name="internship.document",
                                     compute="_compute_internship_documents")

    def _compute_internship_documents(self):
        for partner in self:
            partner.documents_ids = self.env['internship.document'].search([(
                'res_model', '=', partner.model), ('res_id', '=', partner.id)])


#TODO
"internship_documentation_line_manager","internship_documentation_manager","model_internship_documentation","sales_team.group_sale_salesman",1,1,1,1
"internship_documentation_user","internship_documentation_user","model_internship_documentation","base.group_user",1,0,0,0
"document_type_manager","document_type_manager","model_documentation_type","sales_team.group_sale_salesman",1,1,1,1
"document_type_user","document_type_user","model_documentation_type","base.group_user",1,0,0,0
"document_state_manager","document_state_manager","model_document_state","sales_team.group_sale_salesman",1,1,1,1
"document_state_user","document_state_user","model_document_state","base.group_user",1,0,0,0