# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from prasadam_flow.controllers.thresholds import is_transfer_allowed
from prasadam_flow.controllers.credits import get_custodian_coupon_credits


class PFCouponTransfer(Document):
    def before_cancel(self):
        ## There can be an issue only with the custodian who has received because he might have used them.
        avl_credits_to_custodian = get_custodian_coupon_credits(
            self.to_custodian, self.coupon_data, self.use_date
        )

        if avl_credits_to_custodian - self.number < 0:
            frappe.throw(
                "This can't be canceled as coupons have already been issued against this transfer."
            )
        return

    def before_submit(self):
        admin_role = frappe.db.get_single_value("PF Manage Settings", "admin_role")
        if (admin_role not in frappe.get_roles()) and (
            frappe.session.user != self.to_custodian
        ):
            frappe.throw("Only Admin or the receiver can approve this Transfer.")
        return

    def validate(self):
        self.validate_available_credits()
        self.validate_transfer_threshold()
        return

    def validate_transfer_threshold(self):
        if not is_transfer_allowed(self.coupon_data, self.use_date):
            frappe.throw("Transfer disallowed due to timing constraints.")
        return

    def validate_available_credits(self):
        avl_credits = get_custodian_coupon_credits(
            self.from_custodian, self.coupon_data, self.use_date
        )
        if avl_credits < self.number:
            frappe.throw(
                f"Transfer disallowed due to insufficient balance : {avl_credits}"
            )
        return
