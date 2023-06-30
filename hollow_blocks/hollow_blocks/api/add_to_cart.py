import frappe
import json

@frappe.whitelist()
def addToCart(itemcode, sitewiseqty):
    sitewiseqty = (json.loads(sitewiseqty) if(isinstance(sitewiseqty, str)) else sitewiseqty)
    for site in sitewiseqty:
        qty = site.get('qty') or 0
        so_list = frappe.get_all("Sales Order", {'project': site.get('name'), 'docstatus': 0})
        if not so_list and not (qty if not (isinstance(qty, str)) else qty not in ['0', '0.0', '0.00']):
            continue

        if not so_list:
            sales_order = frappe.new_doc("Sales Order")
            sales_order.delivery_date = frappe.utils.nowdate()
            sales_order.update({
                'project': site.get('name'),
                'customer': frappe.get_value('Customer', {'user': frappe.session.user}, 'name'),
            })
        else:
            sales_order=frappe.get_doc("Sales Order", so_list[0].name)
        
        updated = False
        for item in sales_order.get('items') or []:
            if item.item_code == itemcode:
                item.qty = qty
                updated = True
                break
        
        if not updated:
            sales_order.update({
                "items": (sales_order.get('items') or []) + [{'item_code': itemcode, 'qty': qty}]
            })
            updated = True
        
        sales_order.update({
            "items": [item for item in sales_order.items if item.get('qty')] 
        })

        frappe.local.response['sales_order'] = sales_order.name
        if not sales_order.items:
            sales_order.delete()
            frappe.local.response['delete'] = True
        else:
            sales_order.save()
        frappe.db.commit()
    
    frappe.local.response['show_alert'] = {
        'message': 'Cart Updated!',
        'indicator': 'green'
    }
