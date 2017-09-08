# -*- coding: utf-8 -*-
# Copyright (c) 2015, bobzz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import  date_diff,flt,cint
import math

class SalesCommision(Document):
	def on_submit(self):
		#inv in kupon commision redeeed
		inv_list=""
		for row in kupon_list:
			if inv_list=="":
				inv_list=""" "{}" """.format(row.inv_no)
			else:
				inv_list="""{},"{}" """.format(inv_list,row.inv_no)
		frappe.db.sql("""update `tabSales Invoice` set commision_redeemed =1 where name IN ({}) """.format(inv_list),as_list=1)
		
		#payemnt entry reference di kursi susun tertagih*
		frappe.db.sql("""update `tabPayment Entry Reference` set commision_redeemed=1 where name IN ({}) """.format(self.kursi_susun_tertagih),as_list=1)
		#inv di obp
		inv_list=""
		for row in omset:
			if inv_list=="":
				inv_list=""" "{}" """.format(row.inv_no)
			else:
				inv_list="""{},"{}" """.format(inv_list,row.inv_no)
		frappe.db.sql("""update `tabSales Invoice` set commision_redeemed =1 where name IN ({}) """.format(inv_list),as_list=1)
		#inv di insentif bonus*
		frappe.db.sql("""update `tabSales Invoice` set insentif_redeemed=1 where name IN ({}) """.format(self.insentif_redeemed),as_list=1)
		#inv di kursi susun jual
		inv_list=""
		for row in kursi_susun_jual:
			if inv_list=="":
				inv_list=""" "{}" """.format(row.inv_no)
			else:
				inv_list="""{},"{}" """.format(inv_list,row.inv_no)
		frappe.db.sql("""update `tabSales Invoice` set commision_redeemed =1 where name IN ({}) """.format(inv_list),as_list=1)
		#pr commision redeemed untuk komisi tagih*
		frappe.db.sql("""update `tabPayment Entry Reference` set commision_redeemed=1 where name IN ({}) """.format(self.komisi_tagih_payment_list),as_list=1)
		
	def get_target(self):
		sales_target = frappe.db.sql("""select target,brand from `tabSales Target` where sales = "{}" """.format(self.sales),as_dict=1)
		for da in sales_target:
			det_item = self.append("targets",{})
			det_item.brand=da['brand']
			det_item.target = da['target']
	def get_payment_list(self):
		payment_data = frappe.db.sql("""select (pr.allocated_amount-pr.discount_accumulated) as "payment",
			DATEDIFF(pe.posting_date,si.posting_date) as 'days' , si.name as "invoice" , pr.name as "rname"
			from `tabPayment Entry Reference` pr 
			join `tabPayment Entry` pe on pr.parent=pe.name
			left join `tabSales Invoice` si on pr.reference_name = si.name
			where pr.reference_doctype="Sales Invoice" and si.commision_type="OBP" and pe.docstatus=1 and pr.commision_redeemed=0 and pr.sales="{}" and pe.posting_date < "{}"
		""".format(self.sales,self.to_date),as_dict=1)
		komisi_tagih = frappe.db.sql("""select days,commision from `tabKomisi Tagih` order by days asc""",as_dict=1)
		total_komisi_tagih=0
		pr_list=""
		for p in payment_data:
			det_item = self.append("payment_list",{})
			det_item.inv_no = p['invoice']
			det_item.age =p['days']
			det_item.payment =p['payment']
			if pr_list=="":
				pr_list=""" "{}" """.format(p['rname'])
			elif not p['rname'] in pr_list:
				pr_list=""" {},"{}" """.format(pr_list,p['rname'])
			lc=0
			komisi=0
			for kt in komisi_tagih:
				if kt['days']>p['days']:
					komisi= flt(kt['commision'])*flt(p['payment'],3)/100
					lc=-1
					break
				lc = flt(kt['commision'],3)
			#give the last tier of commision
			if lc >-1:
				komisi=lc*flt(p['payment'],3)/100
			det_item.komisi = komisi
			total_komisi_tagih+=komisi
		self.komisi_tagih_payment_list=pr_list
		self.total_komisi_tagih=total_komisi_tagih
		self.grand_total=self.total_komisi_tagih+self.total_insentif+self.total_kupon+self.total_special_brand+self.total_obp
	def get_kupon(self):
		invoice_kupon = frappe.db.sql("""select sit.kupon_bonus as 'bonus',si.name
		from `tabSales Invoice Item` sit
		join `tabSales Invoice` si on sit.parent=si.name
		where si.docstatus=1 and si.commision_type="Kupon" and si.sales="{}" and si.commision_redeemed =0 and si.posting_date<"{}" 
		""".format(self.sales,self.to_date),as_dict=1)
		total_kupon=0
		for row_kupon in invoice_kupon:
			det_item = self.append("kupon_list",{})
			det_item.inv_no = row_kupon['name']
			det_item.komisi = flt(row_kupon['bonus'])
			total_kupon+=flt(row_kupon['bonus'])
		self.total_kupon=total_kupon
		self.grand_total=self.total_komisi_tagih+self.total_insentif+self.total_kupon+self.total_special_brand+self.total_obp

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

		payment = frappe.db.sql("""select p.name as "idx",si.sales, si.name,si.customer_name,DATEDIFF(pe.posting_date,si.posting_date) as "days",p.allocated_amount as "payment"
			from `tabPayment Entry Reference` p
			join `tabSales Invoice` si on p.reference_name = si.name
			join `tabPayment Entry` pe on pe.name = p.parent
			where p.reference_doctype="Sales Invoice" and p.commision_redeemed=0 and si.commision_type="Kursi susun"
			and si.posting_date < "{}" and p.sales = "{}" and si.outstanding_amount<=0
			 """.format(self.to_date,self.sales),as_dict=1)
		invoice_with_payment={}
		pe_not_valid=""
		pe_list=""
		for x in payment:
			if self.sales!=x['sales']:
				if pe_not_valid=="":
					pe_not_valid=""" "{}" """.format(x['idx'])
				else:
					pe_not_valid=""" {},"{}" """.format(pe_not_valid,x['idx'])
			else:
				if pe_list=="":
					pe_list=""" "{}" """.format(x['idx'])
				else:
					pe_list=""" {},"{}" """.format(pe_list,x['idx'])
				if x['days']<=spesial_hangus:
					if x['name'] in invoice_with_payment:
						invoice_with_payment[x['name']]+=flt(x['payment'])
					else:
						invoice_with_payment[x['name']]=flt(x['payment'])
		for inv in invoice_with_payment:
			items = frappe.db.sql("""select qty,rate,amount from `tabSales Invoice Item` where parent= "{}" order by amount desc""".format(inv),as_dict=1)
			sisa = invoice_with_payment[inv]
			komisi =0
			qty=0
			for i in items:
				if sisa > flt(i['amount']):
					sisa = sisa - flt(i['amount'])
					komisi += flt(i['qty'])*bonus_tagih
					qty += flt(i['qty'])
				else:
					qty+=math.floor(sisa/flt(i['rate']))
					komisi += math.floor(sisa/flt(i['rate']))*bonus_tagih
					sisa =0
					break
			det_item = self.append("kursi_susun_bayar",{})
			det_item.inv_no = inv
			det_item.qty=flt(qty)
			det_item.komisi = komisi
			komisi_bayar+=komisi
		self.kursi_susun_tertagih=pe_list
		self.total_special_brand=komisi_bayar+komisi_jual
		self.grand_total=self.total_komisi_tagih+self.total_insentif+self.total_kupon+self.total_special_brand+self.total_obp
		#if pe_not_valid!="":
			#temp=frappe.db.sql("""update `tabPayment Entry Reference` set commision_redeemed=1 where name IN ({}) """.format(pe_not_valid),as_list=1)
	
	def get_insentif(self):
		total_insentif=0
		target_map={}
		for t in self.targets:
			target_map[t.brand]=t.target
		invoice = frappe.db.sql("""select si.name,si.posting_date,si.brand , si.sales , si.grand_total , si.commision_type
			from `tabSales Invoice`  si 
			where si.docstatus=1 and si.brand is not null and si.insentif_redeemed =0 and si.commision_type in ("OBP")
			and si.posting_date < "{}" and si.sales="{}"
		 """.format(self.to_date,self.sales),as_dict=1)
		total_insentif=0
		result_temp={}
		inv_list=""
		for inv in invoice:
			if inv_list=="":
				inv_list=""" "{}" """.format(inv.name)
			elif not inv.name in inv_list:
				inv_list=""" {},"{}" """.format(inv_list,inv.name)
			if not inv.brand in result_temp:
				result_temp[inv['brand']]=flt(inv['grand_total'])
			else:
				result_temp[inv['brand']]+=flt(inv['grand_total'])
		for r in result_temp:
			if r in target_map:
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
		self.total_insentif=total_insentif
		self.grand_total=self.total_komisi_tagih+self.total_insentif+self.total_kupon+self.total_special_brand+self.total_obp
		self.insentif_redeemed=inv_list
	def generate_obp(self):
		jual_hangus = flt(frappe.db.get_single_value('Commision Setting','jual_hangus'),3)

		invoice = frappe.db.sql("""select si.name,si.customer,si.posting_date,si.brand , si.sales , sit.qty as "jumlah", si.grand_total  , DATEDIFF(pe.posting_date,si.posting_date) as "days" , si.commision_type
			from `tabSales Invoice Item` sit
			left join `tabPayment Entry Reference` per on per.reference_name = sit.parent
			left join `tabPayment Entry` pe on per.parent=pe.name
			join `tabSales Invoice`  si on si.name = sit.parent
			where si.docstatus=1 and si.outstanding_amount<=0 and si.brand is not null and si.commision_redeemed =0 and si.commision_type in ("OBP")
			and si.posting_date < "{}" and si.sales="{}"
		 """.format(self.to_date,self.sales),as_dict=1)
		result_temp={}
		total_obp=0
		total_omset_obp=0
		for inv in invoice:
			omset = self.append("omset",{})
			omset.inv_no=inv['name']
			omset.brand=inv['brand']
			omset.customer = inv['customer']
			omset.amount = flt(inv['grand_total'])
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

		self.total_obp=total_obp
		#self.total_insentif=total_insentif
		self.total_omset_obp=total_omset_obp
		self.grand_total=self.total_komisi_tagih+self.total_insentif+self.total_kupon+self.total_special_brand+self.total_obp

def invoice_validate(doc,method):
	if doc.commision_type!="OBP":
		doc.insentif_redeemed=1
	else:
		doc.insentif_redeemed=0

def invoice_on_submit(doc,method):
	if doc.commision_type=="Kupon":
		coupon = frappe.db.sql("""select item,qty,bonus,valid_to,valid_from from `tabCoupon Bonus` where valid_from<="{}" and valid_to >="{}" """.format(doc.posting_date),as_dict=1)
		for item in doc.items:
			for x in coupon:
				if item.item_code == x.item:
					item.kupon_bonus = floor(flt(item.qty)/flt(x.qty))*flt(x.bonus)
					continue