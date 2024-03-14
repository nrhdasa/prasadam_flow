import frappe


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


## This will give coupon
