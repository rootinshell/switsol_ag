# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from mailchimp.doctype.mailchimp_settings.mailchimp_settings import get_api_key, get_data


def daily():
	api_key = get_api_key()
	if api_key:
		get_data(api_key)
