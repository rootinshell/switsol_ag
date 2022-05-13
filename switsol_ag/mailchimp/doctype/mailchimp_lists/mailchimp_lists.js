// Copyright (c) 2018, Switsol AG and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mailchimp Lists', {
	refresh: function(frm) {
		frm.add_custom_button(__("Synchronize with Mailchimp"), cur_frm.synchronize_mailchimp);
	}
});

cur_frm.synchronize_mailchimp = function(frm) {
	frappe.call({
		method: "switsol_ag.mailchimp.doctype.mailchimp_lists.mailchimp_lists.update_data",
		args: {
			mailchimp: cur_frm.doc.name
		},
		callback: function(r) {
			if(!r.exception) {
				console.log(r)
			}
		}
	})
}

frappe.ui.form.on("Mailchimp List Member", "members_add", function(frm) {
	$.each(frm.doc.members, function(i, member) {
		member.list_id = cur_frm.doc.list_id;
	})
})
