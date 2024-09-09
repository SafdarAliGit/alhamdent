frappe.ui.form.on('Sales Invoice', {
    refresh: function (frm) {
        frm.fields_dict['file_no'].get_query = function (doc) {
            return {
                filters: [["FILE NO", "status", "=", "Open"]]

            };
        };
    }
});
