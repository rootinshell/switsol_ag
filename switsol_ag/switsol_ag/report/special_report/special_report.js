// Copyright (c) 2016, Switsol AG and contributors
// For license information, please see license.txt

frappe.query_reports["Special Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
			"reqd": 1
		},
	],
	onload: function(report) {
		var me = this;
		var reporter = frappe.query_reports["Special Report"];
	},
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if(value == __("No")) {
			value = '<span class="red" style="background-color: #e4401d; display: block; height: 28px;">' + value + '</span>';
		} else if(value == __("Yes")) {
			value = '<span class="green" style="background-color: #37f112; display: block; height: 28px;">' + value + '</span>';
		} else if(value == "Repeat") {
			value = '<span class="violet" style="background-color: #f112c8; display: block; height: 28px;">' + __("No") + '</span>';
		}
		return value;
	},
}
