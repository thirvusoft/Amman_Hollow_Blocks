import frappe, erpnext
import json
import re
from frappe.utils import formatdate
from erpnext.accounts.party import get_dashboard_info
from frappe.utils.data import getdate
from hollow_blocks.hollow_blocks.api.sitecartlist import getsitecartlist
from frappe.desk.form.linked_with import get_submitted_linked_docs


"""
	core changes for api
	password_reset.html
	app.py
	user.py
"""

@frappe.whitelist()
def transactions(args):
	if isinstance(args, str):
		args = json.loads(args)

	data={}

	user = frappe.session.user
	customer = frappe.get_value("Customer", {"user": user}, "name")
	if not customer:
		return data

	filters = {
		"customer": customer,
		"docstatus": 1
	}
	if args.get("status"):
		filters["status"] = args.get("status")
	if args.get("site"):
		filters["project"] = args.get("site")
	
	# SALES ORDER
	so_list = frappe.db.get_all('Sales Order',filters=filters, fields = [
		"name", "status", "delivery_date", "total_qty", "total as net_total", "total_taxes_and_charges as tax_amount", "grand_total", "project", "sales_order_approved"
	])
	for so in so_list:		
		item_list = frappe.get_all("Sales Order Item", filters = {
			"parenttype": "Sales Order",
			"parent": so.name
		}, fields = [
			"item_code",
			"item_name",
			"qty",
			"rate",
			"amount",
			"uom",
			"conversion_factor",
		])
		links = get_submitted_linked_docs(doctype="Sales Order", name=so.get("name"))
		so.update({
			"is_approved": (so.get("sales_order_approved") or 0) or links.get("count"),
			"project_name": frappe.db.get_value("Project", so.get("project"), "project_name") if so.get("project") else "",
			"items":item_list
		})

	# SALES INVOICE
	sales_inv_list = frappe.db.get_all('Sales Invoice',filters=filters, fields = [
		"name", "status", "posting_date", "total_qty", "total as net_total", "total_taxes_and_charges as tax_amount", "grand_total", "project", "outstanding_amount", "rounded_total"
	])
	for si in sales_inv_list:
		item_list = frappe.get_all("Sales Invoice Item", filters = {
			"parenttype": "Sales Invoice",
			"parent": si.name
		}, fields = [
			"item_code as item",
			"item_name",
			"qty",
			"rate",
			"amount",
			"uom",
			"conversion_factor",
		])

		si.update({
			"project_name": frappe.db.get_value("Project", si.get("project"), "project_name") if si.get("project") else "",
			"items": item_list,
			"other_details": [
				{
					"label": "Paid Amount",
					"value": (si.get("rounded_total") or 0) - (si.get("outstanding_amount") or 0)
				},
				{
					"label": "Outstanding Amount",
					"value": (si.get("outstanding_amount") or 0)
				}
			]
		})
	
	# DELIVERY NOTE
	delivery_note_list = frappe.db.get_all('Delivery Note',filters=filters, fields = [
		"name", "status", "posting_date as delivery_date", "total_qty", "total as net_total", "total_taxes_and_charges as tax_amount", "grand_total", "project"
	])
	for dn in delivery_note_list:
		item_list = frappe.get_all("Delivery Note Item", filters = {
			"parenttype": "Delivery Note",
			"parent": dn.name
		}, fields = [
			"item_code as item",
			"item_name",
			"qty",
			"rate",
			"amount",
			"uom",
			"conversion_factor",
		])
		
		dn.update({
			"project_name": frappe.db.get_value("Project", dn.get("project"), "project_name") if dn.get("project") else "",
			"items":item_list
		})

	# PAYMENT ENTRY
	pe_filters = filters
	pe_filters['party'] = pe_filters["customer"]
	del pe_filters['customer']

	payment_entry = frappe.db.get_all('Payment Entry',filters=pe_filters, fields= [
		"name", "posting_date as date", "mode_of_payment", "paid_amount", "project"
	])
	
	for pe in payment_entry:
		payment_reference = frappe.get_all("Payment Entry Reference", filters = {
			"parenttype": "Payment Entry",
			"parent": pe.name
		}, fields = [
			"reference_doctype as doctype",
			"reference_name as docname",
			"allocated_amount as total_amount"
		])
		for ref in payment_reference:
			ref.project = ''
			ref.project_name = ''
			if ref.reference_doctype in ("Sales Order", "Delivery Note", "Sales Invoice") and ref.reference_name:
				ref.project = frappe.db.get_value(ref.reference_doctype, ref.reference_name, 'project') or ''
				ref.project_name = frappe.db.get_value("Project", ref.get("project"), "project_name") if ref.get("project") else ""

		pe.update({
			"project_name": frappe.db.get_value("Project", pe.get("project"), "project_name") if pe.get("project") else "",
			"references": payment_reference
		})

	data["sales_order"]=so_list or []
	data["sales_invoice"]=sales_inv_list or []
	data["delivery_note"]=delivery_note_list or []
	data["payment_list"]=payment_entry or []
	return data


@frappe.whitelist()
def company_details():
	company = frappe.get_doc("Company", erpnext.get_default_company())

	data = [
		{"label": "", "value": (company.name or "").upper(), "bold": "1"},
		{"label": "GSTIN", "value": company.gstin or ""},
		{"label": "PAN", "value": company.pan or ""},
		{"label": "PHONE", "value": company.phone_no or ""},
	]

	if frappe.db.exists("Bank Account",{"is_company_account":1,"company":company.name}):
		bank_doc=frappe.get_doc("Bank Account",{"is_company_account":1,"company":company.name})
		data += [
			{"label": "BANK", "value": bank_doc.bank or ""},
			{"label": "BRANCH CODE", "value": bank_doc.branch_code or ""},
			{"label": "Acc No", "value": bank_doc.bank_account_no or ""}
		]

	image = company.get("mobile_app_image") or ""

	if image.startswith("/private") or image.startswith('/public') or image.startswith('/files'):
		image = f"{frappe.utils.get_url()}{image}"

	return {
		'image': image, # pass image url to show in mobile app
		'data': data
		}

@frappe.whitelist()
def status_list():
	data={}
	sales_order=frappe.get_meta('Sales Order').get_field('status').options
	sales_invoice=frappe.get_meta('Sales Invoice').get_field('status').options
	delivery_note=frappe.get_meta('Delivery Note').get_field('status').options
	project=frappe.get_meta('Project').get_field('status').options
	data["sales_order"]=sales_order.split("\n")
	data["sales_invoice"]=sales_invoice.split("\n")
	data["delivery_note"]=delivery_note.split("\n")
	data["project"]=project.split("\n")
	return data


## Login Api
@frappe.whitelist(allow_guest=True)
def login(args):
	if isinstance(args, str):
		args=json.loads(args)
		
	frappe.flags.mobile_login = True
	login_manager = frappe.auth.LoginManager()
	login_manager.authenticate(user=args["username"], pwd=args["password"])
	login_manager.post_login()
	frappe.db.commit()
	frappe.flags.mobile_login = False
	
	cust = frappe.db.get_value("Customer", {"user": frappe.session.user}, "name")
	if cust:
		frappe.response["message"] = {
			"message":"Logged In"
		}

	else:
		frappe.response["message"] = {
			"message":"Please Signup",
		}

@frappe.whitelist(allow_guest=True)
def signup(args):
	frappe.session.user = "Administrator"
	if isinstance(args, str):
		args=json.loads(args)

	data = {"message":""}
	user = frappe.new_doc("User")
	if not args["name"]:
		data["message"] = "Name cannot be null"
		return data

	if not args["mobile_no"]:
		data["message"] = "Mobile No cannot be null"
		return data

	if not args["email"]:
		b=re.sub(r"\s+", "", args["name"]).lower()
		e=b+"@ahb.com"
		user.email = e
		args["email"]=e
		

	if not args["password"]:
		data["message"] = "Password cannot be null"
		return data

	if frappe.db.get_value("User", args["email"]):
		data["message"] = "Email Id Already Exists"
		return data

	if frappe.db.get_value("User", {"mobile_no": args["mobile_no"]}):
		data["message"] = "Mobile No Already Exists"
		return data

	
	user.email = args["email"]
	user.is_mobile_app_user = True
	user.first_name = args["name"]
	user.send_welcome_email = 0
	user.user_type = 'System User'
	user.mobile_no = args["mobile_no"]

	user.role_profile_name="App User"
	user.save(ignore_permissions=True)
	user.new_password = args["password"]
	user.save(ignore_permissions = True)
	#    user.add_roles('System Manager')

	customer = frappe.new_doc("Customer")
	customer.customer_name = args["name"]
	customer.customer_type = "Individual"
	customer.customer_group = "Individual"
	customer.territory = "India"
	customer.update({
		"_email_id": args["email"],
		"_mobile_no": args["mobile_no"],

		"_gstin": args["gstin"],

		**(
			{"gst_category": "Registered Regular"} if args["gstin"] else {}
		),
		"_pincode":args["pincode"],
		"address_line1": args["address"],
		"address_line2": "",
		"city": args["city"],
		"state": args.get("state"),
		"country": "India"
	})
	if args["gstin"]:
		customer.gstin = args["gstin"]
		customer.gst_category="Registered Regular"
	customer.user = user.name
	customer.save()
	
	frappe.session.user = "Guest"

	data["message"] = "Account Created, Please Login"
	return data



@frappe.whitelist()
def pricing_rule():
	pricing_rule = frappe.db.get_all("Pricing Rule",filters = {
		"selling": 1,
		"disable": 0, 
	})

	item_list=frappe.db.get_list("Item",filters={
        "disabled": 0,
        "has_variants": 0,
        "item_group": ["not in", frappe.db.get_list("Item Group", {"dont_show_in_mobile_app": 1}, pluck="name")]
        }, pluck="name")
	
	item_pricing_rules = []

	for j in pricing_rule:
		pricing_doc = frappe.get_doc("Pricing Rule",j['name'])
		if pricing_doc.valid_upto:
			if getdate(pricing_doc.valid_upto) < getdate(frappe.utils.nowdate()):
				continue

		if pricing_doc.valid_from:
			if getdate(pricing_doc.valid_from) > getdate(frappe.utils.nowdate()):
				continue

		j.update({
			"name":pricing_doc.title,
			"display":pricing_doc.title,
			"offer_id":pricing_doc.name,
			"applicable_for":pricing_doc.applicable_for,
			"valid_from":formatdate(pricing_doc.valid_from),
			"valid_upto":formatdate(pricing_doc.valid_upto),
			"min_qty":pricing_doc.min_qty
		})
		
		items = []
		for item in pricing_doc.items:
			if item.item_code in item_list:
				items.append(item.item_code)

		j.update({
			"items": items
		})

		if j.get("items"):
			item_pricing_rules.append(j)

	return item_pricing_rules

@frappe.whitelist()
def site_list(args):
	if isinstance(args, str):
		args=json.loads(args)
	data={}
	customer = frappe.db.get_value("Customer", {"user": frappe.session.user}, "name")
	if not customer:
		return data
	## site list
	if(customer and args["status"]):
		site_list = frappe.db.get_all('Project',filters={"customer":customer,"status":args["status"]})
		

		for m in site_list:
			project_doc = frappe.get_doc('Project',m['name'])
			m.update({
				"status":project_doc.status,
				"name":project_doc.project_name,
				"id":project_doc.name
				})
	else:
		site_list = frappe.db.get_all('Project',filters={"customer":customer})
	
		for m in site_list:
			project_doc = frappe.get_doc('Project',m['name'])
			m.update({
				"status":project_doc.status,
				"name":project_doc.project_name,
				"id":project_doc.name
				})

	data["site_list"]=site_list

	return data


@frappe.whitelist()
def logout():
   api_key = frappe.request.headers.get('Authorization').split(' ')[1].split(':')[0]
   user = frappe.db.get_value("User", {"api_key": api_key})
 
   login_manager = frappe.auth.LoginManager()
   login_manager.logout(user = user)
   return {"message": "Successfully Logged Out"}



@frappe.whitelist()
def site_creation(args):
	user = frappe.session.user
	customer = frappe.get_value("Customer", {"user": user}, "name")
	message = "created"
	try:
		project_doc=frappe.new_doc("Project")
		project_doc.project_name=args.get("sitename")

		if frappe.db.exists("Project", {"project_name": args.get('sitename')}):
			frappe.local.response["show_alert"] = {
				"message": "Project name must be unique.",
				"indicator": "red"
			}
			return

		project_doc.customer=customer
		project_doc.latitude = args.get('latitude') or ''
		project_doc.longitude = args.get('longitude') or ''
		project_doc.save(ignore_permissions = True)
		address = frappe.new_doc("Address")
		address.address_type = "Shipping"
		address.address_title = args.get("sitename")
		address.address_line1 = args.get("siteaddress")
		address.city = args.get("sitecity")
		address.state = args.get("sitestate")
		address.country = args.get("sitecountry")
		address.pincode = args.get("sitepincode")
		address.append('links', {
					"link_doctype": "Project",
					"link_name": project_doc.name
					})
		address.append('links', {
					"link_doctype": "Customer",
					"link_name": customer
					})
		address.save(ignore_permissions = True)
		project_doc.address=address.name
		project_doc.save(ignore_permissions = True)
		frappe.local.response["show_alert"] = {
			"message": "Site Created Successfully!", 
			"indicator": "green"
		}
		message = "created"
	except:
		message = "Site creation failed, Please check the entered deatils."
		frappe.local.response["show_alert"] = {
			"message": "Site creation failed, Please check the entered deatils.",
			"indicator": "red"
		}
	
	frappe.local.response['site_list'] = getsitecartlist()
	return message


@frappe.whitelist()
def site_status_updation(args):
	updated = False
	message = {}
	try:
		project_doc=frappe.get_doc("Project",args["id"])
		project_doc.status=args["status"]
		project_doc.save()
		updated = True
		message = {"message": "Successfully Site Status Updated", "indicator": "green"}
	except:
		frappe.log_error()
		message = {"message": "Site Status Updation Failed Once Check Enter Deatils", "indicator": "red"}
	
	frappe.local.response['show_alert'] = message
	return "updated" if updated else ""


@frappe.whitelist()
def duplicateSalesOrder(sales_order="", delivery_date=None):
	if not delivery_date:
		delivery_date = frappe.utils.nowdate()
	
	if not frappe.db.exists("Sales Order", sales_order):
		frappe.local.response["show_alert"] = {
			"message": "Couldn't duplicate sales order",
			"indicator": "red"
		}
		return

	so_doc = frappe.get_doc("Sales Order", sales_order)
	if frappe.db.exists("Quotation", {
		"docstatus": 0,
		"project": so_doc.project
	}):
		quotation = frappe.get_doc("Quotation", {
			"docstatus": 0,
			"project": so_doc.project
		})
		items = quotation.get("items") or []
		append_items = []
		added_item = []
		for row in (so_doc.get("items") or []):
			add = False
			for i_row in items:
				if i_row.item_code == row.item_code and row.item_code not in added_item:
					i_row.qty += row.qty or 0
					add = True
					added_item.append(row.item_code)
					continue
			
			if not add:
				append_items.append({
					"item_code": row.item_code,
					"qty": row.qty,
				})
		
		items += append_items

		quotation.update({
			"items": items
		})
		quotation.save()

	else:
		quotation = frappe.new_doc("Quotation")
		quotation.update({
			'quotation_to': 'Customer',
			'project': so_doc.project,
			'party_name': frappe.get_value('Customer', {'user': frappe.session.user}, 'name'),
			"items": [
				{
					"item_code": row.item_code,
					"qty": row.qty,
				}
				for row in so_doc.items
			]
		})
		quotation.save()

	frappe.local.response["show_alert"] = {
			"message": "New Items added in cart. Please find and checkout the items in cart to create order",
			"indicator": "green",
			"long_msg": True
		}
	
	return 'created'

@frappe.whitelist()
def project_list():
	data={}
	user = frappe.session.user
	customer = frappe.get_value("Customer", {"user": user}, "name")
	if(customer):
		site_list = frappe.db.get_all('Project',filters={"customer":customer}, fields=["name", "project_name"])
		data = {site.project_name: site.name for site in site_list}
	return data

@frappe.whitelist()
def get_user_details():
	user = frappe.get_doc("User", frappe.session.user)
	image = user.user_image or ""
	customer = frappe.db.get_value("Customer", {"user": frappe.session.user}, "name") or ""
	customer_name = frappe.db.get_value("Customer", {"user": frappe.session.user}, "customer_name") or ""
	cus_address = frappe.db.get_value("Customer", {"user": frappe.session.user}, "customer_primary_address")
	address = frappe._dict()

	if image.startswith("/private") or image.startswith('/public') or image.startswith('/files'):
		image = f"{frappe.utils.get_url()}{image}"
	if customer:
		info = get_dashboard_info("Customer",customer)
		total = 0
		for i in info:
			total += (i.get("total_unpaid") or 0)
			
		if cus_address: 
			address = frappe.get_doc("Address", cus_address)

	return {
			'image': image,
			'customer': customer_name,
			'mobile': user.mobile_no,
			'userid': user.name,
			"address": address.address_line1 or "",
			"city":address.city or "",
			"gstin":address.gstin or "",
			"unpaid":total or 0.0,
			"pincode":address.pincode or "",
			'email': user.name
		}

		