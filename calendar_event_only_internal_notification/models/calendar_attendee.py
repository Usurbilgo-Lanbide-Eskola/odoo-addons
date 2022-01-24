# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class CalendarAttendee(models.Model):
    _inherit = "calendar.attendee"

    def _send_mail_to_attendees(self, template_xmlid, force_send=False,
                                ignore_recurrence=False):
        no_confidential_attendees = self.env['calendar.attendee']
        for attendee in self:
            no_confidential = attendee.event_id.privacy != "confidential"
            if no_confidential or self.env['res.users'].search(
                    [('partner_id', '=', attendee.partner_id.id)]):
                no_confidential_attendees |= attendee
        return super(CalendarAttendee,
                     no_confidential_attendees)._send_mail_to_attendees(
            template_xmlid, force_send, ignore_recurrence)
