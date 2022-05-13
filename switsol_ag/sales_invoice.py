# Copyright (c) 2017, Switsol AG and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
import json
import datetime
import frappe.defaults

from frappe import _
from frappe.utils.data import flt, add_to_date
from frappe.email.email_body import get_message_id
from frappe.utils import cstr, nowdate, getdate
from frappe import _, msgprint, scrub
from pingen.doctype.pingen_settings.pingen_settings import check_pingen, upload_document


def validate(self, method=None):
    validate_contract_time(self)
    validate_due_date(self)
    improve_remarks(self)
    calculate_item_values(self)
    calculate_discount(self)
    validate_discount(self)
    calculate_discount_per_item(self)
    round_to(self)
    validate_partial_payments(self)


def after_insert(self, method=None):
    pass
    # send_to_pingen(self)


def validate_contract_time(self):
    if (self.contact_start_date and self.contact_end_date and self.contact_end_date <= self.contact_start_date):
        frappe.throw(_("Contract End Date must be greater than Contract Start Date"))


def validate_due_date(self):
    self.due_date = add_to_date(self.posting_date, days=self.payment_period)


def validate_discount(self):
    discount = [item for item in self.items if item.discount_percentage]
    if discount:
        frappe.db.set(self, "check_discount", 1)
    else:
        frappe.db.set(self, "check_discount", 0)


def improve_remarks(self):
    if self.remarks == "No Remarks":
        self.remarks = _("No Remarks")


def calculate_item_values(self):
    items_with_installation_date = []
    for item in self.get("items"):
        self.round_floats_in(item)
        if item.installation_date:
            self.is_date_row = 1
            items_with_installation_date.append(item)
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
    if not len(items_with_installation_date):
        self.is_date_row = 0


def round_to(self):
    correction = 0.5 if self.grand_total >= 0 else -0.5
    round_total = int(self.grand_total / 0.05 + correction) * 0.05
    self.rounded_total_enip = "{:.2f}".format(round_total)


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
    return self


def calculate_discount_per_item(self):
    for i in self.get("items"):
        if self.discount_1_value:
            discount_1_value = i.net_amount * self.discount_1_value / 100
            i.net_amount -= discount_1_value
            # i.base_net_amount -= discount_1_value
        if self.discount_2_value:
            discount_2_value = i.net_amount * self.discount_2_value / 100
            i.net_amount -= discount_2_value
            # i.base_net_amount -= discount_2_value


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


@frappe.whitelist()
def check_fields(customer_address):
    error_message = ""
    if not customer_address:
        error_message = " Please add Customer Address"
    if error_message:
        return frappe.throw(error_message)
    else:
        return True


@frappe.whitelist()
def payment_reminder(customer_name, args, flag, reminder_count, si_name):
    data = json.loads(args) 
    si_doc = frappe.get_doc("Sales Invoice", si_name)
    customer_doc = frappe.get_doc("Customer", customer_name)
    attachments = [frappe.attach_print("Sales Invoice", si_name, file_name=si_name, print_format="Sales Invoice Switsol AG")]
    if flag == "Reminder":
        subject = _("Reminder")
        try:
            frappe.sendmail(
                recipients=data.get("email_id"),
                expose_recipients="header",
                sender=None,
                reply_to=None,
                subject=data.get("subject"),
                content=None,
                reference_doctype=None,
                reference_name=None,
                attachments=attachments,
                message = data.get("greeting") + "<br><br>" + data.get("predefined_text"),
                message_id=None,
                unsubscribe_message=None,
                delayed=False,
                communication=None
            )
            add_email_communication(data.get("predefined_text"), data.get("email_id"), customer_doc, si_doc)
            reminder_logs(si_name, reminder_count)
            return True
        except Exception, e:
            print frappe.get_traceback()
            frappe.throw(_("Mail has not been Sent. Kindly Contact to Administrator"))
    else:
        letter_name = make_new_letter(si_name, reminder_count, data, data.get("greeting"))
        customer_doc.add_comment("Comment", "{0}.".format(reminder_count) + "&nbsp" + _("Reminder") + "&nbsp" + _("had been sent for Sales Invoice :") 
            + " " + "<a href='#Form/Sales Invoice/{0}'>{0}</a>".format(si_name))
        reminder_logs(si_name, reminder_count)
        return letter_name


def add_email_communication(message, email_id, doc, si_doc):
    comm = frappe.get_doc({
        "doctype": "Communication",
        "subject": "Reminder: " + si_doc.name,
        "content": message,
        "sender": None,
        "recipients": email_id,
        "cc": None,
        "communication_medium": "Email",
        "sent_or_received": "Sent",
        "reference_doctype": si_doc.doctype,
        "reference_name": si_doc.name,
        "message_id": get_message_id().strip(" <>"),
        "customer": doc.name
    })
    comm.insert(ignore_permissions=True)


def reminder_logs(si_name, reminder_count):
    reminder_count = json.loads(reminder_count)
    if reminder_count == 1:
        status = "1. Zahlungserinnerung"
    elif reminder_count == 2:
        status = "2. Zahlungserinnerung"
    elif reminder_count == 3:
        status = "Betreibungsandrohung"
    si_doc = frappe.get_doc("Sales Invoice", si_name)
    si_doc.append("reminder_logs", {
        "date": nowdate(),
        "reminder_status": status
    })
    si_doc.reminder_count = si_doc.reminder_count + 1
    si_doc.save(ignore_permissions=True)


def make_new_letter(si_name, reminder_count, data, greeting):
    letter = frappe.new_doc("Letter")
    si_doc = frappe.get_doc("Sales Invoice", si_name)
    letter.name = si_doc.customer_name
    letter.customer = si_doc.customer
    letter.customer_name = si_doc.customer_name
    letter.company = frappe.defaults.get_defaults().company
    letter.date = nowdate()
    letter.clerk_name = frappe.session.user
    letter.status = "Sent"
    letter.customer_address = si_doc.company_address_name if si_doc.company_address_name else si_doc.customer_address
    letter.contact_person = si_doc.contact_person
    letter.contact_display = si_doc.contact_display
    letter.address_display = si_doc.company_address if si_doc.company_address_name else si_doc.address_display
    letter.subject =  data.get("subject")
    letter.contact_greeting = data.get("greeting")
    letter.letter_text = data.get("predefined_text_container")
    letter.body_text = greeting + "<br><br>" + data.get("predefined_text")
    letter.chief_signature = si_doc.chief_signature
    letter.chief_signature_value = frappe.db.get_value("Employee", {"user_id": si_doc.chief_signature}, "signature")
    letter.employee_signature = data.get("signed_by")
    letter.employee_signature_value = frappe.db.get_value("Employee", {"user_id": data.get("signed_by")}, "signature")
    letter.related_doctype = si_doc.doctype
    letter.related_name = si_doc.name
    letter.flags.ignore_permissions = 1
    letter.flags.ignore_mandatory = True
    letter.save()
    letter.submit()
    return letter.name


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
