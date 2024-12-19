# Copyright (c) 2024, Sakthi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus

class LibraryMembership(Document):
	def before_submit(self):
		exists = frappe.db.exists(
			"Library Membership",
			{
				"library_member": self.library_member,
				"docstatus":DocStatus.submitted(),
				"to_date": (">", self.from_date),
			},
		)
		if exists:
			frappe.throw("there is active membership for this member")
		# get loan period and compute to_date by adding loan_period to from_date
		loan_period = frappe.db.get_single_value("Library Settings", "loan")  # library setting loan period and count
		self.to_date = frappe.utils.add_days(self.from_date, loan_period or 30)