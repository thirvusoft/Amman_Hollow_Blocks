from . import __version__ as app_version

app_name = "hollow_blocks"
app_title = "Hollow Blocks"
app_publisher = "TS"
app_description = "Hollow Blllllllocks"
app_email = "ts@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = ["hollow_blocks.bundle.css"]
app_include_js = ["hollow_blocks.bundle.js"]

# include js, css files in header of web template
# web_include_css = "/assets/hollow_blocks/css/hollow_blocks.css"
# web_include_js = "/assets/hollow_blocks/js/hollow_blocks.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hollow_blocks/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Lead" : "hollow_blocks/custom/js/lead.js",
"Opportunity" : "hollow_blocks/custom/js/opportunity.js",
"Sales Order" : "hollow_blocks/custom/js/Sales_order.js",
"Sales Invoice" : "hollow_blocks/custom/js/sales_invoice.js",
"Quotation" : "hollow_blocks/custom/js/quotation.js",
"Customer" : "hollow_blocks/custom/js/customer.js",
"Delivery Note" : "hollow_blocks/custom/js/delivery_note.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "hollow_blocks.utils.jinja_methods",
#	"filters": "hollow_blocks.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hollow_blocks.install.before_install"
# after_install = "hollow_blocks.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hollow_blocks.uninstall.before_uninstall"
# after_uninstall = "hollow_blocks.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hollow_blocks.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Order": {
		"on_cancel": "hollow_blocks.hollow_blocks.custom.py.sales_order.validate_cancel",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"hollow_blocks.tasks.all"
#	],
#	"daily": [
#		"hollow_blocks.tasks.daily"
#	],
#	"hourly": [
#		"hollow_blocks.tasks.hourly"
#	],
#	"weekly": [
#		"hollow_blocks.tasks.weekly"
#	],
#	"monthly": [
#		"hollow_blocks.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "hollow_blocks.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "hollow_blocks.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "hollow_blocks.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hollow_blocks.utils.before_request"]
# after_request = ["hollow_blocks.utils.after_request"]

# Job Events
# ----------
# before_job = ["hollow_blocks.utils.before_job"]
# after_job = ["hollow_blocks.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"hollow_blocks.auth.validate"
# ]
