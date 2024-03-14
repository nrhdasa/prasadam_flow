# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

    custodians = frappe.get_all("PF Custodian", pluck="name")

    custodian_map = get_coupon_credits_map(
        custodians, filters.get("coupon_data"), filters.get("use_date")
    )

    for u in frappe.db.sql(
        """
				SELECT pc.name, u.full_name
				FROM `tabPF Custodian` pc
				JOIN `tabUser` u ON pc.name = u.name 
					""",
        as_dict=1,
    ):
        custodian_map[u["name"]]["custodian"] = u["full_name"]

    for c in custodian_map.values():
        c["unissued"] = c["booked"] + c["received"] - c["transfered"] - c["issued"]
        c["unused"] = c["issued"] - c["used"]

    # for k,v in custodian_map.items():
    # 	v['cooking'] = v['booked'] +

    columns = get_columns()

    data = list(custodian_map.values())

    return columns, data


def get_coupon_credits_map(custodians, coupon_data, use_date):
    custodian_map = {}
    blank_coupon_map = frappe._dict(
        booked=0, received=0, transfered=0, issued=0, used=0, unissued=0, unused=0
    )
    for custodian in custodians:
        custodian_map.setdefault(
            custodian,
            {**blank_coupon_map},
        )

    ## Booked
    for b in frappe.db.sql(
        f"""
		SELECT custodian, SUM(number) as credits
		FROM `tabPF Coupon Book`
		WHERE docstatus = 1
			AND use_date = '{use_date}'
			AND coupon_data = '{coupon_data}'
		GROUP BY custodian		
		""",
        as_dict=1,
    ):
        custodian_map[b["custodian"]]["booked"] = b["credits"]

    ## Transferred / Received
    for t in frappe.db.sql(
        f"""
		SELECT from_custodian, to_custodian, number
		FROM `tabPF Coupon Transfer`
		WHERE docstatus = 1
			AND use_date = '{use_date}'
			AND coupon_data = '{coupon_data}'	
		""",
        as_dict=1,
    ):

        custodian_map[t["from_custodian"]]["transfered"] += t["number"]
        custodian_map[t["to_custodian"]]["received"] += t["number"]

    ## Issued
    for i in frappe.db.sql(
        f"""
		SELECT custodian, used, SUM(number) as credits
		FROM `tabPF Coupon Issue`
		WHERE docstatus = 1
			AND use_date = '{use_date}'
			AND coupon_data = '{coupon_data}'
		GROUP BY custodian, used	
		""",
        as_dict=1,
    ):
        if i["used"]:
            custodian_map[i["custodian"]]["used"] = i["credits"]

        custodian_map[i["custodian"]]["issued"] += i["credits"]

    return custodian_map


def get_columns():
    columns = [
        {
            "label": "Custodian",
            "fieldname": "custodian",
            "fieldtype": "Data",
            "width": 200,
        },
    ]
    columns.extend(
        [
            {
                "label": v,
                "fieldname": v.lower(),
                "fieldtype": "Int",
                "width": 120,
            }
            for v in [
                "Booked",
                "Received",
                "Transfered",
                "Issued",
                "Unissued",
                "Used",
                "Unused",
            ]
        ]
    )

    return columns
