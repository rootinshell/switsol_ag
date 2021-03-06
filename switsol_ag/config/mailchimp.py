# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Documents"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Mailchimp Settings",
                    "label": _("Mailchimp Settings")
                },
                {
                    "type": "doctype",
                    "name": "Mailchimp Lists",
                    "label": _("Mailchimp Lists")
                }                
            ]
        }
    ]
