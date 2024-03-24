import frappe
from frappe.utils import getdate


@frappe.whitelist()
def custodian_available_coupons(custodian, use_date):
    from prasadam_flow.controllers.credits import get_custodian_credits

    coupons_map = get_custodian_credits(custodian, use_date)
    only_coupons_with_balance = {
        k: v for k, v in coupons_map.items() if v["balance"] > 0
    }
    return list(only_coupons_with_balance.values())


@frappe.whitelist()
def single_coupon_availibility(coupon_data, use_date):
    from prasadam_flow.controllers.credits import get_credits_for_all_custodians

    custodians_map = get_credits_for_all_custodians(coupon_data, use_date)

    only_custodians_with_balance = {
        k: v for k, v in custodians_map.items() if v["balance"] > 0
    }
    return list(only_custodians_with_balance.values())


@frappe.whitelist()
def get_custodian_stats_day(custodian, use_date):
    from prasadam_flow.controllers.constraints import get_custodian_group_constraints

    custodian_group = frappe.db.get_value("PF Custodian", custodian, "group")
    constraints_map = get_custodian_group_constraints(custodian_group)
    use_month = getdate(use_date).strftime("%B")
    allowed = constraints_map[use_month]

    from prasadam_flow.controllers.credits import get_custodian_credits

    coupons_map = get_custodian_credits(custodian, use_date)

    for value in coupons_map.values():
        value["allowed"] = allowed[value["category"]]

    only_coupons_map_with_data = {
        k: v
        for k, v in coupons_map.items()
        if (v["balance"] > 0 or v["booked"] > 0 or v["issued"] > 0 or v["received"] > 0)
    }

    coupons_data = list(only_coupons_map_with_data.values())
    return sorted(coupons_data, key=lambda x: x["balance"], reverse=True)
