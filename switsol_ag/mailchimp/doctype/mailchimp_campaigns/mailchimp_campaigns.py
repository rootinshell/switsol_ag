# -*- coding: utf-8 -*-
# Copyright (c) 2018, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.integrations.utils import make_get_request, make_post_request
from switsol_ag.mailchimp.doctype.mailchimp_settings.mailchimp_settings import get_auth, get_api_key, get_lists_url, get_members_url


class MailchimpCampaigns(Document):
    pass


@frappe.whitelist(allow_guest=True)
def get_mailchimp_campaign(api_key):
    auth = get_auth()
    try:
        campaigns_url = get_campaigns_url(api_key) + "/?count=1000"
        resp = make_get_request(url=campaigns_url, auth=auth)
        if resp.get("campaigns"):
            message = ""
            for i in resp.get("campaigns"):
                campaign_id = i.get("id")
                mailchimp_campaign = frappe.db.sql("""
                    select
                        name
                    from
                        `tabMailchimp Campaigns`
                    where
                        campaign_id=%s""", campaign_id)
                if not mailchimp_campaign:
                    create_mailchimp_campaign(campaign_id, i, api_key)
                    message = "Mailchimp Сampaigns have been created"
                else:
                    update_mailchimp_campaign(campaign_id, i, api_key)
                    message = "Mailchimp Сampaigns have been updated"
                frappe.db.commit()
            frappe.msgprint(_(message))
        else:
            frappe.log_error(str(resp), "Mailchimp doesn't have any Сampaigns")
    except Exception as exc:
        frappe.throw(exc)


@frappe.whitelist()
def create_mailchimp_campaign(campaign_id, i, api_key):
    auth = get_auth()
    # creating mailchimp campaign
    doc_mail_campaign = frappe.new_doc("Mailchimp Campaigns")
    doc_mail_campaign.flags.dont_sync_lists = True
    doc_mail_campaign.update({
        "campaign_id": i.get("id"),
        "web_id": i.get("web_id"),
        "type": i.get("type").title(),
        "campaign_name": i.get("name"),
        "create_time": i.get("create_time"),
        "archive_url": i.get("archive_url"),
        "long_archive_url": i.get("long_archive_url"),
        "status": i.get("status").title(),
        "emails_sent": i.get("emails_sent"),
        "send_time": i.get("send_time"),
        "content_type": i.get("content_type")
    })
    # adding mailchimp settings
    settings = i.get("settings")
    if settings:
        settings_dict = get_settings_dict(settings)
        doc_mail_campaign.append("settings", settings_dict)
    # adding mailchimp recipients
    recipient = i.get("recipients")
    if recipient:
        recipients_dict = get_recipients_dict(recipient)
        doc_mail_campaign.append("recipients", recipients_dict)
    doc_mail_campaign.insert()


@frappe.whitelist()
def update_mailchimp_campaign(campaign_id, i, api_key):
    auth = get_auth()
    # creating mailchimp campaign
    doc_mail_campaign = frappe.get_doc("Mailchimp Campaigns", {"campaign_id": campaign_id})
    doc_mail_campaign.flags.dont_sync_lists = True
    doc_mail_campaign.settings = []
    doc_mail_campaign.recipients = []
    doc_mail_campaign.web_id = i.get("web_id")
    doc_mail_campaign.type = i.get("type").title()
    doc_mail_campaign.archive_url = i.get("archive_url")
    doc_mail_campaign.long_archive_url = i.get("long_archive_url")
    doc_mail_campaign.status = i.get("status").title()
    doc_mail_campaign.emails_sent = i.get("emails_sent")
    doc_mail_campaign.send_time = i.get("send_time")
    doc_mail_campaign.content_type = i.get("content_type")
    # adding mailchimp settings
    settings = i.get("settings")
    if settings:
        settings_dict = get_settings_dict(settings)
        doc_mail_campaign.append("settings", settings_dict)
    # adding mailchimp recipients
    recipient = i.get("recipients")
    if recipient:
        recipients_dict = get_recipients_dict(recipient)
        doc_mail_campaign.append("recipients", recipients_dict)
    doc_mail_campaign.save()


@frappe.whitelist()
def get_campaigns_url(api_key):
    return "https://{0}.api.mailchimp.com/3.0/campaigns".format(api_key.split("-")[1])


@frappe.whitelist()
def get_settings_dict(settings):
    return {
        "subject_line": settings.get("subject_line"),
        "preview_text": settings.get("preview_text"),
        "title": settings.get("title"),
        "from_name": settings.get("from_name"),
        "reply_to": settings.get("reply_to"),
        "use_conversation": settings.get("use_conversation"),
        "to_name": settings.get("to_name"),
        "folder_id": settings.get("folder_id"),
        "authenticate": settings.get("authenticate"),
        "auto_footer": settings.get("auto_footer"),
        "inline_css": settings.get("inline_css"),
        "auto_tweet": settings.get("auto_tweet"),
        "auto_fb_post": settings.get("auto_fb_post"),
        "fb_comments": settings.get("fb_comments"),
        "timewarp": settings.get("timewarp"),
        "template_id": settings.get("template_id"),
        "drag_and_drop": settings.get("drag_and_drop")
    }


@frappe.whitelist()
def get_recipients_dict(recipient):
    return {
        "list_id": recipient.get("list_id"),
        "list_name": recipient.get("list_name"),
        "segment_text": recipient.get("segment_text"),
        "recipient_count": recipient.get("recipient_count")
    }
