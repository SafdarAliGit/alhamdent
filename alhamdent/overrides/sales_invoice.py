import frappe


def before_submit(doc, method):
    for item in doc.items:
        # Check if batch_no is missing
        if not item.batch_no:
            frappe.throw(f"Batch ID is missing for item {item.item_code}.")

        # Check if batch_rate is missing
        if not item.batch_rate:
            frappe.throw(f"Batch Rate is missing for item {item.item_code}.")

        # Check if both batch_no and batch_rate exist, and rate should not be less than batch_rate
        if item.batch_no and item.batch_rate:
            if item.rate < item.batch_rate:
                frappe.throw(f"Rate for item {item.item_code} cannot be less than the Batch Rate.")