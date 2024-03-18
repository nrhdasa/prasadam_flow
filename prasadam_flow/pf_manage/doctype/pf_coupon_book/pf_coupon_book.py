# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from prasadam_flow.controllers.constraints import get_custodian_quota
from prasadam_flow.controllers.thresholds import is_booking_allowed, is_cancel_allowed
from prasadam_flow.controllers.credits import get_custodian_coupon_credits


class PFCouponBook(Document):
    def before_cancel(self):

        if not is_cancel_allowed(self.coupon_data, self.use_date):
            frappe.throw("Cancellation is not allowed due to date & time thresholds.")

        ## There can be an issue only with the custodian who has received because he might have used them.
        avl_credits = get_custodian_coupon_credits(
            self.custodian, self.coupon_data, self.use_date
        )

        if avl_credits - self.number < 0:
            frappe.throw(
                "This can't be canceled as coupons have already been issued against this booking."
            )

        ## Check if user is Custodian OR Admin
        settings_doc = frappe.get_cached_doc("PF Manage Settings")
        user_roles = frappe.get_roles(frappe.session.user)

        if (settings_doc.admin_role not in user_roles) and (
            self.custodian != frappe.session.user
        ):
            frappe.throw(
                "You are not allowed to cancel this as you are not Custodian of this booking."
            )

        return

    def validate(self):
        self.validate_coupon_quota()
        self.validate_booking_threshold()
        return

    def validate_booking_threshold(self):
        if not is_booking_allowed(self.coupon_data, self.use_date):
            frappe.throw("Booking is not allowed due to date & time thresholds.")
        return

    def validate_coupon_quota(self):
        quota = get_custodian_quota(self.custodian, self.use_date, self.coupon_data)
        if quota < self.number:
            frappe.throw(
                f"Booking is not allowed due to constraints for this month. (Available Quota : {quota})"
            )
        return
