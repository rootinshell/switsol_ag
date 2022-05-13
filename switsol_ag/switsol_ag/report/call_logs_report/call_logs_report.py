# Copyright (c) 2013, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _


def execute(filters=None):
    columns = get_colums()
    data = get_data(filters)
    return columns, data


def get_data(filters):
    if filters:
        result = frappe.db.sql("""
            SELECT
                name,
                date(creation),
                phone_number,
                contact_person,
                client,
                contact_type,
                start_time,
                end_time,
                TIMEDIFF(end_time, start_time),
                call_attendant,
                subject
            FROM `tabCall Logs` {0}
            ORDER BY name ASC""".format(get_cond(filters)), as_list=1)
    else:
        result = frappe.db.sql("""
            SELECT
                name,
                date(creation),
                phone_number,
                contact_person,
                client,
                contact_type,
                start_time,
                end_time,
                TIMEDIFF(end_time, start_time),
                call_attendant,
                subject
            FROM `tabCall Logs`
            ORDER BY name ASC""", as_list=1)
    return result


def get_cond(filters):
    cond = ""
    if filters.get("client_info").split("//")[0] == "Call Logs":
        cond = "where phone_number = '{0}' and client = '{1}'".format(filters.get('client_info').split("//")[-1], filters.get('client_info').split("//")[2])
    if filters.get("client_info").split("//")[0] == "Contact":
        cond = "where phone_number = '{0}' and contact_person = '{1}'".format(filters.get('client_info').split("//")[2], filters.get('client_info').split("//")[1])
    if filters.get("client_info").split("//")[0] == "Customer":
        cond = "where client = '{0}' and contact_type = 'Customer' ".format(filters.get('client_info').split("//")[1])
    if filters.get("client_info").split("//")[0] == "Supplier":
        cond = "where client = '{0}' and contact_type = 'Supplier' ".format(filters.get('client_info').split("//")[1])
    if filters.get("client_info").split("//")[0] == "Sales Partner":
        cond = "where client = '{0}' and contact_type = 'Sales Partner' ".format(filters.get('client_info').split("//")[1])
    return cond


def get_colums():
    columns = []
    columns.append({
        "fieldname": "name",
        "label": _("Telefon Protokoll"),
        "width": 40,
        "fieldtype": "Link",
        "options": "Call Logs"
    })
    columns.append({
        "fieldname": "date",
        "label": _("Date"),
        "width": 80,
        "fieldtype": "Date"
    })
    columns.append({
        "fieldname": "phone_number",
        "label": _("Telefonnummer"),
        "width": 70,
        "fieldtype": "Data"
    })
    columns.append({
        "fieldname": "contact_person",
        "label": _("Contact Person"),
        "width": 150,
        "fieldtype": "Link",
        "options": "Contact"
    })
    columns.append({
        "fieldname": "client",
        "label": _("Customer"),
        "width": 100,
        "fieldtype": "Dynamic Link/",
        "options": "Contact Type"
    })
    columns.append({
        "fieldname": "contact_type",
        "label": _("Contact Type"),
        "width": 100,
        "fieldtype": "Data"
    })
    columns.append({
        "fieldname": "start_time",
        "label": _("Start Time"),
        "width": 100,
        "fieldtype": "Data"
    })
    columns.append({
        "fieldname": "end_time",
        "label": _("End Time"),
        "width": 80,
        "fieldtype": "Data"
    })
    columns.append({
        "fieldname": "difference",
        "label": _("Dauer des Anrufs"),
        "width": 80,
        "fieldtype": "Data"
    })
    columns.append({
        "fieldname": "user",
        "label": _("User"),
        "width": 180,
        "fieldtype": "Link",
        "options": "User"
    })
    columns.append({
        "fieldname": "subject",
        "label": _("Subject"),
        "width": 180,
        "fieldtype": "Small Text"
    })
    return columns
