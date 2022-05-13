// Copyright (c) 2017, Switsol AG and contributors
// For license information, please see license.txt
// cur_frm.add_fetch("postal_code", "canton", "canton");
cur_frm.add_fetch("town", "canton", "canton")

frappe.ui.form.on("Address", {
	onload: function(frm) {
		frm.set_query("country", function() {
			return {
				filters: {
					"flag": 1
				}
			};
		});
		frm.set_query("postal_code", function(doc, cdt, cdn) {
			if(frm.doc.town) {
				return {
					query: "switsol_ag.address.postal_code_query",
					filters: {
						"town": frm.doc.town
					}
				}
			}
		});
		frm.set_query("town", function(doc, cdt, cdn) {
			if(frm.doc.postal_code) {
				return {
					query: "switsol_ag.address.city_query",
					filters: {
						"postal_code": frm.doc.postal_code
					}
				}
			}
		});
	},
	refresh: function(frm) {
		if(frappe.route_options) {
			cur_frm.set_value("address_title", frappe.route_options.address_title);
			cur_frm.set_value("address_type", "Billing");
			cur_frm.set_value("country", frappe.sys_defaults.country);
		}
	},
	town: function(frm) {
		frappe.call({
			method: "switsol_ag.address.get_list_switsol",
			args: {
				doctype: "City Postal Code",
				filters: [
					["parent", "=", frm.doc.town]
				],
				fields: ["postal_code"]
			},
			callback: function(r) {
				if(r.message) {
					let postal_codes = [];
					$.each(r.message, function(j, data) {
						postal_codes.push(data.postal_code);
					})
					if(postal_codes.length == 1) {
						frm.set_value("postal_code", postal_codes[0]);
					}
				}
			}
		})
	}
});
