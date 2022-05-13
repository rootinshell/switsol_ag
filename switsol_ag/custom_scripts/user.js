// Copyright (c) 2017, Switsol AG and contributors
// For license information, please see license.txt


frappe.ui.form.on("User", "refresh", function(frm) {
	if(!cur_frm.doc.background_image) {
		cur_frm.set_value("background_image", "/files/erp-desktop-background.jpg");
	}
	if(!cur_frm.doc.__islocal && cur_frm.doc.email && user == cur_frm.doc.email) {
		cur_frm.add_custom_button(__("SaltKey generieren"),
		function() {
			frappe.call({
				method: "switsol_ag.switsol_ag.make_user.get_salt_key",
				args: {
					"user": cur_frm.doc.email
				},
				callback: function(r) {
					if(r.message) {
						frappe.msgprint({title: __("Salt Key"), indicator: 'red',
							message: __("<b>" + r.message[0]["password"] + "</b>")
						})
					}
				}
			})
		})
	}
})
