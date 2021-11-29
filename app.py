import os, mysql.connector, pymysql.cursors
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.shared_data import SharedDataMiddleware

from controllers.dev import app as dev_controller
from controllers.users import app as users_controller
from controllers.owners import app as owners_controller
from controllers.locations import app as locations_controller
from controllers.menus import app as menus_controller
from controllers.products import app as products_controller
from controllers.carts import app as carts_controller
from controllers.services import app as services_controller
from controllers.schedules import app as schedules_controller
from controllers.transactions import app as transactions_controller

from flask import Flask, request, json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from info import *

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(None, {
	'/flask/dev': dev_controller,
	'/flask/users': users_controller,
	'/flask/owners': owners_controller,
	'/flask/locations': locations_controller,
	'/flask/menus': menus_controller,
	'/flask/products': products_controller,
	'/flask/carts': carts_controller,
	'/flask/services': services_controller,
	'/flask/schedules': schedules_controller,
	'/flask/transactions': transactions_controller
})

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/flask/static': os.path.join(os.path.dirname(__file__), 'static')
})

if __name__ == "__main__":
	run_simple(apphost, 5000, app, use_reloader=True, use_debugger=True, use_evalex=True)
