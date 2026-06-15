# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PositionContract(Document):
	def validate(self):
		if self.status == 'Signed' and not self.accepted_by:
			frappe.throw('A signed Position Contract must record who accepted accountability.')
