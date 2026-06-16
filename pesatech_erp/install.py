import frappe


def after_install():
    """Seed default settings on install."""
    if frappe.db.exists("DocType", "Procurement Settings"):
        ps = frappe.get_single("Procurement Settings")
        ps.low_value_max = ps.low_value_max or 50000
        ps.rfq_max = ps.rfq_max or 1000000
        ps.approval_threshold_officer = ps.approval_threshold_officer or 20000
        ps.approval_threshold_manager = ps.approval_threshold_manager or 100000
        ps.standstill_days = ps.standstill_days or 14
        ps.enforce_prequalification = 1
        ps.save(ignore_permissions=True)

    if frappe.db.exists("DocType", "Finance Settings"):
        fs = frappe.get_single("Finance Settings")
        fs.current_fiscal_year = fs.current_fiscal_year or "2026"
        fs.default_currency = fs.default_currency or "KES"
        fs.reminder_lead_days = fs.reminder_lead_days or 3
        fs.enable_commitment_control = 1
        fs.block_over_budget = 1
        fs.save(ignore_permissions=True)

    if frappe.db.exists("DocType", "HCM Settings"):
        hs = frappe.get_single("HCM Settings")
        hs.nssf_rate = hs.nssf_rate or 6
        hs.nssf_cap = hs.nssf_cap or 72000
        hs.shif_rate = hs.shif_rate or 2.75
        hs.housing_levy_rate = hs.housing_levy_rate or 1.5
        hs.personal_relief = hs.personal_relief or 2400
        hs.training_completion_target = hs.training_completion_target or 90
        hs.post_payroll_to_finance = 1
        hs.save(ignore_permissions=True)

    if frappe.db.exists("DocType", "Sales Marketing Settings"):
        sm = frappe.get_single("Sales Marketing Settings")
        sm.discount_approval_threshold = sm.discount_approval_threshold or 10
        sm.default_commission_rate = sm.default_commission_rate or 5
        sm.mql_score_threshold = sm.mql_score_threshold or 50
        sm.sql_score_threshold = sm.sql_score_threshold or 75
        sm.save(ignore_permissions=True)

    if frappe.db.exists("DocType", "Pesatech CRM Settings"):
        cs = frappe.get_single("Pesatech CRM Settings")
        cs.sla_urgent_hours = cs.sla_urgent_hours or 4
        cs.sla_high_hours = cs.sla_high_hours or 8
        cs.sla_medium_hours = cs.sla_medium_hours or 24
        cs.sla_low_hours = cs.sla_low_hours or 48
        cs.renewal_reminder_days = cs.renewal_reminder_days or 30
        cs.target_retention_rate = cs.target_retention_rate or 95
        cs.save(ignore_permissions=True)

    if frappe.db.exists("DocType", "Control Tower Settings"):
        ct = frappe.get_single("Control Tower Settings")
        ct.rag_green = ct.rag_green or 80
        ct.rag_amber = ct.rag_amber or 70
        ct.reminder_lead_days = ct.reminder_lead_days or 1
        ct.points_per_task = ct.points_per_task or 10
        ct.require_manager_signoff = 1
        ct.save(ignore_permissions=True)

    try:
        from pesatech_erp.pesatech_sales_marketing.social_seed import seed_all
        seed_all()
    except Exception:
        frappe.log_error(title="Social media seed failed")

    frappe.db.commit()
