import frappe
from hollow_blocks.hollow_blocks.api.sitecartlist import get_item_image_attachments
from erpnext.stock.get_item_details import get_item_price, get_price_list_rate

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
        CONCAT(
            pr.title,
            CASE
                WHEN pr.rate_or_discount = "Discount Percentage"
                    THEN CONCAT(' - ', ROUND(pr.discount_percentage, 2), ' Percent\n')
                ELSE
                    CONCAT(' - ', ROUND(pr.discount_amount, 2), ' Amount\n')
            END,
            CASE
                WHEN (IFNULL(pr.valid_from, '') != '') OR (IFNULL(pr.valid_upto, '') != '')
                    THEN CONCAT(
                        CASE
                            WHEN IFNULL(pr.valid_from, '') != ''
                                THEN CONCAT("Valid From: ", pr.valid_from, " ")
                            ELSE 
                                ''
                        END,
                        CASE
                            WHEN IFNULL(pr.valid_upto, '') != ''
                                THEN CONCAT("Valid Upto: ", pr.valid_upto, " ")
                            ELSE 
                                ''
                        END,
                        '\n'
                    )
                ELSE
                    ''
            END,
            CASE
                WHEN (IFNULL(pr.min_qty, 0) > 0) OR (IFNULL(pr.max_qty, 0) > 0)
                    THEN CONCAT(
                        CASE
                            WHEN IFNULL(pr.min_qty, 0) > 0
                                THEN CONCAT("Min Qty: ", ROUND(pr.min_qty, 2), " ")
                            ELSE 
                                ''
                        END,
                        CASE
                            WHEN IFNULL(pr.max_qty, 0)
                                THEN CONCAT("Max Qty: ", ROUND(pr.max_qty, 2))
                            ELSE 
                                ''
                        END,
                        '\n'
                    )
                ELSE
                    ''
            END,
            CASE
                WHEN (IFNULL(pr.min_amt, 0) > 0) OR (IFNULL(pr.max_amt, 0) > 0)
                    THEN CONCAT(
                        CASE
                            WHEN IFNULL(pr.min_amt, 0) > 0
                                THEN CONCAT("Min Amt: ", ROUND(pr.min_amt, 2), " ")
                            ELSE 
                                ''
                        END,
                        CASE
                            WHEN IFNULL(pr.max_amt, 0)
                                THEN CONCAT("Max Amt: ", ROUND(pr.max_amt, 2))
                            ELSE 
                                ''
                        END,
                        '\n'
                    )
                ELSE
                    ''
            END
        ) as offer,
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
        CASE
            WHEN IFNULL(pr.valid_from, '') != ''
                THEN pr.valid_from <= "{frappe.utils.nowdate()}"
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
                'offer': [],
                'offer_display': []
                }
        item_wise_offers[row.item_code]['offer_id'].append(row.get('offer_id') or '')
        item_wise_offers[row.item_code]['pricing_rules'].append(row)
        item_wise_offers[row.item_code]['offer_display'].append(row.get("name") or "")
        item_wise_offers[row.item_code]['offer'].append(row.get("offer") or "")

    item_list=frappe.db.get_list("Item",filters={
        "disabled": 0,
        "has_variants": 0,
        "item_group": ["not in", frappe.db.get_list("Item Group", {"dont_show_in_mobile_app": 1}, pluck="name")]
        },fields=["name as item_code", "description", "stock_uom as uom", "item_group", "name"])
    
    selling_price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list")

    for item in item_list:
        args = frappe._dict({
            "item_code": item.name,
            "customer": frappe.db.get_value('Customer', {'user': frappe.session.user}, 'name'),
            "quotation_to": "Customer",
            "price_list": selling_price_list,
            "order_type": "Sales",
            "doctype": "Quotation",
            "conversion_rate": 1,
            "plc_conversion_rate": 1,
            "conversion_factor": 1.0,
            "uom": item.uom,
        })

        item_price = get_price_list_rate(args, frappe.get_doc("Item", item.name)).get('price_list_rate') or 0

        item.update({
            "currency": "₹",
            "favourite": f'"{frappe.session.user}"' in (frappe.db.get_value("Item", item.name, "_liked_by") or ""),
            "offer": (item_wise_offers.get(item.item_code) or {}).get('offer') or [],
            "offer_display": ", ".join((item_wise_offers.get(item.item_code) or {}).get('offer_display') or []),
            "price_list_rate": item_price, 
            "image": get_item_image_attachments(item['item_code'], {}),
            "pricing_rules": (item_wise_offers.get(item.item_code) or {}).get('pricing_rules') or [],
            "offer_id": (item_wise_offers.get(item.item_code) or {}).get('offer_id') or []
        })

    return {
            'items': item_list,
            'item_groups': item_group_list()
            }
