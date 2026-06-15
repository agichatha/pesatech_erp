# Copyright (c) 2026, Pesatech Solutions Limited and contributors
# For license information, please see license.txt

import frappe  # noqa: F401

# NOTE: Indicative Kenyan PAYE bands (monthly). CONFIRM against current KRA rates
# before production use. Other statutory rates are configurable in HCM Settings.
PAYE_BANDS = [
	(0, 24000, 0.10),
	(24000, 32333, 0.25),
	(32333, 500000, 0.30),
	(500000, 800000, 0.325),
	(800000, None, 0.35),
]


def compute_paye_gross(taxable):
	tax = 0.0
	for lo, hi, rate in PAYE_BANDS:
		if taxable > lo:
			upper = taxable if hi is None else min(taxable, hi)
			tax += (upper - lo) * rate
	return tax


def compute_statutory(gross, nssf_rate=6.0, nssf_cap=72000.0, shif_rate=2.75,
		housing_rate=1.5, personal_relief=2400.0):
	"""Return statutory deductions and net pay for a monthly gross (KES).
	Rates are percentages. Tax treatment is simplified for the prototype."""
	gross = float(gross or 0)
	nssf = min(gross, nssf_cap) * (nssf_rate / 100.0)
	shif = max(gross * (shif_rate / 100.0), 300.0)
	housing = gross * (housing_rate / 100.0)
	taxable = max(0.0, gross - nssf)
	paye = max(0.0, compute_paye_gross(taxable) - personal_relief)
	total = paye + nssf + shif + housing
	return {
		'paye': round(paye, 2), 'nssf': round(nssf, 2), 'shif': round(shif, 2),
		'housing_levy': round(housing, 2), 'total_deductions': round(total, 2),
		'net_pay': round(gross - total, 2),
	}
