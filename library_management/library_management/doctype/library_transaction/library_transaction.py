import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus

class LibraryTransaction(Document):
    def before_submit(self):
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()
            # Set the article status to 'Issued' when the article is being issued
            article = frappe.get_doc("Article", self.article)
            article.status = "Issued"
            article.save()
        
        elif self.type == "Return":
            self.validate_return()
            # Set the article status to 'Available' when the article is being returned
            article = frappe.get_doc("Article", self.article)
            article.status = "Available"
            article.save()

    def validate_issue(self):
        self.validate_membership()  # Check if the member has a valid membership
        article = frappe.get_doc("Article", self.article)
        
        # Article cannot be issued if it is already issued
        if article.status == "Issued":
            frappe.throw("Article is already issued by another member")

    def validate_return(self):
        article = frappe.get_doc("Article", self.article)
        
        # Article cannot be returned if it is not issued
        if article.status == "Available":
            frappe.throw("Article cannot be returned without being issued first")

    def validate_maximum_limit(self):
        # check for the max article issue to member
        max_articles = frappe.db.get_single_value("Library Settings", "maximum_number_of_issued_articles")
        count = frappe.db.count(
            "Library Transaction",
            {
                "library_member": self.library_member, 
                "type": "Issue", 
                "docstatus": 1
            },
        )
        if count >= max_articles:
            frappe.throw("Maximum limit reached for issuing articles")

    def validate_membership(self):
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": 1,
                "from_date": ("<", self.date),  # Membership start date before the transaction date
                "to_date": (">", self.date),    # Membership end date after the transaction date
            }
        )
        
        if not valid_membership:
            frappe.throw("The member does not have a valid membership")
            
	