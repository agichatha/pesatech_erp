# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class SourcingEvent(Document):
	def validate(self):
		self.set_recommended_method()
		self.validate_dates()
		self.validate_prequalification()

	def set_recommended_method(self):
		s = frappe.get_single('Procurement Settings')
		val = self.estimated_value or 0
		if val <= (s.low_value_max or 0):
			self.recommended_method = 'Low Value Procurement'
		elif val <= (s.rfq_max or 0):
			self.recommended_method = 'Request for Quotation (RFQ)'
		else:
			self.recommended_method = 'Open Tender'

	def validate_dates(self):
		if self.closing_date and self.opening_date:
			if get_datetime(self.opening_date) < get_datetime(self.closing_date):
				frappe.throw('Bid opening date must be on or after the closing date.')

	def validate_prequalification(self):
		s = frappe.get_single('Procurement Settings')
		if not (self.require_prequalification or s.enforce_prequalification):
			return
		for row in (self.suppliers or []):
			if not row.prequalified:
				ok = frappe.db.exists('Supplier Prequalification',
					{'supplier': row.supplier, 'status': 'Approved'})
				row.prequalified = 1 if ok else 0

	def before_bids_open(self):
		# Guard used by Bid Evaluation: bids must not be evaluated before opening
		if self.status not in ('Closed', 'Under Evaluation', 'Awarded'):
			frappe.throw('Bids cannot be processed before the event is closed/opened.')
