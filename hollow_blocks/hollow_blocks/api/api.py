from hollow_blocks.hollow_blocks.api.sitecartlist import get_item_image_attachments
import frappe
from json import loads
import json
import re
from frappe.utils import today
from erpnext.accounts.party import get_dashboard_info

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
				"total_qty":sales_doc.total_qty,
				"net_total":sales_doc.total,
				"tax_amount":sales_doc.total_taxes_and_charges,
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
				"total_qty":dn_doc.total_qty,
				"net_total":dn_doc.total,
				"tax_amount":dn_doc.total_taxes_and_charges,
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
			pay_doc = frappe.get_doc('Payment Entry',m['name'])
			m.update({
				
				"date":pay_doc.posting_date,
				"mode_of_payment":pay_doc.mode_of_payment,"paid_amount":pay_doc.paid_amount})
				
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
		sales_inv_list = frappe.db.get_all('Sales Invoice',filters={"customer":args["customer"],"status":args["status"]})
		

		for j in sales_inv_list:
			sales_doc = frappe.get_doc('Sales Invoice',j['name'])
			j.update({
				"status":sales_doc.status,
				"posting_date":sales_doc.posting_date,
				"total_qty":sales_doc.total_qty,
				"net_total":sales_doc.total,
				"tax_amount":sales_doc.total_taxes_and_charges,
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
				"total_qty":sales_doc.total_qty,
				"net_total":sales_doc.total,
				"tax_amount":sales_doc.total_taxes_and_charges,
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
				"total_qty":dn_doc.total_qty,
				"net_total":dn_doc.total,
				"tax_amount":dn_doc.total_taxes_and_charges,
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
				"total_qty":sales_doc.total_qty,
				"net_total":sales_doc.total,
				"tax_amount":sales_doc.total_taxes_and_charges,
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
	project=frappe.get_meta('Project').get_field('status').options
	data["sales_order"]=sales_order.split("\n")
	data["sales_invoice"]=sales_invoice.split("\n")
	data["delivery_note"]=delivery_note.split("\n")
	data["project"]=project.split("\n")
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
		if customer and customer.customer_primary_address: 
			info=get_dashboard_info("Customer",customer.name)
			total=0
			for i in info:
				total+=i["total_unpaid"]

			address = frappe.get_doc("Address", customer.customer_primary_address)
			frappe.response["message"] = {

				"message":"Logged In",
				"token":token,
				"name":user.full_name,
				"customer":customer.name or "",
				"mobile_no":user.mobile_no,
				"email":user.name,
				"address": address.address_line1 or "",
				"city":address.city or "",
				"gstin":address.gstin or "",
				"outstanding":total or "",
				"pincode":address.pincode or "",
				
		}

		elif customer:
			frappe.response["message"] = {

				"message":"Logged In",
				"token":token,
				"name":user.full_name,
				"customer":customer.name or "",
				"mobile_no":user.mobile_no,
				"email":user.email,
				"address": "",
				"city":"",
				"refered_by":"",
				"gstin":"",
				"pincode":"",
				
			}
	else:
		frappe.response["message"] = {

			"message":"Please Signup",
			
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



@frappe.whitelist(allow_guest=True)
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
				"item":item.item_code,
				
			})
			item_list.append(item_details)
		j.update({
			"items":item_list
		})
	data["price_list"]=pricing_rule

	return data

@frappe.whitelist(allow_guest=True)
def site_list(args):
	# args=json.loads(args)
	data={}
	## site list
	if(args["customer"] and args["status"]):
		site_list = frappe.db.get_all('Project',filters={"customer":args["customer"],"status":args["status"]})
		

		for m in site_list:
			project_doc = frappe.get_doc('Project',m['name'])
			m.update({
				"status":project_doc.status,
				"name":project_doc.project_name,
				"id":project_doc.name
				})
	else:
		site_list = frappe.db.get_all('Project',filters={"customer":args["customer"]})
	
		for m in site_list:
			project_doc = frappe.get_doc('Project',m['name'])
			m.update({
				"status":project_doc.status,
				"name":project_doc.project_name,
				"id":project_doc.name
				})

	data["site_list"]=site_list

	return data
	
		
		
		

@frappe.whitelist(allow_guest=True)
def item_group_list():
	final_list=[]
	item_group=frappe.get_all("Item Group")
	for i in item_group:
		final_list.append(i["name"])
	return final_list

@frappe.whitelist(allow_guest=True)
def item_list():
	
	item_list = item_list=frappe.get_all("Item",filters={"disabled":0,"has_variants":0},fields=["item_code","description","stock_uom as uom","item_group","name"])
		
	for m in item_list:	
		m.update({"currency":"₹","favourite":True,"offer":"","price_list_rate":""})
		v=frappe.get_all("Item Price",filters={"item_code":m["item_code"],"selling":1,"price_list":"Standard Selling","valid_from":("<=",today())},fields=["name"])
		discount=frappe.get_all("Pricing Rule Item Code")
		
		if v:
			d=frappe.get_doc("Item Price",v[0]["name"])
			m.update({"price_list_rate":d.price_list_rate,})
		
		m.update({
		"image":get_item_image_attachments(m['item_code'], {})
		})
		for j in frappe.get_all("Pricing Rule",filters={"disable":0,"selling":1,"apply_on":"Item Code"}):
			pricing_doc=frappe.get_doc("Pricing Rule",j["name"])
			for i in pricing_doc.items:
				if i.item_code == m["item_code"]:
					m.update({
						"offer_id":pricing_doc.name})
					if pricing_doc.rate_or_discount == "Discount Percentage":
						m.update({
						"offer":str(pricing_doc.discount_percentage or 0) + "%"})
					if pricing_doc.rate_or_discount == "Discount Amount":
						m.update({
						"offer":str(pricing_doc.discount_amount or 0) + " Amount Discount"})
					if pricing_doc.min_qty:
						m.update({
						"min_qty":pricing_doc.min_qty,
						})
					if pricing_doc.max_qty:
						m.update({
						"max_qty":pricing_doc.max_qty,
						})
					if pricing_doc.min_amt:
						m.update({
						"max_qty":pricing_doc.min_amt,
						})
					if pricing_doc.max_amt:
						m.update({
						"max_qty":pricing_doc.max_amt,
						})


	return item_list




@frappe.whitelist(allow_guest=True)
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
   generate_token(user)
   return {"message": "Successfully Logged Out"}



@frappe.whitelist()
def site_creation(args):
	try:
		project_doc=frappe.new_doc("Project")
		project_doc.project_name=args["site_name"]
		project_doc.customer=args["customer"]
		project_doc.save(ignore_permissions = True)
		address = frappe.new_doc("Address")
		address.address_title = args["site_name"]
		address.address_line1 = args["address"]
		address.city = args["city"]
		address.pincode = args["pincode"]
		address.append('links', {
					"link_doctype": "Project",
					"link_name": project_doc.name
					})
		address.save(ignore_permissions = True)
		project_doc.address=address.name
		project_doc.save(ignore_permissions = True)
		return {"message": "Successfully Site Created"}
	except:
		return {"message": "Site Creation Failed Once Check Enter Deatils"}


@frappe.whitelist()
def site_status_updation(args):
	try:
		project_doc=frappe.get_doc("Project",args["id"])
		project_doc.status=args["status"]
		project_doc.save(ignore_permissions=True)
		return {"message": "Successfully Site Status Updated"}
	except:
		return {"message": "Site Status Updation Failed Once Check Enter Deatils"}
