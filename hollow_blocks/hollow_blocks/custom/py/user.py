import frappe
from frappe.core.doctype.user.user import User
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils.data import cint
from frappe.utils.password import check_password

def create_user_fields():
    create_custom_fields({
        'User': [
            {
                "fieldname": "is_mobile_app_user",
                "label": "Mobile App User",
                "fieldtype": "Check",
                "read_only": 1,
                "insert_after": "username"
            }
        ]
    })
