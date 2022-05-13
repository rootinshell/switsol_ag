# -*- coding: utf-8 -*-
# Copyright (c) 2018, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import hashlib
from frappe.model.document import Document
from frappe import _
from frappe.integrations.utils import make_get_request, make_post_request
from frappe.utils import getdate
from frappe.utils.data import format_datetime


class MailchimpSettings(Document):
    pass


@frappe.whitelist(allow_guest=True)
def get_data(api_key):
    auth = get_auth()
    try:
        lists_url = get_lists_url(api_key) + "/?count=1000"
        resp = make_get_request(url=lists_url, auth=auth)
        if resp.get("lists"):
            message = ""
            for i in resp.get("lists"):
                list_id = i.get("id")
                mailchimp_list = frappe.db.sql("""
                    select
                        name
                    from
                        `tabMailchimp Lists`
                    where
                        list_id=%s""", list_id)
                if not mailchimp_list:
                    create_mailchimp_list(list_id, i, api_key)
                    message = "Mailchimp Lists have been created"
                else:
                    update_mailchimp_list(list_id, i, api_key)
                    message = "Mailchimp Lists have been updated"
                frappe.db.commit()
            frappe.msgprint(_(message))
            from switsol_ag.mailchimp.doctype.mailchimp_campaigns.mailchimp_campaigns import get_mailchimp_campaign
            get_mailchimp_campaign(api_key)
        else:
            frappe.log_error(str(resp), "Mailchimp doesn't have any Lists")
    except Exception as exc:
        frappe.throw(exc)
        # frappe.throw(_("Seems API Key is wrong !!!"))


@frappe.whitelist()
def create_mailchimp_list(list_id, i, api_key):
    auth = get_auth()
    # creating mailchimp list
    doc_mail_list = frappe.new_doc("Mailchimp Lists")
    doc_mail_list.flags.dont_sync_lists = True
    doc_mail_list.update({
        "list_id": i.get("id"),
        "web_id": i.get("web_id"),
        "list_name": i.get("name"),
        "double_optin": 1 if i.get("double_optin")==True else 0,
        "permission_reminder": i.get("permission_reminder"),
        "use_archive_bar": 1 if i.get("use_archive_bar")==True else 0,
        "notify_on_subscribe": i.get("notify_on_subscribe"),
        "notify_on_unsubscribe": i.get("notify_on_unsubscribe"),
        "date_created": i.get("date_created"),
        "list_rating": i.get("list_rating"),
        "email_type_option": 1 if i.get("email_type_option")==True else 0,
        "subscribe_url_short": i.get("subscribe_url_short"),
        "subscribe_url_long": i.get("subscribe_url_long"),
        "beamer_address": i.get("beamer_address"),
        "visibility": "Public" if i.get("visibility")=="pub" else "Private",
        "total_items": i.get("total_items")
    })
    # adding mailchimp contact
    contact = i.get("contact")
    if contact:
        contact_dict = get_contact_dict(contact)
        doc_mail_list.append("contacts", contact_dict)
    # adding mailchimp campaign
    campain = i.get("campaign_defaults")
    if campain:
        campain_dict = get_campain_dict(campain)
        doc_mail_list.append("campaign_defaults", campain_dict)
    doc_mail_list.insert()
    # adding interests
    interests_url = get_interests_url(api_key, list_id) + "/?count=1000"
    group_resp = make_get_request(url=interests_url, auth=auth)
    groups = []
    if group_resp.get("categories"):
        for group in group_resp.get("categories"):
            doc_mail_list.append("interests", {
                "interest": group.get("title"),
                "category_id": group.get("id"),
                "display_order": group.get("display_order"),
                "display_type": group.get("type").title()
            })
            name = frappe.db.sql("""
                select
                    name
                from
                    `tabInterest Category`
                where
                    list_id=%s and
                    category_id=%s""", (i.get("id"), group.get("id")))
            if name:
                doc_interest = frappe.get_doc("Interest Category", name[0][0])
                doc_interest.group_name = group.get("title")
                doc_interest.display_order = group.get("display_order")
                doc_interest.display_type = group.get("type").title()
                doc_interest.save()
            else:
                create_interest(doc_mail_list.name, group)
            groups.append(group.get("id"))
    members_url = get_members_url(api_key, list_id) + "/?count=1000"
    resp = make_get_request(url=members_url, auth=auth)
    for member in resp.get("members"):
        contact = get_contact_name(member)
        member_dict = get_member_dict(member, contact)
        doc_mail_list.append("members", member_dict)
        if contact:
            update_contact(member, doc_mail_list.list_name, contact, groups)


@frappe.whitelist()
def update_mailchimp_list(list_id, i, api_key):
    auth = get_auth()
    doc_mail_list = frappe.get_doc("Mailchimp Lists", {"list_id": list_id})
    doc_mail_list.flags.dont_sync_lists = True
    doc_mail_list.contacts = []
    doc_mail_list.members = []
    doc_mail_list.interests = []
    doc_mail_list.campaign_defaults = []
    doc_mail_list.web_id = i.get("web_id")
    doc_mail_list.list_name = i.get("name")
    doc_mail_list.double_optin = 1 if i.get("double_optin")==True else 0
    doc_mail_list.permission_reminder = i.get("permission_reminder")
    doc_mail_list.use_archive_bar = 1 if i.get("use_archive_bar")==True else 0
    doc_mail_list.notify_on_subscribe = i.get("notify_on_subscribe")
    doc_mail_list.notify_on_unsubscribe = i.get("notify_on_unsubscribe")
    doc_mail_list.date_created = i.get("date_created")
    doc_mail_list.list_rating = i.get("list_rating")
    doc_mail_list.email_type_option = 1 if i.get("email_type_option")==True else 0
    doc_mail_list.subscribe_url_short = i.get("subscribe_url_short")
    doc_mail_list.subscribe_url_long = i.get("subscribe_url_long")
    doc_mail_list.beamer_address = i.get("beamer_address")
    doc_mail_list.visibility = "Public" if i.get("visibility")=="pub" else "Private"
    doc_mail_list.total_items = i.get("total_items")
    contact = i.get("contact")
    if contact:
        contact_dict = get_contact_dict(contact)
        doc_mail_list.append("contacts", contact_dict)
    campain = i.get("campaign_defaults")
    if campain:
        campain_dict = get_campain_dict(campain)
        doc_mail_list.append("campaign_defaults", campain_dict)
    interests_url = get_interests_url(api_key, list_id) + "/?count=1000"
    group_resp = make_get_request(url=interests_url, auth=auth)
    groups = []
    if group_resp.get("categories"):
        for group in group_resp.get("categories"):
            doc_mail_list.append("interests", {
                "interest": group.get("title"),
                "category_id": group.get("id"),
                "display_order": group.get("display_order"),
                "display_type": group.get("type").title()
            })
            name = frappe.db.sql("""select name from `tabInterest Category`
                where
                    list_id=%s and
                    category_id=%s""", (i.get("id"), group.get("id")))
            if name:
                doc_interest = frappe.get_doc("Interest Category", name[0][0])
                doc_interest.group_name = group.get("title")
                doc_interest.display_order = group.get("display_order")
                doc_interest.display_type = group.get("type").title()
                doc_interest.save()
            else:
                create_interest(doc_mail_list.name, group)
            groups.append(group.get("id"))
    members_url = get_members_url(api_key, list_id) + "/?count=1000"
    resp = make_get_request(url=members_url, auth=auth)
    for member in resp.get("members"):
        contact = get_contact_name(member)
        member_dict = get_member_dict(member, contact)
        doc_mail_list.append("members", member_dict)
        if contact:
            update_contact(member, doc_mail_list.list_name, contact, groups)
    doc_mail_list.save()


@frappe.whitelist()
def get_contact_name(member):
    return frappe.db.sql("""
        select
            name
        from
            tabContact
        where
            email_id=%s and
            first_name=%s and
            last_name=%s""", (
        member.get("email_address"),
        member.get("merge_fields").get("FNAME"),
        member.get("merge_fields").get("LNAME")))


@frappe.whitelist()
def update_contact(member, list_name, contact, groups):
    api_key = get_api_key()
    doc_contact = frappe.get_doc("Contact", contact[0][0])
    doc_contact.flags.dont_sync_lists = True
    doc_contact.mailchimp_lists = []
    doc_contact.phone = member.get("merge_fields").get("PHONE")
    doc_contact.birthday = getdate(member.get("merge_fields").get("BIRTHDAY"))
    interests = member.get("interests")
    mailchimp_list_names = []
    if interests:
        interests_name = [name for name, interest in interests.iteritems() if interest]
        if interests_name:
            for inter_name in interests_name:
                group = frappe.db.sql("""
                    select
                        name, category_id, category_name
                    from
                        `tabMailchimp Interest`
                    where
                        interest_id=%s""", inter_name, as_dict=1)
                if group:
                    doc_contact.append("mailchimp_lists", {
                        "mailchimp_list": list_name,
                        "mailchimp_list_id": member.get("list_id"),
                        "category_id": group[0].category_id,
                        "group_name": group[0].category_name,
                        "interest": group[0].name,
                        "interest_id": inter_name,
                        "email_id": member.get("id"),
                        "subscribed": 1 if member.get("status")=="subscribed" else 0
                    })
                    mailchimp_list_names.append(list_name)
                else:
                    for category in groups:
                        interests_url = "https://{0}.api.mailchimp.com/3.0/lists/{1}/interest-categories/{2}/interests/{3}/?count=1000".format(api_key.split("-")[1], member.get("list_id"), category, name)
                        headers = {}
                        auth = get_auth()
                        try:
                            group_resp = make_get_request(url=interests_url, auth=auth)
                            interest = create_mailchimp_interest(member.get("list_id"), group_resp)
                            group_name = get_group_name(category)[0][0]
                            doc_contact.append("mailchimp_lists", {
                                "mailchimp_list": list_name,
                                "mailchimp_list_id": member.get("list_id"),
                                "group_name": group_name,
                                "category_id": category,
                                "interest": interest,
                                "interest_id": group_resp.get("id"),
                                "email_id": member.get("id"),
                                "subscribed": 1 if member.get("status")=="subscribed" else 0
                            })
                        except Exception as exc:
                            continue
        else:
            if list_name not in mailchimp_list_names:
                doc_contact.append("mailchimp_lists", {
                    "mailchimp_list": list_name,
                    "mailchimp_list_id": member.get("list_id"),
                    "email_id": member.get("id"),
                    "subscribed": 1 if member.get("status")=="subscribed" else 0
                })
                mailchimp_list_names.append(list_name)
    else:
        doc_contact.append("mailchimp_lists", {
            "mailchimp_list_id": member.get("list_id"),
            "mailchimp_list": list_name,
            "email_id": member.get("id"),
            "subscribed": 1 if member.get("status")=="subscribed" else 0
        })
    message = add_member_activity(member, doc_contact.name)
    if message:
        doc_contact.add_comment("Comment", message)
    doc_contact.save()


@frappe.whitelist()
def create_interest(list_name, group):
    doc_interest = frappe.new_doc("Interest Category")
    doc_interest.update({
        "list_name": list_name,
        "list_id": group.get("list_id"),
        "group_name": group.get("title"),
        "category_id": group.get("id"),
        "display_order": group.get("display_order"),
        "display_type": group.get("type").title()
    })
    doc_interest.insert()
    frappe.db.commit()
    api_key = get_api_key()
    headers = {}
    auth = get_auth()
    interests_url = "https://{0}.api.mailchimp.com/3.0/lists/{1}/interest-categories/{2}/interests/?count=1000".format(api_key.split("-")[1], group.get("list_id"), group.get("id"))
    group_resp = make_get_request(url=interests_url, auth=auth)
    if group_resp.get("interests"):
        for group in group_resp.get("interests"):
            create_mailchimp_interest(group.get("list_id"), group)


@frappe.whitelist()
def create_mailchimp_interest(list_id, group_resp):
    interest = frappe.db.sql("""
        select
            name
        from
            `tabMailchimp Interest`
        where
            interest_id=%s""", group_resp.get("id"))
    category = frappe.db.sql("""
        select
            name
        from
            `tabInterest Category`
        where
            category_id=%s""", group_resp.get("category_id"))
    if not interest:
        doc_mail_interest = frappe.new_doc("Mailchimp Interest")
        doc_mail_interest.update({
            "list_id": group_resp.get("list_id"),
            "list_name": get_list_name(group_resp.get("list_id"))[0][0],
            "category_name": category[0][0],
            "category_id": group_resp.get("category_id"),
            "interest_id": group_resp.get("id"),
            "interest_name": group_resp.get("name"),
            "subscriber_count": group_resp.get("subscriber_count"),
            "display_order": group_resp.get("display_order")
        })
        doc_mail_interest.insert()
    else:
        doc_mail_interest = frappe.get_doc("Mailchimp Interest", interest[0][0])
        doc_mail_interest.interest_name = group_resp.get("name")
        doc_mail_interest.subscriber_count = group_resp.get("subscriber_count")
        doc_mail_interest.display_order = group_resp.get("display_order")
        doc_mail_interest.save()
    frappe.db.commit()
    return doc_mail_interest.name


@frappe.whitelist()
def add_member_activity(member, contact):
    api_key = get_api_key()
    auth = get_auth()
    message = ""
    try:
        subscriber_hash = hashlib.md5(member.get("email_address")).hexdigest()
        activity_url = "https://{0}.api.mailchimp.com/3.0/lists/{1}/members/{2}/activity/?count=1000".format(api_key.split("-")[1], member.get("list_id"), subscriber_hash)
        resp = make_get_request(url=activity_url, auth=auth)
        if resp.get("activity"):
            for i in resp.get("activity"):
                campaign_url = get_campaigns_url(api_key, i.get("campaign_id"))
                campaign_resp = make_get_request(url=campaign_url, auth=auth)
                member_activity = frappe.db.sql("""
                    select
                        name
                    from
                        `tabMailchimp Member Activity`
                    where
                        campaign_id=%s and
                        list_id=%s and
                        contact=%s""", (i.get("campaign_id"), member.get("list_id"), contact))
                if member_activity:
                    doc_member_activity = frappe.get_doc("Mailchimp Member Activity", member_activity[0][0])
                    doc_member_activity.action = i.get("action")
                    doc_member_activity.save()
                else:
                    if campaign_resp.get("status")== "sent":
                        campain_name = '<a href = "' + campaign_resp.get("archive_url") + '">' + i.get("title") + '</a>'
                        message = "Newsletter von Kampagne {0} wurde am {1} gesendet".format(campain_name, format_datetime(campaign_resp.get("send_time")))
                    doc_member_activity = frappe.new_doc("Mailchimp Member Activity")
                    doc_member_activity.update({
                        "contact": contact,
                        "email_id": member.get("email_address"),
                        # "action": i.get("action"),
                        "action": campaign_resp.get("status") or i.get("action"),
                        "timestamp": i.get("timestamp"),
                        "type": i.get("type"),
                        "campaign_id": i.get("campaign_id"),
                        "title": i.get("title"),
                        "url": i.get("url"),
                        "parent_campaign": i.get("parent_campaign"),
                        "list_id": member.get("list_id")
                    })
                    doc_member_activity.insert()
                    frappe.db.commit()
                    return message
    except Exception as exc:
        frappe.throw(exc)


@frappe.whitelist()
def get_contact_dict(contact):
    return {
        "company": contact.get("company"),
        "address1": contact.get("address1"),
        "address2": contact.get("address2"),
        "city": contact.get("city"),
        "state": contact.get("state"),
        "zip": contact.get("zip"),
        "country": frappe.db.get_value("Country", {"code": contact.get("country").lower()}, "name"),
        "phone": contact.get("phone")
    }


@frappe.whitelist()
def get_group_name(category):
    return frappe.db.sql("""
        select
            name
        from
            `tabInterest Category`
        where
            category_id=%s""", category)


@frappe.whitelist()
def get_list_name(list_id):
    return frappe.db.sql("""
        select
            name
        from
            `tabMailchimp Lists`
        where
            list_id=%s""", list_id)


@frappe.whitelist()
def get_campain_dict(campain):
    return {
        "from_email": campain.get("from_email"),
        "from_name": campain.get("from_name"),
        "language": campain.get("language"),
        "subject": campain.get("subject")
    }


@frappe.whitelist()
def get_member_dict(member, contact):
    return {
        "contact": contact[0][0] if contact else "",
        "email_address": member.get("email_address"),
        "email_client": member.get("email_client"),
        "email_type": member.get("email_type"),
        "email_id": member.get("id"),
        "ip_opt": member.get("ip_opt"),
        "ip_signup": member.get("ip_signup"),
        "language": member.get("language"),
        "last_changed_date": member.get("last_changed"),
        "list_id": member.get("list_id"),
        "status": member.get("status").title(),
        "vip": 1 if member.get("vip")==True else 0,
        "unique_email_id": member.get("unique_email_id"),
        "timestamp_opt": member.get("timestamp_opt"),
        "timestamp_signup": member.get("timestamp_signup"),
        "member_rating": member.get("member_rating"),
        "unsubscribe_reason": member.get("unsubscribe_reason"),
        "first_name": member.get("merge_fields").get("FNAME"),
        "last_name": member.get("merge_fields").get("LNAME"),
        "phone": member.get("merge_fields").get("PHONE"),
        "birthday": getdate(member.get("merge_fields").get("BIRTHDAY"))
    }


@frappe.whitelist()
def get_lists_url(api_key):
    return "https://{0}.api.mailchimp.com/3.0/lists".format(api_key.split("-")[1])


@frappe.whitelist()
def get_members_url(api_key, list_id):
    return "https://{0}.api.mailchimp.com/3.0/lists/{1}/members".format(api_key.split("-")[1], list_id)


@frappe.whitelist()
def get_interests_url(api_key, list_id):
    return "https://{0}.api.mailchimp.com/3.0/lists/{1}/interest-categories".format(api_key.split("-")[1], list_id)


@frappe.whitelist()
def get_campaigns_url(api_key, campaign_id):
    return "https://{0}.api.mailchimp.com/3.0/campaigns/{1}".format(api_key.split("-")[1], campaign_id)


@frappe.whitelist()
def get_auth():
    api_key = get_api_key()
    return ("Authorization", api_key)


@frappe.whitelist()
def get_api_key():
    return frappe.db.get_value("Mailchimp Settings", "Mailchimp Settings", "api_key")
