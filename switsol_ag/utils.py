import frappe
from frappe import _


def update_website_context(context):
    if not frappe.local.conf.get("website_context"):
        frappe.local.conf['website_context'] = {}
    frappe.local.conf['website_context'].update(context)


def get_percent_value(doc, total, percent, add_currency=False):
    total_value = getattr(doc, total)
    discount_value = getattr(doc, percent)
    if total_value and discount_value:
        value = flt(flt(total_value) * discount_value / 100, doc.precision(total))
        value = fmt_money(value)
        if add_currency:
            symbol = frappe.db.get_value("Currency", doc.currency, "symbol")
            return '{} {}'.format(symbol, value)
        return value
    return ''
