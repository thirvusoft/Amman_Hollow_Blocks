import frappe

def validate_cancel(doc, event=None):
    if doc.sales_order_approved:
        frappe.throw("Order is approved and cannot be cancelled.")
