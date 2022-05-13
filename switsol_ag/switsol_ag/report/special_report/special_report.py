# Copyright (c) 2013, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _
from frappe.utils import now_datetime


def execute(filters=None):
    columns = get_column()
    data = prepare_data(filters)
    return columns, data


def get_column():
    return [
        {
            "label": _("Quotation"),
            "fieldtype": "Link",
            "fieldname": "quotation_name",
            "options": "Quotation",
            "width": 120
        },
        {
            "label": _("Quotation Transaction Date"),
            "fieldtype": "Date",
            "fieldname": "quote_date",
            "width": 140
        },
        {
            "label": _("Sales Order"),
            "fieldtype": "Link",
            "fieldname": "sales_order_name",
            "options": "Sales Order",
            "width": 120
        },
        {
            "label": _("Sales Invoice"),
            "fieldtype": "Link",
            "fieldname": "sales_invoice_name",
            "options": "Sales Invoice",
            "width": 120
        },
        {
            "label": _("Customer"),
            "fieldtype": "Link",
            "fieldname": "customer",
            "options": "Customer",
            "width": 120
        },
        {
            "label": _("Answer"),
            "fieldtype": "Data",
            "fieldname": "answer",
            "width": 180
        },
        {
            "label": _("Received Order"),
            "fieldtype": "Data",
            "fieldname": "received_order",
            "width": 180
        },
        {
            "label": _("Sales Order Status"),
            "fieldtype": "Data",
            "fieldname": "sales_order_docstatus",
            "width": 180
        },
        {
            "label": _("Ordered"),
            "fieldtype": "Data",
            "fieldname": "sales_order_status",
            "width": 180
        },
        {
            "label": _("Delivery Date"),
            "fieldtype": "Date",
            "fieldname": "sales_order_delivery_date",
            "width": 140
        },
        {
            "label": _("Approx. Delivery Date from Supplier"),
            "fieldtype": "Date",
            "fieldname": "supplier_delivery_date",
            "width": 140
        },
        {
            "label": _("Delivered"),
            "fieldtype": "Data",
            "fieldname": "delivery_docstatus",
            "width": 180
        },
        {
            "label": _("Sales Invoice Sent"),
            "fieldtype": "Data",
            "fieldname": "invoice_docstatus",
            "width": 180
        },
        {
            "label": _("Sales Invoice Status"),
            "fieldtype": "Data",
            "fieldname": "invoice_status",
            "width": 180
        },
    ]


def get_data(filters):
    return frappe.db.sql("""
        SELECT
            quotation.name AS quotation_name,
            quotation.new_transaction_date AS quote_date,
            customer.name AS customer,
            quotation.status AS quote_status,
            quotation.docstatus AS quote_docstatus
        FROM
            `tabCustomer` customer, `tabQuotation` quotation
        WHERE
            quotation.customer = customer.name
            AND quotation.docstatus = 1
            AND quotation.new_transaction_date BETWEEN %s AND %s
        ORDER BY
            quotation.name
        """, (filters.get("from_date"), filters.get("to_date")), as_dict=1)


def _get_sales_orders(filters, orders):
    return frappe.db.sql("""
        SELECT
            so.name, so.docstatus, so.status, so.customer, so.new_transaction_date, so.new_delivery_date, so.delivery_date, so.per_delivered, so.supplier_delivery_date, customer.name as customer_name
        FROM
            `tabSales Order` so, `tabCustomer` customer
        WHERE
            so.customer = customer.name
            AND so.docstatus = 1
            AND so.new_transaction_date BETWEEN %s AND %s
            AND so.name not IN (%s)
        ORDER BY
            so.name
        """ % ('%s', '%s', ', '.join(['%s'] * len(orders))), tuple([filters.get("from_date"), filters.get("to_date")] + orders), as_dict=1)


def _get_quotation_names(sales_order):
    quotation = frappe.db.sql("""
        SELECT
            si.prevdoc_docname AS name
        FROM
            `tabSales Order Item` si
        WHERE
            si.parent=%s""", sales_order, as_dict=1)
    if quotation:
        quotation_details = frappe.db.sql("""
            SELECT
                quotation.name AS quotation_name,
                quotation.new_transaction_date AS quote_date,
                quotation.status AS quote_status,
                quotation.docstatus AS quote_docstatus
            FROM
                `tabQuotation` quotation
            WHERE
                quotation.name=%s
            """, quotation[0].name, as_dict=1)
        return quotation_details


def _get_sales_order_rows(filters, orders):
    data = []
    sales_orders = _get_sales_orders(filters, orders)
    for i in sales_orders:
        sales_order_docstatus = _("Yes") if i.docstatus == 1 else _("No")
        answer = _("Yes")
        sales_order_status = _("Yes") if i.new_delivery_date or i.delivery_date else _("No")
        sales_order_delivery_date = i.new_delivery_date or i.delivery_date
        sales_order_supplier_delivery = i.supplier_delivery_date
        delivery_docstatus = _("Yes") if i.per_delivered != 0 else _("No")
        invoice = get_sales_invoice(i.customer, i.name)
        invoice_docstatus = _("No")
        invoice_status = _("No")
        sales_invoice_name = ""
        if invoice:
            invoice_docstatus = _("Yes") if invoice[0].docstatus == 1 else _("No")
            invoice_status = _("Yes") if invoice[0].status == "Paid" else _("No")
            sales_invoice_name = invoice[0].name

        row = [
            "",
            i.new_transaction_date,
            i.name,
            sales_invoice_name,
            i.customer_name,
            answer,
            _("Yes"),
            sales_order_docstatus,
            sales_order_status,
            sales_order_delivery_date,
            sales_order_supplier_delivery,
            delivery_docstatus,
            invoice_docstatus,
            invoice_status
        ]
        data.append(row)
    return data


def prepare_data(filters):
    data = []
    customers = get_data(filters)
    orders = [""]
    invoices = [""]
    for d in customers:
        answer = _("Yes")
        if d.quote_status in ("Submitted", "Replied"):
            today = now_datetime().date()
            answer = _("No")
            if (today - d.quote_date).days >= 14:
                answer = _("Repeat")
        order = get_sales_order(d.customer, d.quotation_name)
        received_order = _("Yes") if order else _("No")
        sales_order_status = _("No")
        sales_order_docstatus = _("No")
        delivery_docstatus = _("No")
        sales_order_name = ""
        sales_order_delivery_date = ""
        sales_order_supplier_delivery = ""
        if order:
            orders.append(order[0].name)
            sales_order_name = order[0].name
            sales_order_status = _("Yes") if order[0].new_delivery_date else _("No")
            sales_order_docstatus = _("Yes") if order[0].docstatus == 1 else _("No")
            delivery_docstatus = _("Yes") if order[0].per_delivered != 0 else _("No")
            sales_order_delivery_date = order[0].new_delivery_date if order else ""
            sales_order_supplier_delivery = order[0].supplier_delivery_date if order else ""
        invoice = ""
        if order:
            invoice = get_sales_invoice(d.customer, order[0].name)
        invoice_docstatus = _("No")
        invoice_status = _("No")
        sales_invoice_name = ""
        if invoice:
            invoice_docstatus = _("Yes") if invoice[0].docstatus == 1 else _("No")
            invoice_status = _("Yes") if invoice[0].status == "Paid" else _("No")
            sales_invoice_name = invoice[0].name
            invoices.append(invoice[0].name)

        row = [
            d.quotation_name,
            d.quote_date,
            sales_order_name,
            sales_invoice_name,
            d.customer,
            answer,
            received_order,
            sales_order_docstatus,
            sales_order_status,
            sales_order_delivery_date,
            sales_order_supplier_delivery,
            delivery_docstatus,
            invoice_docstatus,
            invoice_status
        ]
        data.append(row)
    sales_orders_rows = _get_sales_order_rows(filters, orders)
    data.extend(sales_orders_rows)
    sales_invoices_rows = _get_sales_invoices_rows(filters, orders)
    data.extend(sales_invoices_rows)
    return data


def get_sales_order(customer, quote):
    return frappe.db.sql("""SELECT si.parent,
        so.name, so.docstatus, so.status, so.new_delivery_date, so.per_delivered, so.supplier_delivery_date
        FROM `tabSales Order` so, `tabSales Order Item` si
        WHERE
            so.customer=%s
            AND si.prevdoc_docname=%s
            AND so.name=si.parent
        ORDER BY so.creation DESC""", (customer, quote), as_dict=1)


def get_sales_invoice(customer, sales_order):
    return frappe.db.sql("""SELECT sii.parent,
        si.name, si.docstatus, si.status
        FROM `tabSales Invoice` si, `tabSales Invoice Item` sii
        WHERE
            si.customer=%s
            AND sii.sales_order=%s
            AND si.name=sii.parent""", (customer, sales_order), as_dict=1)


def get_delivery_note(customer, sales_order):
    return frappe.db.sql("""SELECT dn.parent
        FROM `tabDelivery Note` dn, `tabDelivery Note Item` dni
        WHERE
            dn.customer=%s
            AND dni.against_sales_order=%s
            AND dn.name=dni.parent""", (customer, sales_order), as_dict=1)


def _get_sales_invoices(filters, invoices):
    return frappe.db.sql("""
        SELECT
            si.name, si.docstatus, si.status, si.customer, customer.name as customer_name
        FROM
            `tabSales Invoice` si, `tabCustomer` customer
        WHERE
            si.customer = customer.name
            AND si.posting_date BETWEEN %s AND %s
            AND si.name not IN (%s)
        ORDER BY
            si.name
        """ % ('%s', '%s', ', '.join(['%s'] * len(invoices))), tuple([filters.get("from_date"), filters.get("to_date")] + invoices), as_dict=1)


def _get_sales_invoices_rows(filters, invoices):
    data = []
    sales_invoices = _get_sales_invoices(filters, invoices)
    for i in sales_invoices:
        invoice_docstatus = _("Yes") if i.docstatus == 1 else _("No")
        invoice_status = _("Yes") if i.status == "Paid" else _("No")

        row = [
            "",
            "",
            "",
            i.name,
            i.customer_name,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            invoice_docstatus,
            invoice_status
        ]
        data.append(row)
    return data
