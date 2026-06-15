#!/usr/bin/env python3
"""
PPRA Procurement flow - standalone simulation (no Frappe required).

This mirrors the business logic of the pesatech_erp Frappe app so the
PPRA evaluation and award chain can be demonstrated and verified without a full
ERPNext stack. Run:  python3 ppra_simulation.py
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# ----------------------------------------------------------------------
# Procurement Settings (defaults; configurable in the Frappe Single doctype)
# ----------------------------------------------------------------------
SETTINGS = {
    "low_value_max": 50_000,
    "rfq_max": 1_000_000,
    "approval_threshold_officer": 20_000,
    "approval_threshold_manager": 100_000,
    "standstill_days": 14,
    "technical_pass_mark": 70.0,
}

def recommend_method(estimated_value):
    if estimated_value <= SETTINGS["low_value_max"]:
        return "Low Value Procurement"
    if estimated_value <= SETTINGS["rfq_max"]:
        return "Request for Quotation (RFQ)"
    return "Open Tender"

def approval_level(value):
    if value <= SETTINGS["approval_threshold_officer"]:
        return "Procurement Officer"
    if value <= SETTINGS["approval_threshold_manager"]:
        return "Managing Director"
    return "Director / Board"

# ----------------------------------------------------------------------
# Lightweight domain objects
# ----------------------------------------------------------------------
@dataclass
class Supplier:
    name: str
    prequalified: bool = False
    agpo: str = "None"

@dataclass
class Criterion:
    criterion: str
    stage: str          # Preliminary | Technical | Financial
    weight: float = 0.0  # % for Technical/Financial
    mandatory: bool = False

@dataclass
class Bid:
    supplier: str
    total_value: float
    submitted_on: datetime
    scores: dict = field(default_factory=dict)  # criterion -> raw score
    sealed: bool = True
    status: str = "Submitted"

@dataclass
class SourcingEvent:
    title: str
    estimated_value: float
    closing_date: datetime
    opening_date: datetime
    criteria: list = field(default_factory=list)
    suppliers: list = field(default_factory=list)
    bids: list = field(default_factory=list)
    status: str = "Draft"

    @property
    def recommended_method(self):
        return recommend_method(self.estimated_value)

# ----------------------------------------------------------------------
# Process steps
# ----------------------------------------------------------------------
def line(c="-"):
    print(c * 70)

def receive_bid(event, bid):
    if bid.submitted_on > event.closing_date:
        print(f"  REJECTED (late): {bid.supplier} submitted after closing")
        return
    if not any(s.name == bid.supplier and s.prequalified for s in event.suppliers):
        print(f"  REJECTED (not prequalified): {bid.supplier}")
        return
    bid.sealed = True
    event.bids.append(bid)
    print(f"  ACCEPTED (sealed): {bid.supplier}  [KES {bid.total_value:,.0f}]")

def open_bids(event):
    if datetime.now() < event.opening_date and False:
        raise RuntimeError("Cannot open before opening date")
    for b in event.bids:
        b.sealed = False
    event.status = "Under Evaluation"
    print(f"  Bid opening register created. {len(event.bids)} bids unsealed.")
    for b in event.bids:
        print(f"    read out: {b.supplier:<22} KES {b.total_value:>12,.0f}")

def evaluate(event, committee_coi_ok=True):
    if not committee_coi_ok:
        raise RuntimeError("Committee COI declarations incomplete")
    results = []
    for b in event.bids:
        prelim = [c for c in event.criteria if c.stage == "Preliminary"]
        prelim_ok = all(b.scores.get(c.criterion, 0) >= 1 for c in prelim)
        tech = sum(b.scores.get(c.criterion, 0) * c.weight / 100.0
                   for c in event.criteria if c.stage == "Technical")
        fin = sum(b.scores.get(c.criterion, 0) * c.weight / 100.0
                  for c in event.criteria if c.stage == "Financial")
        tech_ok = tech >= SETTINGS["technical_pass_mark"]
        responsive = prelim_ok and tech_ok
        b.status = "Responsive" if responsive else "Non-Responsive"
        results.append({"supplier": b.supplier, "bid": b, "tech": tech,
                        "fin": fin, "combined": tech + fin,
                        "prelim_ok": prelim_ok, "responsive": responsive})
    for r in results:
        flag = "RESPONSIVE" if r["responsive"] else "NON-RESPONSIVE"
        print(f"    {r['supplier']:<22} prelim={'PASS' if r['prelim_ok'] else 'FAIL'}"
              f"  tech={r['tech']:5.1f}  fin={r['fin']:5.1f}"
              f"  combined={r['combined']:5.1f}  -> {flag}")
    responsive = [r for r in results if r["responsive"]]
    ranked = sorted(responsive, key=lambda r: r["combined"], reverse=True)
    return ranked

def award(event, ranked):
    if not ranked:
        print("  NO RESPONSIVE BIDS -> re-advertise procurement")
        return None
    winner = ranked[0]
    bid = winner["bid"]
    bid.status = "Awarded"
    lvl = approval_level(bid.total_value)
    standstill = datetime.now() + timedelta(days=SETTINGS["standstill_days"])
    print(f"  Recommended award: {winner['supplier']} "
          f"(combined score {winner['combined']:.1f}, KES {bid.total_value:,.0f})")
    print(f"  Approval required at: {lvl}")
    print(f"  Standstill period until: {standstill:%d %b %Y}")
    print(f"  Notifications -> successful: {winner['supplier']}; "
          f"unsuccessful: {', '.join(b.supplier for b in event.bids if b.supplier != winner['supplier'])}")
    event.status = "Awarded"
    return winner

# ----------------------------------------------------------------------
# DEMO RUN
# ----------------------------------------------------------------------
def main():
    print("=" * 70)
    print("PESATECH PPRA PROCUREMENT - SIMULATED END-TO-END RUN")
    print("=" * 70)

    now = datetime.now()
    event = SourcingEvent(
        title="Supply of 50 Laptops for Field Teams",
        estimated_value=4_200_000,
        closing_date=now + timedelta(days=14),
        opening_date=now + timedelta(days=14, hours=1),
        criteria=[
            Criterion("Mandatory documents complete", "Preliminary", mandatory=True),
            Criterion("Tax compliance valid", "Preliminary", mandatory=True),
            Criterion("Technical specification compliance", "Technical", weight=50),
            Criterion("Delivery & support capacity", "Technical", weight=30),
            Criterion("Price competitiveness", "Financial", weight=20),
        ],
        suppliers=[
            Supplier("Alpha Tech Ltd", prequalified=True, agpo="Youth"),
            Supplier("Beta Systems Ltd", prequalified=True),
            Supplier("Gamma Computers", prequalified=True),
            Supplier("Delta Traders", prequalified=False),  # not prequalified
        ],
    )

    print(f"\nEvent: {event.title}")
    print(f"Estimated value: KES {event.estimated_value:,.0f}")
    print(f"System-recommended method: {event.recommended_method}")
    line()

    print("STEP 1 - Receive sealed bids (deadline + prequalification enforced)")
    receive_bid(event, Bid("Alpha Tech Ltd", 4_050_000, now + timedelta(days=10),
        {"Mandatory documents complete": 1, "Tax compliance valid": 1,
         "Technical specification compliance": 92, "Delivery & support capacity": 85,
         "Price competitiveness": 88}))
    receive_bid(event, Bid("Beta Systems Ltd", 3_780_000, now + timedelta(days=12),
        {"Mandatory documents complete": 1, "Tax compliance valid": 1,
         "Technical specification compliance": 78, "Delivery & support capacity": 70,
         "Price competitiveness": 95}))
    receive_bid(event, Bid("Gamma Computers", 5_010_000, now + timedelta(days=13),
        {"Mandatory documents complete": 1, "Tax compliance valid": 0,  # fails preliminary
         "Technical specification compliance": 80, "Delivery & support capacity": 75,
         "Price competitiveness": 60}))
    receive_bid(event, Bid("Delta Traders", 3_500_000, now + timedelta(days=9), {}))  # not prequalified
    receive_bid(event, Bid("Alpha Tech Ltd", 3_900_000, now + timedelta(days=20), {}))  # late
    line()

    print("STEP 2 - Public bid opening")
    open_bids(event)
    line()

    print("STEP 3 - Committee evaluation (preliminary -> technical -> financial)")
    print(f"  Technical pass mark: {SETTINGS['technical_pass_mark']:.0f}")
    ranked = evaluate(event, committee_coi_ok=True)
    line()

    print("STEP 4 - Award recommendation, approval routing & notification")
    award(event, ranked)
    line("=")
    print("Simulation complete. This mirrors the controller logic in the Frappe app:")
    print("  Sourcing Event.set_recommended_method / validate_prequalification")
    print("  Bid.enforce_deadline   BidOpeningRegister.on_submit")
    print("  BidEvaluation.compute  ProcurementAward.set_approval_level/notify")


if __name__ == "__main__":
    main()
