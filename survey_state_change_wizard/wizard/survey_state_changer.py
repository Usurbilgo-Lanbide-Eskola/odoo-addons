# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class SurveyStateChanger(models.Model):
    _name = "survey.state.changer"

    dest_state = fields.Selection(selection=[('draft', 'Draft'),
                                             ('open', 'In progress'),
                                             ('closed', 'Closed')],
                                  string="Change to State")

    def change_state(self):
        survey_ids = self._context.get("active_ids")
        surveys = self.env['survey.survey'].browse(survey_ids)
        if self.dest_state == 'draft':
            open_surveys = surveys.filtered(lambda x: x.state == 'closed')
            open_surveys.action_draft()
        elif self.dest_state == 'open':
            open_surveys = surveys.filtered(
                lambda x: x.state == 'draft' and x.id)
            open_surveys.action_open()
        else:
            open_surveys = surveys.filtered(lambda x: x.state == 'open')
            open_surveys.action_close()
        return
