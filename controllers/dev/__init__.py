from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, os, json, stripe
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from twilio.rest import Client

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
stripe.api_key = "sk_test_lft1B76yZfF2oEtD5rI3y8dz"

account_sid = "AC8c3cd78674e391f0834a086891304e52"
auth_token = "b7f9e3b46ac445302a4a0710e95f44c1"
mss = "MG376dcb41368d7deca0bda395f36bf2a7"
client = Client(account_sid, auth_token)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(10), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	profile = db.Column(db.String(25))
	info = db.Column(db.String(60))

	def __init__(self, cellnumber, password, username, profile, info):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.profile = profile
		self.info = info

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
	name = db.Column(db.String(50))
	addressOne = db.Column(db.String(50))
	addressTwo = db.Column(db.String(50))
	city = db.Column(db.String(50))
	province = db.Column(db.String(50))
	postalcode = db.Column(db.String(7))
	phonenumber = db.Column(db.String(10), unique=True)
	logo = db.Column(db.String(20))
	longitude = db.Column(db.String(15))
	latitude = db.Column(db.String(15))
	owners = db.Column(db.Text)
	type = db.Column(db.String(20))
	hours = db.Column(db.Text)
	accountId = db.Column(db.String(25))
	state = db.Column(db.String(6))

	def __init__(
		self, 
		name, addressOne, addressTwo, city, province, postalcode, phonenumber, logo, 
		longitude, latitude, owners, type, hours, accountId, state
	):
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
		self.accountId = accountId
		self.state = state

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

class Schedule(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	serviceId = db.Column(db.Text)
	time = db.Column(db.String(15))
	status = db.Column(db.String(10))
	cancelReason = db.Column(db.String(200))
	nextTime = db.Column(db.String(15))
	locationType = db.Column(db.String(15))
	customers = db.Column(db.Text)
	note = db.Column(db.String(225))
	orders = db.Column(db.Text)
	table = db.Column(db.String(20))

	def __init__(self, userId, locationId, menuId, serviceId, time, status, cancelReason, nextTime, locationType, customers, note, orders, table):
		self.userId = userId
		self.locationId = locationId
		self.menuId = menuId
		self.serviceId = serviceId
		self.time = time
		self.status = status
		self.cancelReason = cancelReason
		self.nextTime = nextTime
		self.locationType = locationType
		self.customers = customers
		self.note = note
		self.orders = orders
		self.table = table

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
	others = db.Column(db.Text)
	sizes = db.Column(db.String(150))
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, info, image, options, others, sizes, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.info = info
		self.image = image
		self.options = options
		self.others = others
		self.sizes = sizes
		self.price = price

	def __repr__(self):
		return '<Product %r>' % self.name

class Cart(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	productId = db.Column(db.Integer)
	quantity = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(225))
	note = db.Column(db.String(100))
	status = db.Column(db.String(10))
	orderNumber = db.Column(db.String(10))

	def __init__(self, locationId, productId, quantity, adder, callfor, options, others, sizes, note, status, orderNumber):
		self.locationId = locationId
		self.productId = productId
		self.quantity = quantity
		self.adder = adder
		self.callfor = callfor
		self.options = options
		self.others = others
		self.sizes = sizes
		self.note = note
		self.status = status
		self.orderNumber = orderNumber

	def __repr__(self):
		return '<Cart %r>' % self.productId

class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	groupId = db.Column(db.String(20)) # same for each cart
	productId = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(150))
	time = db.Column(db.String(15))

	def __init__(self, groupId, productId, adder, callfor, options, others, sizes, time):
		self.groupId = groupId
		self.productId = productId
		self.adder = adder
		self.callfor = callfor
		self.options = options
		self.others = others
		self.sizes = sizes
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

@app.route("/")
def welcome_dev():
	num = str(randint(0, 9))

	return { "msg": "welcome to dev of easygo: " + num }

@app.route("/reset")
def reset():
	delete = False
	users = query("select * from user", True)
	
	for user in users:
		delete = True
		info = json.loads(user['info'])

		stripe.Customer.delete(info['customerId'])

		query("delete from user where id = " + str(user['id']), False)

	if delete == True:
		query("ALTER table user auto_increment = 1", False)

	delete = False
	owners = query("select * from owner", True)
	for owner in owners:
		delete = True
		query("delete from owner where id = " + str(owner['id']), False)

	if delete == True:
		query("ALTER table owner auto_increment = 1", False)

	delete = False
	locations = query("select * from location", True)
	for location in locations:
		delete = True
		logo = location['logo']
		accountid = location['accountId']

		stripe.Account.delete(accountid)

		if logo != "" and os.path.exists("static/" + logo):
			os.remove("static/" + logo)

		query("delete from location where id = " + str(location['id']), False)

	if delete == True:
		query("ALTER table location auto_increment = 1", False)

	delete = False
	menus = query("select * from menu", True)
	for menu in menus:
		delete = True
		image = menu['image']

		if image != "" and os.path.exists("static/" + image):
			os.remove("static/" + image)

		query("delete from menu where id = " + str(menu['id']), False)

	if delete == True:
		query("ALTER table menu auto_increment = 1", False)

	delete = False
	services = query("select * from service", True)
	for service in services:
		delete = True
		image = service['image']

		if image != "" and os.path.exists("static/" + image):
			os.remove("static/" + image)

		query("delete from service where id = " + str(service['id']), False)

	if delete == True:
		query("ALTER table service auto_increment = 1", False)

	delete = False
	schedules = query("select * from schedule", True)
	for schedule in schedules:
		delete = True

		query("delete from schedule where id = " + str(schedule['id']), False)

	if delete == True:
		query("ALTER table schedule auto_increment = 1", False)

	delete = False
	products = query("select * from product", True)
	for product in products:
		delete = True
		image = product['image']

		if image != "" and os.path.exists("static/" + image):
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
			if file != "" and os.path.exists("static/" + file):
				os.remove("static/" + file)		

	return { "reset": True }

@app.route("/charge/<id>")
def charge(id):
	user = User.query.filter_by(id=id).first()

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]
		amount = 2.00

		stripe.Charge.create(
			amount=int(amount * 100),
			currency="cad",
			customer=customerid,
			description="this is a test charge for user: " + user.username
		)

		return { "msg": "charge of $ 2.00 works on " + user.username }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/payout/<id>")
def payout(id):
	location = Location.query.filter_by(id=id).first()

	if location != None:
		data = stripe.Balance.retrieve()
		balance = data.available[0].amount
		amount = 2.00

		if balance > amount:
			accountid = location.accountId

			stripe.Transfer.create(
				amount=int(amount * 100),
				currency="cad",
				destination=accountid
			)

			return { "msg": "transfer of $ 2.00 to " + location.name + " works" }
		else:
			msg = "Balance is " + str(balance) + " which isn't enough"
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }

@app.route("/twilio_test")
def twilio_test():
	'''incoming_phone_number = client.incoming_phone_numbers \
		.create(
			phone_number='+15005550006',
			voice_url='http://demo.twilio.com/docs/voice.xml'
		)'''

	message = client.messages.create(
		body='All in the game, yo',
		messaging_service_sid=mss,
		to='+16479263868'
	)

	print(message)

	return { "message": message.sid }
