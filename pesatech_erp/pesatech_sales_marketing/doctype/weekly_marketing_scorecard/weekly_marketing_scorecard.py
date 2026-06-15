# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WeeklyMarketingScorecard(Document):
	def validate(self):
		self.cpl = (self.marketing_spend or 0) / self.mql if self.mql else 0
		self.demo_to_proposal = 100.0 * (self.proposals or 0) / self.demos if self.demos else 0
		misses = []
		if (self.mql or 0) < (self.mql_target or 0):
			misses.append('MQL')
		if (self.sql or 0) < (self.sql_target or 0):
			misses.append('SQL')
		self.target_status = 'Missed: ' + ', '.join(misses) if misses else 'On target'
