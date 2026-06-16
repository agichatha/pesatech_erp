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
		fields=['name', 'objective_name', 'progress', 'rag'],
		ignore_permissions=True)
	leaderboard = frappe.get_all('Tower Member',
		fields=['employee', 'points_total', 'current_streak', 'completion_rate'],
		order_by='points_total desc', limit_page_length=10, ignore_permissions=True)
	return {'objectives': objectives, 'leaderboard': leaderboard}


@frappe.whitelist()
def seed_demo():
	"""One-click demo seed so the Control Tower dashboards have data to show.
	Idempotent: safe to run more than once. Returns a summary dict."""
	from frappe.utils import nowdate, add_days
	out = {}

	# 1) Strategic Objectives (one per pillar, varied progress + RAG)
	objs = [
		("Launch PesaPay 2.0 platform", "Innovation & Product Leadership", 88, "Green"),
		("Grow SME client base by 40%", "Market Expansion", 72, "Amber"),
		("Achieve 95% customer satisfaction", "Customer Experience Excellence", 64, "Red"),
		("Attain ISO 27001 certification", "Operational Excellence & Governance", 84, "Green"),
		("Build a high-performance culture", "Talent Development & Culture", 78, "Amber"),
	]
	created = []
	for name, pillar, prog, rag in objs:
		if not frappe.db.exists("Strategic Objective", {"objective_name": name}):
			d = frappe.get_doc({
				"doctype": "Strategic Objective", "objective_name": name,
				"pillar": pillar, "fiscal_year": "2026", "progress": prog,
				"rag": rag, "description": "Seeded demo objective.",
			})
			d.insert(ignore_permissions=True)
			created.append(d.name)
	out["objectives_created"] = created

	# 2) Employee to own the activities
	emp = frappe.db.get_value("Employee", {"employee_name": "Demo Marketing Lead"}, "name")
	if not emp:
		company = (frappe.defaults.get_global_default("company")
			or frappe.db.get_value("Company", {}, "name"))
		e = frappe.get_doc({
			"doctype": "Employee", "first_name": "Demo", "last_name": "Marketing Lead",
			"gender": "Male", "date_of_birth": "1990-01-01",
			"date_of_joining": "2026-01-01", "company": company, "status": "Active",
		})
		e.insert(ignore_permissions=True)
		emp = e.name
	out["employee"] = emp

	# 3) Generate activities from the marketing template
	tpl = "Marketing Lead - Social Media Rhythm"
	if frappe.db.exists("Activity Template", tpl) and not frappe.db.exists(
			"Employee Activity", {"employee": emp}):
		generate_for_employee(emp, tpl)
	# push one into Overdue so that card lights up
	acts = frappe.get_all("Employee Activity", {"employee": emp}, ["name"], limit=1)
	if acts:
		a = frappe.get_doc("Employee Activity", acts[0].name)
		a.next_due_date = add_days(nowdate(), -2)
		a.save(ignore_permissions=True)
	out["activities"] = frappe.db.count("Employee Activity", {"employee": emp})

	# 4) Tower Member with points + completion (drives leaderboard + avg-completion card)
	tm = frappe.db.get_value("Tower Member", {"employee": emp}, "name")
	if not tm:
		m = frappe.get_doc({"doctype": "Tower Member", "employee": emp})
		m.insert(ignore_permissions=True)
		tm = m.name
	m = frappe.get_doc("Tower Member", tm)
	m.completion_rate = 86
	m.points_total = 140
	m.current_streak = 6
	m.longest_streak = 9
	m.save(ignore_permissions=True)
	out["tower_member"] = tm

	frappe.db.commit()
	return out


@frappe.whitelist()
def get_dashboard():
	"""Single endpoint powering the /control-tower page (fetched client-side)."""
	data = get_leadership_summary()
	counts = {}
	for r in frappe.get_all("Employee Activity",
			fields=["status", "count(name) as c"], group_by="status",
			ignore_permissions=True):
		counts[r.status] = r.c
	data["counts"] = counts
	data["pending"] = counts.get("Pending", 0)
	data["overdue"] = counts.get("Overdue", 0)
	data["done"] = counts.get("Done", 0)
	return data
