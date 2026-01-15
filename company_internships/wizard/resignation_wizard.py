# Copyright 2026 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class ResignationWizard(models.TransientModel):
    _name = "resignation.wizard"
    _description = "Resignation Wizard"

    reason = fields.Char(string="Reason", required=True)
    clear_old_data = fields.Boolean(string="Clear Old Data", default=True)

    def action_submit(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            historical = self.env['school.year.historical'].browse(active_id)
            # Create resigned.internship.line with copied fields
            vals = {
                'record_id': historical.id,
                'student_company_id': historical.student_company_id.id,
                'description': self.reason,
                'student_tutor_id': historical.student_tutor_id.id,
                'student_instructor_id': historical.student_instructor_id.id,
                'internship_type': historical.internship_type.id,
                'agreement_type_id': historical.agreement_type_id.id,
                'special_internship': historical.special_internship,
                'special_internship_reason_id': historical.special_internship_reason_id.id,
                'notes': historical.notes,
                'unsubscribed': historical.unsubscribed,
                'turn': historical.turn,
                'student_delivery_id': historical.student_delivery_id.id,
            }
            self.env['resigned.internship.line'].create(vals)
            if self.clear_old_data:
                historical.write({
                    'student_company_id': False,
                    'student_instructor_id': False,
                    'internship_type': False,
                    'agreement_type_id': False,
                    'special_internship': False,
                    'special_internship_reason_id': False,
                    'notes': False,
                    'unsubscribed': False,
                    'turn': False,
                    'student_delivery_id': False,
                    'state': 'draft',
                })
        return {'type': 'ir.actions.act_window_close'}