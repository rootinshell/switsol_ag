// Copyright (c) 2016, Switsol AG and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Unapproved Timesheet Summary"] = {
	"filters": [
	],
	onload: function(report) {
		//Create a button for setting the default supplier
		var me = this;
		var reporter = frappe.query_reports["Daily Unapproved Timesheet Summary"];
		report.page.add_inner_button(__("Bewilligen"), function() { // Make Approved Button				
			reporter.make_signature_dialog(report);
		});
	},
	make_signature_dialog: function(report) {
		var me = this;
		var dialog = new frappe.ui.Dialog({
			title: __("Signature"),
			fields: [
				{
					"fieldtype": "Signature" ,
					"fieldname": "signature",
					"label": "Signature"
				}
			]
		});
		dialog.$wrapper.find(".modal-dialog").css("width", "600px");
		dialog.$wrapper.find(".modal-dialog").css("height", "450px");
		var list_of_timesheet = [];
		$.each($(".dt-cell"), function(i, d) {
			if($(d).find("._select").is(":checked")) {
				list_of_timesheet.push($(d).find("._select").attr("value"))
			}
		});
		dialog.set_primary_action(__("Relink"), function () {
			var values = dialog.get_values();
			me.update_timesheet(list_of_timesheet, values.signature);
			dialog.hide();
		})
		dialog.show();
	},
	update_timesheet: function(list_of_timesheet, signature) {
		var me  = this;
		frappe.call({
			method: "switsol_ag.switsol_ag.report.daily_unapproved_timesheet_summary.daily_unapproved_timesheet_summary.update_timesheet",
			args: {
				"list_of_timesheet": list_of_timesheet,
				"signature_svg": signature
			},
			callback: function(r) {
				if(r.message) {
					frappe.query_report.refresh()
				}
			}
		});
	},
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if(column.id == "empty") {
			if(data['Zeiterfassung']) {
				value = "<input type='checkbox' class='_select' value=" + data['Zeiterfassung'] + " >" + value + "</input>";
			}
			if(data['Timesheet']) {
				value = "<input type='checkbox' class='_select' value=" + data['Timesheet'] + " >" + value + "</input>";
			}
		}
		if(column.id == "test") {
			value = "<input type='checkbox' class='_select' value=" + data.timesheet + " ></input>";
		}
		return value;
	}
}
