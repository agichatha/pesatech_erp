# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime, time_diff_in_hours


class SupportTicket(Document):
	def validate(self):
		self.set_sla()
		self.check_breach()

	def set_sla(self):
		if self.sla_hours:
			return
		s = frappe.get_single('Pesatech CRM Settings')
		mapping = {'Urgent': s.sla_urgent_hours or 4, 'High': s.sla_high_hours or 8,
			'Medium': s.sla_medium_hours or 24, 'Low': s.sla_low_hours or 48}
		self.sla_hours = mapping.get(self.priority, 24)

	def check_breach(self):
		if self.status == 'Resolved' and self.opened_on and self.resolved_on:
			hrs = time_diff_in_hours(get_datetime(self.resolved_on), get_datetime(self.opened_on))
			self.resolution_hours = round(hrs, 1)
			self.sla_breached = 1 if hrs > (self.sla_hours or 0) else 0
