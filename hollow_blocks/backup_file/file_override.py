import os
import shutil
def file_override():
    list = [
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/item.json',
            'destination':'/erpnext/erpnext/stock/doctype/item/item.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/lead.json',
            'destination':'/erpnext/erpnext/crm/doctype/lead/lead.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/payment_entry.json',
            'destination':'/erpnext/erpnext/accounts/doctype/payment_entry/payment_entry.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/purchase_invoice.json',
            'destination':'/erpnext/erpnext/accounts/doctype/purchase_invoice/purchase_invoice.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/purchase_order.json',
            'destination':'/erpnext/erpnext/buying/doctype/purchase_order/purchase_order.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/purchase_receipt.json',
            'destination':'/erpnext/erpnext/stock/doctype/purchase_receipt/purchase_receipt.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/quotation.json',
            'destination':'/erpnext/erpnext/selling/doctype/quotation/quotation.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/sales_invoice.json',
            'destination':'/erpnext/erpnext/accounts/doctype/sales_invoice/sales_invoice.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/sales_order.json',
            'destination':'/erpnext/erpnext/selling/doctype/sales_order/sales_order.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/supplier.json',
            'destination':'/erpnext/erpnext/buying/doctype/supplier/supplier.json'
        },
        {
            'source':'/hollow_blocks/hollow_blocks/backup_file/customer.json',
            'destination':'/erpnext/erpnext/selling/doctype/customer/customer.json'
        },
    ]
    for i in list:
        source_to_destination(i['source'],i['destination'])

def source_to_destination(s,d):
    directory = os.getcwd()
    path = directory.replace('sites','apps')
    source = path+s
    destination = path+d
    shutil.copy(source, destination)