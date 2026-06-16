# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe


def get_active_budget(fiscal_year=None, cost_center=None):
	filters = {'status': 'Approved'}
	if fiscal_year:
		filters['fiscal_year'] = fiscal_year
	if cost_center:
		filters['cost_center'] = cost_center
	name = frappe.db.get_value('Pesatech Budget', filters, 'name')
	return frappe.get_doc('Pesatech Budget', name) if name else None


def check_budget_available(account, cost_center, amount, fiscal_year=None):
	"""Return {'available': x, 'ok': bool} for a prospective spend."""
	budget = get_active_budget(fiscal_year, cost_center)
	if not budget:
		return {'available': None, 'ok': True, 'reason': 'No active budget; control skipped.'}
	for line in budget.lines:
		if line.account == account and (not cost_center or line.cost_center == cost_center):
			avail = (line.budget_amount or 0) - (line.committed_amount or 0) - (line.actual_amount or 0)
			return {'available': avail, 'ok': amount <= avail, 'budget': budget.name}
	return {'available': 0, 'ok': False, 'reason': 'No matching budget line.'}


def create_commitment(account, cost_center, amount, reference_doctype=None,
		reference_name=None, budget=None, submit=True):
	"""Create (and optionally submit) a Budget Commitment that reserves budget."""
	doc = frappe.get_doc({
		'doctype': 'Budget Commitment', 'budget': budget, 'account': account,
		'cost_center': cost_center, 'amount': amount, 'status': 'Reserved',
		'reference_doctype': reference_doctype, 'reference_name': reference_name,
	})
	doc.insert(ignore_permissions=True)
	if submit:
		doc.submit()
	return doc.name
