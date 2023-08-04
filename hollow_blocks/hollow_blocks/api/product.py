import frappe
from hollow_blocks.hollow_blocks.api.sitecartlist import get_item_image_attachments
from erpnext.stock.get_item_details import get_item_price

@frappe.whitelist()
def item_group_list():
    item_group = frappe.db.sql("""
        SELECT
            ig.name as item_group
        FROM `tabItem Group` ig
        WHERE
            ig.is_group = 0
        ORDER BY
            IFNULL((
                SELECT
                    COUNT(soi.name)
                FROM `tabSales Order Item` soi
                WHERE
                    soi.docstatus = 1 AND
                    soi.item_group = ig.name
            ), 0) + IFNULL((
                SELECT
                    COUNT(sii.name)
                FROM `tabSales Invoice Item` sii
                WHERE
                    sii.docstatus = 1 AND
                    sii.item_group = ig.name
            ), 0) DESC
    """, as_dict=True)

    return [ig.get('item_group') for ig in item_group]

@frappe.whitelist()
def get_item_list():
    item_list = item_list=frappe.db.get_list("Item",filters={"disabled":0,"has_variants":0},fields=["name as item_code","description","stock_uom as uom","item_group","name"])
    for item in item_list:	
        item.update({
            "currency": "₹",
            "favourite": f'"{frappe.session.user}"' in (frappe.db.get_value("Item", item.name, "_liked_by") or ""),
            "offer": "",
            "price_list_rate": ""
            })
        # discount=frappe.db.get_list("Pricing Rule Item Code")
        item_price = get_item_price(
            args= {
                'customer': frappe.db.get_value('Customer', {'user': frappe.session.user}, 'name'),
                'transaction_date': frappe.utils.nowdate()
            },
            item_code = item.name
        )
        item.update({"price_list_rate":item_price[0][1] if item_price else 0.0})
        
        item.update({
            "image":get_item_image_attachments(item['item_code'], {})
        })
        for j in frappe.db.get_list("Pricing Rule",filters={"disable":0,"selling":1,"apply_on":"Item Code"}):
            pricing_doc=frappe.get_doc("Pricing Rule",j["name"])
            for i in pricing_doc.items:
                if i.item_code == item["item_code"]:
                    item.update({
                        "offer_id":pricing_doc.name})
                    if pricing_doc.rate_or_discount == "Discount Percentage":
                        item.update({
                        "offer":str(pricing_doc.discount_percentage or 0) + "%"})
                    if pricing_doc.rate_or_discount == "Discount Amount":
                        item.update({
                        "offer":str(pricing_doc.discount_amount or 0) + " Amount Discount"})
                    if pricing_doc.min_qty:
                        item.update({
                        "min_qty":pricing_doc.min_qty,
                        })
                    if pricing_doc.max_qty:
                        item.update({
                        "max_qty":pricing_doc.max_qty,
                        })
                    if pricing_doc.min_amt:
                        item.update({
                        "max_qty":pricing_doc.min_amt,
                        })
                    if pricing_doc.max_amt:
                        item.update({
                        "max_qty":pricing_doc.max_amt,
                        })
    return {
            'items': item_list,
            'item_groups': item_group_list()
            }
