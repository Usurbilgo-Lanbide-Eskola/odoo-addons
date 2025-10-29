# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CrmInternshipPartialWon(models.TransientModel):
    _name = "crm.internship.partial.won"
    _description = "Wizard to mark internship opportunity as partially won"

    lead_id = fields.Many2one("crm.lead", required=True, readonly=True)
    line_ids = fields.One2many(
        comodel_name="crm.internship.partial.won.line",
        inverse_name="wizard_id",
        string="Lines",
    )

    def generate_line_dict(self, lead=None):
        if lead is None:
            return 
        return{
            "internship_line_id": lead.id,
            "student_group_id": lead.student_group_id.id,
            "original_qty": lead.student_qty,
            "won_qty": 0,
            "agreement_type": lead.agreement_type.id,
        }

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get(
            "default_lead_id") or self.env.context.get("active_id")
        if active_id:
            lead = self.env["crm.lead"].browse(active_id)
            res["lead_id"] = lead.id
            # Prefill wizard lines from lead internship lines
            lines = []
            for line in lead.internship_line_ids:
                lines.append(
                    (
                        0,
                        0,
                        self.generate_line_dict(line)
                    )
                )
            res["line_ids"] = lines
        return res

    def action_confirm(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_("There are no internship lines to process."))

        # Validate quantities
        for l in self.line_ids:
            if l.won_qty < 0:
                raise ValidationError(_("Won quantity cannot be negative."))
            if l.won_qty > l.original_qty:
                raise ValidationError(
                    _("Won quantity cannot exceed original quantity for group %s.")
                    % (l.student_group_id.display_name,)
                )

        if not any(l.won_qty > 0 for l in self.line_ids):
            raise ValidationError(
                _("At least one line must have a won quantity greater than zero."))

        lead = self.lead_id.sudo()

        # Prepare won lead copy values: only lines with won_qty > 0
        new_lines = []
        for l in self.line_ids.filtered(lambda x: x.won_qty > 0):
            new_lines.append(
                (0, 0, l.get_line_dict())
            )

        copy_vals = {
            "name": _("%s (Partially Won)") % lead.name,
            "internship_line_ids": new_lines,
        }

        won_lead = lead.copy(copy_vals)

        # Set copied lead as won
        # Use standard CRM API to mark as won
        if hasattr(won_lead, "action_set_won"):
            won_lead.action_set_won()
        else:
            won_lead.action_set_won_rainbowman()

        # Deduct won quantities from original lead
        for l in self.line_ids:
            if not l.internship_line_id:
                continue
            remaining = (l.original_qty or 0) - (l.won_qty or 0)
            if remaining <= 0:
                l.internship_line_id.unlink()
            else:
                l.internship_line_id.student_qty = remaining

        # Return action to open the newly won lead
        return {
            "type": "ir.actions.act_window",
            "res_model": "crm.lead",
            "view_mode": "form",
            "res_id": won_lead.id,
            "target": "current",
        }


class CrmInternshipPartialWonLine(models.TransientModel):
    _name = "crm.internship.partial.won.line"
    _description = "Wizard line for internship partial won"

    wizard_id = fields.Many2one(
        "crm.internship.partial.won", required=True, ondelete="cascade")
    internship_line_id = fields.Many2one("internship.line", string="Original Line")
    student_group_id = fields.Many2one(
        "product.product", string="Student Group", readonly=True)
    agreement_type = fields.Many2one(
        "agreement.type", string="Agreement Type", readonly=True)
    original_qty = fields.Integer(string="Original Qty", readonly=True)
    won_qty = fields.Integer(string="Won Qty")

    @api.constrains("won_qty")
    def _check_won_qty(self):
        for rec in self:
            if rec.won_qty is not None and rec.won_qty < 0:
                raise ValidationError(_("Won quantity cannot be negative."))
            if rec.original_qty is not None and rec.won_qty is not None and rec.won_qty > rec.original_qty:
                raise ValidationError(_("Won quantity cannot exceed original quantity."))

    def get_line_dict(self):
        self.ensure_one()
        return {
            "student_group_id": self.student_group_id.id,
            "student_qty": self.won_qty,
            "agreement_type": self.agreement_type.id if self.agreement_type else False,
        }
        
