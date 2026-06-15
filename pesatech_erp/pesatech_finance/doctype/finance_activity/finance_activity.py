# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, add_days, add_months


FREQ_DAYS = {'Daily': 1, 'Weekly': 7}


class FinanceActivity(Document):
	def validate(self):
		if self.next_due_date and self.status != 'Done':
			if getdate(self.next_due_date) < getdate(nowdate()):
				self.status = 'Overdue'

	@frappe.whitelist()
	def mark_done(self):
		self.last_completed = nowdate()
		self.next_due_date = self.advance(self.next_due_date or nowdate())
		self.status = 'Pending'
		self.save()

	def advance(self, from_date):
		freq = self.frequency or 'Monthly'
		if freq in FREQ_DAYS:
			return add_days(from_date, FREQ_DAYS[freq])
		if freq == 'Monthly':
			return add_months(from_date, 1)
		if freq == 'Quarterly':
			return add_months(from_date, 3)
		return add_months(from_date, 12)
