# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesDeal(Document):
	def validate(self):
		self.apply_pricing()
		self.compute_commission()
		self.check_discount()

	def apply_pricing(self):
		if self.pricing_plan and not self.list_price:
			self.list_price = frappe.db.get_value('Pricing Plan', self.pricing_plan, 'base_price')
		disc = self.discount_pct or 0
		if not self.deal_value:
			self.deal_value = (self.list_price or 0) * (1 - disc / 100.0)

	def compute_commission(self):
		if self.agent:
			rate = frappe.db.get_value('Sales Agent', self.agent, 'commission_rate') or 0
			self.commission_rate = rate
			self.commission_amount = (self.deal_value or 0) * rate / 100.0

	def check_discount(self):
		s = frappe.get_single('Sales Marketing Settings')
		limit = s.discount_approval_threshold or 0
		if (self.discount_pct or 0) > limit and not self.discount_approved_by:
			frappe.msgprint(
				'Discount %.0f%% exceeds the %.0f%% threshold and requires MD approval.'
				% (self.discount_pct, limit), alert=True)
