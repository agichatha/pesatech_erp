# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class BudgetCommitment(Document):
	def validate(self):
		if not self.commitment_date:
			self.commitment_date = nowdate()

	def on_submit(self):
		self.apply_to_budget(1)

	def on_cancel(self):
		self.apply_to_budget(-1)

	def apply_to_budget(self, sign):
		# Reserve (sign=+1) or release (sign=-1) the amount on the matching budget line
		if not (self.budget and self.account):
			return
		budget = frappe.get_doc('Pesatech Budget', self.budget)
		matched = False
		for line in (budget.lines or []):
			if line.account == self.account and (
				not self.cost_center or line.cost_center == self.cost_center):
				line.committed_amount = (line.committed_amount or 0) + sign * (self.amount or 0)
				line.available_amount = (line.budget_amount or 0) \
					- (line.committed_amount or 0) - (line.actual_amount or 0)
				matched = True
				break
		if matched:
			budget.flags.ignore_validate_update_after_submit = True
			budget.save(ignore_permissions=True)
