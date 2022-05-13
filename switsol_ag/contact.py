# Copyright (c) 2017, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import hashlib
from frappe import _
from mailchimp.doctype.mailchimp_settings.mailchimp_settings import get_auth, get_api_key
from mailchimp.doctype.mailchimp_lists.mailchimp_lists import update_data


def validate(self, method=None):
    if self.first_name:
        self.first_name = self.first_name.strip()
    if self.last_name:
        self.last_name = self.last_name.strip()


def on_update(self, method=None):
    if self.flags.dont_sync_lists: return
    if self.mailchimp_lists:
        mailchimp_lists = []
        for mailchimp in self.mailchimp_lists:
            if mailchimp.group_name and not mailchimp.interest:
                frappe.throw(_("You should add Group Interest"))
            if not mailchimp.group_name and mailchimp.interest:
                frappe.throw(_("You should add Group"))
            if mailchimp.mailchimp_list not in mailchimp_lists:
                member_name = frappe.db.sql("""
                    SELECT
                        name
                    FROM
                        `tabMailchimp List Member`
                    WHERE
                        contact=%s AND
                        list_id=%s""", (self.name, mailchimp.mailchimp_list_id))
                if not member_name:
                    doc_mail_list = frappe.get_doc("Mailchimp Lists", mailchimp.mailchimp_list)
                    doc_mail_list.append("members", {
                        "contact": self.name,
                        "email_address": self.email_id,
                        "phone": self.phone,
                        "list_id": mailchimp.mailchimp_list_id,
                        "status": "Subscribed" if mailchimp.subscribed==1 else "Unsubscribed",
                        "first_name": self.first_name,
                        "last_name": self.last_name,
                        "birthday": self.contact_birthday
                    })
                    doc_mail_list.save()
                else:
                    member_name = frappe.db.sql("""
                        SELECT
                            name
                        FROM
                            `tabMailchimp List Member`
                        WHERE
                            contact=%s AND
                            list_id=%s""", (self.name, mailchimp.mailchimp_list_id), as_dict=1)
                    if member_name:
                        mailchimp_member = frappe.get_doc("Mailchimp List Member", member_name[0].name)
                        mailchimp_member.last_name = self.last_name
                        mailchimp_member.first_name = self.first_name
                        mailchimp_member.email_address = self.email_id
                        mailchimp_member.status = "Subscribed" if mailchimp.subscribed==1 else "Unsubscribed"
                        mailchimp_member.phone = self.phone
                        mailchimp_member.birthday = self.contact_birthday
                        mailchimp_member.save()
                        frappe.db.commit()
                    doc_mail_list = frappe.get_doc("Mailchimp Lists", mailchimp.mailchimp_list)
                    doc_mail_list.save()
                mailchimp_lists.append(mailchimp.mailchimp_list)
            frappe.db.commit()
