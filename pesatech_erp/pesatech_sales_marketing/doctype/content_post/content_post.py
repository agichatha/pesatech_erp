# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContentPost(Document):
	def validate(self):
		if not self.pillar or not self.funnel_stage:
			frappe.throw('Every post must map to a value pillar and a funnel stage \u2014 random, unlinked posts are not permitted.')
