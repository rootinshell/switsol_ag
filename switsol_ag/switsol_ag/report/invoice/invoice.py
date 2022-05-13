# Copyright (c) 2013, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _


def execute(filters=None):
    columns = get_column()
    data = get_data(filters)
    return columns, data


def get_column():
    return [
        _("Sales Invoice") + ":Link/Sales Invoice:120",
        _("Customer") + ":Link/Customer:120",
        _("Status") + ":Data:180",
        _("Due Date") + ":Date:180",
    ]


def get_data(filters):
    return frappe.db.sql("""
        SELECT
            name,
            customer,
            status,
            due_date
        FROM
            `tabSales Invoice`
        WHERE
            docstatus=1
            AND posting_date BETWEEN %s AND %s
        ORDER BY
            name
        """, (filters.get("from_date"), filters.get("to_date")))
