# Copyright 2025 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CrmInternshipPartialMove(models.TransientModel):
    _name = "crm.internship.partial.move"
    _description = "Wizard to mark internship opportunity as partially move"

    lead_id = fields.Many2one("crm.lead", required=True, readonly=True)
    target_stage_id = fields.Many2one(
        "crm.stage", 
        string="Target Stage", 
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name="crm.internship.partial.move.line",
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
            "move_qty": 0,
            "internship_type_id": lead.internship_type_id.id,
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
            if l.move_qty < 0:
                raise ValidationError(_("move quantity cannot be negative."))
            if l.move_qty > l.original_qty:
                raise ValidationError(
                    _("Move quantity cannot exceed original quantity for group %s.")
                    % (l.student_group_id.display_name,)
                )

        if not any(l.move_qty > 0 for l in self.line_ids):
            raise ValidationError(
                _("At least one line must have a move quantity greater than zero."))

        lead = self.lead_id.sudo()

        # Prepare move lead copy values: only lines with move_qty > 0
        new_lines = []
        internship_line_obj = self.env["internship.line"]
        for l in self.line_ids.filtered(lambda x: x.move_qty > 0):
            line_dict = l.get_line_dict()
            existing_line = internship_line_obj.search(
                [("school_year_id", "=", lead.school_year_id.id), 
                 ("student_group_id", "=", line_dict["student_group_id"]),
                 ("internship_type_id", "=", line_dict.get("internship_type_id")),
                 ("agreement_type", "=", line_dict.get("agreement_type")),
                 ("lead_id.stage_id", "=", self.target_stage_id.id)
                 ("partner_id", "=", lead.partner_id.id)])
            if existing_line:
                existing_line.student_qty += line_dict["student_qty"]
            else:           
                new_lines.append(
                    (0, 0, line_dict)
                )

        # Only create a new lead if we have new lines to add
        if new_lines:
            copy_vals = {
                "name": _("%s (Moved to %s)") % (lead.name, self.target_stage_id.name),
                "internship_line_ids": new_lines,
                "stage_id": self.target_stage_id.id,
            }

            move_lead = lead.copy(copy_vals)
        else:
            move_lead = None

        # Deduct moved quantities from original lead
        for l in self.line_ids:
            if not l.internship_line_id:
                continue
            remaining = (l.original_qty or 0) - (l.move_qty or 0)
            if remaining <= 0:
                l.internship_line_id.unlink()
            else:
                l.internship_line_id.student_qty = remaining

        # Return action to open the newly moved lead if created
        if move_lead:
            return {
                "type": "ir.actions.act_window",
                "res_model": "crm.lead",
                "view_mode": "form",
                "res_id": move_lead.id,
                "target": "current",
            }
        else:
            return {"type": "ir.actions.act_window_close"}


class CrmInternshipPartialMoveLine(models.TransientModel):
    _name = "crm.internship.partial.move.line"
    _description = "Wizard line for internship partial move"

    wizard_id = fields.Many2one(
        "crm.internship.partial.move", required=True, ondelete="cascade")
    internship_line_id = fields.Many2one("internship.line", string="Original Line")
    student_group_id = fields.Many2one(
        "product.product", string="Student Group", readonly=True)
    internship_type_id = fields.Many2one(
        "internship.type", string="Internship Type", readonly=True)
    agreement_type = fields.Many2one(
        "agreement.type", string="Agreement Type", readonly=True)
    original_qty = fields.Integer(string="Original Qty", readonly=True)
    move_qty = fields.Integer(string="Move Qty")
    current_stage = fields.Char(related="internship_line_id.lead_id.stage_id.name", string="Current Stage", readonly=True)

    @api.constrains("move_qty")
    def _check_move_qty(self):
        for rec in self:
            if rec.move_qty is not None and rec.move_qty < 0:
                raise ValidationError(_("Move quantity cannot be negative."))
            if rec.original_qty is not None and rec.move_qty is not None and rec.move_qty > rec.original_qty:
                raise ValidationError(_("Move quantity cannot exceed original quantity."))

    def get_line_dict(self):
        self.ensure_one()
        return {
            "student_group_id": self.student_group_id.id,
            "student_qty": self.move_qty,
            "agreement_type": self.agreement_type.id if self.agreement_type else False,
            "internship_type_id": self.internship_type_id.id if self.internship_type_id else False,
        }
        
