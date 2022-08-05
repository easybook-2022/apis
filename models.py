from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from info import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + user + ':' + password + '@' + host + '/' + database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = database

db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(10), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	info = db.Column(db.String(155))

	def __init__(self, cellnumber, password, username, info):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.info = info

	def __repr__(self):
		return '<User %r>' % self.cellnumber

class Owner(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(15), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	profile = db.Column(db.String(70))
	hours = db.Column(db.String(900))
	info = db.Column(db.String(110))

	def __init__(self, cellnumber, password, username, profile, hours, info):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.profile = profile
		self.hours = hours
		self.info = info

	def __repr__(self):
		return '<Owner %r>' % self.cellnumber

class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	phonenumber = db.Column(db.String(10), unique=True)
	logo = db.Column(db.String(70))
	longitude = db.Column(db.String(20))
	latitude = db.Column(db.String(20))
	owners = db.Column(db.Text)
	type = db.Column(db.String(20))
	hours = db.Column(db.String(710))
	info = db.Column(db.String(720))

	def __init__(
		self, 
		name, phonenumber, logo, 
		longitude, latitude, owners, type, hours, info
	):
		self.name = name
		self.phonenumber = phonenumber
		self.logo = logo
		self.longitude = longitude
		self.latitude = latitude
		self.owners = owners
		self.type = type
		self.hours = hours
		self.info = info

	def __repr__(self):
		return '<Location %r>' % self.name

class DiningTable(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tableId = db.Column(db.String(22), unique=True)
	name = db.Column(db.String(20))
	locationId = db.Column(db.Integer)
	orders = db.Column(db.Text)
	status = db.Column(db.String(7))

	def __init__(
		self,
		tableId, name, locationId, orders, status
	):
		self.tableId = tableId
		self.name = name
		self.locationId = locationId
		self.orders = orders
		self.status = status

	def __repr__(self):
		return '<Table %r>' % self.name

class DiningRecord(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tableId = db.Column(db.String(22))
	orders = db.Column(db.Text)
	time = db.Column(db.String(95), unique=True)

	def __init__(
		self,
		tableId, orders, time
	):
		self.tableId = tableId
		self.orders = orders
		self.time = time

	def __repr__(self):
		return '<DiningPaymentRecords %r>' % self.name

class Menu(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	parentMenuId = db.Column(db.String(10))
	name = db.Column(db.String(200))
	description = db.Column(db.String(200))
	image = db.Column(db.String(70))

	def __init__(self, locationId, parentMenuId, name, description, image):
		self.locationId = locationId
		self.parentMenuId = parentMenuId
		self.name = name
		self.description = description
		self.image = image

	def __repr__(self):
		return '<Menu %r>' % self.name

class Service(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.String(10))
	name = db.Column(db.String(200))
	description = db.Column(db.String(300))
	image = db.Column(db.String(70))
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, description, image, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.description = description
		self.image = image
		self.price = price

	def __repr__(self):
		return '<Service %r>' % self.name

class Schedule(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer)
	workerId = db.Column(db.Integer)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.String(10))
	serviceId = db.Column(db.Integer)
	userInput = db.Column(db.String(70))
	day = db.Column(db.Integer)
	month = db.Column(db.Integer)
	date = db.Column(db.Integer)
	year = db.Column(db.Integer)
	hour = db.Column(db.Integer)
	minute = db.Column(db.Integer)
	status = db.Column(db.String(15))
	cancelReason = db.Column(db.String(200))
	locationType = db.Column(db.String(15))
	customers = db.Column(db.Text)
	note = db.Column(db.String(225))
	orders = db.Column(db.Text)
	info = db.Column(db.String(100))

	def __init__(self, userId, workerId, locationId, menuId, serviceId, userInput, day, month, date, year, hour, minute, status, cancelReason, locationType, customers, note, orders, info):
		self.userId = userId
		self.workerId = workerId
		self.locationId = locationId
		self.menuId = menuId
		self.serviceId = serviceId
		self.userInput = userInput
		self.day = day
		self.month = month
		self.date = date
		self.year = year
		self.status = status
		self.cancelReason = cancelReason
		self.locationType = locationType
		self.customers = customers
		self.note = note
		self.orders = orders
		self.info = info

	def __repr__(self):
		return '<Appointment %r>' % self.time

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.String(10))
	number = db.Column(db.String(10))
	name = db.Column(db.String(200))
	description = db.Column(db.String(300))
	image = db.Column(db.String(70))
	options = db.Column(db.Text)
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, number, name, description, image, options, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.description = description
		self.image = image
		self.options = options
		self.price = price

	def __repr__(self):
		return '<Product %r>' % self.name

class Cart(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	productId = db.Column(db.Integer)
	userInput = db.Column(db.String(70))
	quantity = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	options = db.Column(db.Text)
	note = db.Column(db.String(100))
	status = db.Column(db.String(10))
	orderNumber = db.Column(db.String(20))
	waitTime = db.Column(db.String(50))

	def __init__(self, locationId, productId, userInput, quantity, adder, options, note, status, orderNumber, waitTime):
		self.locationId = locationId
		self.productId = productId
		self.userInput = userInput
		self.quantity = quantity
		self.adder = adder
		self.options = options
		self.note = note
		self.status = status
		self.orderNumber = orderNumber
		self.waitTime = waitTime

	def __repr__(self):
		return '<Cart %r>' % self.productId
