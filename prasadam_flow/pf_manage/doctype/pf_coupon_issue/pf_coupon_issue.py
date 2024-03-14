# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from prasadam_flow.controllers.credits import get_custodian_coupon_credits


class PFCouponIssue(Document):
    def validate(self):
        self.validate_coupon_availability()
        return

    def validate_coupon_availability(self):
        avl_credits = get_custodian_coupon_credits(
            self.custodian, self.coupon_data, self.use_date
        )
        if avl_credits < self.number:
            frappe.throw(
                f"You don't have sufficent balance of coupons to Issue. Balance : {avl_credits}"
            )
        return
