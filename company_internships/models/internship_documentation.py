# Copyright 2024 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _

DOCUMENT_MODELS = [("intership", "Internship"),
                   ("company", "Company")]

class InternshipDocumentation(models.Model):
    _name = "internship.documentation"

    @api.model
    def get_type_states(self):
        states = False#get from type
        return [(state.model,state.name) for state in states]

    no_signed = fields.Binary(string="No Signed")
    # model_id = fields.Many2one("ir.model", "Model",
    #                            readonly=True)

    school_signed = fields.Binary(string="School Director Signed")
    second_party_signed = fields.Binary(string="Second Party Signed")
    documentation_type = fields.Many2one(comodel_name="documentation.type")
    signed = fields.Boolean()#compute="_internship_is_signed")
    #state = fields.Reference(selection="_get_type_states")


    @api.depends("no_signed", "school_signed", "second_party_signed")
    def _internship_is_signed(self):
        if all([self.no_signed, self.school_signed, self.second_party_signed]):
            self.signed = True

class DocumentState(models.Model):
    _name = "document.state"

    name = fields.Char("Name")
    description = fields.Char("Description")
    custom_partners_notification = True
    notification_partners



class DocumentationType(models.Model):
    _name = "documentation.type"

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search(
            [("res_model", "in", True)])
        return [(model.model, model.name) for model in models]

    name = fields.Char("Name")
    model_id = fields.Reference(
        string="Model", selection="_selection_target_model")
    description = fields.Char("Description")
    state_ids = fields.Many2many("document.state")


class ResPartnerDocumentation(models.Model):
    _inherit = "res.partner"

    documents_ids = fields.Many2many(comodel_name="internship.documentation")


