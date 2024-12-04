// Copyright (c) 2024, VUT and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["File No Custom Report Without LCV"] = {
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
