import frappe


def before_submit(doc, method):
    for item in doc.items:
        if item.batch_no:
            batch = frappe.get_doc("Batch", item.batch_no)
            batch.rate = item.base_rate
            batch.file_no = item.file_no
            try:
                batch.save()
                # frappe.db.commit()
            except Exception as e:
                frappe.throw(frappe._("Error saving BATCH NO: {0}".format(str(e))))