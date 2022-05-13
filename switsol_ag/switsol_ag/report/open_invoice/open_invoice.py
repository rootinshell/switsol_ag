# -*- coding: utf-8 -*-

# Copyright (c) 2013, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _


def execute(filters=None):
    columns = get_column()
    data = prepare_data(filters)
    return columns, data


def get_column():
    return [
        {
            "label": _("Sales Invoice"),
            "fieldtype": "Link",
            "fieldname": "sales_invoice",
            "options": "Sales Invoice",
            "width": 120
        },
        {
            "label": _("Customer"),
            "fieldtype": "Link",
            "fieldname": "customer",
            "options": "Customer",
            "width": 160
        },
        {
            "label": _("Status"),
            "fieldtype": "Data",
            "fieldname": "status",
            "width": 120
        },
        {
            "label": _("Due Date"),
            "fieldtype": "Date",
            "fieldname": "due_date",
            "width": 120
        },
        {
            "label": _("Reminder Status"),
            "fieldtype": "Data",
            "fieldname": "reminder_status",
            "width": 180
        },
        {
            "label": _("Reminder Date 1"),
            "fieldtype": "Date",
            "fieldname": "reminder_date_1",
            "width": 180
        },
        {
            "label": _("Reminder Date 2"),
            "fieldtype": "Date",
            "fieldname": "reminder_date_2",
            "width": 180
        },
        {
            "label": _("Reminder Date 3"),
            "fieldtype": "Date",
            "fieldname": "reminder_date_3",
            "width": 180
        },
    ]


def get_data(filters):
    conditions = "and status != 'Paid'"
    if filters.get("paid_invoices"):
        conditions = ""
    return frappe.db.sql("""
        SELECT
            name,
            customer,
            status,
            due_date,
            reminder_status,
            reminder_count
        FROM
            `tabSales Invoice`
        WHERE
            docstatus = 1
            AND posting_date BETWEEN %(from_date)s AND %(to_date)s
            {conditions}
        ORDER BY
            name
        """.format(conditions=conditions), filters, as_dict=1)


def prepare_data(filters):
    data = []
    sales_invoices = get_data(filters)

    for d in sales_invoices:
        date_1 = ""
        date_2 = ""
        date_3 = ""
        dates = get_reminder_dates(d.name)
        date_1 = dates[0].date if len(dates) >= 1 else ""
        date_2 = dates[1].date if len(dates) >= 2 else ""
        date_3 = dates[2].date if len(dates) >= 3 else ""
        reminder_status = _get_reminder_status(d.name)
        row = [
            d.name,
            d.customer,
            _(d.status),
            d.due_date,
            reminder_status,
            date_1,
            date_2,
            date_3
        ]
        data.append(row)

    return data


def get_date_reminder_comment(customer, reminder_count, sales_invoice):
    subject_en = "{0}.".format(int(reminder_count - 1)) + "&nbsp" + _("Reminder") + "&nbsp" + _("had been sent for Sales Invoice :") + " " + sales_invoice
    subject_de = "{0}.".format(int(reminder_count - 1)) + "&nbsp" + _("Zahlungserinnerung") + "&nbsp" + _("für folgende Rechnung gesendet :") + " " + sales_invoice
    date = frappe.db.sql("""SELECT
        date_format(creation, '%%Y-%%m-%%d')
        FROM tabCommunication
        WHERE
            reference_name=%s
            AND subject=%s OR subject=%s""", (customer, subject_en, subject_de))
    if date:
        return date[0][0]


def get_date_reminder_email(customer, reminder_count, sales_invoice):
    subject_en = "{0}.".format(int(reminder_count - 1)) + " " + _("Reminder") + " " + sales_invoice
    subject_de = "{0}.".format(int(reminder_count - 1)) + " " + _("Zahlungserinnerung") + " " + sales_invoice
    date = frappe.db.sql("""SELECT
        date_format(creation, '%%Y-%%m-%%d')
        FROM `tabEmail Queue`
        WHERE
            message LIKE '%%%s%%' OR message LIKE '%%%s%%' """ % (subject_en, subject_de))
    if date:
        return date[0][0]


def _get_reminder_status(sales_invoice):
    reminder = ""
    reminder_status = frappe.db.sql("""SELECT
        reminder_status
        FROM `tabReminder Log`
        WHERE parent=%s
        ORDER BY reminder_status""", sales_invoice, as_dict=1)
    if len(reminder_status) == 1:
        reminder = reminder_status[0].reminder_status
    if len(reminder_status) == 2:
        reminder = reminder_status[1].reminder_status
    if len(reminder_status) == 3:
        reminder = reminder_status[2].reminder_status
    return reminder


def get_reminder_dates(sales_invoice):
    return frappe.db.sql("""SELECT
        date
        FROM `tabReminder Log`
        WHERE parent=%s""", sales_invoice, as_dict=1)
