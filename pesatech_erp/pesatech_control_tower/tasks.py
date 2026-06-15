# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, getdate, add_days


def send_activity_reminders():
	"""Daily: remind employees of activities due within lead days; flag overdue."""
	s = frappe.get_single('Control Tower Settings')
	lead = s.reminder_lead_days or 1
	today = getdate(nowdate())
	for a in frappe.get_all('Employee Activity',
			filters={'status': ['!=', 'Done']},
			fields=['name', 'employee', 'activity', 'next_due_date', 'status']):
		if not a.next_due_date:
			continue
		due = getdate(a.next_due_date)
		if due < today and a.status != 'Overdue':
			frappe.db.set_value('Employee Activity', a.name, 'status', 'Overdue')
		if today >= add_days(due, -lead):
			frappe.logger().info('Control Tower reminder: %s due %s for %s'
				% (a.activity, a.next_due_date, a.employee))
