# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from pesatech_erp.pesatech_hcm.payroll_api import compute_statutory


class PayrollRun(Document):
	def validate(self):
		s = frappe.get_single('HCM Settings')
		rates = dict(nssf_rate=s.nssf_rate or 6, nssf_cap=s.nssf_cap or 72000,
			shif_rate=s.shif_rate or 2.75, housing_rate=s.housing_levy_rate or 1.5,
			personal_relief=s.personal_relief or 2400)
		g = d = n = 0
		for row in (self.entries or []):
			res = compute_statutory(row.gross_pay, **rates)
			row.paye = res['paye']
			row.nssf = res['nssf']
			row.shif = res['shif']
			row.housing_levy = res['housing_levy']
			row.total_deductions = res['total_deductions']
			row.net_pay = res['net_pay']
			g += (row.gross_pay or 0)
			d += res['total_deductions']
			n += res['net_pay']
		self.total_gross = g
		self.total_deductions = d
		self.total_net = n

	def on_submit(self):
		self.post_to_finance()

	def post_to_finance(self):
		# Reserve/record the payroll cost against the Finance budget (cross-module)
		try:
			from pesatech_erp.pesatech_finance.budget_api import create_commitment
			s = frappe.get_single('HCM Settings')
			if not s.post_payroll_to_finance:
				return
			create_commitment(account=s.payroll_account, cost_center=s.payroll_cost_center,
				amount=self.total_gross, reference_doctype='Payroll Run',
				reference_name=self.name, budget=s.payroll_budget, submit=True)
			frappe.msgprint('Payroll cost posted to Finance for %s.' % self.name, alert=True)
		except Exception:
			frappe.log_error(title='HCM post_to_finance failed')
