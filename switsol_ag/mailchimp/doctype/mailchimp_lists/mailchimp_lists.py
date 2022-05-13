# -*- coding: utf-8 -*-
# Copyright (c) 2018, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import md5
import hashlib
from frappe.model.document import Document
from frappe import _
from frappe.utils import get_request_session
from frappe.integrations.utils import make_get_request, make_post_request
from switsol_ag.mailchimp.doctype.mailchimp_settings.mailchimp_settings import get_auth, get_api_key, get_lists_url, get_members_url


class MailchimpLists(Document):
    def autoname(self):
        self.name = self.list_name

    def before_insert(self):
        if not self.list_id:
            auth = get_auth()
            api_key = get_api_key()
            country = frappe.db.get_value("Country", {"name": self.contacts[0].country}, "code")
            data = {
                "name": self.list_name,
                "permission_reminder": self.permission_reminder,
                "use_archive_bar": True if self.use_archive_bar==1 else False,
                "notify_on_subscribe": self.notify_on_subscribe or "",
                "notify_on_unsubscribe": self.notify_on_unsubscribe or "",
                "visibility": "pub" if self.visibility=="Public" else "prv",
                "total_items": self.total_items or "",
                "double_optin": True if self.double_optin==1 else False,
                "contact": {
                    "company": self.contacts[0].company,
                    "address1": self.contacts[0].address1,
                    "address2": self.contacts[0].address2 or "",
                    "city": self.contacts[0].city,
                    "state": self.contacts[0].state or "",
                    "zip": self.contacts[0].zip or "",
                    "country": country.upper(),
                    "phone": self.contacts[0].phone or ""
                },
                "campaign_defaults": {
                    "from_name": self.campaign_defaults[0].from_name,
                    "from_email": self.campaign_defaults[0].from_email,
                    "subject": self.campaign_defaults[0].subject or "",
                    "language": self.campaign_defaults[0].language
                },
                "email_type_option": True if self.email_type_option==1 else False,
            }
            headers = {}
            try:
                lists_url = get_lists_url(api_key)
                frappe.flags.integration_request = requests.post(lists_url, json=data, auth=auth, headers=headers)
                frappe.flags.integration_request.raise_for_status()
                resp = frappe.flags.integration_request.json()
                self.flags.dont_sync_lists = True
                self.list_id = resp.get("id")
                self.web_id = resp.get("web_id")
                self.subscribe_url_short = resp.get("subscribe_url_short")
                self.subscribe_url_long = resp.get("subscribe_url_long")
                self.beamer_address = resp.get("beamer_address")
                self.total_items = resp.get("total_items")
                self.date_created = resp.get("date_created")
                self.list_rating = resp.get("list_rating")
                if resp.get("id") and self.members:
                    members_url = get_members_url(api_key, resp.get("id"))
                    for member in self.members:
                        main_interests = get_interests_dict(member)
                        member_data = {
                            "email_address": member.email_address,
                            "status": member.status.lower(),
                            "language": member.language,
                            "vip": True if member.vip==1 else False,
                            "email_id": member.get("id"),
                            "ip_opt": member.get("ip_opt"),
                            "ip_signup": member.get("ip_signup"),
                            "list_id": member.get("list_id"),
                            "merge_fields": {
                                "FNAME": member.first_name,
                                "LNAME": member.last_name,
                                "BIRTHDAY": member.birthday,
                                "PHONE": member.phone or ""
                            },
                            "interests": main_interests
                        }
                        frappe.flags.integration_request = requests.post(members_url, json=member_data, auth=auth, headers=headers)
                        frappe.flags.integration_request.raise_for_status()
                        member_resp = frappe.flags.integration_request.json()
                        member.email_id = member_resp.get("id")
                        member.unique_email_id = member_resp.get("unique_email_id")
                        member.email_client = member_resp.get("email_client")
                        member.member_rating = member_resp.get("member_rating")
                        member.last_changed = member_resp.get("last_changed")
            except Exception as exc:
                frappe.throw(exc)
                # raise exc
                # frappe.throw(_("Seems API Key is wrong !!!"))

    def on_update(self):
        if self.flags.dont_sync_lists: return
        update_data(self.name)


@frappe.whitelist(allow_guest=True)
def get_list_dict(mailchimp):
    mailchimp_list = frappe.get_doc("Mailchimp Lists", mailchimp)
    country = frappe.db.get_value("Country", {"name": mailchimp_list.contacts[0].country}, "code")
    return {
        "name": mailchimp_list.list_name,
        "permission_reminder": mailchimp_list.permission_reminder,
        "use_archive_bar": True if mailchimp_list.use_archive_bar==1 else False,
        "notify_on_subscribe": mailchimp_list.notify_on_subscribe or "",
        "notify_on_unsubscribe": mailchimp_list.notify_on_unsubscribe or "",
        "visibility": "pub" if mailchimp_list.visibility=="Public" else "prv",
        "total_items": mailchimp_list.total_items,
        "double_optin": True if mailchimp_list.double_optin==1 else False,
        "contact": {
            "company": mailchimp_list.contacts[0].company,
            "address1": mailchimp_list.contacts[0].address1,
            "address2": mailchimp_list.contacts[0].address2 or "",
            "city": mailchimp_list.contacts[0].city,
            "state": mailchimp_list.contacts[0].state or "",
            "zip": mailchimp_list.contacts[0].zip or "",
            "country": country,
            "phone": mailchimp_list.contacts[0].phone or ""
        },
        "campaign_defaults": {
            "from_name": mailchimp_list.campaign_defaults[0].from_name,
            "from_email": mailchimp_list.campaign_defaults[0].from_email,
            "subject": mailchimp_list.campaign_defaults[0].subject or "",
            "language": mailchimp_list.campaign_defaults[0].language
        },
        "email_type_option": True if mailchimp_list.email_type_option==1 else False,
    }


@frappe.whitelist(allow_guest=True)
def update_data(mailchimp):
    auth = get_auth()
    api_key = get_api_key()
    data = get_list_dict(mailchimp)
    headers = {}
    mailchimp_list = frappe.get_doc("Mailchimp Lists", mailchimp)
    try:
        lists_url = "https://{0}.api.mailchimp.com/3.0/lists/{1}".format(api_key.split("-")[1], mailchimp_list.list_id)
        frappe.flags.integration_request = requests.patch(lists_url, json=data, auth=auth, headers=headers)
        frappe.flags.integration_request.raise_for_status()
        for member in mailchimp_list.members:
            interests_dict = get_interests_dict(member)
            member_data = {
                "email_address": member.email_address,
                "email_type": member.email_type or "html",
                "unsubscribe_reason": member.unsubscribe_reason or "",
                "status": member.status.lower(),
                "language": member.language or "",
                "vip": True if member.vip==1 else False,
                "list_id": mailchimp_list.list_id,
                "merge_fields": {
                    "FNAME": member.first_name,
                    "LNAME": member.last_name,
                    "BIRTHDAY": member.birthday.strftime('%Y-%m-%dT%H:%M:%S.%f%z') if member.birthday else "",
                    "PHONE": member.phone or ""
                },
                "interests": interests_dict
            }
            if member.email_id:
                subscriber_hash = hashlib.md5(member.email_address).hexdigest()
                members_url = "https://{0}.api.mailchimp.com/3.0/lists/{1}/members/{2}".format(api_key.split("-")[1], mailchimp_list.list_id, member.email_id)
                frappe.flags.integration_request = requests.patch(members_url, json=member_data, auth=auth, headers=headers)
                member_resp = frappe.flags.integration_request.json()
                frappe.db.sql("""
                    update
                        `tabContact Mailchimp`
                    set
                        email_id=%(id)s
                    where parent=%(parent)s and
                        mailchimp_list=%(mailchimp_list)s""", {
                        "id": member_resp.get("id"),
                        "parent": member.contact,
                        "mailchimp_list": member_resp.get("list_id")
                    }
                )
            else:
                # members_url = "https://{0}.api.mailchimp.com/3.0/lists/{1}/members".format(api_key.split("-")[1], mailchimp_list.list_id)
                members_url = get_members_url(api_key, mailchimp_list.list_id)
                try:
                    frappe.flags.integration_request = requests.post(members_url, json=member_data, auth=auth, headers=headers)
                    frappe.flags.integration_request.raise_for_status()
                except Exception as exc:
                    frappe.msgprint(exc)
                member_resp = frappe.flags.integration_request.json()
                frappe.db.sql("""
                    update
                        `tabMailchimp List Member`
                    set
                        email_id=%(id)s,
                        unique_email_id=%(unique)s,
                        email_client=%(client)s,
                        member_rating=%(rating)s,
                        last_changed_date=%(last)s
                    where name=%(name)s""", {
                        "id": member_resp.get("id"),
                        "unique": member_resp.get("unique_email_id"),
                        "client": member_resp.get("email_client"),
                        "rating": member_resp.get("member_rating"),
                        "last": member_resp.get("last_changed"),
                        "name": member.name
                    }
                )
                parent = frappe.db.sql("""
                    select
                        name
                    from
                        tabContact
                    where
                        email_id=%(email_address)s and
                        first_name=%(first_name)s""", {
                    "email_address": member.email_address,
                    "first_name": member.first_name
                })
                if parent:
                    frappe.db.sql("""
                        update
                            `tabContact Mailchimp`
                        set
                            email_id=%(id)s
                        where parent=%(parent)s and
                            mailchimp_list=%(mailchimp_list)s""", {
                            "id": member_resp.get("id"),
                            "parent": parent[0],
                            "mailchimp_list": member_resp.get("list_id")
                        }
                    )
                frappe.db.commit()
        frappe.db.commit()
        return frappe.msgprint(_("Successfully Updated"))
    except Exception as exc:
        frappe.log_error()
        raise exc


@frappe.whitelist(allow_guest=True)
def get_interests_dict(member):
    main_interests = {}
    category_interests = frappe.db.sql("""
        select
            interest_id
        from
            `tabMailchimp Interest`
        where
            list_id=%s""", member.list_id)
    interests = frappe.db.sql("""
        select
            interest_id
        from
            `tabContact Mailchimp`
        where
            parent=%s and
            mailchimp_list_id=%s""", (member.contact, member.list_id))
    main_interests = {i[0]: False for i in category_interests}
    for interest in interests:
        if interest[0]:
            main_interests[interest[0]] = True
    return main_interests
