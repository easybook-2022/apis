from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, json, os
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from info import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + user + ':' + password + '@' + host + '/' + database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = database

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(10), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	profile = db.Column(db.String(25))
	info = db.Column(db.String(155))

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
	username = db.Column(db.String(20))
	profile = db.Column(db.String(25))
	hours = db.Column(db.Text)
	info = db.Column(db.String(120))

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
	addressOne = db.Column(db.String(50))
	addressTwo = db.Column(db.String(50))
	city = db.Column(db.String(50))
	province = db.Column(db.String(50))
	postalcode = db.Column(db.String(7))
	phonenumber = db.Column(db.String(10), unique=True)
	logo = db.Column(db.String(20))
	longitude = db.Column(db.String(20))
	latitude = db.Column(db.String(20))
	owners = db.Column(db.Text)
	type = db.Column(db.String(20))
	hours = db.Column(db.Text)
	info = db.Column(db.Text)

	def __init__(
		self, 
		name, addressOne, addressTwo, city, province, postalcode, phonenumber, logo, 
		longitude, latitude, owners, type, hours, info
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
		self.info = info

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
	workerId = db.Column(db.Integer)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	serviceId = db.Column(db.Integer)
	userInput = db.Column(db.Text)
	time = db.Column(db.String(15))
	status = db.Column(db.String(10))
	cancelReason = db.Column(db.String(200))
	nextTime = db.Column(db.String(15))
	locationType = db.Column(db.String(15))
	customers = db.Column(db.Text)
	note = db.Column(db.String(225))
	orders = db.Column(db.Text)
	table = db.Column(db.String(20))
	info = db.Column(db.String(100))

	def __init__(self, userId, workerId, locationId, menuId, serviceId, userInput, time, status, cancelReason, nextTime, locationType, customers, note, orders, table, info):
		self.userId = userId
		self.workerId = workerId
		self.locationId = locationId
		self.menuId = menuId
		self.serviceId = serviceId
		self.userInput = userInput
		self.time = time
		self.status = status
		self.cancelReason = cancelReason
		self.nextTime = nextTime
		self.locationType = locationType
		self.customers = customers
		self.note = note
		self.orders = orders
		self.table = table
		self.info = info

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
	userInput = db.Column(db.Text)
	quantity = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(225))
	note = db.Column(db.String(100))
	status = db.Column(db.String(10))
	orderNumber = db.Column(db.String(10))

	def __init__(self, locationId, productId, userInput, quantity, adder, callfor, options, others, sizes, note, status, orderNumber):
		self.locationId = locationId
		self.productId = productId
		self.userInput = userInput
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
	groupId = db.Column(db.String(20))
	locationId = db.Column(db.Integer)
	productId = db.Column(db.Integer)
	serviceId = db.Column(db.Integer)
	userInput = db.Column(db.Text)
	quantity = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(200))
	time = db.Column(db.String(15))

	def __init__(self, groupId, locationId, productId, serviceId, userInput, quantity, adder, callfor, options, others, sizes, time):
		self.groupId = groupId
		self.locationId = locationId
		self.productId = productId
		self.serviceId = serviceId
		self.userInput = userInput
		self.quantity = quantity
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

def trialInfo(): # days before over | cardrequired | trialover (id, time)
	# user = User.query.filter_by(id=id).first()
	# info = json.loads(user.info)

	# customerid = info['customerId']

	# stripeCustomer = stripe.Customer.list_sources(
	# 	customerid,
	# 	object="card",
	# 	limit=1
	# )
	# cards = len(stripeCustomer.data)
	# status = ""
	# days = 0

	# if "trialstart" in info:
	# 	if (time - info["trialstart"]) >= (86400000 * 30): # trial is over, payment required
	# 		if cards == 0:
	# 			status = "cardrequired"
	# 		else:
	# 			status = "trialover"
	# 	else:
	# 		days = 30 - int((time - info["trialstart"]) / (86400000 * 30))
	# 		status = "notover"
	# else:
	# 	if cards == 0:
	# 		status = "cardrequired"
	# 	else:
	# 		status = "trialover"

	days = 30
	status = "notover"

	return { "days": days, "status": status }

def getRanStr():
	strid = ""

	for k in range(6):
		strid += str(randint(0, 9))

	return strid

def stripeFee(amount):
	return (amount + 0.30) / (1 - 0.029)

def calcTax(amount):
	pst = 0.08 * amount
	hst = 0.05 * amount

	return pst + hst

def pushInfo(to, title, body, data):
	return PushMessage(to=to, title=title, body=body, data=data)

def customerPay(amount, userid, locationid):
	chargeamount = stripeFee(amount + calcTax(amount))
	transferamount = amount + calcTax(amount)

	user = User.query.filter_by(id=userid).first()
	info = json.loads(user.info)
	customerid = info["customerId"]

	charge = stripe.Charge.create(
		amount=int(chargeamount * 100),
		currency="cad",
		customer=customerid
	)

	if locationid != None:
		location = Location.query.filter_by(id=locationid).first()
		info = json.loads(location.info)
		accountid = info["accountId"]

		transfer = stripe.Transfer.create(
			amount=int(transferamount * 100),
			currency="cad",
			destination=accountid,
		)
	else:
		transfer = None

	return charge != None and (transfer != None or locationid == None)

def push(messages):
	if type(messages) == type([]):
		resp = PushClient().publish_multiple(messages)

		for info in resp:
			if info.status != "ok":
				return { "status": "failed" }
	else:
		resp = PushClient().publish(messages)

		if resp.status != "ok":
			return { "status": "failed" }

	return { "status": "ok" }

@app.route("/welcome_dev")
def welcome_dev():
	num = str(randint(0, 9))

	return { "msg": "welcome to dev of easygo: " + num }

@app.route("/test_like")
def test_like():
	location = Location.query.filter(Location.name=='Hair salon', Location.city.like("%Toro%")).first()

	if location != None:
		return { "location": location.name }

	return { "nonexist": True }

@app.route("/reset")
def reset():
	delete = False
	users = query("select * from user", True)
	
	for user in users:
		delete = True
		info = json.loads(user['info'])

		try:
			stripe.Customer.delete(info['customerId'])
		except:
			print("no id exist")

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

		locationInfo = json.loads(location['info'])
		accountid = locationInfo['accountId']

		try:
			stripe.Account.delete(accountid)
		except:
			print("no id exist")

		if logo != "" and logo != None and os.path.exists("static/" + logo):
			os.remove("static/" + logo)

		query("delete from location where id = " + str(location['id']), False)

	if delete == True:
		query("ALTER table location auto_increment = 1", False)

	delete = False
	menus = query("select * from menu", True)
	for menu in menus:
		delete = True
		image = menu['image']

		if image != "" and image != None and os.path.exists("static/" + image):
			os.remove("static/" + image)

		query("delete from menu where id = " + str(menu['id']), False)

	if delete == True:
		query("ALTER table menu auto_increment = 1", False)

	delete = False
	services = query("select * from service", True)
	for service in services:
		delete = True
		image = service['image']

		if image != "" and image != None and os.path.exists("static/" + image):
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

		if image != "" and image != None and os.path.exists("static/" + image):
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
			if file != "" and file != None and os.path.exists("static/" + file):
				os.remove("static/" + file)

	accounts = stripe.Account.list().data
	customers = stripe.Customer.list().data

	for account in accounts:
		try:
			stripe.Account.delete(account.id)
		except:
			print(account.id)

	for customer in customers:
		stripe.Customer.delete(customer.id)

	return { "reset": True }

@app.route("/payout")
def payout():
	msg = ""
	status = ""

	accounts = stripe.Account.retrieve("acct_1K0w28PNuTzXPjNj").external_accounts.data
	bankid = ""

	for account in accounts:
		if account["default_for_currency"] == True:
			bankid = account["id"]

	payout = stripe.Payout.create(
		amount=50,
		currency="cad",
		destination=bankid
	)

	return { "payout": payout }

@app.route("/charge")
def charge():
	amount = 120.00

	pay = customerPay(amount, 1, 1)

	return { "error": False, "pay": pay }

@app.route("/restore_balance")
def restore_balance():
	balance = stripe.Balance.retrieve().available[0].amount

	user = User.query.filter_by(id=1).first()
	info = json.loads(user.info)
	customerid = info["customerId"]

	if balance < 0:
		balance = -balance
		balance = balance + 50 if balance < 50 else balance

		stripe.Charge.create(
			customer=customerid,
			amount=balance,
			currency="cad"
		)

	return { "balance": balance }

@app.route("/return_all")
def return_all():
	data = stripe.Charge.list().data
	charges = []

	for info in data:
		try:
			stripe.Refund.create(charge=info.id)
		except:
			charges.append(info.id)

	data = stripe.Transfer.list().data
	transfers = []

	for info in data:
		try:
			stripe.Transfer.retrieve_reversal(
				info.id,
				amount=info.amount
			)
		except:
			transfers.append(info.id)

	return { "charges": charges, "transfers": transfers }

@app.route("/test_deposit", methods=["POST"])
def test_deposit():
	content = request.get_json()

	action = content['action']

	users = User.query.all()

	for user in users:
		info = json.loads(user.info)

		if action == '-':
			info["trialstart"] -= 100000000000
		elif action == '+':
			info["trialstart"] += 100000000000

		user.info = json.dumps(info)

	db.session.commit()

	return { "error": False }

@app.route("/push", methods=["POST"])
def push():
	content = request.get_json()

	type = content['type']

	if type == 'user':
		userid = content['userid']
		user = User.query.filter_by(id=userid).first()
	else:
		ownerid = content['ownerid']
		user = Owner.query.filter_by(id=ownerid).first()

	message = content['message']
	data = content['data']

	errormsg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		pushtoken = info["pushToken"]

		response = PushClient().publish(
			PushMessage(
				to="ExponentPushToken[aO_8AtDRjS7gpfSzMyh9DS]",
				title="this is the title",
				body=message,
				data=data
			)
		)

		if response.status == "ok":
			return { "msg": "push sent successfully" }

		errormsg = "push failed to sent"
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/delete_transaction", methods=["POST"])
def delete_transaction():
	content = request.get_json()

	ids = content['ids']

	transactions = Transaction.query.filter(Transaction.id.in_(ids)).all()

	for data in transactions:
		db.session.delete(data)

	db.session.commit()

	return { "deleted": True }

@app.route("/getin", methods=["POST"])
def getin():
	username = request.form['username']

	return { "username": username }

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

	return { "message": message.sid }
