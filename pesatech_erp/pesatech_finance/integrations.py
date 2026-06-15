# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from pesatech_erp.pesatech_finance.budget_api import create_commitment


def commit_award(doc, method=None):
	"""doc_event: when a Procurement Award is submitted, reserve budget in Finance.
	Uses Finance Settings defaults for the budget/account/cost center when available.
	Best-effort: never blocks the award if Finance is not yet configured."""
	try:
		s = frappe.get_single('Finance Settings')
		if not s.enable_commitment_control:
			return
		create_commitment(
			account=s.default_account, cost_center=s.default_cost_center,
			amount=doc.award_value, reference_doctype='Procurement Award',
			reference_name=doc.name, budget=s.default_budget, submit=True)
		frappe.msgprint('Budget commitment reserved for award %s.' % doc.name, alert=True)
	except Exception:
		frappe.log_error(title='Finance commit_award failed')
