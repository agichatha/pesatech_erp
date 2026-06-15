#!/usr/bin/env python3
"""
Pesatech HCM - standalone simulation (no Frappe required).

Mirrors the HCM module logic: E-Myth Position Contracts, performance review against
position standards, Kenyan statutory payroll, and payroll cost posting to Finance.
Run:  python3 hcm_simulation.py
"""
from dataclasses import dataclass, field

# ---- HCM Settings (defaults; configurable in the Single doctype) ----------
SETTINGS = dict(nssf_rate=6.0, nssf_cap=72000.0, shif_rate=2.75,
                housing_rate=1.5, personal_relief=2400.0)

# Indicative monthly Kenyan PAYE bands - CONFIRM against current KRA rates.
PAYE_BANDS = [(0, 24000, 0.10), (24000, 32333, 0.25), (32333, 500000, 0.30),
              (500000, 800000, 0.325), (800000, None, 0.35)]


def compute_paye_gross(taxable):
    tax = 0.0
    for lo, hi, rate in PAYE_BANDS:
        if taxable > lo:
            upper = taxable if hi is None else min(taxable, hi)
            tax += (upper - lo) * rate
    return tax


def compute_statutory(gross, nssf_rate, nssf_cap, shif_rate, housing_rate, personal_relief):
    nssf = min(gross, nssf_cap) * nssf_rate / 100.0
    shif = max(gross * shif_rate / 100.0, 300.0)
    housing = gross * housing_rate / 100.0
    taxable = max(0.0, gross - nssf)
    paye = max(0.0, compute_paye_gross(taxable) - personal_relief)
    total = paye + nssf + shif + housing
    return dict(paye=paye, nssf=nssf, shif=shif, housing=housing,
                total=total, net=gross - total)


def line(c="-"):
    print(c * 78)


# ----------------------------------------------------------------------
@dataclass
class PositionKPI:
    kpi: str
    target: str
    weight: float


@dataclass
class PositionContract:
    title: str
    holder: str
    standards: list = field(default_factory=list)
    status: str = "Draft"
    accepted_by: str = ""

    def sign(self, who):
        if not who:
            raise ValueError("A signed Position Contract must record who accepted accountability.")
        self.accepted_by = who
        self.status = "Signed"


def review(position, ratings):
    """Performance review against the position's own standards."""
    overall = 0.0
    rows = []
    for kpi in position.standards:
        rating = ratings.get(kpi.kpi, 0)
        weighted = rating * kpi.weight / 100.0
        overall += weighted
        rows.append((kpi.kpi, kpi.weight, rating, weighted))
    return overall, rows


def main():
    print("=" * 78)
    print("PESATECH HCM - POSITION CONTRACTS, PERFORMANCE & STATUTORY PAYROLL (SIMULATION)")
    print("=" * 78)

    # 1. Position Contract (E-Myth: positions before people)
    print("\nSTEP 1 - Position Contract (E-Myth franchise prototype)")
    sl = PositionContract("Sales Lead", "EMP-0007", standards=[
        PositionKPI("Qualified leads / quarter", ">=120", 30),
        PositionKPI("Demo-to-proposal conversion", ">=50%", 30),
        PositionKPI("New client contracts / quarter", "3-5", 40),
    ])
    print(f"  {sl.title} (held by {sl.holder}) - standards:")
    for k in sl.standards:
        print(f"    - {k.kpi:<32} target {k.target:<8} weight {k.weight:.0f}%")
    try:
        PositionContract("Vacant Role", "").sign("")    # demonstrate validation
    except ValueError as e:
        print(f"  validation works: {e}")
    sl.sign("J. Mwangi (MD)")
    print(f"  Position Contract status: {sl.status}, accepted by {sl.accepted_by}")
    line()

    # 2. Quarterly performance review against the position's standards
    print("STEP 2 - Performance Review vs Position Contract standards (Q2 2026)")
    overall, rows = review(sl, {
        "Qualified leads / quarter": 90,
        "Demo-to-proposal conversion": 80,
        "New client contracts / quarter": 75,
    })
    print(f"  {'KPI':<32}{'Weight':>8}{'Rating':>8}{'Weighted':>10}")
    for kpi, wt, rating, weighted in rows:
        print(f"  {kpi:<32}{wt:>7.0f}%{rating:>8.0f}{weighted:>10.1f}")
    print(f"  Overall rating: {overall:.1f} / 100")
    line()

    # 3. Statutory payroll run
    print("STEP 3 - Payroll Run (Kenyan statutory deductions) - June 2026")
    staff = [("EMP-0007 Sales Lead", 280_000), ("EMP-0011 Relationship Mgr", 120_000),
             ("EMP-0019 Support Officer", 65_000), ("EMP-0024 Intern", 30_000)]
    print(f"  {'Employee':<28}{'Gross':>10}{'PAYE':>10}{'NSSF':>8}{'SHIF':>8}{'AHL':>8}{'Net':>11}")
    tot_g = tot_d = tot_n = 0
    for name, gross in staff:
        r = compute_statutory(gross, **SETTINGS)
        tot_g += gross; tot_d += r['total']; tot_n += r['net']
        print(f"  {name:<28}{gross:>10,.0f}{r['paye']:>10,.0f}{r['nssf']:>8,.0f}"
              f"{r['shif']:>8,.0f}{r['housing']:>8,.0f}{r['net']:>11,.0f}")
    print(f"  {'TOTALS':<28}{tot_g:>10,.0f}{'':>26}{tot_n:>19,.0f}")
    print(f"  Total gross KES {tot_g:,.0f} | deductions KES {tot_d:,.0f} | net KES {tot_n:,.0f}")
    line()

    # 4. Payroll cost posts to Finance (cross-module)
    print("STEP 4 - Payroll cost posted to Finance (commitment against budget)")
    print(f"  PAY-2026-00006 -> Budget Commitment KES {tot_g:,.0f} "
          f"(account: 6100 - Salaries, ref: Payroll Run)")
    print("  (mirrors PayrollRun.post_to_finance -> budget_api.create_commitment)")
    line("=")
    print("Simulation complete. Mirrors the HCM module logic:")
    print("  PositionContract.validate (signature)   PerformanceReview.validate (weighted)")
    print("  payroll_api.compute_statutory           PayrollRun.validate / post_to_finance")
    print("  Onboarding.before_insert (Week-1 checklist) / validate (completion %)")


if __name__ == "__main__":
    main()
