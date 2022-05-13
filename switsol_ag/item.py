# Copyright (c) 2017, Switsol AG and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _


def validate(self, method=None):
	item_price = frappe.db.sql("""
		SELECT
			name,
			price_list_rate
		FROM
			`tabItem Price`
		WHERE
			item_code=%s
			AND selling=1""", self.name, as_dict=1)
	if item_price:
		if item_price[0].price_list_rate != self.standard_rate:
			frappe.db.sql("""
				UPDATE
					`tabItem Price`
				SET
					price_list_rate=%s
				WHERE
					name=%s""",(self.standard_rate, item_price[0].name))
