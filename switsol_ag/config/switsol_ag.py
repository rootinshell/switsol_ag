# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Switsol AG"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Description Text",
                    "label": _("Description Text")
                },
                {
                    "type": "doctype",
                    "name": "Payment",
                    "label": _("Payment")
                },
                {
                    "type": "doctype",
                    "name": "Predefined Text Container",
                    "label": _("Predefined Text Container")
                },
                {
                    "type": "doctype",
                    "name": "Letter",
                    "label": _("Letter")
                },
                {
                    "type": "doctype",
                    "name": "Letter Text",
                    "label": _("Letter Text")
                },
                {
                    "type": "doctype",
                    "name": "Mailchimp Settings",
                    "label": _("Mailchimp Settings")
                },
                {
                    "type": "doctype",
                    "name": "Mailchimp Lists",
                    "label": _("Mailchimp Lists")
                },

            ]
        },
        {
            "label": _("Reports"),
            "icon": "icon-star",
            "items": [
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Call Logs Report",
                    "label": _("Call Logs Report"),
                    "description": _("Record of Call Logs Report"),
                    "doctype": "Call Logs",
                },
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Daily Unapproved Timesheet Summary",
                    "label": _("Daily Unapproved Timesheet Summary"),
                    "description": _("Record of Daily Unapproved Timesheet Summary"),
                    "doctype": "Timesheet",
                }
            ]
        }
    ]
