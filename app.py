from flask import Flask, request, jsonify
from werkzeug.serving import run_simple
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.shared_data import SharedDataMiddleware

from controllers.users import app as users_controller
from controllers.locations import app as locations_controller
from controllers.menus import app as menus_controller
from controllers.products import app as products_controller

local = True

host = 'localhost'
user = 'geottuse'
password = 'G3ottu53?'
database = 'easygo'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + user + ':' + password + '@' + host + '/' + database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = database

db = SQLAlchemy(app)
mydb = mysql.connector.connect(
	host=host,
	user=user,
	password=password,
	database=database
)
mycursor = mydb.cursor()
migrate = Migrate(app, db)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(10), unique=True)
	password = db.Column(db.String(110), unique=True)

	def __init__(self, cellnumber, password):
		self.cellnumber = cellnumber
		self.password = password

	def __repr__(self):
		return '<User %r>' % self.cellnumber

class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
	addressOne = db.Column(db.String(30))
	addressTwo = db.Column(db.String(20))
	city = db.Column(db.String(20))
	province = db.Column(db.String(20))
	postalcode = db.Column(db.String(7))
	logo = db.Column(db.String(20))
	longitude = db.Column(db.String(15))
	latitude = db.Column(db.String(15))
	owners = db.Column(db.Text)

	def __init__(self, name, addressOne, addressTwo, city, province, postalcode, logo, longitude, latitude, owners):
		self.name = name
		self.addressOne = addressOne
		self.addressTwo = addressTwo
		self.city = city
		self.province = province
		self.postalcode = postalcode
		self.logo = logo
		self.longitude = longitude
		self.latitude = latitude
		self.owners = owners

	def __repr__(self):
		return '<Location %r>' % self.name

class Menu(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	categories = db.Column(db.Text)
	name = db.Column(db.String(20))
	image = db.Column(db.String(20))

	def __init__(self, locationId, categories, name, image):
		self.locationId = locationId
		self.categories = categories
		self.name = name
		self.image = image

	def __repr__(self):
		return '<Menu %r>' % self.name

class Service(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Integer)
	name = db.Column(db.String(20))
	info = db.Column(db.Text)
	image = db.Column(db.String(20))

	def __init__(self, locationId, menuId, name, info, image):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.info = info
		self.image = image

	def __repr__(self):
		return '<Service %r>' % self.name

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Integer)
	name = db.Column(db.String(20))
	image = db.Column(db.String(20))
	options = db.Column(db.Text)
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, options, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.image = image
		self.options = options
		self.price = price

	def __repr__(self):
		return '<Product %r>' % self.name

app.wsgi_app = DispatcherMiddleware(None, {
	'/users': users_controller,
	'/locations': locations_controller,
	'/menus': menus_controller,
	'/products': products_controller
})

app = SharedDataMiddleware(app, {
    '/static': os.path.join(os.path.dirname(__file__), 'static')
})

if __name__ == "__main__":
	run_simple("192.168.0.150", 5000, app, use_reloader=True, use_debugger=True, use_evalex=True)
