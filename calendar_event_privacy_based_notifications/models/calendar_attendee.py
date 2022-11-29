# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class CalendarAttendee(models.Model):
    _inherit = "calendar.attendee"

    def _send_mail_to_attendees(self, template_xmlid, force_send=False,
                                ignore_recurrence=False):
        attendees = self.env['calendar.attendee']
        for attendee in self:
            public = attendee.event_id.privacy == "public"
            private = attendee.event_id.privacy == "private"
            attendee_partner_id = attendee.partner_id.id
            event_owner_partner_id = attendee.event_id.create_uid.partner_id.id
            if private:
                if attendee_partner_id == event_owner_partner_id:
                    attendees |= attendee
            elif public or self.env['res.users'].search(
                    [('partner_id', '=', attendee.partner_id.id)]):
                attendees |= attendee
        return super(CalendarAttendee,
                     attendees)._send_mail_to_attendees(
            template_xmlid, force_send, ignore_recurrence)
