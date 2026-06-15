# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerExit(Document):
	def on_submit(self):
		# Reflect churn on the related subscription
		if self.subscription:
			frappe.db.set_value('Customer Subscription', self.subscription, 'status', 'Churned')
