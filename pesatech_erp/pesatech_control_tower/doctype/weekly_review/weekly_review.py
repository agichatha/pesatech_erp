# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WeeklyReview(Document):
	def validate(self):
		planned = self.planned_count or 0
		self.completion_rate = round(100.0 * (self.completed_count or 0) / planned, 0) if planned else 0

	def on_submit(self):
		s = frappe.get_single('Control Tower Settings')
		if s.require_manager_signoff and not self.signed_off:
			frappe.throw('Manager sign-off is required before submitting the weekly review.')
