# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PipelineLead(Document):
	def validate(self):
		s = frappe.get_single('Sales Marketing Settings')
		score = self.lead_score or 0
		if score >= (s.sql_score_threshold or 75):
			self.qualification = 'SQL'
		elif score >= (s.mql_score_threshold or 50):
			self.qualification = 'MQL'
		else:
			self.qualification = 'Unqualified'
