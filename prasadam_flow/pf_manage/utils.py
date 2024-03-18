import frappe


def execute():
    for f in frappe.get_all("PF Coupon Transfer", pluck="name"):
        doc = frappe.get_doc("PF Coupon Transfer", f)
        from_full_name = frappe.db.get_value("User", doc.from_custodian, "full_name")
        frappe.db.set_value(
            "PF Coupon Transfer", f, "from_custodian_name", from_full_name
        )
        to_full_name = frappe.db.get_value("User", doc.to_custodian, "full_name")
        frappe.db.set_value("PF Coupon Transfer", f, "to_custodian_name", to_full_name)
    frappe.db.commit()
