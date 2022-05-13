// Copyright (c) 2017, Switsol AG and contributors
// For license information, please see license.txt


cur_frm.cscript.show_logs_customer = function() {
	if(frappe.route_options) {
		// console.log("in if cond")
		//frappe.route_options["client_info"] = cur_frm.doc.doctype+"//"+cur_frm.doc.name
	} else {
		frappe.route_options = {
			"client_info": cur_frm.doc.doctype + "//" + cur_frm.doc.name
		}
	}
	frappe.set_route("query-report", "Call Logs Report");
}


cur_frm.cscript.make_log_customer = function(flag) {
	if(frappe.route_options["contact_person"]) {
		var contact_person = frappe.route_options["contact_person"];
		var phone_number = frappe.route_options["mobile_no"];
		var call_receive_time = frappe.route_options["call_receive_time"];
		var contact_type = frappe.route_options["contact_type"];
		var call_type = frappe.route_options["call_type"];
		if(flag == "Yes") {
			frappe.route_options = null;
			tn = frappe.model.make_new_doc_and_get_name("Call Logs", false);
			locals["Call Logs"][tn].call_type = call_type;
			locals["Call Logs"][tn].contact_person = contact_person;
			locals["Call Logs"][tn].phone_number = phone_number;
			locals["Call Logs"][tn].client = cur_frm.doc.name;
			locals["Call Logs"][tn].start_time = call_receive_time.split(" ")[1];
			locals["Call Logs"][tn].call_attendant = frappe.session.user;
			locals["Call Logs"][tn].contact_type = contact_type;
			// frappe.set_route('Form', 'Call Logs', tn);
		}
		sessionStorage.setItem("call_type", call_type)
		sessionStorage.setItem("contact_person", contact_person)
		sessionStorage.setItem("phone_number", phone_number)
		sessionStorage.setItem("client", cur_frm.doc.name)
		sessionStorage.setItem("start_time", call_receive_time.split(" ")[1])
		sessionStorage.setItem("call_attendant", frappe.session.user)
		sessionStorage.setItem("contact_type", contact_type)
	} else {
		if(flag == "Yes") {
			let tn = frappe.model.make_new_doc_and_get_name("Call Logs", false);
			locals["Call Logs"][tn].call_type = "Incoming"
			if(cur_frm.doc.call_comming_from) {
				locals["Call Logs"][tn].contact_person = cur_frm.doc.call_comming_from.split("/")[1]
				locals["Call Logs"][tn].phone_number = cur_frm.doc.call_comming_from.split("/")[0]
			} else {
				locals["Call Logs"][tn].contact_person = cur_frm.doc.customer_primary_contact;
				locals["Call Logs"][tn].phone_number = cur_frm.doc.mobile_no;
			}
			locals["Call Logs"][tn].client = cur_frm.doc.name
			locals["Call Logs"][tn].start_time = frappe.datetime.now_time()
			locals["Call Logs"][tn].call_attendant = frappe.session.user
			locals["Call Logs"][tn].contact_type = cur_frm.doc.doctype
			frappe.set_route("Form", "Call Logs", tn);
		}
		sessionStorage.setItem("call_type", "Incoming")
		if(cur_frm.doc.call_comming_from) {
			sessionStorage.setItem("contact_person", cur_frm.doc.call_comming_from.split("/")[1])
			sessionStorage.setItem("phone_number", cur_frm.doc.call_comming_from.split("/")[0])
		} else {
			sessionStorage.setItem("contact_person", cur_frm.doc.customer_primary_contact)
			sessionStorage.setItem("phone_number", cur_frm.doc.mobile_no)
		}
		sessionStorage.setItem("client", cur_frm.doc.name)
		sessionStorage.setItem("start_time", frappe.datetime.now_time())
		sessionStorage.setItem("call_attendant", frappe.session.user)
		sessionStorage.setItem("contact_type", cur_frm.doc.doctype)
	}
}


cur_frm.cscript.custom_refresh = function() {
	cur_frm.toggle_display("naming_series", 0);
	if(!cur_frm.doc.__islocal && (cur_frm.doc.call_comming_from && cur_frm.doc.call_comming_from != "" || frappe.route_options)) {
		// Make Log button
		cur_frm.add_custom_button(__("Protokoll erstellen"), function() {
			cur_frm.cscript.make_log_customer("Yes");
		}, __('Make'));
	}

	// if(!cur_frm.doc.__islocal && (cur_frm.doc.call_comming_from && cur_frm.doc.call_comming_from != "" || frappe.route_options)) {
	// 	cur_frm.cscript.make_log_customer("No");
	// 	if(frappe.boot.user["language"] == "en") {
	// 		window.open(frappe.urllib.get_base_url() + "/desk#Form/Call%20Logs/New%20Call%20Logs");
	// 	}
	// 	if(frappe.boot.user["language"] == "de") {
	// 		window.open(frappe.urllib.get_base_url() + "/desk#Form/Call%20Logs/Neu%20Telefon%20Protokoll");
	// 	}
	// }

	if(!cur_frm.doc.__islocal && !frappe.route_options && cur_frm.doc.call_comming_from == "") {
		// Show Log Button
		cur_frm.add_custom_button(__("Show Log"), function() {
			cur_frm.cscript.show_logs_customer();
		});
	}
	if(cur_frm.doc.__islocal) {
		frappe.model.get_value("Account", {"account_number": "1100"}, "name", function(r) {
			cur_frm.add_child("accounts", {"company": frappe.boot.sysdefaults.company, "account": r.name});
			cur_frm.refresh_field("accounts")
		});
		cur_frm.set_value("language","de")
	}
	if(!cur_frm.doc.territory && frappe.defaults.get_default("company") == "Gilgen Storen AG") {
		cur_frm.set_value("territory", "Schweiz");
	}
	cur_frm.refresh_fields();
}


cur_frm.cscript.customer_primary_contact = function() {
	frappe.model.get_value("Contact", {"name": cur_frm.doc.customer_primary_contact}, "mobile_no2", function(r) {
		if(r && !r.exception) {
			cur_frm.set_value("mobile_no", r.mobile_no2);
		}
	});
}


frappe.ui.form.on("Customer", {
	onload: function(frm) {
		if(!cur_frm.doc.territory &&  frappe.boot.sysdefaults.company == "Gilgen Storen AG") {
			cur_frm.set_value("territory", "Schweiz");
		}
	},
})
