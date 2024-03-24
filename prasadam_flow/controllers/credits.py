import frappe


### This will get coupon credits of a custodian on a given date.


def get_custodian_coupon_credits(custodian, coupon_data, use_date):
    booked = received = transferred = issued = 0

    ## Booked
    booked_query_result = frappe.db.sql(
        f""" 
                SELECT SUM(number)
                FROM `tabPF Coupon Book`
                WHERE docstatus = 1 and custodian = '{custodian}' and coupon_data = '{coupon_data}' and use_date = '{use_date}'"""
    )
    if booked_query_result[0][0]:
        booked = booked_query_result[0][0]
    ## Received
    received_query_result = frappe.db.sql(
        f""" 
                SELECT SUM(number)
                FROM `tabPF Coupon Transfer`
                WHERE docstatus = 1 and to_custodian = '{custodian}' and coupon_data = '{coupon_data}' and use_date = '{use_date}'"""
    )
    if received_query_result[0][0]:
        received = received_query_result[0][0]

    ## Transfered
    transfered_query_result = frappe.db.sql(
        f""" 
                SELECT SUM(number)
                FROM `tabPF Coupon Transfer`
                WHERE docstatus = 1 and from_custodian = '{custodian}' and coupon_data = '{coupon_data}' and use_date = '{use_date}'"""
    )
    if transfered_query_result[0][0]:
        transferred = transfered_query_result[0][0]

    ## Issued
    issued_query_result = frappe.db.sql(
        f""" 
                SELECT SUM(number)
                FROM `tabPF Coupon Issue`
                WHERE docstatus = 1 and custodian = '{custodian}' and coupon_data = '{coupon_data}' and use_date = '{use_date}'"""
    )
    if issued_query_result[0][0]:
        issued = issued_query_result[0][0]

    return booked + received - transferred - issued


##


def get_custodian_credits(custodian, use_date):
    coupons_map = {}
    blank_credits = frappe._dict(booked=0, received=0, transferred=0, issued=0, used=0)
    for c in frappe.get_all("PF Coupon Data", fields=["*"], filters={"active": 1}):
        coupons_map.setdefault(c["name"], {**c, **blank_credits})

    ## Booked
    for b in frappe.db.sql(
        f""" 
                SELECT coupon_data, SUM(number) as credits
                FROM `tabPF Coupon Book`
                WHERE docstatus = 1 and custodian = '{custodian}' and use_date = '{use_date}'
                GROUP BY coupon_data """,
        as_dict=1,
    ):
        coupons_map[b["coupon_data"]]["booked"] = b["credits"]

    ## Received
    for b in frappe.db.sql(
        f""" 
                SELECT coupon_data, SUM(number) as credits
                FROM `tabPF Coupon Transfer`
                WHERE docstatus = 1 and to_custodian = '{custodian}' and use_date = '{use_date}'
                GROUP BY coupon_data """,
        as_dict=1,
    ):
        coupons_map[b["coupon_data"]]["received"] = b["credits"]

    ## Transferred
    for b in frappe.db.sql(
        f""" 
                SELECT coupon_data, SUM(number) as credits
                FROM `tabPF Coupon Transfer`
                WHERE docstatus = 1 and from_custodian = '{custodian}' and use_date = '{use_date}'
                GROUP BY coupon_data """,
        as_dict=1,
    ):
        coupons_map[b["coupon_data"]]["transferred"] = b["credits"]

    ## Issued
    for b in frappe.db.sql(
        f""" 
                SELECT coupon_data, SUM(number) as credits, SUM(used) as used
                FROM `tabPF Coupon Issue`
                WHERE docstatus = 1 and custodian = '{custodian}' and use_date = '{use_date}'
                GROUP BY coupon_data """,
        as_dict=1,
    ):
        coupons_map[b["coupon_data"]]["issued"] = b["credits"]
        coupons_map[b["coupon_data"]]["used"] = b["used"]

    for key, value in coupons_map.items():
        value["balance"] = (
            value["booked"] + value["received"] - value["transferred"] - value["issued"]
        )
    return coupons_map


def get_credits_for_all_custodians(coupon_data, use_date):
    custodians_map = {}
    blank_credits = frappe._dict(booked=0, received=0, transferred=0, issued=0)
    for c in frappe.get_all("PF Custodian", fields=["name", "group", "full_name"]):
        custodians_map.setdefault(c["name"], {**c, **blank_credits})

    ## Booked
    for b in frappe.db.sql(
        f""" 
                SELECT custodian, SUM(number) as credits
                FROM `tabPF Coupon Book`
                WHERE docstatus = 1 and coupon_data = '{coupon_data}' and use_date = '{use_date}'
                GROUP BY custodian """,
        as_dict=1,
    ):
        custodians_map[b["custodian"]]["booked"] = b["credits"]

    ## Received
    for b in frappe.db.sql(
        f""" 
                SELECT to_custodian, SUM(number) as credits
                FROM `tabPF Coupon Transfer`
                WHERE docstatus = 1 and coupon_data = '{coupon_data}' and use_date = '{use_date}'
                GROUP BY to_custodian """,
        as_dict=1,
    ):
        custodians_map[b["to_custodian"]]["received"] = b["credits"]

    ## Transferred
    for b in frappe.db.sql(
        f""" 
                SELECT from_custodian, SUM(number) as credits
                FROM `tabPF Coupon Transfer`
                WHERE docstatus = 1 and coupon_data = '{coupon_data}' and use_date = '{use_date}'
                GROUP BY from_custodian """,
        as_dict=1,
    ):
        custodians_map[b["from_custodian"]]["transferred"] = b["credits"]

    ## Issued
    for b in frappe.db.sql(
        f""" 
                SELECT custodian, SUM(number) as credits
                FROM `tabPF Coupon Issue`
                WHERE docstatus = 1 and coupon_data = '{coupon_data}' and use_date = '{use_date}'
                GROUP BY custodian """,
        as_dict=1,
    ):
        custodians_map[b["custodian"]]["issued"] = b["credits"]

    for key, value in custodians_map.items():
        value["balance"] = (
            value["booked"] + value["received"] - value["transferred"] - value["issued"]
        )
    return custodians_map
