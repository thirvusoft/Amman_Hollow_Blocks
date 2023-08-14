import frappe
import json
from frappe.utils import flt

@frappe.whitelist()
def addToCart(itemcode, sitewiseqty):
    sitewiseqty = (json.loads(sitewiseqty) if(isinstance(sitewiseqty, str)) else sitewiseqty)
    for site in sitewiseqty:
        qty = flt(site.get('qty') or 0)
        so_filters = {'project': site.get('name'), 'docstatus': 0}
        if site.get("quotation") and frappe.db.exists("Quotation", {
            "name": site.get("quotation")
        }):
            so_filters["name"] = site.get("quotation")
            
        so_list = frappe.get_all("Quotation", so_filters)
        if not so_list and not qty:
            continue

        if not so_list:
            quotation = frappe.new_doc("Quotation")
            quotation.delivery_date = frappe.utils.nowdate()
            quotation.update({
                'quotation_to': 'Customer',
                'project': site.get('name'),
                'party_name': frappe.get_value('Customer', {'user': frappe.session.user}, 'name'),
            })
        else:
            quotation=frappe.get_doc("Quotation", so_list[0].name)
        
        updated = False
        for item in quotation.get('items') or []:
            if item.item_code == itemcode:
                item.qty = qty
                updated = True
                break
        
        if not updated:
            quotation.update({
                "items": (quotation.get('items') or []) + [{'item_code': itemcode, 'qty': qty}]
            })
            updated = True
        
        quotation.update({
            "items": [item for item in quotation.items if item.get('qty')] 
        })

        frappe.local.response['quotation'] = quotation.name
        if not quotation.items:
            quotation.delete()
            frappe.local.response['delete'] = True
        else:
            items = quotation.items
            update_items = []
            count = 0
            for row in items or []:
                if row.item_code == itemcode:
                    if count == 0:
                        row.qty = qty
                        update_items.append(row)
                        count += 1
                else:
                    update_items.append(row)
            
            quotation.update({
                "items": update_items
            })
            quotation.save()

        frappe.db.commit()
    
    frappe.local.response['show_alert'] = {
        'message': 'Cart Updated!',
        'indicator': 'green'
    }
