# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt"


from __future__ import unicode_literals
import frappe

def boot_session(bootinfo):
	sales = frappe.db.sql("""select name from `tabSales` where user="{}" """.format(frappe.session['user']),as_dict=1)
	for row in sales:
		frappe.session['sales']=row['name']
		bootinfo.sysdefaults.sales=row['name']
