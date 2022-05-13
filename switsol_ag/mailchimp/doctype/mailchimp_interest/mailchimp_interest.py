# -*- coding: utf-8 -*-
# Copyright (c) 2018, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
from frappe.model.document import Document
from frappe.integrations.utils import make_get_request, make_post_request
from switsol_ag.mailchimp.doctype.mailchimp_settings.mailchimp_settings import create_interest, get_auth, get_api_key


class MailchimpInterest(Document):
    def autoname(self):
        self.name = self.interest_name

    def before_insert(self):
        headers = {}
        auth = get_auth()
        api_key = get_api_key()
        if not self.interest_id:
            data = {
                "name": self.interest_name,
                "display_order": self.display_order or 0
            }
            interests_url = "https://{0}.api.mailchimp.com/3.0/lists/{1}/interest-categories/{2}/interests".format(api_key.split("-")[1], self.list_id, self.category_id)
            frappe.flags.integration_request = requests.post(interests_url, json=data, auth=auth, headers=headers)
            frappe.flags.integration_request.raise_for_status()
            interests_resp = frappe.flags.integration_request.json()
            self.interest_id = interests_resp.get("id")
            self.subscriber_count = interests_resp.get("subscriber_count")

    def after_insert(self):
        if self.category_id and self.interest_id:
            interests = frappe.db.sql("""
                select
                    name
                from
                    `tabMailchimp Interest Category`
                where
                    interest_id=%s""", self.interest_id)
            if not interests:
                doc_category = frappe.get_doc("Interest Category", {"category_id": self.category_id})
                doc_category.append("interests", {
                    "mailchimp_interest": self.name,
                    "list_name": self.list_name,
                    "list_id": self.list_id,
                    "interest_id": self.interest_id,
                    "interest_name": self.interest_name,
                    "subscriber_count": self.subscriber_count,
                    "display_order": self.display_order
                })
                doc_category.save()
                frappe.db.commit()
