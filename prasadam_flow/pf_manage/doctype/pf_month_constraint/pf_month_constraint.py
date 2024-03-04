# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hkm.utils import validate_child_single_field_duplicacy

class PFMonthConstraint(Document):
	def validate(self):
		validate_child_single_field_duplicacy(self, "constraints", "coupon_category")
		return
