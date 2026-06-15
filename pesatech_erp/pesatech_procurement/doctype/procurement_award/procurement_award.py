# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days


class ProcurementAward(Document):
	def validate(self):
		self.set_approval_level()
		self.set_standstill()

	def set_approval_level(self):
		s = frappe.get_single('Procurement Settings')
		val = self.award_value or 0
		if val <= (s.approval_threshold_officer or 0):
			self.approval_level = 'Procurement Officer'
		elif val <= (s.approval_threshold_manager or 0):
			self.approval_level = 'Managing Director'
		else:
			self.approval_level = 'Director / Board'

	def set_standstill(self):
		s = frappe.get_single('Procurement Settings')
		self.standstill_until = add_days(nowdate(), int(s.standstill_days or 0))

	def on_submit(self):
		self.notify_bidders()

	def notify_bidders(self):
		# Notify the successful bidder and all unsuccessful bidders (standstill notice)
		try:
			bids = frappe.get_all('Bid', filters={'sourcing_event': self.sourcing_event},
				fields=['name', 'supplier'])
			for b in bids:
				successful = (b['name'] == self.bid)
				frappe.logger().info('Award notice -> %s (%s)' % (
					b['supplier'], 'AWARDED' if successful else 'unsuccessful'))
			self.db_set('notification_sent', 1)
		except Exception:
			frappe.log_error(title='Award notification failed')
