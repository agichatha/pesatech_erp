# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, getdate, add_days, add_months

CADENCE_DAYS = {'Daily': 1, 'Weekly': 7}


def advance(from_date, cadence):
	if cadence in CADENCE_DAYS:
		return add_days(from_date, CADENCE_DAYS[cadence])
	if cadence == 'Monthly':
		return add_months(from_date, 1)
	if cadence == 'Quarterly':
		return add_months(from_date, 3)
	return add_months(from_date, 12)


def get_member(employee):
	name = frappe.db.get_value('Tower Member', {'employee': employee}, 'name')
	if name:
		return frappe.get_doc('Tower Member', name)
	doc = frappe.get_doc({'doctype': 'Tower Member', 'employee': employee})
	doc.insert(ignore_permissions=True)
	return doc


def award(employee, points, on_time):
	"""Add points and update the completion streak for an employee."""
	m = get_member(employee)
	m.points_total = (m.points_total or 0) + (points or 0)
	if on_time:
		m.current_streak = (m.current_streak or 0) + 1
	else:
		m.current_streak = 0
	m.longest_streak = max(m.longest_streak or 0, m.current_streak)
	m.save(ignore_permissions=True)
	return m.name


@frappe.whitelist()
def generate_for_employee(employee, template):
	"""Create Employee Activity records from a position's Activity Template."""
	tpl = frappe.get_doc('Activity Template', template)
	created = []
	for item in (tpl.activities or []):
		doc = frappe.get_doc({
			'doctype': 'Employee Activity', 'employee': employee,
			'activity': item.activity, 'cadence': item.cadence,
			'objective': item.objective, 'kpi': item.kpi,
			'points': item.points or 10, 'source': 'Template',
			'next_due_date': nowdate(), 'status': 'Pending',
		})
		doc.insert(ignore_permissions=True)
		created.append(doc.name)
	return created


def get_leadership_summary():
	"""Roll-up powering the leadership dashboard: team completion, leaderboard,
	and objective progress."""
	objectives = frappe.get_all('Strategic Objective',
		fields=['name', 'objective_name', 'progress', 'rag'])
	leaderboard = frappe.get_all('Tower Member',
		fields=['employee', 'points_total', 'current_streak', 'completion_rate'],
		order_by='points_total desc', limit_page_length=10)
	return {'objectives': objectives, 'leaderboard': leaderboard}
