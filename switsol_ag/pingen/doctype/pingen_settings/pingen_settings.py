# -*- coding: utf-8 -*-
# Copyright (c) 2018, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_request_session
from frappe import _
from frappe.utils.file_manager import save_file

from frappe import _


class PingenSettings(Document):
    pass


def get_documents():
    token = get_token()
    auth = ''
    headers = {}
    if token:
        url = 'https://api.pingen.com/document/list/' + token
        s = get_request_session()
        frappe.flags.integration_request = s.get(url, data={}, auth=auth, headers=headers)
        frappe.flags.integration_request.raise_for_status()
        documents = frappe.flags.integration_request.json()
        for document in documents.get("items"):
            pingen_doc = frappe.new_doc("Pingen Object")
            pingen_doc.update({
                "id": int(document.get("id")),
                "filename": document.get("filename"),
                "date": document.get("date"),
                "user_id": int(document.get("user_id")),
                "address": document.get("address"),
                "country": document.get("country"),
                "size": int(document.get("size")),
                "pages": int(document.get("pages")),
                "rightaddress": int(document.get("rightaddress")),
                "status": int(document.get("status")),
                "sent": int(document.get("sent")),
                "fileremoved": int(document.get("fileremoved")),
                "requirement_failure": int(document.get("requirement_failure"))
            })
            pingen_doc.insert()
        frappe.db.commit()


@frappe.whitelist()
def check_pingen(doc_name):
    pingen_document = frappe.db.sql("""
        select
            name
        from
            `tabFile`
        where
            attached_to_name=%s""", doc_name)
    if pingen_document:
        return True


@frappe.whitelist()
def upload_document(doc_type, doc_name):
    token = get_token()
    auth = ''
    headers = {}
    si_doc = frappe.get_doc(doc_type, doc_name)
    attachment = frappe.attach_print(si_doc.doctype, si_doc.name, file_name=si_doc.name, print_format="Pingen SI")
    file_data = save_file(attachment['fname'], attachment['fcontent'], si_doc.doctype, si_doc.name)
    frappe.db.commit()
    if token:
        # url = 'https://stage-api.pingen.com/document/upload/token/63e25e8098cba87f8dae316d42c960d7/'
        url = 'https://api.pingen.com/document/upload/' + token
        from frappe.utils.file_manager import get_file_path
        filename = get_file_path(file_data.name)
        data = get_data_settings()
        files = {
            "file": (filename, open(filename, 'rb'), "multipart/form-data")
        }
        s = get_request_session()
        frappe.flags.integration_request = s.post(url, data=data, files=files, auth=auth, headers=headers)
        frappe.flags.integration_request.raise_for_status()
        documents = frappe.flags.integration_request.json()
        message = _("{} was added to Pingen".format(file_data.file_name))
        si_doc.add_comment("Comment", message)
        si_doc.save()
        return data


def get_token():
    token = frappe.db.get_value("Pingen Settings", "Pingen Settings", "api_token")
    if token:
        return 'token/' + token


def get_data_settings():
    settings = frappe.db.get_value("Pingen Settings", "Pingen Settings", ["send", "speed", "color", "duplex", "rightaddress"], as_dict=1)
    color = 0
    if settings.color == "Color":
        color = 1
    elif settings.color == "Mixed":
        color = 2
    return {
        "send": "true" if int(settings.send) else "false",
        "speed": 1 if settings.speed == "Priority" else 2,
        "color": color,
        "duplex": 0 if settings.duplex == "Simplex" else 1,
        "rightaddress": 0 if settings.rightaddress == "Address left" else 1
    }
