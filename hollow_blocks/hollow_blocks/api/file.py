import frappe
from frappe.handler import upload_file

@frappe.whitelist()
def upload_user_image():
    frappe.form_dict.docname = frappe.session.user
    file = upload_file()
    frappe.db.set_value("User", frappe.session.user, 'user_image', file.file_url)
    image = file.file_url or ""
    if image.startswith("/private") or image.startswith('/public') or image.startswith('/files'):
        image = f"{frappe.utils.get_url()}{image}"
    
    return image