# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StrategicTarget(Document):
	def validate(self):
		# Re-roll the parent objective's progress when a target changes
		if self.objective and not self.flags.in_insert:
			try:
				obj = frappe.get_doc('Strategic Objective', self.objective)
				obj.save(ignore_permissions=True)
			except Exception:
				pass
