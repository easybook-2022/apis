from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, os
from werkzeug.security import generate_password_hash, check_password_hash

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
	username = db.Column(db.String(20))
	profile = db.Column(db.String(25))

	def __init__(self, cellnumber, password, username, profile):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.profile = profile

	def __repr__(self):
		return '<User %r>' % self.cellnumber

class Owner(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(15), unique=True)
	password = db.Column(db.String(110), unique=True)
	locationId = db.Column(db.Text)

	def __init__(self, cellnumber, password, locationId):
		self.cellnumber = cellnumber
		self.password = password
		self.locationId = locationId

	def __repr__(self):
		return '<Owner %r>' % self.cellnumber

class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
	addressOne = db.Column(db.String(30))
	addressTwo = db.Column(db.String(20))
	city = db.Column(db.String(20))
	province = db.Column(db.String(20))
	postalcode = db.Column(db.String(7))
	phonenumber = db.Column(db.String(10), unique=True)
	logo = db.Column(db.String(20))
	longitude = db.Column(db.String(15))
	latitude = db.Column(db.String(15))
	owners = db.Column(db.Text)
	type = db.Column(db.String(20))
	hours = db.Column(db.Text)

	def __init__(self, name, addressOne, addressTwo, city, province, postalcode, phonenumber, logo, longitude, latitude, owners, type, hours):
		self.name = name
		self.addressOne = addressOne
		self.addressTwo = addressTwo
		self.city = city
		self.province = province
		self.postalcode = postalcode
		self.phonenumber = phonenumber
		self.logo = logo
		self.longitude = longitude
		self.latitude = latitude
		self.owners = owners
		self.type = type
		self.hours = hours

	def __repr__(self):
		return '<Location %r>' % self.name

class Menu(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	parentMenuId = db.Column(db.Text)
	name = db.Column(db.String(20))
	info = db.Column(db.String(100))
	image = db.Column(db.String(20))

	def __init__(self, locationId, parentMenuId, name, info, image):
		self.locationId = locationId
		self.parentMenuId = parentMenuId
		self.name = name
		self.info = info
		self.image = image

	def __repr__(self):
		return '<Menu %r>' % self.name

class Service(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	name = db.Column(db.String(20))
	info = db.Column(db.Text)
	image = db.Column(db.String(20))
	price = db.Column(db.String(10))
	duration = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, info, image, price, duration):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.info = info
		self.image = image
		self.price = price
		self.duration = duration

	def __repr__(self):
		return '<Service %r>' % self.name
		
class Appointment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	serviceId = db.Column(db.Text)
	time = db.Column(db.String(15))
	status = db.Column(db.String(10))
	cancelReason = db.Column(db.String(200))
	nextTime = db.Column(db.String(15))

	def __init__(self, userId, locationId, menuId, serviceId, time, status, cancelReason, nextTime):
		self.userId = userId
		self.locationId = locationId
		self.menuId = menuId
		self.serviceId = serviceId
		self.time = time
		self.status = status
		self.cancelReason = cancelReason
		self.nextTime = nextTime

	def __repr__(self):
		return '<Appointment %r>' % self.time

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	name = db.Column(db.String(20))
	info = db.Column(db.String(100))
	image = db.Column(db.String(20))
	options = db.Column(db.Text)
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, info, image, options, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.info = info
		self.image = image
		self.options = options
		self.price = price

	def __repr__(self):
		return '<Product %r>' % self.name

class Cart(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	productId = db.Column(db.Integer)
	quantity = db.Column(db.Integer)
	adder = db.Column(db.String(20))
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)

	def __init__(self, productId, quantity, adder, callfor, options):
		self.productId = productId
		self.quantity = quantity
		self.adder = adder
		self.callfor = callfor
		self.options = options

	def __repr__(self):
		return '<Cart %r>' % self.productId

class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	groupId = db.Column(db.String(20)) # same for each cart
	productId = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	time = db.Column(db.String(15))

	def __init__(self, groupId, productId, adder, callfor, options, time):
		self.groupId = groupId
		self.productId = productId
		self.adder = adder
		self.callfor = callfor
		self.options = options
		self.time = time

	def __repr__(self):
		return '<Transaction %r>' % self.groupId

def query(sql, output):
	dbconn = pymysql.connect(
		host=host, user=user,
		password=password, db=database,
		charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor, 
		autocommit=True
	)

	cursorobj = dbconn.cursor()
	cursorobj.execute(sql)

	if output == True:
		results = cursorobj.fetchall()

		return results

@app.route("/reset")
def reset():
	delete = False
	owners = query("select * from owner", True)
	for owner in owners:
		delete = True
		query("delete from owner where id = " + str(owner['id']), False)

	if delete == True:
		query("ALTER table owner auto_increment = 1", False)

	delete = False
	users = query("select * from user", True)
	for user in users:
		delete = True
		query("delete from user where id = " + str(user['id']), False)

	if delete == True:
		query("ALTER table user auto_increment = 1", False)

	delete = False
	locations = query("select * from location", True)
	for location in locations:
		delete = True
		logo = location['logo']

		if os.path.exists("static/" + logo):
			os.remove("static/" + logo)

		query("delete from location where id = " + str(location['id']), False)

	if delete == True:
		query("ALTER table location auto_increment = 1", False)

	delete = False
	menus = query("select * from menu", True)
	for menu in menus:
		delete = True
		image = menu['image']

		if os.path.exists("static/" + image):
			os.remove("static/" + image)

		query("delete from menu where id = " + str(menu['id']), False)

	if delete == True:
		query("ALTER table menu auto_increment = 1", False)

	delete = False
	services = query("select * from service", True)
	for service in services:
		delete = True
		image = service['image']

		if os.path.exists("static/" + image):
			os.remove("static/" + image)

		query("delete from service where id = " + str(service['id']), False)

	if delete == True:
		query("ALTER table service auto_increment = 1", False)

	delete = False
	products = query("select * from product", True)
	for product in products:
		delete = True
		image = product['image']

		if os.path.exists("static/" + image):
			os.remove("static/" + image)

		query("delete from product where id = " + str(product['id']), False)

	if delete == True:
		query("ALTER table product auto_increment = 1", False)

	delete = False
	carts = query("select * from cart", True)
	for cart in carts:
		delete = True

		query("delete from cart where id = " + str(cart['id']), False)

	if delete == True:
		query("ALTER table cart auto_increment = 1", False)

	delete = False
	transactions = query("select * from transaction", True)
	for transaction in transactions:
		delete = True

		query("delete from transaction where id = " + str(transaction['id']), False)

	if delete == True:
		query("ALTER table transaction auto_increment = 1", False)

	files = os.listdir("static")

	for file in files:
		if ".jpg" in file:
			if os.path.exists("static/" + file):
				os.remove("static/" + file)

	return { "reset": True }

@app.route("/insert")
def insert():
	owner = Owner('["6479263868"]', 'pbkdf2:sha256:260000$BzgxZLKtKboLRanr$23dfb9509c7b66274be23a027845cf77cea26fbcaa92ce0a5ad0d39dca17d829')

	db.session.add(owner)
	db.session.commit()

	return { "msg": "" }
