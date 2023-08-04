import frappe, erpnext
from json import loads
import json
import re
from frappe.utils import today
from erpnext.accounts.party import get_dashboard_info
from hollow_blocks.hollow_blocks.api.sitecartlist import getsitecartlist

@frappe.whitelist()
def transactions(args):
	if isinstance(args, str):
		args = josn.loads(args)

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
		"name", "status", "delivery_date", "total_qty", "total as net_total", "total_taxes_and_charges as tax_amount", "grand_total",
	])
	for so in so_list:		
		item_list = frappe.get_all("Sales Order Item", filters = {
			"parenttype": "Sales Order",
			"parent": so.name
		}, fields = [
			"item_code",
			"item_name",
			"qty",
			"amount",
			"uom",
			"conversion_factor",
		])
		
		so.update({
			"items":item_list
		})

	# SALES INVOICE
	sales_inv_list = frappe.db.get_all('Sales Invoice',filters=filters, fields = [
		"status", "posting_date", "total_qty", "total as net_total", "total_taxes_and_charges as tax_amount", "grand_total"
	])
	for si in sales_inv_list:
		item_list = item_list = frappe.get_all("Sales Invoice Item", filters = {
			"parenttype": "Sales Invoice",
			"parent": so.name
		}, fields = [
			"item_code as item",
			"item_name",
			"qty",
			"amount",
			"uom",
			"conversion_factor",
		])

		si.update({
			"items":item_list
		})
	
	# DELIVERY NOTE
	delivery_note_list = frappe.db.get_all('Delivery Note',filters=filters, fields = [
		"name", "status", "posting_date as delivery_date", "total_qty", "total as net_total", "total_taxes_and_charges as tax_amount", "grand_total",
	])
	for dn in delivery_note_list:
		item_list = frappe.get_all("Delivery Note Item", filters = {
			"parenttype": "Delivery Note",
			"parent": dn.name
		}, fields = [
			"item_code as item",
			"item_name",
			"qty",
			"amount",
			"uom",
			"conversion_factor",
		])
		
		dn.update({
			"items":item_list
		})

	# PAYMENT ENTRY
	pe_filters = filters
	pe_filters['party'] = pe_filters["customer"]
	del pe_filters['customer']

	payment_entry = frappe.db.get_all('Payment Entry',filters=pe_filters, fields= [
		"name", "posting_date as date", "mode_of_payment", "paid_amount"
	])
	
	for pe in payment_entry:
		item_list = frappe.get_all("Payment Entry Reference", filters = {
			"parenttype": "Payment Entry",
			"parent": pe.name
		}, fields = [
			"reference_name as doctype",
			"amount as total_amount"
		])
		pe.update({
			"items":item_list
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
	# args=json.loads(args)
	try:
		login_manager = frappe.auth.LoginManager()
		login_manager.authenticate(user=args["username"], pwd=args["password"])
		login_manager.post_login()
	except frappe.exceptions.AuthenticationError:
		frappe.clear_messages()
		frappe.local.response["message"] = {
			
			"message":"Incorrect Username or Password"
		}
		return
	frappe.db.commit()
	user = frappe.get_doc('User', frappe.session.user)
	cust = frappe.db.get_value("Customer", {"user": user.name}, "name")
	
	if cust:
		customer = frappe.get_doc("Customer", cust)
		image = user.user_image or ""

		if image.startswith("/private") or image.startswith('/public') or image.startswith('/files'):
			image = f"{frappe.utils.get_url()}{image}"

		if customer and customer.customer_primary_address: 
			info=get_dashboard_info("Customer",customer.name)
			total=0
			for i in info:
				total+=i["total_unpaid"]

			address = frappe.get_doc("Address", customer.customer_primary_address)
			frappe.response["message"] = {

				"message":"Logged In",
				"name":user.full_name,
				"customer":customer.name or "",
				"mobile_no":user.mobile_no,
				"email":user.name,
				"address": address.address_line1 or "",
				"city":address.city or "",
				"gstin":address.gstin or "",
				"outstanding":total or 0.0,
				"pincode":address.pincode or "",
				"user_image": image
		}

		elif customer:
			frappe.response["message"] = {
				"message":"Logged In",
				"name":user.full_name,
				"customer":customer.name or "",
				"mobile_no":user.mobile_no,
				"email":user.email,
				"address": "",
				"city":"",
				"gstin":"",
				"pincode":"",
				"user_image": image
			}
	else:
		frappe.response["message"] = {
			"message":"Please Signup",
		}

@frappe.whitelist(allow_guest=True)
def signup(args):
#    args=json.loads(args)
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
	if args["gstin"]:
		customer.gstin = args["gstin"]
		customer.gst_category="Registered Regular"
	customer.user = user.name
	customer.save(ignore_permissions = True)

	address = frappe.new_doc("Address")
	address.address_title = args["name"]
	address.address_line1 = args["address"]
	address.city = args["city"]
	address.state = args.get("state")
	address.gst_state = args.get('state')
	if args["gstin"]:
		address.gstin = args["gstin"]
		address.gst_category="Registered Regular"
	# address.district = args["district"] or ""
	address.pincode = args["pincode"]
	address.append('links', {
				"link_doctype": "Customer",
				"link_name": customer.name
				})
	address.save(ignore_permissions = True)
	contact = frappe.new_doc("Contact")
	contact.first_name=args["name"]
	contact.email_id=args["email"]
	contact.user=args["email"]
	contact.mobile_no=args["mobile_no"]
	contact.append('email_ids',{
		"email_id":args["email"],
		"is_primary":1
	})
	contact.append('phone_nos',{
		"phone":args["mobile_no"],
		"is_primary_mobile_no":1

	})
	contact.append('links',{
		"link_doctype": "Customer",
		"link_name": customer.name

	})
	contact.save(ignore_permissions = True)
	customer.customer_primary_address = address.name
	customer.customer_primary_contact = contact.name
	customer.save(ignore_permissions = True)


	data["message"] = "Account Created, Please Login"
	return data



@frappe.whitelist()
def pricing_rule():
	data={}
	pricing_rule = frappe.db.get_all("Pricing Rule",filters={"selling":1,"disable":0})

	for j in pricing_rule:
		pricing_doc = frappe.get_doc("Pricing Rule",j['name'])
		j.update({
			"name":pricing_doc.title,
			"display":pricing_doc.title,
			"offer_id":pricing_doc.name,
			"applicable_for":pricing_doc.applicable_for,
			"valid_from":pricing_doc.valid_from,
			"valid_upto":pricing_doc.valid_upto,
			"min_qty":pricing_doc.min_qty})
		item_list = []
		for item in pricing_doc.items:
			item_details = frappe._dict()
			item_details.update({
				"item":item.item_code
				
			})
			item_list.append(item_details)
		j.update({
			"items":item_list
		})
	data["price_list"]=pricing_rule

	return data

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
def sitelit_with_orderitems():
	data={}
	site_list=frappe.get_all("Project",{"customer":"testing"})
	for k in site_list:
		salesdoc_list=frappe.get_all("Sales Order",{"project":k['name']})
		for j in salesdoc_list:
			salesord_doc = frappe.get_doc('Sales Order',j['name'])
			
			item_list = []
			for item in salesord_doc.items:
				item_details = frappe._dict()
				item_details.update({
					"item":item.item_code,
					"qty":item.qty,
					"image":f"""{"http://"+frappe.local.request.host+item.image}"""
					
				})
				item_list.append(item_details)
				j.update({
					"cart_items":item_list
				})
	data["site_list"]=salesdoc_list
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
		project_doc.save(ignore_permissions = True)
		address = frappe.new_doc("Address")
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
			"message": "Couldn't create sales order",
			"indicator": "red"
		}
		return

	so_doc = frappe.get_doc("Sales Order", sales_order)
	doc = frappe.copy_doc(so_doc)
	doc.delivery_date = delivery_date
	if frappe.db.exists("Sales Order", {
		"docstatus": 0,
		"project": so_doc.project
	}):
		sales_order = frappe.get_doc("Sales Order", {
			"docstatus": 0,
			"project": so_doc.project
		})
		items = sales_order.get("items") or []
		append_items = []
		added_item = []
		for row in (doc.get("items") or []):
			add = False
			for i_row in items:
				if i_row.item_code == row.item_code and row.item_code not in added_item:
					i_row.qty += row.qty or 0
					add = True
					added_item.append(row.item_code)
					continue
			
			if not add:
				append_items.append(row)
		
		items += append_items

		sales_order.update({
			"items": items
		})
		sales_order.save()

	else:
		doc.save()

	frappe.local.response["show_alert"] = {
			"message": "New Order added in cart. Please find and checkout the items in cart to create sales order",
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
def get_user_imgae():
	user = frappe.get_doc("User", frappe.session.user)
	image = user.user_image or ""

	if image.startswith("/private") or image.startswith('/public') or image.startswith('/files'):
		image = f"{frappe.utils.get_url()}{image}"

	return image