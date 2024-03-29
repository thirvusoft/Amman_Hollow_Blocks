import frappe


@frappe.whitelist()
def last_invoice_item_rate(customer,item):
   item=frappe.db.sql("""SELECT  sii.item_code as item_name,sii.rate FROM `tabSales Invoice` si inner join `tabSales Invoice Item` sii on (si.name=sii.parent) WHERE si.customer =%s AND si.docstatus != 2 AND sii.item_code=%s  ORDER BY si.posting_date desc """,(customer,item), as_dict = 1)
   return item