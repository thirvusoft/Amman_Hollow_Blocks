import frappe
import json
from frappe.utils import flt
from erpnext.stock.get_item_details import get_item_details

def get_item_image_attachments(item_code, item_attachments):
    if item_code not in item_attachments:
        attachments = frappe.db.get_all('File', filters={'attached_to_name': item_code, 'attached_to_doctype': 'Item', 'attached_to_field': "image"}, fields=['file_url'], order_by='creation desc')
        attachments += frappe.db.get_all('File', filters={'attached_to_name': item_code, 'attached_to_doctype': 'Item', 'attached_to_field': ["!=", "image"]}, fields=['file_url'], order_by='creation desc')
        item_attachments[item_code] = [f"{frappe.utils.get_url()}{attachment.file_url}" if attachment.file_url.startswith(('/')) else attachment.file_url for attachment in attachments if attachment.file_url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg'))]
    return item_attachments[item_code]

@frappe.whitelist()
def getsitecartlist(project=None, allsites=False):
    user = frappe.session.user or user
    customer = frappe.db.get_value("Customer", {"user": user}, "name")
    sitelist = []
    if customer:
        item_attachments = {}
        filters = {"docstatus": 0, "party_name": customer, 'project': ['is', 'set']}
        if project:
            filters['project'] = project
        
        quotation_list = frappe.db.get_list("Quotation", filters=filters, fields=["name", "project"])
        
        if not project:
            filters = {'customer': customer}
            if not allsites:
                filters['status'] = ['not in', ['Completed', 'Cancelled']]

            projects = frappe.db.get_list("Project", filters, pluck="name")
            
            so_projects = [i.project for i in quotation_list]
            for pr in projects:
                if pr not in so_projects:
                    quotation_list.append({
                        'name': '',
                        'project': pr
                    })

        for name in quotation_list:
            
            sitedetails={
                "name": name['project'],
                "status": frappe.db.get_value("Project", name["project"], "status"),
                "project_name": frappe.db.get_value("Project", name["project"], "project_name"),
                "qty": 0,
                "amount": 0,
                'cart_items': [],
                'quotation': '',
                'checkout_page_details': []
            }
            if name.get('name'):
                cart_items = frappe.get_all(
                    "Quotation Item",
                    filters={
                        'parent': name['name'],
                        'parenttype': 'Quotation',
                    },
                    fields=[
                        "item_code", 
                        "cast(ifnull(sum(qty), 0) as int) as qty",
                        "avg(rate) as rate",
                        "sum(amount) as amount",
                        "'₹' as currency"
                        ],
                    group_by = "item_code",
                    order_by = "idx"
                )
                for item in cart_items:
                    item.update({
                        'image': get_item_image_attachments(item['item_code'], item_attachments)
                    })
                checkout_page_details = []
                so_details = frappe.db.get_all("Quotation", 
                                        {'name': name['name']},
                                        [
                                            'cast(ifnull(total_qty, 0) as int) as total_qty', 
                                            'total', 
                                            'total_taxes_and_charges',
                                            'grand_total',
                                            'discount_amount'
                                        ]
                                    )
                if so_details:
                    sitedetails["qty"] = so_details[0]['total_qty']
                    sitedetails['amount'] = so_details[0]['grand_total']

                    for field in so_details[0]:
                        if (so_details[0][field]):
                            checkout_page_details.append({
                                "label": {
                                            'total_qty': 'Total Qty', 
                                            'total': "Total Amount", 
                                            'total_taxes_and_charges': 'Tax Amount',
                                            'discount_amount': "Discount",
                                            'grand_total': "Grand Total",
                                        }[field],
                                "value": so_details[0][field],
                                "bold": 1 if field == 'grand_total' else 0
                            })
                sitedetails['cart_items'] = cart_items
                sitedetails['quotation'] = name['name']
                sitedetails['checkout_page_details'] = checkout_page_details
            
            sitelist.append(sitedetails)

        return sitelist
                
@frappe.whitelist()
def updateCartItems(quotation, items):
    quotation = frappe.get_doc("Quotation", quotation)
    items = (json.loads(items) if(isinstance(items, str)) else items)
    for i in items:
        if 'image' in i:
            del i['image']
    quotation.update({
        "items": [item for item in items if flt(item.get('qty'))]
    })
    if not quotation.items:
        quotation.delete()
        frappe.local.response['delete'] = True
    else:
        quotation.save()
    frappe.db.commit()
    frappe.local.response["show_alert"] = {
        'message': 'Cart Updated!', 
        'indicator': 'green'
    }
    return getsitecartlist()

@frappe.whitelist()
def submitCartOrder(quotation, delivery_date=None):
    try:
        doc=frappe.get_doc("Quotation", quotation)
        sales_doc=frappe.new_doc("Sales Order")
       
        if delivery_date:
            doc.update({
                "delivery_date": delivery_date
            })
            for item in doc.items:
                item.delivery_date = delivery_date

        doc.save()
        doc.submit()
        
        sales_doc.customer=doc.party_name
        sales_doc.transaction_date=doc.transaction_date
        sales_doc.delivery_date =doc.delivery_date
        for item in doc.items:
            sales_doc.append(
                "items",{
                    "item_code":item.item_code,
                    "qty":item.qty,
                    "rate":item.rate,
                    "delivery_date":doc.delivery_date
                }
            )
        sales_doc.save()
       
        frappe.local.response['show_alert'] = {
            "message": "Order Placed!",
            "indicator": "green"
        }
        return getsitecartlist()
    except:
        frappe.log_error(title=f"API - delivery_date  {quotation}  {delivery_date}", message=frappe.get_traceback())
        frappe.local.response['show_alert'] = {
            "message": "OOPS! Something went wrong.",
            "indicator": "red"
        }
        frappe.local.response['http_status_code'] = 500
