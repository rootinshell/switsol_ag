// Copyright (c) 2017, Switsol AG and contributors
// For license information, please see license.txt

cur_frm.add_fetch("description_text_name", "description_text", "description_text");
cur_frm.add_fetch("predefined_text_container", "predefined_text_container", "items_description1");
cur_frm.add_fetch("payment_name", "payment_details", "payment_details");


frappe.ui.form.on("Quotation", {
	setup: function(frm) {
		if(frm.doc.company == "Gilgen Storen AG") {
			cur_frm.add_fetch("item_code", "width_asl_size", "width_asl_size");
			cur_frm.add_fetch("item_code", "width_hight_ht", "width_hight_ht");
			cur_frm.add_fetch("item_code", "width_hight_hl", "width_hight_hl");
			cur_frm.add_fetch("item_code", "location", "location");
			cur_frm.add_fetch("additional_item", "width_asl_size", "width_asl_size");
			cur_frm.add_fetch("additional_item", "width_hight_ht", "width_hight_ht");
			cur_frm.add_fetch("additional_item", "width_hight_hl", "width_hight_hl");
			cur_frm.add_fetch("additional_item", "location", "location")
			// cur_frm.add_fetch("customer", "pricing_rate", "pricing_rate");
			// cur_frm.add_fetch("customer", "hidden_discount_rate", "hidden_discount_rate");
			// cur_frm.add_fetch("customer", "discount", "discount");
			// cur_frm.add_fetch("customer", "skonto", "skonto");
		}
	},
	onload: function(frm) {
		cur_frm.set_query("predefined_text_container", function() {
			return {
				filters: {
					"using_doctype": cur_frm.doc.doctype,
					"is_default": 1
				}
			};
		});
		cur_frm.set_query("description_text_name", function() {
			return {
				filters: {
					"using_doctype": cur_frm.doc.doctype,
					"is_default": 1
				}
			};
		});
		if(frm.doc.company == "Gilgen Storen AG") {
			if(!cur_frm.doc.payment_name) {
				cur_frm.set_value("payment_name", "PostFinance");
			}
			frm.set_query("company_address_name", function() {
				return {
					filters: {
						"customer": cur_frm.doc.company_name
					}
				}
			});
			if(cur_frm.doc.docstatus == 0) {
				if(!cur_frm.doc.taxes_and_charges || cur_frm.doc.taxes_and_charges == "MWST (8%)") {
					cur_frm.set_value("taxes_and_charges", "MWST (7.7%)");
				}
				if(cur_frm.doc.company_name == cur_frm.doc.customer) {
					cur_frm.set_value("company_name", "");
				}
				if(cur_frm.doc.partial_payment_2_name != "bei Montagebeginn") {
					cur_frm.set_value("partial_payment_2_name", "bei Montagebeginn");
				}
				if(cur_frm.doc.partial_payment_3_name != "nach Montage 10 Tage netto") {
					cur_frm.set_value("partial_payment_3_name", "nach Montage 10 Tage netto");
				}
				if(!cur_frm.doc.discount_1_name) {
					cur_frm.set_value("discount_1_name", "Rabatt");
				}
				if(!cur_frm.doc.discount_2_name) {
					cur_frm.set_value("discount_2_name", "Skonto");
				}
			}
		}
	},
	refresh: function() {
		if(!cur_frm.doc.__islocal) {
			// cur_frm.add_custom_button(__("An Pingen übermitteln"), cur_frm.cscript.upload_to_pingen);
		}
	},
	company_address_name: function() {
		erpnext.utils.get_address_display(cur_frm, "company_address_name", "additional_company_address");
	},
	company_name: function() {
		cur_frm.set_value("company_address_name", "");
	},
})


cur_frm.cscript.custom_refresh = function() {
	cur_frm.toggle_display("naming_series", 0);
	if(cur_frm.doc.__islocal) {
		cur_frm.set_value("valid_till", frappe.datetime.add_months(cur_frm.doc.transaction_date, 12))
	}
	if(cur_frm.doc.__islocal && cur_frm.doc.company != "Gilgen Storen AG") {
		cur_frm.set_value("employee_signature", "");
	}
	if(!cur_frm.doc.description_text) {
		frappe.model.get_value("Description Text", {"using_doctype": cur_frm.doc.doctype, "is_default": true}, "*", function(r) {
			if(r && !r.exception) {
				cur_frm.set_value("description_text_name", r.title);
				cur_frm.set_value("description_text", r.description_text);
			}
		});
	}
	if(!cur_frm.doc.predefined_text_container) {
		frappe.model.get_value("Predefined Text Container", {"using_doctype": cur_frm.doc.doctype, "is_default": true}, "*", function(r) {
			if(r && !r.exception) {
				cur_frm.set_value("predefined_text_container", r.title);
				cur_frm.set_value("items_description1", r.predefined_text_container);
			}
		});
	}
	if(frappe.session.user != "Administrator" && !cur_frm.doc.clerk_name) {
		cur_frm.set_value("clerk_name", frappe.session.user);
		cur_frm.set_value("chief_signature", frappe.session.user);
		cur_frm.set_value("employee_signature", "");
	}
	if(cur_frm.doc.company == "Gilgen Storen AG") {
		if(!cur_frm.doc.payment_name) {
			cur_frm.set_value("payment_name", "PostFinance");
		}
		if(cur_frm.doc.pricing_rate) {
			$("div[data-fieldname=pricing_rate]").find('.like-disabled-input').css({'color': '#c0392b !important'});
		}
		if(cur_frm.doc.hidden_discount_rate) {
			$("div[data-fieldname=hidden_discount_rate]").find('.like-disabled-input').css({'color': '#c0392b !important'});
		}
		if(cur_frm.doc.discount) {
			$("div[data-fieldname=discount]").find('.like-disabled-input').css({'color': '#c0392b !important'});
		}
		if(cur_frm.doc.skonto) {
			$("div[data-fieldname=skonto]").find('.like-disabled-input').css({'color': '#c0392b !important'});
		}
		if(cur_frm.doc.docstatus == 0) {
			if(cur_frm.doc.company_name == cur_frm.doc.customer) {
				cur_frm.set_value("company_name", "");
			}
			if(!cur_frm.doc.taxes_and_charges || cur_frm.doc.taxes_and_charges == "MWST (8%)") {
				cur_frm.set_value("taxes_and_charges", "MWST (7.7%)");
			}

			if(!cur_frm.doc.quote_expiration_date) {
				cur_frm.set_value("quote_expiration_date", frappe.datetime.add_months(frappe.datetime.get_today(), 3));
			}
			if(cur_frm.doc.partial_payment_2_name != "bei Montagebeginn") {
				cur_frm.set_value("partial_payment_2_name", "bei Montagebeginn");
			}
			if(cur_frm.doc.partial_payment_3_name != "nach Montage 10 Tage netto") {
				cur_frm.set_value("partial_payment_3_name", "nach Montage 10 Tage netto");
			}
			if(!cur_frm.doc.discount_1_name) {
				cur_frm.set_value("discount_1_name", "Rabatt");
			}
			if(!cur_frm.doc.discount_2_name) {
				cur_frm.set_value("discount_2_name", "Skonto");
			}
		}
	}
}

cur_frm.cscript.employee_signature = function() {
	frappe.model.get_value("Employee", {"user_id": cur_frm.doc.employee_signature}, "signature", function(r) {
		if(r && !r.exception) {
			cur_frm.set_value("employee_signature_value", r.signature);
		} else {
			cur_frm.set_value("employee_signature_value", "");
		}
	});
}

cur_frm.cscript.chief_signature = function() {
	frappe.model.get_value("Employee", {"user_id": cur_frm.doc.chief_signature}, "signature", function(r) {
		if(r && !r.exception) {
			cur_frm.set_value("chief_signature_value", r.signature);
		} else {
			cur_frm.set_value("chief_signature_value", "");
		}
	});
}

cur_frm.cscript.clerk_name = function() {
	frappe.model.get_value("Employee", {"user_id": cur_frm.doc.clerk_name}, "signature", function(r) {
		if(r && !r.exception) {
			// if(cur_frm.doc.company == "Gilgen Storen AG") {
			cur_frm.set_value("chief_signature", cur_frm.doc.clerk_name);
			cur_frm.set_value("chief_signature_value", r.signature);
			// } else {
			// 	cur_frm.set_value("employee_signature", cur_frm.doc.clerk_name);
			// 	cur_frm.set_value("employee_signature_value", r.signature);
			// }
		} else {
			cur_frm.set_value("employee_signature", "");
			cur_frm.set_value("employee_signature_value", "");
			// if(cur_frm.doc.company == "Gilgen Storen AG") {
			// 	cur_frm.set_value("chief_signature", "");
			// 	cur_frm.set_value("chief_signature_value", "");
			// }
		}
	});
}

cur_frm.cscript.contact_person = function() {
	if(!cur_frm.doc.contact_person && cur_frm.doc.customer) {
		frappe.model.get_value("Customer", cur_frm.doc.customer, ["salutation", "customer_name"], function(r) {
			if(r) {
				cur_frm.set_value("customer_name", r.customer_name);
				var surname = cur_frm.doc.customer.split(" ").slice(-1);
				if(cur_frm.doc.customer_name) {
					var surname = cur_frm.doc.customer_name.split(" ").slice(-1);
				}
				var greeting = surname.join(" ")
				if(r.salutation) {
					greeting = r.salutation + " " + surname.join(" ");
				}
				cur_frm.set_value("contact_greeting", greeting);
			}
		});
		cur_frm.set_value("contact_display", "");
	}
	erpnext.TransactionController.prototype.contact_person.call(this);
}

cur_frm.cscript.customer = function() {
	erpnext.utils.get_party_details(cur_frm, null, null, function() {
		if(cur_frm.doc.contact_person) {
			frappe.model.get_value("Contact", cur_frm.doc.contact_person, ["salutation", "last_name"], function(r) {
				if(r && !r.exception) {
					var greeting = r.last_name
					if(r.salutation) {
						greeting = r.salutation + " " + r.last_name;
					}
					cur_frm.set_value("contact_greeting", greeting);
				}
			});
		}
	});
}


cur_frm.cscript.add_company_address = function() {
	var dialog = new frappe.ui.Dialog({
		title: __("Add Company Address"),
		fields: [
			{
				"label": __("Address"),
				"fieldname": "address",
				"fieldtype": "Link",
				"options": "Address",
				"only_select": true,
				"get_query": function() {
					if(cur_frm.doc.company_name) {
						return {
							query: "frappe.contacts.doctype.address.address.address_query",
							filters: {
								link_doctype: "Customer",
								link_name: cur_frm.doc.company_name
							}
						}
					}
				},
				"reqd": 1
			}
		],
		secondary_action_label: (__("Create"))
	});

	dialog.set_primary_action(__("Add"), function() {
		var args = dialog.get_values();
		if(!args) return;
		dialog.hide();
		cur_frm.set_value("company_address_name", args.address);
		cur_frm.refresh_field("company_address_name");
	});
	dialog.$wrapper.find(".btn-modal-close").click(function() {
		var new_address = frappe.model.make_new_doc_and_get_name("Address");
		frappe.dynamic_link = {doc: cur_frm.doc, fieldname: "company_name", doctype: "Customer"};
		frappe.route_options = {"address_title": cur_frm.doc.company_name};
		frappe.set_route("Form", "Address", new_address);
	});
	dialog.show();
}

cur_frm.cscript.discount_1_value = function() {
	var discount_amount = cur_frm.cscript.calculate_discount();
	cur_frm.set_value("grand_total", flt(cur_frm.doc.total) - flt(discount_amount));
	cur_frm.set_value("discount_amount", discount_amount)
	$.each(cur_frm.doc["items"] || [], function(i, item) {
		let distributed_amount = flt(item.rate*flt(cur_frm.doc.discount_1_value) / 100);
		item.net_amount = flt(item.net_amount - distributed_amount, precision("net_amount", item));
		item.net_rate = flt(item.net_rate / item.qty, precision("net_rate", item));
		item.amount = flt(item.amount - distributed_amount, precision("amount", item));
	});
	cur_frm.refresh_field("items");
}

cur_frm.cscript.discount_2_value = function() {
	var discount_amount = cur_frm.cscript.calculate_discount();
	cur_frm.set_value("grand_total", flt(cur_frm.doc.total) - flt(discount_amount));
	cur_frm.set_value("discount_amount", discount_amount)
	$.each(cur_frm.doc["items"] || [], function(i, item) {
		let discount = 0.0;
		if(cur_frm.doc.discount_1_value) {
			discount += cur_frm.doc.discount_1_value;
		}
		let distributed_amount = flt(item.rate*flt(discount + cur_frm.doc.discount_2_value) / 100);
		item.net_amount = flt(item.net_amount - distributed_amount, precision("net_amount", item));
		item.net_rate = flt(item.net_rate / item.qty, precision("net_rate", item));
		item.amount = flt(item.amount - distributed_amount, precision("amount", item));
	});
	cur_frm.refresh_field("items");
}

cur_frm.cscript.discount_3_value = function() {
	var discount_amount = cur_frm.cscript.calculate_discount();
	cur_frm.set_value("grand_total", flt(cur_frm.doc.total) - flt(discount_amount));
	cur_frm.set_value("discount_amount", discount_amount)
	$.each(cur_frm.doc["items"] || [], function(i, item) {
		let distributed_amount = flt(item.rate*flt(cur_frm.doc.discount_3_value) / 100);
		item.net_amount = flt(item.net_amount - distributed_amount, precision("net_amount", item));
		item.net_rate = flt(item.net_rate / item.qty, precision("net_rate", item));
		item.amount = flt(item.amount - distributed_amount, precision("amount", item));
	});
	cur_frm.refresh_field("items");
}


cur_frm.cscript.calculate_discount = function() {
	var total = flt(cur_frm.doc.total);
	var discount_amount = 0;
	if(cur_frm.doc.discount_1_value || cur_frm.doc.discount_2_value || cur_frm.doc.discount_3_value) {
		cur_frm.set_value("discount_1_rate", 0);
		cur_frm.set_value("discount_2_rate", 0);
		var current_total = total;
		if(cur_frm.doc.discount_1_value) {
			discount_amount = flt(total*flt(cur_frm.doc.discount_1_value) / 100,
				precision("discount_amount"));
			current_total -= discount_amount;
			cur_frm.set_value("discount_1_rate", discount_amount);
		}
		if(cur_frm.doc.discount_2_value) {
			discount_amount = flt(current_total*flt(cur_frm.doc.discount_2_value) / 100,
				precision("discount_amount"));
			current_total -= discount_amount;
			cur_frm.set_value("discount_2_rate", discount_amount);
		}
		if(cur_frm.doc.discount_3_value) {
			current_total -= flt(cur_frm.doc.discount_3_value);
		}
		discount_amount = total - current_total;
	} else {
		discount_amount = flt(total*flt(cur_frm.doc.additional_discount_percentage) / 100,
			precision("discount_amount"));
	}
	return discount_amount
}

cur_frm.cscript.hide_original_price = function(frm, cdt, cdn) {
	cur_frm.custom_rate(frm, cdt, cdn);
	cur_frm.refresh_fields();
}

cur_frm.cscript.rate = function(frm, cdt, cdn) {
	cur_frm.custom_rate(frm, cdt, cdn);
}

cur_frm.custom_rate = function(frm, cdt, cdn) {
	var item = frappe.get_doc(cdt, cdn);
	frappe.model.round_floats_in(item, ["rate", "price_list_rate"]);
	if(item.price_list_rate && !item.hide_original_price) {
		item.discount_percentage = flt((1 - item.rate / item.price_list_rate) * 100.0, precision("discount_percentage", item));
	} else {
		item.discount_percentage = 0.0;
	}
}

frappe.ui.form.on("Quotation Additional", "rate", function(frm, cdt, cdn) {
	var d = frappe.model.get_doc(cdt, cdn);
	d.amount = d.rate * d.qty;
	cur_frm.refresh_fields();
})

frappe.ui.form.on("Quotation Additional", "qty", function(frm, cdt, cdn) {
	var d = frappe.model.get_doc(cdt, cdn);
	d.amount = d.rate * d.qty;
	cur_frm.refresh_fields();
})

frappe.ui.form.on("Quotation Additional", "additional_item", function(frm, cdt, cdn) {
	var me = this;
	var item = frappe.get_doc(cdt, cdn);
	if(item.additional_item) {
		cur_frm.call({
			method: "erpnext.stock.get_item_details.get_item_details",
			child: item,
			args: {
				args: {
					item_code: item.additional_item,
					customer: cur_frm.doc.customer,
					currency: cur_frm.doc.currency,
					conversion_rate: cur_frm.doc.conversion_rate,
					price_list: cur_frm.doc.selling_price_list,
					price_list_currency: cur_frm.doc.price_list_currency,
					plc_conversion_rate: cur_frm.doc.plc_conversion_rate,
					company: cur_frm.doc.company,
					transaction_date: cur_frm.doc.transaction_date,
					ignore_pricing_rule: cur_frm.doc.ignore_pricing_rule,
					doctype: cur_frm.doc.doctype,
					name: cur_frm.doc.name,
					qty: item.qty || 1,
					stock_qty: item.stock_qty,
					conversion_factor: item.conversion_factor
				}
			},
			callback: function(r) {
				if(!r.exc) {
					item.rate = r.message.price_list_rate;
					item.amount = item.qty*item.rate;
				}
				cur_frm.refresh_field("additional");
			}
		});
	}
})

cur_frm.cscript.partial_payment_1_value = function(frm) {
	if(cur_frm.doc.rounded_total) {
		cur_frm.set_value("partial_payment_1", (cur_frm.doc.rounded_total * cur_frm.doc.partial_payment_1_value) / 100);
	}
}

cur_frm.cscript.partial_payment_2_value = function(frm) {
	if(cur_frm.doc.rounded_total) {
		cur_frm.set_value("partial_payment_2", (cur_frm.doc.rounded_total * cur_frm.doc.partial_payment_2_value) / 100);
	}
}

cur_frm.cscript.partial_payment_3_value = function(frm) {
	if(cur_frm.doc.rounded_total) {
		cur_frm.set_value("partial_payment_3", (cur_frm.doc.rounded_total * cur_frm.doc.partial_payment_3_value) / 100);
	}
}

cur_frm.cscript.partial_payment_4_value = function(frm) {
	if(cur_frm.doc.rounded_total) {
		cur_frm.set_value("partial_payment_4", (cur_frm.doc.rounded_total * cur_frm.doc.partial_payment_4_value) / 100);
	}
}

cur_frm.cscript.upload_to_pingen = function(frm) {
	frappe.call({
		method: "switsol_ag.pingen.doctype.pingen_settings.pingen_settings.check_pingen",
		args: {
			doc_name: cur_frm.doc.name
		},
		callback: function(r) {
			if(!r.exception) {
				if(r.message) {
					frappe.prompt({
						fieldtype: "Heading",
						fieldname: "company_name",
						label: __("The document has already been sent to Pingen.")
					},
					function(data) {
						frappe.call({
							method: "switsol_ag.pingen.doctype.pingen_settings.pingen_settings.upload_document",
							args: {
								doc_type: cur_frm.doc.doctype,
								doc_name: cur_frm.doc.name
							},
							callback: function(r) {
								cur_frm.reload_doc();
							}
						})
					},
					__(" "), __("Resend it?")
					);
				} else {
					frappe.call({
						method: "switsol_ag.pingen.doctype.pingen_settings.pingen_settings.upload_document",
						args: {
							doc_type: cur_frm.doc.doctype,
							doc_name: cur_frm.doc.name
						},
						callback: function(r) {
							frappe.msgprint(__("The document has already been sent to Pingen."));
							cur_frm.reload_doc();
						}
					})
				}
			}
		}
	})
}

// cur_frm.cscript.partial_payment_1 = function(frm) {
// 	if(cur_frm.doc.grand_total) {
// 		cur_frm.set_value("partial_payment_1_value", flt(cur_frm.doc.partial_payment_1 * 100 / cur_frm.doc.grand_total, precision("partial_payment_1_value")));
// 	}
// }

// cur_frm.cscript.partial_payment_2 = function(frm) {
// 	if(cur_frm.doc.grand_total) {
// 		cur_frm.set_value("partial_payment_2_value", flt(cur_frm.doc.partial_payment_2 * 100 / cur_frm.doc.grand_total, precision("partial_payment_2_value")));
// 	}
// }

// cur_frm.cscript.partial_payment_3 = function(frm) {
// 	if(cur_frm.doc.grand_total) {
// 		cur_frm.set_value("partial_payment_3_value", flt(cur_frm.doc.partial_payment_3 * 100 / cur_frm.doc.grand_total, precision("partial_payment_3_value")));
// 	}
// }

// cur_frm.cscript.partial_payment_4 = function(frm) {
// 	if(cur_frm.doc.grand_total) {
// 		cur_frm.set_value("partial_payment_4_value", flt(cur_frm.doc.partial_payment_4 * 100 / cur_frm.doc.grand_total, precision("partial_payment_4_value")));
// 	}
// }
