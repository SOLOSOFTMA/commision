# -*- coding: utf-8 -*-
# Copyright (c) 2015, bobzz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import  date_diff,flt,cint
import math

class CommisionSummary(Document):
	pass
#def generate(self):
def tes():
	#get all setting vriable
	special_brand = frappe.db.get_single_value('Commision Setting','brand')
	bonus_jual = flt(frappe.db.get_single_value('Commision Setting','bonus_jual'))
	bonus_tagih = flt(frappe.db.get_single_value('Commision Setting','bonus_tagih'))
	spesial_hangus = flt(frappe.db.get_single_value('Commision Setting','spesial_hangus'))
	jual_hangus = flt(frappe.db.get_single_value('Commision Setting','jual_hangus'))
	#Selecting invoice due and save to an array
	#list of sales
	sales = frappe.db.sql("""select name,supervisor from tabSales """,as_dict=1)
	#get kpon per sales
	coupon = frappe.db.sql("""select item,qty,bonus,valid_to,valid_from from `tabCoupon Bonus` order by valid_to desc """,as_dict=1)
	#list of invoice for sales commision OBP ,kupon, insentif
	invoice = frappe.db.sql("""select si.name,si.posting_date,sit.item_code,si.brand , si.sales , sit.qty as "jumlah", sit.amount as "omset" , DATEDIFF(pe.posting_date,si.posting_date) as "days" 
		from `tabSales Invoice Item` sit
		left join `tabPayment Entry Reference` per on per.reference_name = sit.parent
		left join `tabPayment Entry` pe on per.parent=pe.name
		join `tabSales Invoice`  si on si.name = sit.parent
		where si.docstatus=1 and si.outstanding_amount=0 and si.brand is not null and si.sales is not null and commision_redeemed =0

	 """,as_dict=1)
	#and si.posting_date < "{}" .format(self.to_date)
	sales_total={}
	kupon={}
	payment={}
	sales_commision={}
	supervisor_commision={}
	inv_list=""
	inv_special_brand=""
	#filter total sales per brand
	for row in invoice:
		cupon_applied =0
		if inv_list=="":
			inv_list=""" "{}" """.format(si.name)
		elif not si.name in inv_list:
			inv_list=""" {},"{}" """.format(inv_list,si.name)
		if row['brand'] != special_brand:
			if inv_special_brand=="":
				inv_special_brand=""" "{}" """.format(si.name)
			elif not si.name in inv_special_brand:
				inv_special_brand=""" {},"{}" """.format(inv_special_brand,si.name)
		for data in coupon:
			if data['item']==row['item_code'] and date_diff(row['posting_date'],data[valid_from]) >=0 and date_diff(data[valid_to],row['posting_date'])>=0:
				cupon_applied =1
				if row['sales'] in kupon:
					found=0
					for gg in kupon[row['sales']]:
						if gg['item']==data['item']:
							found=1
							gg['total_qty']+=flt(row['jumlah'])
					if found==0:
						kupon[row['sales']].append({"item":data['item'],"qty_rules":flt(data['qty']),"bonus_rules":flt(row['amount']),"total_qty":flt(row['jumlah'])})
				else:
					kupon[row['sales']]=[]
					kupon[row['sales']].append({"item":data['item'],"qty_rules":flt(data['qty']),"bonus_rules":flt(row['amount']),"total_qty":flt(row['jumlah'])})
				break
		if not row['sales'] in sales_total:
			sales_total[row['sales']]={}
		if not row['brand'] in sales_total[row['sales']]:
			sales_total[row['sales']][row['brand']]={}
		if cupon_applied ==0:
			if row['days'] <= jual_hangus:
				sales_total[row['sales']][row['brand']]['qty']+=flt(row['jumlah'])
				sales_total[row['sales']][row['brand']]['total']+=flt(row['amount'])
			if special_brand==row['brand'] and row['days']<=spesial_hangus:
				if not key in sales_commision:
					sales_commision[key]={}
				sales_commision[key]['special_brand'] = sales_total[da['sales']][special_brand]['qty']*bonus_jual
		
		sales_total[row['sales']][row['brand']]['total_penjualan']+=flt(row['amount'])
		
	#get sales target
	sales_target = frappe.db.sql("""select sales,target,brand from `tabSales Target`""",as_dict=1)
	for da in sales_target:
		if not da['sales'] in sales_total:
			sales_total[da['sales']]={}
		if not da['brand'] in sales_total[da['sales']]:
			sales_total[da['sales']][da['brand']]={}
		sales_total[da['sales']][da['brand']]['target']=flt(da.target)
		
	#get insentf per sales
	brand_with_insentif = frappe.db.sql("""select brand from `tabTarget Matrix`""",as_list=1)
	for brand in brand_with_insentif:
		level = frappe.db.sql("""select target,bonus from `tabTarget Matrix Item` order by target asc """,as_list=1)
		for key in sales_total.keys():
			if not brand in sales_total[key]:
				continue
			if (sales_total[key][brand]['total']*0.95)>=sales_total[key][brand]['target']:
				if not key in sales_commision:
					sales_commision[key]={}
					sales_commision[key]['sales']=key
					sales_commision[key]['insentif']=0
				for step in level:
					if step[0]==sales_total[key][brand]['target']:
						sales_commision[key]['insentif']+=step[1]
						break

	#get sales OBP per sales
	brand_with_obp = frappe.db.sql("""select brand from `tabOBP Matrix`""",as_list=1)
	for brand in brand_with_insentif:
		level = frappe.db.sql("""select achieve,commision from `tabOBP Matrix Item` order by achieve asc """,as_list=1)
		for key in sales_total.keys():
			if not brand in sales_total[key]:
				continue
			obp = ((sales_total[key][brand]['total']*0.95)/sales_total[key][brand]['target'])*100
			if not key in sales_commision:
				sales_commision[key]={}
				sales_commision[key]['sales']=key
				sales_commision[key]['obp']=0
			multi=0
			for step in level:
				if step[0]<obp:
					multi=step[1]
			sales_commision[key]['obp']+=multi*(sales_total[key][brand]['total']*0.95)
			if obp>=100:
				sales_commision[key]['supervisor_insentif']+=0.13*(sales_total[key][brand]['total_penjualan']*0.95)
			else:
				sales_commision[key]['supervisor_insentif']+=0.1*(sales_total[key][brand]['total_penjualan']*0.95)

	
	#calculate kupon
	for key in kupon.keys():
		sales_commision[key]['kupon']+=math.floor(kupon['total_qty']/kupon['qty_rules'])*kupon['bonus_rules']
	#get komisi tagih per sales

	return sales_commision;
	#get payment data
	#payment_data = frappe.db.sql("""select pr.sales,(pr.allocated_amount-pr.discount_accumulated) as "payment",DATEDIFF(pe.posting_date,si.posting_date)
	#	from `tabPayment Entry Reference` pr 
	#	join `tabPayment Entry` pe on pr.parent=pe.name
	#	left join `tabSales Invoice` si on pr.reference_name = si.name
	#	where pr.reference_doctype="Sales Invoice" and pe.docstatus=1 and si.outstanding_amount=0 and si.brand is not null and si.sales is not null and commision_redeemed =0 and si.posting_date < "{}"
	#""",as_dict=1)