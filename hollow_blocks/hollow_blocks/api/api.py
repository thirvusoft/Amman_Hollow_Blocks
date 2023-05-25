import frappe
from json import loads
import json

@frappe.whitelist(allow_guest=True)
def transactions(args):
    # args=json.loads(args)
    data={}
    result=[]
    if(args["customer"] and args["status"]):
        ## sales order
        sales_ord_list = frappe.db.get_all('Sales Order',filters={"customer":args["customer"],"status":args["status"]})
        
        for i in sales_ord_list:
            sales_doc = frappe.get_doc('Sales Order',i['name'])
            i.update({
                "status":sales_doc.status,
                "delivery_date":sales_doc.delivery_date,
                "grand_total":sales_doc.grand_total})
            item_list = []
            for item in sales_doc.items:
                item_details = frappe._dict()
                item_details.update({
                    "item":item.item_code,
                    "item_name":item.item_name,
                    "qty":item.qty,
                    "amount":item.amount
                })
                item_list.append(item_details)
            i.update({
                "items":item_list
            })
         ## Delivery Note
        delivery_note_list = frappe.db.get_all('Delivery Note',filters={"customer":args["customer"],"status":args["status"]})
        
        for k in delivery_note_list:
            dn_doc = frappe.get_doc('Delivery Note',k['name'])
            k.update({
                "status":dn_doc.status,
                "delivery_date":dn_doc.posting_date,
                "grand_total":dn_doc.grand_total})
            item_list = []
            for item in dn_doc.items:
                item_details = frappe._dict()
                item_details.update({
                    "item":item.item_code,
                    "item_name":item.item_name,
                    "qty":item.qty,
                    "amount":item.amount
                })
                item_list.append(item_details)
            k.update({
                "items":item_list
            })

        payment_entry = frappe.db.get_all('Payment Entry',filters={"party":args["customer"],"status":args["status"]})
        
        for m in payment_entry:
            pay_doc = frappe.get_doc('Payment Entry',k['name'])
            m.update({
                
                "date":pay_doc.posting_date,
                "mode_of_payment":pay_doc.mode_of_payment})
            item_list = []
            for item in dn_doc.references:
                item_details = frappe._dict()
                item_details.update({
                    "doctype":item.reference_name,
                    "amount":item.total_amount,
                    
                })
                item_list.append(item_details)
            m.update({
                "items":item_list
            })


        ## sales invoice
        sales_inv_list = frappe.db.get_all('Sales Invoice',filters={"customer":args["customer"],"status":args["status"]})
        

        for j in sales_inv_list:
            sales_doc = frappe.get_doc('Sales Invoice',j['name'])
            j.update({
                "status":sales_doc.status,
                "posting_date":sales_doc.posting_date,
                "grand_total":sales_doc.grand_total})
            item_list = []
            for item in sales_doc.items:
                item_details = frappe._dict()
                item_details.update({
                    "item":item.item_code,
                    "item_name":item.item_name,
                    "qty":item.qty,
                    "amount":item.amount
                })
                item_list.append(item_details)
            j.update({
                "items":item_list
            })

    else:
        ##sales order
        sales_ord_list = frappe.db.get_all('Sales Order',filters={"customer":args["customer"]})
        
        for i in sales_ord_list:
            sales_doc = frappe.get_doc('Sales Order',i['name'])
            i.update({
                "status":sales_doc.status,
                "delivery_date":sales_doc.delivery_date,
                "grand_total":sales_doc.grand_total})
            item_list = []
            for item in sales_doc.items:
                item_details = frappe._dict()
                item_details.update({
                    "item":item.item_code,
                    "item_name":item.item_name,
                    "qty":item.qty,
                    "amount":item.amount
                })
                item_list.append(item_details)
            i.update({
                "items":item_list
            })
        ## Delivery Note
        delivery_note_list = frappe.db.get_all('Delivery Note',filters={"customer":args["customer"]})
        
        for k in delivery_note_list:
            dn_doc = frappe.get_doc('Delivery Note',k['name'])
            k.update({
                "status":dn_doc.status,
                "delivery_date":dn_doc.posting_date,
                "grand_total":dn_doc.grand_total})
            item_list = []
            for item in dn_doc.items:
                item_details = frappe._dict()
                item_details.update({
                    "item":item.item_code,
                    "item_name":item.item_name,
                    "qty":item.qty,
                    "amount":item.amount
                })
                item_list.append(item_details)
            k.update({
                "items":item_list
            })
        ## payment entry
        payment_entry = frappe.db.get_all('Payment Entry',filters={"party":args["customer"]})
        
        for m in payment_entry:
            pay_doc = frappe.get_doc('Payment Entry',m['name'])
            m.update({
               
                "date":pay_doc.posting_date,
                "mode_of_payment":pay_doc.mode_of_payment})
            item_list = []
            for item in pay_doc.references:
                item_details = frappe._dict()
                item_details.update({
                    "doctype":item.reference_name,
                    "amount":item.total_amount,
                    
                })
                item_list.append(item_details)
            m.update({
                "items":item_list
            })

        ## sales invoice
        sales_inv_list = frappe.db.get_all('Sales Invoice',filters={"customer":args["customer"]})
        

        for j in sales_inv_list:
            sales_doc = frappe.get_doc('Sales Invoice',j['name'])
            j.update({
                "status":sales_doc.status,
                "posting_date":sales_doc.posting_date,
                "grand_total":sales_doc.grand_total})
            item_list = []
            for item in sales_doc.items:
                item_details = frappe._dict()
                item_details.update({
                    "item":item.item_code,
                    "item_name":item.item_name,
                    "qty":item.qty,
                    "amount":item.amount
                })
                item_list.append(item_details)
            j.update({
                "items":item_list
            })
          
  
    data["sales_order"]=sales_ord_list
    data["sales_invoice"]=sales_inv_list
    data["delivery_note"]=delivery_note_list
    data["payment_list"]=payment_entry
    return data


@frappe.whitelist(allow_guest=True)
def company_details():
    # data={}
    company_dict={}
    company=frappe.get_all("Company")
    for i in company:
        comp_doc=frappe.get_doc("Company",i["name"])
        bank_doc=frappe.get_doc("Bank Account",{"is_company_account":1,"company":comp_doc.name})
        company_dict.update({
            "comp_name":comp_doc.name or "",
            "gstin":comp_doc.gstin or "",
            "pan":comp_doc.pan or "",
            "phone":comp_doc.phone_no or "",
            "bank_name":bank_doc.bank or "",
            "branch_code":bank_doc.branch_code or "",
            "acc_no":bank_doc.bank_account_no or ""
        })
    return company_dict

@frappe.whitelist(allow_guest=True)
def status_list():
    data={}
    sales_order=frappe.get_meta('Sales Order').get_field('status').options
    sales_invoice=frappe.get_meta('Sales Invoice').get_field('status').options
    delivery_note=frappe.get_meta('Delivery Note').get_field('status').options
    data["sales_order"]=sales_order.split("\n")
    data["sales_invoice"]=sales_invoice.split("\n")
    data["delivery_note"]=delivery_note.split("\n")
    return data


    