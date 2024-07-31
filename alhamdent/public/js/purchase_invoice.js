frappe.ui.form.on("Purchase Invoice", {
    refresh: function (frm) {

    }

});

frappe.ui.form.on("Purchase Invoice Item", {
    item_code: function (frm,cdt,cdn) {
        var d = locals[cdt][cdn];
        var file_no = frm.doc.file_no;
        if (file_no) {
           frappe.model.set_value(d.doctype, d.name, "file_no", file_no);
        }else {
            frappe.throw(__('Please Enter File No'));
        }

    }

});
