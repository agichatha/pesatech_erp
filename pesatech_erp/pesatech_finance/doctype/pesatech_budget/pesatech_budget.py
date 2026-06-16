# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PesatechBudget(Document):
	def validate(self):
		total = 0
		for line in (self.lines or []):
			line.available_amount = (line.budget_amount or 0) \
				- (line.committed_amount or 0) - (line.actual_amount or 0)
			total += (line.budget_amount or 0)
		self.total_budget = total
