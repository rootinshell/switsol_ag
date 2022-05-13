// Copyright (c) 2018, Switsol AG and contributors
// For license information, please see license.txt
frappe.ui.form.on("Contact", {
	onload: function(frm) {
		// cur_frm.add_custom_button(__("Check Mailchimp Activity"), cur_frm.check_mailchimp_activity)
		frm.set_query("group_name", "mailchimp_lists", function(frm, cdt, cdn) {
			var lists = locals[cdt][cdn];
			return {
				filters: {
					list_id: lists.mailchimp_list_id
				}
			}
		})
		frm.set_query("interest", "mailchimp_lists", function(frm, cdt, cdn) {
			var lists = locals[cdt][cdn];
			return {
				filters: {
					category_id: lists.group_id
				}
			}
		})
	},
	refresh: function(frm) {
		if(!cur_frm.doc.__islocal && frappe.route_options) {
			if(frappe.route_options["doctype"] && frappe.route_options["doc_name"] && frappe.route_options["new_contact"] == "Yes") {
				frappe.route_options["contact_person"] = cur_frm.doc.name
				//frappe.route_options["mobile_no"] = cur_frm.doc.mobile_no
				frappe.set_route("Form", frappe.route_options["doctype"], frappe.route_options["doc_name"])
				//frappe.route_options = null;
			}
			if(frappe.route_options["mobile_no"] && frappe.route_options["mobile_or_phone"] == "mobile") {
				cur_frm.set_value("mobile_no", frappe.route_options["mobile_no"]);
			} else if(frappe.route_options["mobile_no"] && frappe.route_options["mobile_or_phone"] == "phone") {
				cur_frm.set_value("phone", frappe.route_options["mobile_no"]);
			}
		}
		if(!cur_frm.doc.__islocal && !cur_frm.doc.__unsaved) {
			// show log button
			cur_frm.add_custom_button(__("Anrufe anzeigen"), function() {
				cur_frm.cscript.show_logs_contact()
			});
		}
	},
	validate: function(frm) {
		if(!cur_frm.doc.__islocal && frappe.route_options) {
			frappe.route_options["new_contact"] = "Yes";
		}
		if(cur_frm.doc.mobile_no2) {
			cur_frm.set_value("mobile_no", frm.doc.mobile_no2);
		}
	}
})


cur_frm.cscript.show_logs_contact = function() {
	if(frappe.route_options) {
		frappe.route_options["client_info"] = cur_frm.doc.doctype + "//" + cur_frm.doc.name + "//" + cur_frm.doc.mobile_no
	} else {
		frappe.route_options = {
			"client_info": cur_frm.doc.doctype + "//" + cur_frm.doc.name + "//" + cur_frm.doc.mobile_no
		}
	}
	frappe.set_route("query-report", "Call Logs Report");
}


cur_frm.check_mailchimp_activity = function() {
	frappe.route_options = {"contact": cur_frm.doc.name};
	frappe.set_route("List", "Mailchimp Member Activity");
}


frappe.ui.form.on("Contact Mailchimp", {
	mailchimp_list: function(frm, cdt, cdn) {
		var lists = locals[cdt][cdn];
		lists.subscribed = 1;
		refresh_field("subscribed", cdn, "mailchimp_lists")
	},
	subscribed: function(frm, cdt, cdn) {
		var lists = locals[cdt][cdn];
		$.each(cur_frm.doc["mailchimp_lists"] || [], function(i, list) {
			if(list.mailchimp_list_id == lists.mailchimp_list_id){
				list.subscribed = lists.subscribed;
			}
		})
		cur_frm.refresh_fields();
	}
})
