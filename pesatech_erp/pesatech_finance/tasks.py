# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, getdate, add_days


def send_finance_reminders():
	"""Daily scheduler: remind owners of finance activities due within lead days,
	and flag overdue ones."""
	today = getdate(nowdate())
	for a in frappe.get_all('Finance Activity',
			filters={'status': ['!=', 'Done']},
			fields=['name', 'activity', 'next_due_date', 'reminder_lead_days', 'responsible', 'status']):
		if not a.next_due_date:
			continue
		due = getdate(a.next_due_date)
		lead = a.reminder_lead_days or 3
		if due < today and a.status != 'Overdue':
			frappe.db.set_value('Finance Activity', a.name, 'status', 'Overdue')
		if today >= add_days(due, -lead):
			_notify(a)


def _notify(activity):
	msg = 'Finance activity due: %s (by %s)' % (activity.activity, activity.next_due_date)
	if activity.responsible:
		try:
			frappe.sendmail(recipients=[activity.responsible], subject='Finance reminder', message=msg)
		except Exception:
			frappe.logger().info(msg)
	else:
		frappe.logger().info(msg)
