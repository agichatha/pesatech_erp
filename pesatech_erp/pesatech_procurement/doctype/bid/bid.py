# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class Bid(Document):
	def validate(self):
		self.compute_totals()
		self.enforce_deadline()

	def compute_totals(self):
		total = 0
		for it in (self.items or []):
			it.amount = (it.qty or 0) * (it.unit_price or 0)
			total += it.amount
		if not self.total_bid_value:
			self.total_bid_value = total

	def enforce_deadline(self):
		if not self.sourcing_event:
			return
		closing = frappe.db.get_value('Sourcing Event', self.sourcing_event, 'closing_date')
		submitted = get_datetime(self.submitted_on or now_datetime())
		if closing and submitted > get_datetime(closing):
			frappe.throw('Bid submitted after the closing deadline and cannot be accepted.')
		if self.is_new() and not self.submitted_on:
			self.submitted_on = now_datetime()
			self.sealed = 1
