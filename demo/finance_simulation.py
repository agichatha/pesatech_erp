#!/usr/bin/env python3
"""
Pesatech Finance - standalone simulation (no Frappe required).

Mirrors the budget & commitment-control and activity-reminder logic of the
Pesatech Finance module so it can be demonstrated without a full ERPNext stack.
Run:  python3 finance_simulation.py
"""
from dataclasses import dataclass, field
from datetime import date, timedelta

# ---- Finance Settings (defaults; configurable in the Single doctype) ------
SETTINGS = {"block_over_budget": True, "reminder_lead_days": 3, "fiscal_year": "2026"}


# ----------------------------------------------------------------------
# Budget + commitment control
# ----------------------------------------------------------------------
@dataclass
class BudgetLine:
    account: str
    cost_center: str
    budget_amount: float
    committed_amount: float = 0.0
    actual_amount: float = 0.0

    @property
    def available(self):
        return self.budget_amount - self.committed_amount - self.actual_amount


@dataclass
class Budget:
    name: str
    fiscal_year: str
    lines: list = field(default_factory=list)

    def line_for(self, account, cost_center):
        for l in self.lines:
            if l.account == account and l.cost_center == cost_center:
                return l
        return None

    @property
    def total(self):
        return sum(l.budget_amount for l in self.lines)


def check_budget_available(budget, account, cost_center, amount):
    line = budget.line_for(account, cost_center)
    if not line:
        return {"available": 0, "ok": False, "reason": "no matching budget line"}
    return {"available": line.available, "ok": amount <= line.available}


def create_commitment(budget, account, cost_center, amount, ref, block_over_budget=True):
    """Reserve budget (encumbrance). Mirrors BudgetCommitment.on_submit + budget_api."""
    chk = check_budget_available(budget, account, cost_center, amount)
    if not chk["ok"] and block_over_budget:
        print(f"  BLOCKED: {ref} KES {amount:,.0f} on {account}/{cost_center} "
              f"exceeds available KES {chk['available']:,.0f}")
        return False
    line = budget.line_for(account, cost_center)
    line.committed_amount += amount
    flag = "" if chk["ok"] else "  (OVER BUDGET - allowed with warning)"
    print(f"  COMMITTED: {ref} KES {amount:,.0f} on {account}/{cost_center}"
          f"  -> available now KES {line.available:,.0f}{flag}")
    return True


def post_actual(budget, account, cost_center, amount, ref):
    """Convert a commitment to actual spend (e.g. supplier invoice paid)."""
    line = budget.line_for(account, cost_center)
    line.committed_amount = max(0.0, line.committed_amount - amount)
    line.actual_amount += amount
    print(f"  ACTUAL:    {ref} KES {amount:,.0f} on {account}/{cost_center}"
          f"  -> committed KES {line.committed_amount:,.0f}, actual KES {line.actual_amount:,.0f}")


# ----------------------------------------------------------------------
# Finance activity reminders
# ----------------------------------------------------------------------
FREQ = {"Daily": 1, "Weekly": 7, "Monthly": 30, "Quarterly": 91, "Annual": 365}


@dataclass
class FinanceActivity:
    activity: str
    frequency: str
    next_due_date: date
    reminder_lead_days: int = 3
    status: str = "Pending"

    def evaluate(self, today):
        if self.next_due_date < today:
            self.status = "Overdue"
        due_window = self.next_due_date - timedelta(days=self.reminder_lead_days)
        return today >= due_window

    def mark_done(self):
        self.next_due_date = self.next_due_date + timedelta(days=FREQ[self.frequency])
        self.status = "Pending"


def line(c="-"):
    print(c * 70)


# ----------------------------------------------------------------------
# DEMO
# ----------------------------------------------------------------------
def main():
    print("=" * 70)
    print("PESATECH FINANCE - BUDGET / COMMITMENT CONTROL + REMINDERS (SIMULATION)")
    print("=" * 70)

    budget = Budget("BUD-2026-00001", "2026", lines=[
        BudgetLine("5100 - IT Equipment", "Operations", 5_000_000),
        BudgetLine("5200 - Marketing", "Sales & Marketing", 2_000_000),
        BudgetLine("5300 - Travel", "Operations", 800_000),
    ])
    print(f"\nBudget {budget.name} (FY{budget.fiscal_year}) - total KES {budget.total:,.0f}")
    for l in budget.lines:
        print(f"  {l.account:<24} {l.cost_center:<18} budget KES {l.budget_amount:>11,.0f}")
    line()

    print("STEP 1 - Procurement awards reserve budget (commitment/encumbrance)")
    # This is what hooks.commit_award does when a Procurement Award is submitted
    create_commitment(budget, "5100 - IT Equipment", "Operations", 4_050_000, "AWD-2026-00001 (laptops)")
    create_commitment(budget, "5200 - Marketing", "Sales & Marketing", 1_200_000, "AWD-2026-00002 (event)")
    line()

    print("STEP 2 - Budget control blocks an over-budget commitment")
    create_commitment(budget, "5100 - IT Equipment", "Operations", 1_500_000, "AWD-2026-00003 (servers)")
    print(f"  (available on IT Equipment is only KES "
          f"{budget.line_for('5100 - IT Equipment','Operations').available:,.0f})")
    line()

    print("STEP 3 - Supplier invoice paid -> commitment becomes actual")
    post_actual(budget, "5100 - IT Equipment", "Operations", 4_050_000, "PINV-2026-00001")
    line()

    print("STEP 4 - Budget position")
    print(f"  {'Account':<24}{'Budget':>12}{'Committed':>12}{'Actual':>12}{'Available':>12}")
    for l in budget.lines:
        print(f"  {l.account:<24}{l.budget_amount:>12,.0f}{l.committed_amount:>12,.0f}"
              f"{l.actual_amount:>12,.0f}{l.available:>12,.0f}")
    line()

    print("STEP 5 - Finance activity reminders (operating rhythm)")
    today = date(2026, 6, 15)
    activities = [
        FinanceActivity("Monthly bank reconciliation", "Monthly", date(2026, 6, 16)),
        FinanceActivity("VAT return filing (KRA)", "Monthly", date(2026, 6, 20)),
        FinanceActivity("Management accounts", "Monthly", date(2026, 6, 10)),
        FinanceActivity("Quarterly budget review", "Quarterly", date(2026, 6, 30)),
    ]
    print(f"  Today: {today:%d %b %Y}")
    for a in activities:
        due_soon = a.evaluate(today)
        tag = "REMIND NOW" if due_soon else "scheduled"
        print(f"  [{a.status:<8}] {a.activity:<30} due {a.next_due_date:%d %b} -> {tag}")
    line("=")
    print("Simulation complete. Mirrors the Finance module logic:")
    print("  Budget.validate / Budget Commitment.apply_to_budget")
    print("  budget_api.check_budget_available / create_commitment")
    print("  integrations.commit_award (Procurement Award -> commitment)")
    print("  tasks.send_finance_reminders / FinanceActivity.advance")


if __name__ == "__main__":
    main()
