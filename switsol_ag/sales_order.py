# Copyright (c) 2017, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _
from frappe.utils import add_to_date
from frappe.utils.data import flt
from frappe.utils import now_datetime, cint
from frappe.model.naming import make_autoname
from pingen.doctype.pingen_settings.pingen_settings import check_pingen, upload_document


def after_insert(self, method=None):
    send_to_pingen(self)
    if not self.reference_number and self.company=="Gilgen Storen AG":
        year = now_datetime().year
        frappe.db.set(self, "reference_number", make_autoname(str(year)))


@frappe.whitelist(allow_guest=True)
def validate(self, method=None):
    validate_contract_time(self)
    # validate_delivery_date(self)
    validate_discount(self)
    round_to(self)
    calculate_item_values(self)
    calculate_discount(self)
    validate_items(self)
    validate_partial_payments(self)


def validate_delivery_date(self):
    self.delivery_date = add_to_date(self.transaction_date, days=2)

    if self.order_type == 'Sales' and not self.delivery_date:
        frappe.throw(_("Please enter 'Expected Delivery Date'"))


def round_to(self):
    correction = 0.5 if self.grand_total >= 0 else -0.5
    round_total = int(self.grand_total / 0.05 + correction) * 0.05
    self.rounded_total_enip = "{:.2f}".format(round_total)


def calculate_item_values(self):
    for item in self.get("items"):
        self.round_floats_in(item)
        if not item.hide_original_price:
            if item.discount_percentage == 100:
                item.rate = 0.0
            elif not item.rate:
                item.rate = flt(item.price_list_rate * (1.0 - (item.discount_percentage / 100.0)), item.precision("rate"))

            item.net_rate = item.rate
            item.amount = flt(item.rate * item.qty, item.precision("amount"))
            item.net_amount = item.amount

            item.item_tax_amount = 0.0
        else:
            item.discount_percentage = 0.0
            item.margin_type = ""
            item.margin_rate_or_amount = 0.0


def validate_discount(self):
    discount = [item for item in self.items if item.discount_percentage]
    if discount:
        frappe.db.set(self, "check_discount", 1)
    else:
        frappe.db.set(self, "check_discount", 0)


def validate_contract_time(self):
    if (self.contact_start_date and self.contact_end_date and self.contact_end_date <= self.contact_start_date):
        frappe.throw(_("Contract End Date must be greater than Contract Start Date"))


def calculate_discount(self):
    current_total = self.total
    total_discount = 0.0
    if self.discount_1_value:
        discount_amount = flt(current_total * flt(self.discount_1_value) / 100, self.precision("discount_amount"));
        current_total -= flt(discount_amount)
        total_discount += discount_amount
    if self.discount_2_value:
        discount_amount = flt(current_total * flt(self.discount_2_value) / 100, self.precision("discount_amount"));
        current_total -= flt(discount_amount)
        total_discount += discount_amount
    if self.discount_3_value:
        current_total -= flt(self.discount_3_value)
        total_discount += flt(self.discount_3_value)
    if current_total != self.total:
        frappe.db.set(self, "discount_amount", total_discount)


def validate_items(self):
    for item in self.items:
        if item.description.lower() == "leer":
            item.show_in_details = 0
        else:
            item.show_in_details = 1
    show_in_details = [i for i in self.items if i.show_in_details]
    if show_in_details:
        frappe.db.set(self, "item_details", 1)
    else:
        frappe.db.set(self, "item_details", 0)


def validate_partial_payments(self):
    if self.partial_payment_1_value and not self.partial_payment_1:
        self.partial_payment_1 = (flt(self.rounded_total) * flt(self.partial_payment_1_value)) / 100
    if self.partial_payment_2_value and not self.partial_payment_2:
        self.partial_payment_2 = (flt(self.rounded_total) * flt(self.partial_payment_2_value)) / 100
    if self.partial_payment_3_value and not self.partial_payment_3:
        self.partial_payment_3 = (flt(self.rounded_total) * flt(self.partial_payment_3_value)) / 100
    if self.partial_payment_4_value and not self.partial_payment_4:
        self.partial_payment_4 = (flt(self.rounded_total) * flt(self.partial_payment_4_value)) / 100

    if self.partial_payment_1:
        partial_payment_1_value = (flt(self.partial_payment_1) * 100) / flt(self.rounded_total)
        if self.partial_payment_1_value != partial_payment_1_value:
            self.partial_payment_1_value = partial_payment_1_value
    if self.partial_payment_2:
        partial_payment_2_value = (flt(self.partial_payment_2) * 100) / flt(self.rounded_total)
        if self.partial_payment_2_value != partial_payment_2_value:
            self.partial_payment_2_value = partial_payment_2_value
    if self.partial_payment_3:
        partial_payment_3_value = (flt(self.partial_payment_3) * 100) / flt(self.rounded_total)
        if self.partial_payment_3_value != partial_payment_3_value:
            self.partial_payment_3_value = partial_payment_3_value
    if self.partial_payment_4:
        partial_payment_4_value = (flt(self.partial_payment_4) * 100) / flt(self.rounded_total)
        if self.partial_payment_4_value != partial_payment_4_value:
            self.partial_payment_4_value = partial_payment_4_value
    if self.partial_payment_1 or self.partial_payment_2 or self.partial_payment_3 or self.partial_payment_4:
        if flt(self.partial_payment_1) + flt(self.partial_payment_2) + flt(self.partial_payment_3) + flt(self.partial_payment_4) != self.rounded_total:
            frappe.throw(_("The total of the partial-payments isn't equal to the total invoice amount. Please correct."))


def send_to_pingen(self):
    auto_send = frappe.db.get_value("Pingen Settings", "Pingen Settings", fieldname=["auto_send", "api_token"], as_dict=1)
    document_sent = check_pingen(self.name)
    if auto_send and auto_send.get("api_token"):
        if int(auto_send.get("auto_send")) and not document_sent:
            s = upload_document(self.doctype, self.name)
            if s.get("send") == "true":
                frappe.msgprint(_("Document has been sent through Pingen. If you want stop it, please check Pingen."))
            else:
                frappe.msgprint(_("Document is saved in Pingen. You can release it there."))
