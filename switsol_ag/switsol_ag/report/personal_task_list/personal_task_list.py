# -*- coding: utf-8 -*-

# Copyright (c) 2017, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _
from frappe.utils import formatdate


def execute(filters=None):
    columns = get_column()
    data = prepare_data(filters)
    return columns, data


def get_column():
    return [
        _("Due Date") + ":Date:160",
        _("Expected Start Date") + ":Date:160",
        _("Responsible Person") + ":Link/User:240",
        _("Subject") + ":Data:120",
        _("Status") + ":Data:120",
        _("Name") + ":Data:120"
    ]


def get_data(filters):
    statuses = ["Open", "Waiting for Other Person", "Working"]
    if filters.get("done_tasks"):
        statuses.extend(["Done", "Closed", "Unnecessary"])
    responsible_person = ""
    if not filters.get("all_tasks"):
        responsible_person = frappe.session.user
    return frappe.db.sql("""
        SELECT
            exp_end_date,
            exp_start_date,
            _assign,
            name,
            status,
            subject,
            description
        FROM
            `tabTask`
        WHERE
            status IN (%s)
            AND ifnull(_assign,"") LIKE %s
        ORDER BY
            exp_end_date
        """ % (', '.join(['%s'] * len(statuses)), '%s'), tuple(statuses + ["%%%s%%" % responsible_person]), as_dict=1)


def prepare_data(filters):
    data = []
    tasks = get_data(filters)

    for t in tasks:
        assign = frappe.db.sql("""
            SELECT
                owner
            FROM 
                tabToDo
            WHERE reference_type='Task' AND reference_name=%s""", t.name, as_dict=1)
        assign = [i.owner for i in assign]
        row = [
            formatdate(t.exp_end_date),
            formatdate(t.exp_start_date),
            ', '.join(assign),
            str(t.subject) + "\n" + str(t.description),
            _(t.status),
            t.name
        ]
        data.append(row)

    return data
