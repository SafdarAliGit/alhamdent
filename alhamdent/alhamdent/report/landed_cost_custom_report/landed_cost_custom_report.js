

frappe.query_reports["Landed Cost Custom Report"] = {
	"filters": [
		  {
            "fieldname": "name",
            "label": __("Purchase Invoice"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
			"reqd": 1
        }
	]
};
