# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        now = fields.Datetime.now()
        past_events = events.filtered(lambda event: event.start <= now)
        past_events.attendee_ids._send_mail_to_attendees(
            'calendar.calendar_template_meeting_invitation')
        return events

    def write(self, values):
        recurrence_update_setting = values.get('recurrence_update', None)
        res = super().write(values)
        if 'start' in values:
            update_recurrence = recurrence_update_setting in (
                'all_events', 'future_events') and len(self) == 1
            previous_attendees = self.attendee_ids
            current_attendees = self.filtered('active').attendee_ids
            attendees = (current_attendees & previous_attendees)

            start_date = fields.Datetime.to_datetime(values.get('start'))
            if start_date and start_date < fields.Datetime.now():
                attendees._send_mail_to_attendees(
                    'calendar.calendar_template_meeting_changedate',
                    ignore_recurrence=not update_recurrence)
        return res
