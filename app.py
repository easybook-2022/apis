from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.shared_data import SharedDataMiddleware

from controllers.dev import app as dev_controller
from controllers.users import app as users_controller
from controllers.owners import app as owners_controller
from controllers.locations import app as locations_controller
from controllers.dining_tables import app as dining_tables_controller
from controllers.menus import app as menus_controller
from controllers.products import app as products_controller
from controllers.carts import app as carts_controller
from controllers.services import app as services_controller
from controllers.schedules import app as schedules_controller
from info import *
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + user + ':' + password + '@' + host + '/' + database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = database

db.init_app(app)
migrate = Migrate(app, db, compare_type=True)

app.wsgi_app = DispatcherMiddleware(None, {
  '/flask/dev': dev_controller,
	'/flask/users': users_controller,
	'/flask/owners': owners_controller,
	'/flask/locations': locations_controller,
	'/flask/dining_tables': dining_tables_controller,
	'/flask/menus': menus_controller,
	'/flask/products': products_controller,
	'/flask/carts': carts_controller,
	'/flask/services': services_controller,
	'/flask/schedules': schedules_controller
})

app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
	'/flask/static': os.path.join(os.path.dirname(__file__), 'static')
})

if __name__ == "__main__":
	run_simple(apphost, 5001, app, use_reloader=True, use_debugger=True, use_evalex=True)
