frappe.provide('frappe.views');

frappe.views.CommunicationComposer = frappe.views.CommunicationComposer.extend({
	init: function(opts) {
		this._super(opts);
		this.set_default_value();
	},
	set_default_value: function() {
		if(this.doc.company=="Gilgen Storen AG") {
			var me = this
			var name = ""
			this.doc.doctype == 'Quotation' ? name = "Angebot" : ""
			this.doc.doctype == 'Sales Order' ? name = "Auftragsbestaetigung" : ""
			if(name) {
				me.dialog.set_value("email_template", name)
			}
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Email Template",
					fieldname: ["name", "response"],
					filters: {"name": name}
				},
				callback: function(r) {
					if(r.message) {
						me.dialog.set_value("email_template", r.message.name)
						me.dialog.set_value("content", r.message.response)
						me.dialog.fields_dict.email_template.$input.change(function() {
							me.dialog.set_value("content", "")
						})
					}
				}
			});
		}
	}
})
