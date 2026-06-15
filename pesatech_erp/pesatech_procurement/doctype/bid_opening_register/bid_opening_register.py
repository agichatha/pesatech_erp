# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class BidOpeningRegister(Document):
	def on_submit(self):
		# Unseal all bids for the event and record the opening
		for row in (self.entries or []):
			if not row.bid:
				continue
			bid = frappe.get_doc('Bid', row.bid)
			bid.db_set('sealed', 0)
			bid.db_set('status', 'Responsive' if row.responsive else 'Non-Responsive')
		if self.sourcing_event:
			frappe.db.set_value('Sourcing Event', self.sourcing_event, 'status', 'Under Evaluation')
		if not self.opening_datetime:
			self.opening_datetime = now_datetime()
