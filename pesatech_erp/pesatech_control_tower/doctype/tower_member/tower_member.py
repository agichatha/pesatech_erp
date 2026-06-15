# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TowerMember(Document):
	def validate(self):
		s = frappe.get_single('Control Tower Settings')
		g, a = (s.rag_green or 80), (s.rag_amber or 70)
		c = self.completion_rate or 0
		self.rag = 'Green' if c >= g else ('Amber' if c >= a else 'Red')
