# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate
from pesatech_erp.pesatech_control_tower.api import advance, award


class EmployeeActivity(Document):
	def validate(self):
		if self.next_due_date and self.status != 'Done':
			if getdate(self.next_due_date) < getdate(nowdate()):
				self.status = 'Overdue'

	@frappe.whitelist()
	def mark_done(self):
		on_time = True
		if self.next_due_date:
			on_time = getdate(nowdate()) <= getdate(self.next_due_date)
		self.last_completed = nowdate()
		award(self.employee, self.points or 0, on_time)
		self.next_due_date = advance(self.next_due_date or nowdate(), self.cadence)
		self.status = 'Pending'
		self.save()
