import frappe
from json import loads
import json
import re

@frappe.whitelist(allow_guest=True)
def transactions(args):
	# args=json.loads(args)
	data={}
	result=[]
	if(args["customer"] and args["status"]):
		## sales order
		sales_ord_list = frappe.db.get_all('Sales Order',filters={"customer":args["customer"],"status":args["status"]})
		
		for i in sales_ord_list:
			sales_doc = frappe.get_doc('Sales Order',i['name'])
			i.update({
				"status":sales_doc.status,
				"delivery_date":sales_doc.delivery_date,
				"grand_total":sales_doc.grand_total})
			item_list = []
			for item in sales_doc.items:
				item_details = frappe._dict()
				item_details.update({
					"item":item.item_code,
					"item_name":item.item_name,
					"qty":item.qty,
					"amount":item.amount
				})
				item_list.append(item_details)
			i.update({
				"items":item_list
			})
		## Delivery Note
		delivery_note_list = frappe.db.get_all('Delivery Note',filters={"customer":args["customer"],"status":args["status"]})
		
		for k in delivery_note_list:
			dn_doc = frappe.get_doc('Delivery Note',k['name'])
			k.update({
				"status":dn_doc.status,
				"delivery_date":dn_doc.posting_date,
				"grand_total":dn_doc.grand_total})
			item_list = []
			for item in dn_doc.items:
				item_details = frappe._dict()
				item_details.update({
					"item":item.item_code,
					"item_name":item.item_name,
					"qty":item.qty,
					"amount":item.amount
				})
				item_list.append(item_details)
			k.update({
				"items":item_list
			})

		payment_entry = frappe.db.get_all('Payment Entry',filters={"party":args["customer"],"status":args["status"]})
		
		for m in payment_entry:
			pay_doc = frappe.get_doc('Payment Entry',k['name'])
			m.update({
				
				"date":pay_doc.posting_date,
				"mode_of_payment":pay_doc.mode_of_payment,"paid_amount":pay_doc.paid_amount})
				
			item_list = []
			for item in dn_doc.references:
				item_details = frappe._dict()
				item_details.update({
					"doctype":item.reference_name,
					"amount":item.total_amount,
					
				})
				item_list.append(item_details)
			m.update({
				"items":item_list
			})


		## sales invoice
		sales_inv_list = frappe.db.get_all('Sales Invoice',filters={"customer":args["customer"],"status":args["status"]})
		

		for j in sales_inv_list:
			sales_doc = frappe.get_doc('Sales Invoice',j['name'])
			j.update({
				"status":sales_doc.status,
				"posting_date":sales_doc.posting_date,
				"grand_total":sales_doc.grand_total})
			item_list = []
			for item in sales_doc.items:
				item_details = frappe._dict()
				item_details.update({
					"item":item.item_code,
					"item_name":item.item_name,
					"qty":item.qty,
					"amount":item.amount
				})
				item_list.append(item_details)
			j.update({
				"items":item_list
			})

	else:
		##sales order
		sales_ord_list = frappe.db.get_all('Sales Order',filters={"customer":args["customer"]})
		
		for i in sales_ord_list:
			sales_doc = frappe.get_doc('Sales Order',i['name'])
			i.update({
				"status":sales_doc.status,
				"delivery_date":sales_doc.delivery_date,
				"grand_total":sales_doc.grand_total})
			item_list = []
			for item in sales_doc.items:
				item_details = frappe._dict()
				item_details.update({
					"item":item.item_code,
					"item_name":item.item_name,
					"qty":item.qty,
					"amount":item.amount
				})
				item_list.append(item_details)
			i.update({
				"items":item_list
			})
		## Delivery Note
		delivery_note_list = frappe.db.get_all('Delivery Note',filters={"customer":args["customer"]})
		
		for k in delivery_note_list:
			dn_doc = frappe.get_doc('Delivery Note',k['name'])
			k.update({
				"status":dn_doc.status,
				"delivery_date":dn_doc.posting_date,
				"grand_total":dn_doc.grand_total})
			item_list = []
			for item in dn_doc.items:
				item_details = frappe._dict()
				item_details.update({
					"item":item.item_code,
					"item_name":item.item_name,
					"qty":item.qty,
					"amount":item.amount
				})
				item_list.append(item_details)
			k.update({
				"items":item_list
			})
		## payment entry
		payment_entry = frappe.db.get_all('Payment Entry',filters={"party":args["customer"]})
		
		for m in payment_entry:
			pay_doc = frappe.get_doc('Payment Entry',m['name'])
			m.update({
			
				"date":pay_doc.posting_date,
				"paid_amount":pay_doc.paid_amount,
				"mode_of_payment":pay_doc.mode_of_payment})
			item_list = []
			for item in pay_doc.references:
				item_details = frappe._dict()
				item_details.update({
					"doctype":item.reference_name,
					"amount":item.total_amount,
					
				})
				item_list.append(item_details)
			m.update({
				"items":item_list
			})

		## sales invoice
		sales_inv_list = frappe.db.get_all('Sales Invoice',filters={"customer":args["customer"]})
		

		for j in sales_inv_list:
			sales_doc = frappe.get_doc('Sales Invoice',j['name'])
			j.update({
				"status":sales_doc.status,
				"posting_date":sales_doc.posting_date,
				"grand_total":sales_doc.grand_total})
			item_list = []
			for item in sales_doc.items:
				item_details = frappe._dict()
				item_details.update({
					"item":item.item_code,
					"item_name":item.item_name,
					"qty":item.qty,
					"amount":item.amount
				})
				item_list.append(item_details)
			j.update({
				"items":item_list
			})
		

	data["sales_order"]=sales_ord_list
	data["sales_invoice"]=sales_inv_list
	data["delivery_note"]=delivery_note_list
	data["payment_list"]=payment_entry
	return data


@frappe.whitelist(allow_guest=True)
def company_details():
	# data={}
	company_dict={}
	company=frappe.get_all("Company")
	for i in company:
		comp_doc=frappe.get_doc("Company",i["name"])
		bank_doc=frappe.get_doc("Bank Account",{"is_company_account":1,"company":comp_doc.name})
		company_dict.update({
			"comp_name":comp_doc.name or "",
			"gstin":comp_doc.gstin or "",
			"pan":comp_doc.pan or "",
			"phone":comp_doc.phone_no or "",
			"bank_name":bank_doc.bank or "",
			"branch_code":bank_doc.branch_code or "",
			"acc_no":bank_doc.bank_account_no or ""
		})
	return company_dict

@frappe.whitelist(allow_guest=True)
def status_list():
	data={}
	sales_order=frappe.get_meta('Sales Order').get_field('status').options
	sales_invoice=frappe.get_meta('Sales Invoice').get_field('status').options
	delivery_note=frappe.get_meta('Delivery Note').get_field('status').options
	data["sales_order"]=sales_order.split("\n")
	data["sales_invoice"]=sales_invoice.split("\n")
	data["delivery_note"]=delivery_note.split("\n")
	return data


## Login Api
@frappe.whitelist( allow_guest=True )
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
	token = generate_token(frappe.session.user)
	frappe.db.commit()
	user = frappe.get_doc('User', frappe.session.user)
	cust = frappe.db.get_value("Customer", {"user": user.name}, "name")
	if cust:
		customer = frappe.get_doc("Customer", cust)
		frappe.response["message"] = {

			"message":"Logged In",
			"token":token,
			"name":user.full_name,
			"customer":customer.name or "",
			"dob":user.birth_date or "",
			"mobile_no":user.mobile_no,
			"email":user.email,
			"address": "",
			"city":"",
			"district": "",
			"refered_by":"",
			"gstin":"",
			"pincode":"",
			
		}
	else:
		frappe.response["message"] = {

			"message":"Logged In",
			"token":"token "+user.api_key+":"+api_generate["api_secret"],
			"name":user.full_name,
			"customer": "",
			"dob":user.birth_date or "",
			"mobile_no":user.mobile_no,
			"email":user.email,
			"address": "",
			"city":"",
			"district": "",
			"refered_by":"",
			"gstin":"",
			"pincode":"",
		}

def generate_token(user):
	user_details = frappe.get_doc("User", user)
	api_key = user_details.api_key
	api_secret = frappe.generate_hash(length=15)
	# if api key is not set generate api key
	if not user_details.api_key:
		api_key = frappe.generate_hash(length=15)
		user_details.api_key = api_key
	user_details.api_secret = api_secret
	user_details.save(ignore_permissions=True)

	return f'token {api_key}:{api_secret}'

# def generate_keys(user):
# 	"""
# 	generate api key and api secret

# 	:param user: str
# 	"""
# 	# frappe.only_for("System Manager")
# 	user_details = frappe.get_doc("User", user)
# 	api_secret = frappe.generate_hash(length=15)
# 	# if api key is not set generate api key
# 	if not user_details.api_key:
# 		api_key = frappe.generate_hash(length=15)
# 		user_details.api_key = api_key
# 	user_details.api_secret = api_secret

# 	user_details.save()

# 	return {"api_secret": api_secret}





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
