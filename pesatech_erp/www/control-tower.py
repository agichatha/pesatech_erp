# Copyright (c) 2026, Pesatech Solutions Limited and contributors
import frappe
from pesatech_erp.pesatech_control_tower.api import get_leadership_summary


def get_context(context):
	context.no_cache = 1
	if frappe.session.user == 'Guest':
		frappe.throw('Please log in to view the Control Tower.', frappe.PermissionError)
	data = get_leadership_summary()
	context.objectives = data.get('objectives', [])
	context.leaderboard = data.get('leaderboard', [])
	counts = {}
	for r in frappe.get_all('Employee Activity',
			fields=['status', 'count(name) as c'], group_by='status'):
		counts[r.status] = r.c
	context.pending = counts.get('Pending', 0)
	context.overdue = counts.get('Overdue', 0)
	context.done = counts.get('Done', 0)
	context.status_counts = counts
	return context
