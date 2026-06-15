#!/usr/bin/env python3
"""
Pesatech Sales & Marketing - standalone simulation (no Frappe required).

Mirrors the module logic: commercial pricing models, MQL/SQL lead scoring,
deals with discount approval and agent commission, and the weekly scorecard.
Run:  python3 sales_marketing_simulation.py
"""
from dataclasses import dataclass, field

SETTINGS = dict(discount_threshold=10.0, mql_threshold=50, sql_threshold=75)


def line(c="-"):
    print(c * 76)


# ----------------------------------------------------------------------
@dataclass
class PricingPlan:
    name: str
    model: str
    base_price: float


@dataclass
class SalesAgent:
    name: str
    commission_rate: float


def qualify(score):
    if score >= SETTINGS["sql_threshold"]:
        return "SQL"
    if score >= SETTINGS["mql_threshold"]:
        return "MQL"
    return "Unqualified"


@dataclass
class Deal:
    title: str
    plan: PricingPlan
    discount_pct: float = 0.0
    agent: SalesAgent = None
    approved_by: str = ""

    def evaluate(self):
        list_price = self.plan.base_price
        value = list_price * (1 - self.discount_pct / 100.0)
        commission = value * self.agent.commission_rate / 100.0 if self.agent else 0.0
        needs_approval = self.discount_pct > SETTINGS["discount_threshold"] and not self.approved_by
        return list_price, value, commission, needs_approval


def main():
    print("=" * 76)
    print("PESATECH SALES & MARKETING - PRICING, PIPELINE, DEALS, SCORECARD (SIMULATION)")
    print("=" * 76)

    # 1. Commercial pricing models
    print("\nSTEP 1 - Commercial pricing models (Pricing Plans)")
    plans = [
        PricingPlan("SACCO Core Banking - SaaS", "Subscription (SaaS)", 180_000),
        PricingPlan("Dairy Automation - Revenue Share", "Revenue Share", 0),
        PricingPlan("MFI Platform - One-off Licence", "One-off Licensing", 2_500_000),
    ]
    for p in plans:
        print(f"  {p.name:<34} {p.model:<22} base KES {p.base_price:,.0f}")
    line()

    # 2. Lead pipeline with MQL/SQL scoring
    print("STEP 2 - Pipeline leads scored to MQL/SQL")
    leads = [("Imarisha SACCO", "SACCO", 82), ("Wanake Dairy", "Dairy Cooperative", 64),
             ("Tujenge SHG", "Self-Help Group", 38), ("Faulu MFI", "MFI", 76)]
    print(f"  (MQL >= {SETTINGS['mql_threshold']}, SQL >= {SETTINGS['sql_threshold']})")
    for org, seg, score in leads:
        print(f"  {org:<20} {seg:<20} score {score:>3} -> {qualify(score)}")
    line()

    # 3. Deals: discount approval + agent commission
    print("STEP 3 - Deals: discount approval gate + agent commission")
    agent = SalesAgent("Rift Valley Reseller", 5.0)
    deals = [
        Deal("Imarisha SACCO - Core Banking", plans[0], discount_pct=8, agent=agent),
        Deal("Faulu MFI - Platform Licence", plans[2], discount_pct=18, agent=agent),  # over threshold
        Deal("Faulu MFI - Platform Licence (approved)", plans[2], discount_pct=18, agent=agent,
             approved_by="MD"),
    ]
    for d in deals:
        lp, val, comm, needs = d.evaluate()
        flag = "  >> NEEDS MD APPROVAL" if needs else ""
        print(f"  {d.title:<42}")
        print(f"     list KES {lp:,.0f}  disc {d.discount_pct:.0f}%  ->  value KES {val:,.0f}"
              f"  commission KES {comm:,.0f}{flag}")
    line()

    # 4. Weekly marketing scorecard
    print("STEP 4 - Weekly marketing scorecard vs targets")
    mql, mql_t, sql, sql_t = 8, 10, 4, 3
    demos, proposals, spend = 6, 3, 240_000
    cpl = spend / mql if mql else 0
    d2p = 100 * proposals / demos if demos else 0
    misses = [m for m, ok in [("MQL", mql >= mql_t), ("SQL", sql >= sql_t)] if not ok]
    print(f"  MQL {mql}/{mql_t}   SQL {sql}/{sql_t}   demos {demos}   proposals {proposals}")
    print(f"  CPL KES {cpl:,.0f}   demo-to-proposal {d2p:.0f}%   "
          f"status: {'Missed: ' + ', '.join(misses) if misses else 'On target'}")
    line("=")
    print("Simulation complete. Mirrors the Sales & Marketing module logic:")
    print("  PipelineLead.validate (MQL/SQL)   SalesDeal.validate (pricing/commission/discount)")
    print("  WeeklyMarketingScorecard.validate (CPL, conversion, target status)")


if __name__ == "__main__":
    main()
