// Copyright (c) 2016, bobzz and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Commision', {
	refresh: function(frm) {
		cur_frm.add_fetch("sales","supervisor","supervisor");
		cur_frm.add_fetch("period","to_date","to_date");
	}
});
