app_name = "pesatech_erp"
app_title = "Pesatech ERP"
app_publisher = "Pesatech Solutions Limited"
app_description = "Pesatech ERP - integrated modules (Procurement, Finance, HCM, Sales & Marketing, CRM, Control Tower)."
app_email = "info@pesatechsolutions.com"
app_license = "Proprietary"
required_apps = ["erpnext"]

fixtures = [
    {"dt": "Role", "filters": [["name", "in", [
        "Procurement Officer", "Procurement Manager",
        "Evaluation Committee Member", "Accounting Officer",
        "Finance Officer", "Finance Manager",
        "HR Officer", "HR Manager",
        "Sales Lead", "Marketing Lead", "Relationship Manager",
        "Customer Success", "Product Delivery Lead",
        "Line Manager",
    ]]]},
    {"dt": "Number Card", "filters": [["module", "=", "Pesatech Control Tower"]]},
    {"dt": "Dashboard Chart", "filters": [["module", "=", "Pesatech Control Tower"]]},
    {"dt": "Workspace", "filters": [["module", "in", [
        "Pesatech Control Tower", "Pesatech Procurement", "Pesatech Finance",
        "Pesatech HCM", "Pesatech Sales Marketing", "Pesatech CRM",
    ]]]},
    {"dt": "Workflow", "filters": [["name", "in", [
        "Supplier Prequalification Approval",
        "Sourcing Event Approval",
        "Procurement Award Approval",
        "Budget Approval",
        "Position Contract Approval",
        "Payroll Run Approval",
        "Sales Deal Approval",
        "Onboarding Project Approval",
        "Weekly Review Sign-off",
    ]]]},
]

doc_events = {
    "Procurement Award": {
        "on_submit": "pesatech_erp.pesatech_finance.integrations.commit_award",
    },
}

scheduler_events = {
    "daily": [
        "pesatech_erp.pesatech_finance.tasks.send_finance_reminders",
        "pesatech_erp.pesatech_control_tower.tasks.send_activity_reminders",
    ],
}

after_install = "pesatech_erp.install.after_install"
