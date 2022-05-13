
from __future__ import unicode_literals
import frappe
import json
import base64
from datetime import datetime,date
from frappe.utils import flt, cstr, cint
from random import randrange,uniform
from frappe import _
import frappe.utils.file_manager
from frappe.desk.form.load import get_attachments


def execute(filters=None):
    if not filters:
        filters = {}
    columns = [
        {
            "label": _(""),
            "fieldtype": "",
            "fieldname": "test",
            "default": False,
            "width": 70
        },
        {
            "label": _("Date"),
            "fieldtype": "Date",
            "fieldname": "date",
            "width": 120
        },
        {
            "label": _("Start Time"),
            "fieldtype": "Data",
            "fieldname": "start_time",
            "width": 120
        },
        {
            "label": _("End Time"),
            "fieldtype": "Data",
            "fieldname": "end_time",
            "width": 120
        },
        {
            "label": _("Total Hours"),
            "fieldtype": "Data",
            "fieldname": "total_hours",
            "width": 120
        },
        {
            "label": _("Employee"),
            "fieldtype": "Link",
            "fieldname": "employee",
            "options": "Employee",
            "width": 120
        },
        {
            "label": _("Customer"),
            "fieldtype": "Link",
            "fieldname": "customer",
            "options": "Customer",
            "width": 120
        },
        {
            "label": _("Project"),
            "fieldtype": "Link",
            "fieldname": "project",
            "options": "Project",
            "width": 120
        },
        {
            "label": _("Timesheet"),
            "fieldtype": "Link",
            "fieldname": "timesheet",
            "options": "Timesheet",
            "width": 120
        },
        {
            "label": _("Status"),
            "fieldtype": "Data",
            "fieldname": "status",
            "width": 70
        }
    ]

    conditions = "ts.docstatus = 0"
    if filters.get("from_date"):
        conditions = " and tsd.from_time >= timestamp(%(from_date)s, %(from_time)s)"
    if filters.get("to_date"):
        conditions += " and tsd.to_time <= timestamp(%(to_date)s, %(to_time)s)"

    data = get_data()

    return columns, data


def get_data():
    time_sheet = frappe.db.sql("""
        select
            ts.name,
            date(td.from_time) as date,
            time(td.from_time) as start_time,
            time(td.to_time) as end_date,
            format(td.hours, 3) as total_hours,
            ts.employee as employee,
            td.customer as customer,
            td.project as project,
            ts.name as timesheet,
            ts.status as status
        from `tabTimesheet` ts,`tabTimesheet Detail` td
        where 
            td.parent = ts.name
            and ts.docstatus = 0
            and td.idx = 1
        order by ts.name""", as_list=1)
    return time_sheet


@frappe.whitelist()
def update_timesheet(list_of_timesheet, signature_svg):
    from frappe.handler import uploadfile
    list_of_timesheet = json.loads(list_of_timesheet)
    for time_sheet in list_of_timesheet:
        frappe.form_dict["from_form"] = 1
        frappe.form_dict["doctype"] = "Timesheet"
        frappe.form_dict["docname"] = time_sheet
        frappe.form_dict["filename"] = cstr(randrange(0, 10000)) + cstr(time_sheet)
        frappe.form_dict["filedata"] = signature_svg
        attachment = uploadfile()
        if attachment.get("file_url"):
            time_sheet_doc = frappe.get_doc("Timesheet", time_sheet)
            time_sheet_doc.signature_base64 = attachment.get("file_url")
            time_sheet_doc.docstatus = 1
            time_sheet_doc.signature_time = datetime.now()
            time_sheet_doc.save(ignore_permissions=True)
    return True


def remove_attachment(self, method=None):
    self.signature_base64 = ""
    attachment = get_attachments("Timesheet", self.name)
    file_id = [data.get("name") for data in attachment]
    for fid in file_id:
        frappe.utils.file_manager.remove_file(fid)
