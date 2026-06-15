# Pesatech ERP — ERPNext / Frappe App

`pesatech_erp` is the single custom Frappe app that holds **all of Pesatech's ERP
customisations**, one module per business area from the *Pesatech ERP System Specification*.
It is designed to be installed on top of ERPNext (v15).

## Modules (one app, many modules)

| Module (Frappe module) | Spec area | Status |
|---|---|---|
| **Pesatech Procurement** | Module 2 — Supply Chain / PPRA procurement | ✅ Built (prototype) |
| **Pesatech Finance** | Module 1 — Budgeting & Accounting (budget + commitment control, reminders) | ✅ Built (prototype) |
| **Pesatech HCM** | Module 3 — Human Capital Management (Position Contracts, performance, statutory payroll) | ✅ Built (prototype) |
| **Pesatech Sales & Marketing** | Module 4 — Sales & Marketing (pricing, agents, cooperatives, pipeline, scorecards) | ✅ Built (prototype) |
| **Pesatech CRM** | Module 5 — Customer Relationship Management (onboarding, support/SLA, NPS, renewals, exit) | ✅ Built (prototype) |
| **Pesatech Control Tower** | Strategy-execution layer — per-employee daily→quarterly activities tied to objectives, points/streak, manager sign-off, leadership BI | ✅ Built (prototype) |

Each new module is added as a sibling folder under `pesatech_erp/` (the Python package),
listed in `modules.txt`, and ships through the same Git → Frappe Cloud pipeline.

---

## Pesatech Procurement module (PPRA) — built

Implements the Module 2 chain: supplier prequalification → sourcing event (auto method
selection) → sealed bids → public opening → committee evaluation with conflict-of-interest
checks → award with threshold-based approval and standstill.

### DocTypes (17)
Procurement Settings (Single), Prequalification Category, Supplier Prequalification,
Evaluation Criteria Template (+ Item), Sourcing Event (+ Item, + Supplier), Bid (+ Item),
Bid Opening Register (+ Entry), Evaluation Committee (+ Member), Bid Evaluation (+ Score),
Procurement Award.

### Controllers (business logic)
- **Sourcing Event** — auto-selects procurement method by value vs thresholds; validates timeline; enforces prequalified suppliers.
- **Bid** — computes totals; rejects late bids; seals on submission.
- **Bid Opening Register** — unseals bids on submit; moves event to *Under Evaluation*.
- **Bid Evaluation** — blocks on incomplete/conflicted COI; weighted preliminary/technical/financial scoring; ranks responsive bids and records the recommendation.
- **Procurement Award** — sets approval level (Officer ≤ KES 20k, MD ≤ KES 100k, Director above); standstill date; bidder notifications.

### Workflows & roles (fixtures)
Workflows: Supplier Prequalification, Sourcing Event, and Procurement Award approvals.
Roles: Procurement Officer, Procurement Manager, Evaluation Committee Member, Accounting Officer.

---

## Pesatech Finance module — built

Implements the spec-specific parts of Module 1 that ERPNext does not do natively:
**budget + commitment (encumbrance) control** and the **finance activity reminder engine**.
Native ERPNext Accounts (GL, chart of accounts, journals, invoicing) handles the bookkeeping.

### DocTypes (5)
Finance Settings (Single), Budget (+ Budget Line child), Budget Commitment, Finance Activity.

### Logic
- **Budget** — computes committed/actual/available per line.
- **Budget Commitment** — on submit, reserves (encumbers) the amount on the matching budget line; on cancel, releases it.
- **budget_api** — `check_budget_available()` and `create_commitment()` callable from other modules.
- **integrations.commit_award** — a `doc_event` so that submitting a **Procurement Award** auto-reserves budget in Finance (cross-module wiring; configured via Finance Settings defaults).
- **tasks.send_finance_reminders** — daily scheduler that flags overdue finance activities and reminds owners.
- **FinanceActivity.mark_done / advance** — rolls a recurring activity to its next due date by frequency.

### Fixtures
Roles: Finance Officer, Finance Manager. Workflow: Budget Approval.

---

## Pesatech HCM module — built

Implements the Pesatech-specific HR layer (native ERPNext HR handles employee records,
leave, recruitment/ATS): **E-Myth Position Contracts**, **performance review against those
standards**, and **Kenyan statutory payroll**, with payroll cost posting to Finance.

### DocTypes (9)
HCM Settings (Single), Position Contract (+ Position KPI), Performance Review (+ Item),
Payroll Run (+ Payroll Entry Line), Onboarding (+ Onboarding Task).

### Logic
- **Position Contract** — results, accountabilities, KPI standards, and a required signature to accept accountability (positions before people).
- **Performance Review** — scores an employee against their position's own standards; computes a weighted overall rating.
- **payroll_api.compute_statutory** — PAYE (banded), NSSF, SHIF, and Housing Levy; rates configurable in HCM Settings. *PAYE bands are indicative — confirm against current KRA rules before production.*
- **Payroll Run** — computes per-employee deductions and run totals; on submit, posts the payroll cost to Finance via `budget_api.create_commitment` (cross-module).
- **Onboarding** — auto-populates the Operations Manual Week-1 checklist and tracks completion %.

### Fixtures
Roles: HR Officer, HR Manager. Workflows: Position Contract Approval, Payroll Run Approval.

---

## Pesatech Sales & Marketing module — built

Implements the Pesatech-specific commercial layer (native ERPNext Stock/Item handles
inventory received from production; native CRM/Selling handles quotations & sales orders).

### DocTypes (7)
Sales Marketing Settings (Single), Pricing Plan (commercial models), Sales Agent (agents
database), Cooperative Partner (cooperatives/partners), Pipeline Lead (MQL/SQL scoring +
funnel), Sales Deal (pricing + discount approval + agent commission), Weekly Marketing Scorecard.

### Logic
- **Pipeline Lead** — scores leads to MQL/SQL against configurable thresholds.
- **Sales Deal** — pulls list price from the Pricing Plan, computes discounted deal value and agent commission, and flags discounts above the approval threshold for MD sign-off.
- **Weekly Marketing Scorecard** — computes cost-per-lead and demo-to-proposal conversion and flags MQL/SQL target misses (the marketing operating rhythm).
- **Pricing Plan / Sales Agent / Cooperative Partner** — the commercial models, agents, and cooperative/union registries from the spec.

### Fixtures
Roles: Sales Lead, Marketing Lead, Relationship Manager. Workflow: Sales Deal Approval.

### Social media content engine (from the 12-Month Social Media Strategy)
- **Content Topic** — the 100-topic content library (5 categories), seeded on install.
- **Content Post** — the editorial calendar; enforces the strategy rule that every post maps to a value pillar and funnel stage. The Q1 (Jul–Sep 2026) post-by-post calendar (48 posts) is seeded.
- **Marketing Lead — Social Media Rhythm** Activity Template (Control Tower) is seeded with the strategy's cadence (daily LinkedIn action, 4 posts/week, monthly webinar, quarterly review), so the social plan drives the Marketing Lead's daily/weekly Control Tower tasks.

---

## Pesatech CRM module — built

Implements the full customer lifecycle from the spec (Module 5).

### DocTypes (7)
CRM Settings (Single), Onboarding Project (+ Onboarding Phase), Support Ticket, Customer
Feedback (NPS/CSAT), Customer Subscription, Customer Exit.

### Logic
- **Onboarding Project** — auto-loads the five CSDP implementation phases (Initiation → Support & Optimise), tracks progress %, and flips to Live on completion.
- **Support Ticket** — assigns an SLA from priority and flags breaches by computing resolution time.
- **Customer Feedback** — classifies an NPS score into Promoter / Passive / Detractor.
- **Customer Subscription** — computes days-to-renewal and raises a renewal-due flag inside the reminder window.
- **Customer Exit** — reason-coded churn that marks the linked subscription Churned and tracks offboarding (data handover, access revocation).

### Fixtures
Roles: Customer Success, Product Delivery Lead. Workflow: Onboarding Project Approval.

---

## Pesatech Control Tower module — built

The strategy-execution layer: cascades the Four-Year Strategic Plan down to each
employee's daily/weekly/monthly/quarterly activities, and rolls completion back up to a
leadership BI view. Generalises the personal "Digital Control Tower" to all staff.

### DocTypes (8)
Control Tower Settings (Single), Strategic Objective, Strategic Target, Activity Template
(+ Activity Template Item), Employee Activity, Tower Member, Weekly Review.

### Logic
- **Cascade** — Strategic Objective -> Strategic Target -> Activity Template (per Position Contract) -> `api.generate_for_employee` creates each person's Employee Activities. Objective progress and RAG roll up from its targets.
- **Personal motivator** — `Employee Activity.mark_done` awards points, advances the next due date by cadence, and updates the employee's streak (`api.award` / Tower Member). Each activity carries a **blockers** field.
- **Manager sign-off** — Weekly Review computes completion %, and submission is blocked until the manager signs off (configurable in Control Tower Settings).
- **Leadership roll-up** — `api.get_leadership_summary` powers completion-by-team, the individual leaderboard (by points/streak), and objective-by-objective drilldowns. RAG thresholds: green ≥80 / amber ≥70 / red <70.
- **Daily reminders** — `tasks.send_activity_reminders` flags overdue activities and nudges owners.

### Fixtures
Role: Line Manager. Workflow: Weekly Review Sign-off.

### Dashboards (both layers)
- **Native (zero-code):** a `Control Tower` Workspace with Number Cards (activities pending/overdue, objectives at risk, avg completion), a status chart, and shortcuts — shipped as fixtures, live on deploy.
- **Live HTML page:** `www/control-tower` renders the leadership roll-up (objective progress, leaderboard, status donut) server-side from `api.get_leadership_summary`, reachable at `/control-tower` after login.

> Workspace/Number Card/Dashboard Chart fixtures are starter definitions; if any field differs on your Frappe v15 build, open the item once in the UI and re-save.

---

## Run the logic demos (no install needed)

```bash
cd demo
python3 ppra_simulation.py       # procurement / PPRA flow
python3 finance_simulation.py   # budget, commitments, reminders
python3 hcm_simulation.py       # position contracts, payroll, performance
python3 sales_marketing_simulation.py  # pricing, leads, deals, scorecard
python3 crm_simulation.py       # onboarding, SLA, NPS, renewals, exit
python3 control_tower_simulation.py    # strategy cascade, points, leadership roll-up
```

Prints a full end-to-end run: method selection, prequalification & deadline rejection,
sealed opening, staged scoring, and threshold-based award routing.

---

## Install into an ERPNext site

Requires a Frappe/ERPNext **v15** bench (local WSL2 or Frappe Cloud).

```bash
# local bench
bench get-app pesatech_erp /path/to/pesatech_erp
bench --site yoursite.local install-app pesatech_erp
bench --site yoursite.local migrate
```

For managed hosting, see `Frappe_Cloud_Deployment_Guide.md` (push to GitHub → Private Bench →
add app → deploy → install on site).

---

## Adding the next module (pattern)

1. Create the module folder `pesatech_erp/pesatech_<area>/` with a `doctype/` directory.
2. Add the module name to `pesatech_erp/modules.txt`.
3. Build DocTypes/controllers; set each DocType's `module` to the new module name.
4. Commit and push; redeploy on Frappe Cloud.

Keep one shared data model (Customer, Supplier, Employee) across modules, per the spec.

---

## Prototype limitations / next steps
- Thresholds use sensible defaults (configurable in Procurement Settings).
- Notifications are logged stubs; wire to `frappe.sendmail` / SMS for production.
- Planned: budget commitment check vs Finance, 3-way match, supplier scorecards, procurement dashboard, RFQ/award print formats, supplier self-service portal.
