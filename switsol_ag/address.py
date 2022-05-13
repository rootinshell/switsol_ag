# -*- coding: utf-8 -*-
# Copyright (c) 2017, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def validate(self, method=None):
    self.pincode = self.postal_code.strip() if self.postal_code else ""
    # if self.customer and self.is_primary_address:
    #     frappe.db.set_value("Customer", self.customer, "pincode", self.postal_code)


@frappe.whitelist()
def postal_code_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT
            postal_code
        FROM
            `tabCity Postal Code`
        WHERE
            parent=%s
        AND 
            postal_code LIKE %s
        ORDER BY postal_code DESC
        LIMIT %s, %s""".format(frappe.db.escape(searchfield)), (filters.get("town"), "%{0}%".format(txt), start, page_len))


@frappe.whitelist()
def city_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT
            cp.parent
        FROM
            `tabCity Postal Code` cp
        WHERE
            cp.postal_code=%s
        ORDER BY parent DESC
        LIMIT %s, %s""".format(frappe.db.escape(searchfield)), (filters.get("postal_code"), start, page_len))


@frappe.whitelist()
def make_address(company_name):
    ad = frappe.new_doc("Address")
    ad.customer = company_name
    ad.address_title = company_name
    return ad


@frappe.whitelist()
def get_list_switsol(doctype, fields=None, filters=None, order_by=None,
    limit_start=None, limit_page_length=20, parent=None):
    '''Returns a list of records by filters, fields, ordering and limit

    :param doctype: DocType of the data to be queried
    :param fields: fields to be returned. Default is `name`
    :param filters: filter list by this dict
    :param order_by: Order by this fieldname
    :param limit_start: Start at this index
    :param limit_page_length: Number of records to be returned (default 20)'''
    return frappe.get_list(doctype, fields=fields, filters=filters, order_by=order_by,
        limit_start=limit_start, limit_page_length=limit_page_length, ignore_permissions=False)
