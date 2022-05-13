// Copyright (c) 2017, Switsol AG and contributors
// For license information, please see license.txt


frappe.ui.form.on("Supplier", "refresh", function(frm) {
	if(cur_frm.doc.__islocal) {
		cur_frm.set_value("language", "de");
	}
	if(!cur_frm.doc.__islocal && (cur_frm.doc.call_comming_from && cur_frm.doc.call_comming_from != "" || frappe.route_options)) {
		// Make Log button 
		cur_frm.add_custom_button(__("Anrufe eintragen"), function() {
			cur_frm.cscript.make_log_supplier();
		});
	}
	if(!cur_frm.doc.__islocal && !frappe.route_options && cur_frm.doc.call_comming_from == "") {
		// show log
		cur_frm.add_custom_button(__("Anrufe anzeigen"), function() {
			cur_frm.cscript.show_logs_supplier();
		});
	}
})


cur_frm.cscript.show_logs_supplier = function() {
	if(frappe.route_options) {
		frappe.route_options["client_info"] = cur_frm.doc.doctype + "//" + cur_frm.doc.name
	} else {
		frappe.route_options = {
			"client_info": cur_frm.doc.doctype + "//" + cur_frm.doc.name
		}
	}
	frappe.set_route("query-report", "Call Logs Report");
}


cur_frm.cscript.make_log_supplier = function(name) {
	if(frappe.route_options) {
		var args_dict = {
			"phone_number": frappe.route_options["mobile_no"],
			"contact_person": frappe.route_options["contact_person"],
			"client": cur_frm.doc.name,
			"start_time": frappe.route_options["call_receive_time"].split(" ")[1],
			"call_attendant": frappe.session.user,
			"contact_type": frappe.route_options["contact_type"]
		}
		frappe.route_options = null;
		frappe.call({
			method: "switsol_ag.custom_scripts.supplier.make_log",
			args: {
				"args_dict": args_dict
			},
			async: false,
			callback: function(r) {
				if(r.message) {
					frappe.set_route("Form", "Call Logs", r.message);
				}
			}
		})
	} else {
		tn = frappe.model.make_new_doc_and_get_name("Call Logs");
		locals["Call Logs"][tn].phone_number = cur_frm.doc.call_comming_from.split("/")[0]
		locals["Call Logs"][tn].contact_person = cur_frm.doc.call_comming_from.split("/")[1]
		locals["Call Logs"][tn].client = cur_frm.doc.name 
		locals["Call Logs"][tn].start_time = frappe.datetime.now_datetime().split(" ")[1]
		locals["Call Logs"][tn].call_attendant = user
		locals["Call Logs"][tn].contact_type = cur_frm.doc.doctype
		frappe.set_route("Form", "Call Logs", tn);
	}
}
