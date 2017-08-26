# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "commision"
app_title = "Commision"
app_publisher = "bobzz"
app_description = "COmmision For Rsi"
app_icon = "octicon octicon-law"
app_color = "grey"
app_email = "bobzz.zone@gmail.com"
app_license = "MIT"
boot_session = "commision.boot.boot_session"
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/commision/css/commision.css"
# app_include_js = "/assets/commision/js/commision.js"

# include js, css files in header of web template
# web_include_css = "/assets/commision/css/commision.css"
# web_include_js = "/assets/commision/js/commision.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "commision.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "commision.install.before_install"
# after_install = "commision.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "commision.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"commision.tasks.all"
# 	],
# 	"daily": [
# 		"commision.tasks.daily"
# 	],
# 	"hourly": [
# 		"commision.tasks.hourly"
# 	],
# 	"weekly": [
# 		"commision.tasks.weekly"
# 	]
# 	"monthly": [
# 		"commision.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "commision.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "commision.event.get_events"
# }

