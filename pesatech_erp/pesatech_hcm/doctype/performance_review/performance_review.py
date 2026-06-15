# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PerformanceReview(Document):
	def validate(self):
		total_weight = 0
		overall = 0
		for it in (self.items or []):
			it.weighted_score = (it.rating or 0) * (it.weight or 0) / 100.0
			overall += it.weighted_score
			total_weight += (it.weight or 0)
		self.overall_rating = round(overall, 1)
		if total_weight and abs(total_weight - 100) > 0.01:
			frappe.msgprint('KPI weights total %.0f%% (expected 100%%).' % total_weight, alert=True)
