#!/usr/bin/env python3
"""
Pesatech CRM - standalone simulation (no Frappe required).

Mirrors the module logic: onboarding/implementation, support SLA, NPS, renewals, exit.
Run:  python3 crm_simulation.py
"""
from datetime import date, datetime, timedelta

SLA = {"Urgent": 4, "High": 8, "Medium": 24, "Low": 48}
RENEWAL_WINDOW = 30


def line(c="-"):
    print(c * 74)


def onboarding_progress(done_phases):
    phases = ["Initiation", "Planning", "Build & Configure", "Train & Go-live", "Support & Optimise"]
    pct = round(100 * done_phases / len(phases))
    status = "Live" if done_phases == len(phases) else "In Progress"
    return phases, pct, status


def ticket_sla(priority, opened, resolved):
    sla = SLA[priority]
    hrs = (resolved - opened).total_seconds() / 3600.0
    return sla, round(hrs, 1), hrs > sla


def nps_category(score):
    return "Promoter" if score >= 9 else "Passive" if score >= 7 else "Detractor"


def main():
    print("=" * 74)
    print("PESATECH CRM - ONBOARDING, SUPPORT/SLA, NPS, RENEWALS, EXIT (SIMULATION)")
    print("=" * 74)

    # 1. Onboarding / implementation
    print("\nSTEP 1 - Customer onboarding (CSDP implementation phases)")
    phases, pct, status = onboarding_progress(3)
    print("  Customer: Imarisha SACCO | Suite: Financial Institutions Suite")
    for i, p in enumerate(phases):
        print(f"    [{'x' if i < 3 else ' '}] {p}")
    print(f"  Progress: {pct}%  ->  status {status}")
    line()

    # 2. Support tickets with SLA
    print("STEP 2 - Support tickets vs SLA")
    base = datetime(2026, 6, 15, 9, 0)
    tickets = [
        ("Login outage", "Urgent", base, base + timedelta(hours=3)),
        ("Report error", "High", base, base + timedelta(hours=14)),
        ("Config request", "Medium", base, base + timedelta(hours=20)),
    ]
    print(f"  {'Subject':<18}{'Priority':<10}{'SLA(h)':>7}{'Actual(h)':>11}{'Result':>12}")
    breaches = 0
    for subj, pri, o, r in tickets:
        sla, hrs, breached = ticket_sla(pri, o, r)
        breaches += breached
        print(f"  {subj:<18}{pri:<10}{sla:>7}{hrs:>11}{'BREACH' if breached else 'within SLA':>12}")
    print(f"  SLA breaches: {breaches}/{len(tickets)}")
    line()

    # 3. NPS feedback
    print("STEP 3 - NPS feedback")
    scores = [("Imarisha SACCO", 9), ("Wanake Dairy", 7), ("Faulu MFI", 5)]
    cats = {}
    for cust, s in scores:
        c = nps_category(s)
        cats[c] = cats.get(c, 0) + 1
        print(f"  {cust:<20} score {s:>2} -> {c}")
    promoters = cats.get("Promoter", 0); detractors = cats.get("Detractor", 0)
    nps = round(100 * (promoters - detractors) / len(scores))
    print(f"  NPS = %Promoters - %Detractors = {nps}")
    line()

    # 4. Renewals / retention
    print("STEP 4 - Subscription renewals (reminder window %d days)" % RENEWAL_WINDOW)
    today = date(2026, 6, 15)
    subs = [("Imarisha SACCO", date(2026, 7, 5)), ("Faulu MFI", date(2026, 9, 1)),
            ("Wanake Dairy", date(2026, 6, 20))]
    for cust, rd in subs:
        days = (rd - today).days
        due = "RENEWAL DUE" if 0 <= days <= RENEWAL_WINDOW else "scheduled"
        print(f"  {cust:<20} renews {rd:%d %b %Y}  ({days:>3} days)  -> {due}")
    line()

    # 5. Exit / churn
    print("STEP 5 - Customer exit / churn")
    print("  EXIT-2026-00001  Customer: Tujenge SHG  reason: Budget Cut  win-back: yes")
    print("  -> subscription marked Churned; data handover + access revocation tracked")
    line("=")
    print("Simulation complete. Mirrors the CRM module logic:")
    print("  OnboardingProject.before_insert/validate   SupportTicket.set_sla/check_breach")
    print("  CustomerFeedback.validate (NPS)   CustomerSubscription.validate (renewal_due)")
    print("  CustomerExit.on_submit (churn)")


if __name__ == "__main__":
    main()
