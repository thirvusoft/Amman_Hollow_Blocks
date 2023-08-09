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
            ig.is_group = 0 AND
            ig.dont_show_in_mobile_app = 0
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
    item_wise_pricing_rule = frappe.db.sql(f"""
    SELECT
        pr_item.item_code,
        pr.name as offer_id,
        pr.title as name,
        CASE
            WHEN pr.rate_or_discount = "Discount Percentage"
                THEN pr.discount_percentage
            ELSE
                pr.discount_amount
        END as offer,
        pr.valid_from,
        pr.valid_upto
        FROM `tabPricing Rule` pr
    INNER JOIN `tabPricing Rule Item Code` pr_item
    ON  pr.name = pr_item.parent AND pr_item.parenttype = 'Pricing Rule'
    WHERE
        CASE
            WHEN IFNULL(pr.valid_upto, '') != ''
                THEN pr.valid_upto >= "{frappe.utils.nowdate()}"
            ELSE
                1=1
        END AND
        pr.disable = 0 AND
        pr.selling = 1 AND
        pr.apply_on = "Item Code" 
    """, as_dict=True)
    
    item_wise_offers = {}
    for row in item_wise_pricing_rule:
        if row.item_code not in item_wise_offers:
            item_wise_offers[row.item_code] = {
                'offer_id': [], 
                'pricing_rules': [],
                'offer': []
                }
        item_wise_offers[row.item_code]['offer_id'].append(row.get('offer_id') or '')
        item_wise_offers[row.item_code]['pricing_rules'].append(row)
        item_wise_offers[row.item_code]['offer'].append(row.get('offer') or '')

    item_list=frappe.db.get_list("Item",filters={
        "disabled": 0,
        "has_variants": 0,
        "item_group": ["not in", frappe.db.get_list("Item Group", {"dont_show_in_mobile_app": 1}, pluck="name")]
        },fields=["name as item_code", "description", "stock_uom as uom", "item_group", "name"])
    
    for item in item_list:	
        item_price = get_item_price(
            args= {
                'customer': frappe.db.get_value('Customer', {'user': frappe.session.user}, 'name'),
                'transaction_date': frappe.utils.nowdate()
            },
            item_code = item.name
        )

        item.update({
            "currency": "₹",
            "favourite": f'"{frappe.session.user}"' in (frappe.db.get_value("Item", item.name, "_liked_by") or ""),
            "offer": (item_wise_offers.get(item.item_code) or {}).get('offer') or [],
            "price_list_rate": item_price[0][1] if item_price else 0.0, 
            "image": get_item_image_attachments(item['item_code'], {}),
            "pricing_rules": (item_wise_offers.get(item.item_code) or {}).get('pricing_rules') or [],
            "offer_id": (item_wise_offers.get(item.item_code) or {}).get('offer_id') or []
        })

    return {
            'items': item_list,
            'item_groups': item_group_list()
            }
