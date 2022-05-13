// Copyright (c) 2018, Switsol AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mailchimp Settings', {
	refresh: function(frm) {
		frm.add_custom_button(__("Get Data from Mailchimp"), cur_frm.cscript.get_data_from_mailchimp);
		// frm.add_custom_button(__("Get Campains from Mailchimp"), cur_frm.get_campains_from_mailchimp);
	}
});


cur_frm.cscript.get_data_from_mailchimp = function(frm) {
	frappe.call({
		method: "switsol_ag.mailchimp.doctype.mailchimp_settings.mailchimp_settings.get_data",
		args: {
			api_key: cur_frm.doc.api_key
		},
		callback: function(r) {
			if(!r.exception) {
				console.log(r)
			}
		}
	})
}
