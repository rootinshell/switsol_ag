# -*- coding: utf-8 -*-
# Copyright (c) 2018, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
from frappe.model.document import Document
from switsol_ag.mailchimp.doctype.mailchimp_settings.mailchimp_settings import get_auth, get_api_key


class InterestCategory(Document):
    def autoname(self):
        self.name = self.group_name

    def before_insert(self):
        if not self.category_id:
            headers = {}
            auth = get_auth()
            api_key = get_api_key()
            data = {
                "title": self.group_name,
                "type": self.display_type.lower()
            }
            interests_url = "https://{0}.api.mailchimp.com/3.0/lists/{1}/interest-categories".format(api_key.split("-")[1], self.list_id)
            frappe.flags.integration_request = requests.post(interests_url, json=data, auth=auth, headers=headers)
            frappe.flags.integration_request.raise_for_status()
            interests_resp = frappe.flags.integration_request.json()
            self.category_id = interests_resp.get("id")
            self.display_order = interests_resp.get("display_order")
