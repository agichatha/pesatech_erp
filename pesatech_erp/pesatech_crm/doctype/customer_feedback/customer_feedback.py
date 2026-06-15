# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerFeedback(Document):
	def validate(self):
		# NPS category from a 0-10 score
		score = self.nps_score
		if score is None:
			return
		if score >= 9:
			self.nps_category = 'Promoter'
		elif score >= 7:
			self.nps_category = 'Passive'
		else:
			self.nps_category = 'Detractor'
