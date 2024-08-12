

frappe.query_reports["File No Custom Report"] = {
	"filters": [
		  {
            "fieldname": "file_no",
            "label": __("File No"),
            "fieldtype": "Link",
            "options": "FILE NO",
			"reqd": 1
        }
	]
};
