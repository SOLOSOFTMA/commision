# -*- coding: utf-8 -*-
# Copyright (c) 2015, bobzz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import  date_diff,flt,cint
import math

class SalesCommision(Document):
	def get_target(self):
		sales_target = frappe.db.sql("""select target,brand from `tabSales Target` where sales = "{}" """.format(self.sales),as_dict=1)
		for da in sales_target:
			det_item = self.append("targets",{})
			det_item.brand=da['brand']
			det_item.target = da['target']

	def get_kursi_susun(self):
		special_brand = frappe.db.get_single_value('Commision Setting','brand')
		bonus_jual = flt(frappe.db.get_single_value('Commision Setting','bonus_jual'),3)
		bonus_tagih = flt(frappe.db.get_single_value('Commision Setting','bonus_tagih'),3)
		spesial_hangus = flt(frappe.db.get_single_value('Commision Setting','spesial_hangus'),3)

		komisi_jual=0
		komisi_bayar=0
		invoice = frappe.db.sql("""select si.name,si.posting_date,sit.item_code,sit.item_name,si.brand , si.sales , sit.qty, si.commision_type
			from `tabSales Invoice Item` sit
			join `tabSales Invoice`  si on si.name = sit.parent
			where si.docstatus=1 and si.brand is not null and si.commision_redeemed =0 and si.commision_type in ("Kursi susun")
			and si.posting_date < "{}" and si.sales="{}"
		 """.format(self.to_date,self.sales),as_dict=1)
		for data in invoice:
			det_item = self.append("kursi_susun_jual",{})
			det_item.inv_no = data['name']
			det_item.qty=flt(data['qty'])
			det_item.komisi = flt(data['qty'])*bonus_jual
			komisi_jual+=det_item.komisi
		

	def generate_obp(self):
		jual_hangus = flt(frappe.db.get_single_value('Commision Setting','jual_hangus'),3)

		invoice = frappe.db.sql("""select si.name,si.posting_date,sit.item_code,sit.item_name,si.brand , si.sales , sit.qty as "jumlah", sit.amount  , DATEDIFF(pe.posting_date,si.posting_date) as "days" , si.commision_type
			from `tabSales Invoice Item` sit
			left join `tabPayment Entry Reference` per on per.reference_name = sit.parent
			left join `tabPayment Entry` pe on per.parent=pe.name
			join `tabSales Invoice`  si on si.name = sit.parent
			where si.docstatus=1 and si.outstanding_amount<=0 and si.brand is not null and si.commision_redeemed =0 and si.commision_type in ("OBP")
			and si.posting_date < "{}" and si.sales="{}"
		 """.format(self.to_date,self.sales),as_dict=1)
		result_temp={}
		total_obp=0
		total_insentif=0
		total_omset_obp=0
		for inv in invoice:
			omset = self.append("omset",{})
			omset.inv_no=inv['name']
			omset.brand=inv['brand']
			omset.item_name = inv['item_name']
			omset.amount = flt(inv['amount'])
			omset.age=flt(inv['days'])
			if omset.age <=jual_hangus:
				if not omset.brand in result_temp:
					result_temp[omset.brand]=omset.amount
				else:
					result_temp[omset.brand]+=omset.amount
		target_map={}
		for t in self.targets:
			target_map[t.brand]=t.target
		for r in result_temp:
			res = self.append("obp_result",{})
			res.brand = r
			res.omset = flt(result_temp[r])
			res.netto = flt(res.omset*0.95)
			res.pencapaian = 100*(res.netto/res.omset)
			level = frappe.db.sql("""select achieve,commision from `tabOBP Matrix Item` where parent="{}" order by achieve asc """.format(r),as_list=1)
			multi=0
			for step in level:
				if step[0]<res.pencapaian:
					multi=flt(step[1])
			res.komisi = (multi/100)*res.netto
			total_obp+=res.komisi
			total_omset_obp+=res.omset

			if target_map[r]*0.9<=res.netto:
				incentive = frappe.db.sql("""select target,bonus,bonus90 from `tabTarget Matrix Item` where parent="{}" order by target asc """.format(r),as_list=1)
				for step in incentive:
					if step[0]<=target_map[r]:
						ins = self.append("insentif",{})
						ins.brand=r
						ins.target=target_map[r]
						ins.omset=res.omset
						if target_map[r]<=res.netto:
							ins.komisi = flt(step[1])
						else:
							ins.komisi = flt(step[2])
						ins.bonus=step[1]
						ins.bonus90=step[2]
						total_insentif+=ins.komisi
		self.total_obp=total_obp
		self.total_insentif=total_insentif
		self.total_omset_obp=total_omset_obp