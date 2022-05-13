# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "module_name": "Switsol AG",
            "color": "#8B0000",
            "icon": "octicon octicon-squirrel",
            "type": "module",
            "label": _("Switsol AG")
        },
        {
            "module_name": "Custom Setup Assistent",
            "color": "#003300",
            "icon": "octicon octicon-settings",
            "type": "module",
            "label": _("Custom Setup Assistent")
        },
        {
            "module_name": "Reports",
            "color": "#1abc9c",
            "icon": "octicon octicon-tag",
            "type": "page",
            "link": "reports",
            "label": _("Reports")
        },
        {
            "module_name": "Mailchimp",
            "color": "#003300",
            "icon": "octicon octicon-settings",
            "type": "module",
            "label": _("Mailchimp")
        },
        {
            "module_name": "Switsol",
            "color": "grey",
            "icon": "octicon octicon-file-directory",
            "type": "module",
            "label": _("Switsol")
        },
        {
            "module_name": "Time Log Sheet",
            "color": "#f39c12",
            "icon": "octicon octicon-package",
            "type": "page",
            "link": "time-log-sheet",
            "label": _("Time Log Sheet")
        },
    ]
