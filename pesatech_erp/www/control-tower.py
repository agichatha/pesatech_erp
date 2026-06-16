# Copyright (c) 2026, Pesatech Solutions Limited and contributors
import frappe


def get_context(context):
	context.no_cache = 1
	if frappe.session.user == "Guest":
		frappe.throw("Please log in to view the Control Tower.", frappe.PermissionError)

	# Defaults first so the template never sees an undefined variable.
	context.objectives = []
	context.leaderboard = []
	context.status_counts = {}
	context.pending = 0
	context.overdue = 0
	context.done = 0

	try:
		from pesatech_erp.pesatech_control_tower.api import get_leadership_summary
		data = get_leadership_summary()
		context.objectives = data.get("objectives", []) or []
		context.leaderboard = data.get("leaderboard", []) or []
	except Exception:
		frappe.log_error(title="Control Tower page: leadership summary failed")

	try:
		counts = {}
		for r in frappe.get_all(
			"Employee Activity", fields=["status", "count(name) as c"], group_by="status"
		):
			counts[r.status] = r.c
		context.status_counts = counts
		context.pending = counts.get("Pending", 0)
		context.overdue = counts.get("Overdue", 0)
		context.done = counts.get("Done", 0)
	except Exception:
		frappe.log_error(title="Control Tower page: activity counts failed")

	return context
