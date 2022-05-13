// Copyright (c) 2017, Switsol AG and contributors
// For license information, please see license.txt

cur_frm.add_fetch("description_text_name", "description_text", "description_text");
cur_frm.add_fetch("predefined_text_container", "predefined_text_container", "items_description1");
cur_frm.add_fetch("payment_name", "payment_details", "payment_details");


frappe.ui.form.on("Sales Invoice", {
	setup: function(frm) {
		if(frm.doc.company == "Gilgen Storen AG") {
			cur_frm.add_fetch("item_code", "width_asl_size", "width_asl_size");
			cur_frm.add_fetch("item_code", "width_hight_ht", "width_hight_ht");
			cur_frm.add_fetch("item_code", "width_hight_hl", "width_hight_hl");
			cur_frm.add_fetch("item_code", "location", "location");
			// cur_frm.add_fetch("customer", "pricing_rate", "pricing_rate");
			// cur_frm.add_fetch("customer", "hidden_discount_rate", "hidden_discount_rate");
			// cur_frm.add_fetch("customer", "discount", "discount");
			// cur_frm.add_fetch("customer", "skonto", "skonto");
		}
	},
	onload: function(frm) {
		cur_frm.toggle_display("naming_series", false);
		cur_frm.toggle_reqd("due_date", 0);
		cur_frm.set_value("company_name", "");
		if(frm.doc.__islocal) {
			frm.set_value("reminder_count", 1)
			frm.doc.reminder_logs = []
		}
		if(!cur_frm.doc.due_date) {
			cur_frm.set_value("due_date", frappe.datetime.add_days(cur_frm.doc.posting_date, cur_frm.doc.payment_period));
		};
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
	},
	refresh: function(frm) {
		cur_frm.toggle_display("naming_series", false);
		if(!cur_frm.doc.__islocal) {
			// cur_frm.add_custom_button(__("An Pingen übermitteln"), cur_frm.cscript.upload_to_pingen);
		}
		if(frm.doc.docstatus == 1 && cur_frm.doc.reminder_count <= 3) {
			frm.add_custom_button(__("Zahlungserinnerung") + " " + frm.doc.reminder_count, function() {
				frm.cscript.make_confirm_dialog()
			})
		}
		// if(frm.docstatus == 1 && cur_frm.doc.customer_address) {
		//     cur_frm.add_custom_button(__("Generate ESR"), cur_frm.print_inpayment_invoice);
		// }
		cur_frm.toggle_display("naming_series", 0);
		cur_frm.toggle_reqd("due_date", 0);
		cur_frm.set_value("company_name", "");
		if(cur_frm.doc.__islocal && cur_frm.doc.company != "Gilgen Storen AG") {
			cur_frm.set_value("employee_signature","");
		}
		if(!cur_frm.doc.description_text) {
			frappe.model.get_value("Description Text", {"using_doctype": cur_frm.doc.doctype}, ["title", "description_text"], function(r) {
				if(r && !r.exception) {
					cur_frm.set_value("description_text_name", r.title);
					cur_frm.set_value("description_text", r.description_text);
				}
			});
		}
		if(!cur_frm.doc.predefined_text_container) {
			frappe.model.get_value("Predefined Text Container", {"using_doctype": cur_frm.doc.doctype}, ["title", "predefined_text_container"], function(r) {
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
			if(cur_frm.doc.__islocal) {
				cur_frm.set_value("partial_payment_2_name", "bei Montagebeginn");
				cur_frm.set_value("partial_payment_3_name", "nach Montage 10 Tage netto");
			}
			if(cur_frm.doc.pricing_rate) {
				$("div[data-fieldname=pricing_rate]").find(".like-disabled-input").css({"color": "#c0392b !important"});
			}
			if(cur_frm.doc.hidden_discount_rate) {
				$("div[data-fieldname=hidden_discount_rate]").find(".like-disabled-input").css({"color": "#c0392b !important"});
			}
			if(cur_frm.doc.discount) {
				$("div[data-fieldname=discount]").find(".like-disabled-input").css({"color": "#c0392b !important"});
			}
			if(cur_frm.doc.skonto) {
				$("div[data-fieldname=skonto]").find(".like-disabled-input").css({"color": "#c0392b !important"});
			}
			if(cur_frm.doc.docstatus == 0) {
				if(cur_frm.doc.docstatus != 1) {
					if(!cur_frm.doc.taxes_and_charges || cur_frm.doc.taxes_and_charges == "MWST (8%)") {
						cur_frm.set_value("taxes_and_charges", "MWST (7.7%)");
					}
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
	company_address_name: function() {
		erpnext.utils.get_address_display(cur_frm, "company_address_name", "additional_company_address");
	},
	company_name: function() {
		cur_frm.set_value("company_address_name", "");
	},
})

cur_frm.cscript.due_date = function() {
	cur_frm.set_value("payment_terms_template", "");
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
				var greeting = surname.join(" ");
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
					return {
						query: "frappe.contacts.doctype.address.address.address_query",
						filters: {
							link_doctype: "Customer",
							link_name: cur_frm.doc.company_name
						}
					}
				},
				"reqd": 1
			}
		],
		secondary_action_label: (__("Create"))
	});

	dialog.set_primary_action(__("Add"), function() {
		args = dialog.get_values();
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
	let discount_amount = cur_frm.cscript.calculate_discount();
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
	let discount_amount = cur_frm.cscript.calculate_discount();
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
	let discount_amount = cur_frm.cscript.calculate_discount();
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
	if (cur_frm.doc.discount_1_value || cur_frm.doc.discount_2_value || cur_frm.doc.discount_3_value) {
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
	}
	else {
		discount_amount = flt(total*flt(cur_frm.doc.additional_discount_percentage) / 100, 
			precision("discount_amount"));
	}
	return discount_amount
}

cur_frm.cscript.hide_original_price = function(frm, cdt, cdn) {
	cur_frm.cscript.rate(frm, cdt, cdn);
	cur_frm.refresh_fields();
}

cur_frm.cscript.rate = function(frm, cdt, cdn) {
	cur_frm.cscript.custom_rate(frm, cdt, cdn);
}

cur_frm.cscript.custom_rate = function(frm, cdt, cdn) {
	var item = frappe.get_doc(cdt, cdn);
	frappe.model.round_floats_in(item, ["rate", "price_list_rate"]);
	if(item.price_list_rate && !item.hide_original_price) {
		item.discount_percentage = flt((1 - item.rate / item.price_list_rate) * 100.0, precision("discount_percentage", item));
	} else {
		item.discount_percentage = 0.0;
	}
}

cur_frm.cscript.payment_period = function(frm, cdt, cdn) {
	cur_frm.set_value("due_date", frappe.datetime.add_days(cur_frm.doc.posting_date, cur_frm.doc.payment_period));
}


cur_frm.print_inpayment_invoice = function(frm) {
	frappe.call({
		method: "switsol_ag.sales_invoice.check_fields",
		args: {
			customer_address: cur_frm.doc.customer_address
		},
		callback: function(r) {
			if(!r.exception) {
				window.open(frappe.urllib.get_full_url("/api/method/switsol_ag.download_pdf?doctype=" + encodeURIComponent("Sales Invoice") +"&name="+encodeURIComponent(cur_frm.doc.name)+"&format="+encodeURIComponent("ISR") + "&no_letterhead=0&_lang=de"));
			}
		}
	})
}

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
		cur_frm.set_value("partial_payment_4", (cur_frm.doc.grand_total * cur_frm.doc.partial_payment_4_value) / 100);
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
// 	if(cur_frm.doc.rounded_total) {
// 		cur_frm.set_value("partial_payment_1_value", flt(cur_frm.doc.partial_payment_1 * 100 / cur_frm.doc.rounded_total, precision("partial_payment_1_value")));
// 	}
// }

// cur_frm.cscript.partial_payment_2 = function(frm) {
// 	if(cur_frm.doc.rounded_total) {
// 		cur_frm.set_value("partial_payment_2_value", flt(cur_frm.doc.partial_payment_2 * 100 / cur_frm.doc.rounded_total, precision("partial_payment_2_value")));
// 	}
// }

// cur_frm.cscript.partial_payment_3 = function(frm) {
// 	if(cur_frm.doc.rounded_total) {
// 		cur_frm.set_value("partial_payment_3_value", flt(cur_frm.doc.partial_payment_3 * 100 / cur_frm.doc.rounded_total, precision("partial_payment_3_value")));
// 	}
// }

// cur_frm.cscript.partial_payment_4 = function(frm) {
// 	if(cur_frm.doc.rounded_total) {
// 		cur_frm.set_value("partial_payment_4_value", flt(cur_frm.doc.partial_payment_4 * 100 / cur_frm.doc.grand_total, precision("partial_payment_4_value")));
// 	}
// }

cur_frm.cscript.reminder_logs = function(reminder_status) {
	frappe.call({
		method: "switsol_ag.sales_invoice.reminder_logs",
		args: {
			"si_name": cur_frm.doc.name
		},
		callback: function(r) {
			if(r.message) {
			}
		}
	})
}

cur_frm.cscript.make_confirm_dialog = function() {
	var dialog = new frappe.ui.Dialog({
		title: __("Confirm"),
		fields: [
			{
				"fieldname": "text",
				"fieldtype": "Data",
				"default":__("Möchten Sie die Zahlungserinnerung per Email oder per Briefpost versenden?"),
				"read_only": 1
			},
			{
				"fieldname": "sec_brk",
				"fieldtype": "Section Break"
			},
			{
				"label": __("Per Email senden"), 
				"fieldname": "send_by_email",
				"fieldtype": "Button"
			},
			{
				"fieldname": "col_brk",
				"fieldtype": "Column Break"
			},
			{
				"label": __("Per Briefpost senden"), 
				"fieldname": "send_by_post",
				"fieldtype": "Button"
			}
		]
	});

	dialog.show();
	dialog.fields_dict.send_by_email.$input.click(function() {
		var flag = "Reminder"
		cur_frm.cscript.make_reminder_dialog(flag)
		dialog.hide()
	})
	dialog.fields_dict.send_by_post.$input.click(function() {
		var flag = "Post"
		cur_frm.cscript.make_reminder_dialog(flag)
		dialog.hide()
	})
}

cur_frm.cscript.make_reminder_dialog = function(flag) {
	var dialog = new frappe.ui.Dialog({
		title: __("Zahlungserinnerung"),
		fields: [
			{
				"label": __("Email Id"),
				"fieldname": "email_id",
				"fieldtype": "Data",
				"reqd": 1
			},
			{
				"label": __("Greeting"),
				"fieldname": "greeting",
				"fieldtype": "Data",
			},
			{
				"label": __("Predefined Text Container"),
				"fieldname": "predefined_text_container",
				"fieldtype": "Link", 
				"options": "Predefined Text Container",
				"get_query": function () {
					return {
						filters: [
							["using_doctype", "=", "Payment Entry"],
						]
					}
				},
				change: function() {
					cur_frm.cscript.content_of_predefined_text(dialog)
				}
			},
			{
				"label": __("Subject"),
				"fieldname": "subject",
				"fieldtype": "Data",
			},
			{
				"label": __("Vordefinierter Text"),
				"fieldname": "predefined_text",
				"fieldtype": "Text Editor"
			},
			{
				"label": __("Unterzeichner des Briefes"),
				"fieldname": "signed_by",
				"fieldtype": "Link",
				"options": "User"
			}
		]
	});
	dialog.show();
	cur_frm.cscript.get_greeting(dialog)
	if(flag == "Reminder") {
		var button = __("Zahlungserinnerung senden")
		dialog.fields_dict.signed_by.$wrapper.hide()
		cur_frm.doc.customer_address ? cur_frm.cscript.get_email_id(dialog) : ""
	} else {
		var button = __("Brief erstellen")
		dialog.fields_dict.email_id.$wrapper.hide()
		dialog.get_field("email_id").df.reqd = 0
	}

	dialog.set_primary_action(button, function() {
		cur_frm.cscript.send_payment_reminder(dialog, flag)
		dialog.hide()
	});
}

cur_frm.cscript.content_of_predefined_text = function(dialog) {
	var predefined_content = dialog.fields_dict.predefined_text_container.get_value();
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Predefined Text Container",
			fieldname: ["predefined_text_container", "subject"],
			filters: {name: predefined_content}
		},
		callback: function(r) {
			if(r.message) {
				dialog.set_value("predefined_text", r.message.predefined_text_container)
				dialog.set_value("subject", r.message.subject)
			}
		}
	});
}

cur_frm.cscript.get_email_id = function(dialog) {
	var customer_address = cur_frm.doc.customer_address
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Address",
			fieldname: "email_id",
			filters: {name: customer_address}
		},
		callback: function(r) {
			if(r.message) {
				dialog.set_value("email_id", r.message.email_id)
			}
		}
	});
}

cur_frm.cscript.get_greeting = function(dialog) {
	var customer = cur_frm.doc.customer
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Customer",
			fieldname: "greeting",
			filters: {name: customer}
		},
		callback: function(r) {
			if(r.message) {
				var surname = ""
				var customer_surname = cur_frm.doc.customer_name.split(" ")
				if(customer_surname.length != 0 && customer_surname.length > 1) {
					surname = customer_surname.slice(1).join(" ");
				} else {
					surname = cur_frm.doc.customer_name
				}
				if(frappe.boot.user.language =="de") {
					if(r.message.greeting =="Mrs") {
						var greeting = "Sehr geehrte Frau " + surname
						dialog.set_value("greeting",greeting)
					} else {
						var greeting = "Sehr geehrter Herr " + surname
						dialog.set_value("greeting",greeting)
					}
				} else {
					var greeting = "Dear " + r.message.greeting + ' ' + surname
					dialog.set_value("greeting", greeting)
				}
			}
		}
	});
}

cur_frm.cscript.send_payment_reminder = function(dialog, flag) {
	frappe.call({
		method: "switsol_ag.sales_invoice.payment_reminder",
		freeze: true,
		freeze_message: __("Sending") + ' ' + __(flag),
		args: {
			"customer_name": cur_frm.doc.customer,
			"args": dialog.get_values(),
			"flag": flag,
			"reminder_count": cur_frm.doc.reminder_count,
			"si_name": cur_frm.doc.name
		},
		callback: function(r) {
			if(r.message) {
				cur_frm.reload_doc()
				if(flag=="Post") {
					window.open(frappe.urllib.get_base_url() + "/api/method/frappe.utils.print_format.download_pdf?doctype=Letter&name=" + r.message + "&format=Letter%20SI%20Switsol%20AG&no_letterhead=0&_lang=de");
				}
			}
		}
	})
}
