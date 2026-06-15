# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days


class CustomerSubscription(Document):
	def validate(self):
		if self.renewal_date:
			days = (getdate(self.renewal_date) - getdate(nowdate())).days
			self.days_to_renewal = days
			s = frappe.get_single('CRM Settings')
			window = s.renewal_reminder_days or 30
			if self.status == 'Active' and 0 <= days <= window:
				self.renewal_due = 1
			else:
				self.renewal_due = 0
