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
	info = db.Column(db.String(120))

	def __init__(self, cellnumber, password, username, profile, info):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.profile = profile
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
	longitude = db.Column(db.String(15))
	latitude = db.Column(db.String(15))
	owners = db.Column(db.Text)
	type = db.Column(db.String(20))
	hours = db.Column(db.Text)
	info = db.Column(db.String(100))

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
	info = db.Column(db.String(75))

	def __init__(self, userId, locationId, menuId, serviceId, time, status, cancelReason, nextTime, locationType, customers, note, orders, table, info):
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
	groupId = db.Column(db.String(20))
	locationId = db.Column(db.Integer)
	productId = db.Column(db.Integer)
	serviceId = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(200))
	time = db.Column(db.String(15))

	def __init__(self, groupId, locationId, productId, serviceId, adder, callfor, options, others, sizes, time):
		self.groupId = groupId
		self.locationId = locationId
		self.productId = productId
		self.serviceId = serviceId
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

def trialInfo(id, time): # days before over | cardrequired | trialover
	user = User.query.filter_by(id=id).first()
	info = json.loads(user.info)

	customerid = info['customerId']

	stripeCustomer = stripe.Customer.list_sources(
		customerid,
		object="card",
		limit=1
	)
	cards = len(stripeCustomer.data)
	status = ""
	days = 0

	if "trialstart" in info:
		if (time - info["trialstart"]) >= (86400000 * 30): # trial is over, payment required
			if cards == 0:
				status = "cardrequired"
			else:
				status = "trialover"
		else:
			days = 30 - int((time - info["trialstart"]) / (86400000 * 30))
			status = "notover"
	else:
		if cards == 0:
			status = "cardrequired"
		else:
			status = "trialover"

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

@app.route("/welcome_owners", methods=["GET"])
def welcome_owners():
	datas = Owner.query.all()
	owners = []

	for data in datas:
		owners.append(data.id)

	return { "msg": "welcome to owners of easygo", "owners": owners }

@app.route("/login", methods=["POST"])
def owner_login():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']
	msg = ""
	status = ""

	if cellnumber != "" and password != "":
		data = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True)

		if len(data) > 0:
			owner = data[0]

			if check_password_hash(owner['password'], password):
				ownerid = owner['id']

				data = query("select * from location where owners like '%\"" + str(ownerid) + "\"%'", True)
				storeName = data[0]["name"] if len(data) > 0 else ""

				if len(data) == 0 or storeName == "":
					return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": "", "locationtype": "", "msg": "setup" }
				else:
					data = data[0]

					if data['type'] != "":
						if data['hours'] != "":
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": data['id'], "locationtype": data['type'], "msg": "main" }
						else:
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": data['id'], "locationtype": data['type'], "msg": "setuphours" }
					else:
						return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": data['id'], "locationtype": "", "msg": "typesetup" }
			else:
				msg = "Password is incorrect"
		else:
			msg = "Owner doesn't exist"
	else:
		if cellnumber == "":
			msg = "Phone number is blank"
		else:
			msg = "Password is blank"

	return { "errormsg": msg, "status": status }, 400

@app.route("/verify/<cellnumber>")
def owner_verify(cellnumber):
	verifycode = getRanStr()

	owner = Owner.query.filter_by(cellnumber=cellnumber).first()
	msg = ""
	status = ""

	if owner == None:
		if test_sms == False:
			message = client.messages.create(
				body='Verify code: ' + str(verifycode),
				messaging_service_sid=mss,
				to='+1' + str(cellnumber)
			)

		return { "verifycode": verifycode }
	else:
		msg = "Cell number already used"

	return { "errormsg": msg, "status": status }, 400

@app.route("/register", methods=["POST"])
def owner_register():
	username = request.form['username']
	cellnumber = request.form['cellnumber']
	password = request.form['password']
	confirmPassword = request.form['confirmPassword']
	profilepath = request.files.get('profile', False)
	profileexist = False if profilepath == False else True
	permission = request.form['permission']
	msg = ""
	status = ""

	if username == "":
		msg = "Please provide a username for identification"

	if cellnumber == "":
		msg = "Cell number is blank"
	else:
		data = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True)

		if len(data) > 0:
			msg = "Owner already exist"

	if password != "" and confirmPassword != "":
		if len(password) >= 6:
			if password != confirmPassword:
				msg = "Password is mismatch"
		else:
			msg = "Password needs to be atleast 6 characters long"
	else:
		if password == "":
			msg = "Passwod is blank"
		else:
			msg = "Please confirm your password"

	profilename = ""
	if profileexist == True:
		profile = request.files['profile']
		profilename = profile.filename

		profile.save(os.path.join('static', profilename))
	else:
		if permission == "true":
			msg = "Please provide a profile for identification"
	
	if msg == "":
		password = generate_password_hash(password)
		info = json.dumps({"locationId": "","pushToken": ""})

		owner = Owner(cellnumber, password, username, profilename, info)
		db.session.add(owner)
		db.session.commit()

		return { "id": owner.id }

	return { "errormsg": msg, "status": status }, 400

@app.route("/add_owner", methods=["POST"])
def add_owner():
	ownerid = request.form['ownerid']
	cellnumber = request.form['cellnumber']
	username = request.form['username']
	password = request.form['password']
	confirmPassword = request.form['confirmPassword']
	profilepath = request.files.get('profile', False)
	profileexist = False if profilepath == False else True
	permission = request.form['permission']

	data = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True)
	msg = ""
	status = ""

	if len(data) == 0:
		owner = Owner.query.filter_by(id=ownerid).first()

		if owner != None:
			if username == "":
				msg = "Please provide a username for identification"

			if cellnumber == "":
				msg = "Cell number is blank"

			if password != "" and confirmPassword != "":
				if len(password) >= 6:
					if password != confirmPassword:
						msg = "Password is mismatch"
				else:
					msg = "Password needs to be atleast 6 characters long"
			else:
				if password == "":
					msg = "Please enter a password"
				else:
					msg = "Please confirm your password"

			profilename = ""
			if profileexist == True:
				profile = request.files['profile']
				profilename = profile.filename
				
				profile.save(os.path.join('static', profilename))
			else:
				if permission == "true":
					msg = "Please provide a profile for identification"

			if msg == "":
				ownerInfo = json.loads(owner.info)
				locationId = ownerInfo["locationId"]

				info = {"locationId": locationId, "pushToken": ""}

				password = generate_password_hash(password)
				owner = Owner(cellnumber, password, username, profilename, json.dumps(info))
				db.session.add(owner)
				db.session.commit()

				location = Location.query.filter_by(id=locationId).first()
				owners = json.loads(location.owners)
				owners.append(str(owner.id))

				location.owners = json.dumps(owners)

				db.session.commit()

				return { "id": owner.id, "msg": "New owner added by an owner" }
		else:
			msg = "Owner doesn't exist"
	else:
		msg = "Owner already exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/update_owner", methods=["POST"])
def update_owner():
	ownerid = request.form['ownerid']
	username = request.form['username']
	cellnumber = request.form['cellnumber']
	password = request.form['password']
	confirmPassword = request.form['confirmPassword']
	profilepath = request.files.get('profile', False)
	profileexist = False if profilepath == False else True
	permission = request.form['permission']

	owner = Owner.query.filter_by(id=ownerid).first()
	msg = ""
	status = ""

	if owner != None:
		if username != "":
			owner.username = username

		if cellnumber != "":
			owner.cellnumber = cellnumber

		if profileexist == True:
			profile = request.files['profile']
			newprofilename = profile.filename
			oldprofile = owner.profile

			if oldprofile != "" and os.path.exists("static/" + oldprofile):
				os.remove("static/" + oldprofile)

			profile.save(os.path.join('static', newprofilename))
			owner.profile = newprofilename

		if password != "" or confirmPassword != "":
			if password != "" and confirmPassword != "":
				if len(password) >= 6:
					if password == confirmPassword:
						password = generate_password_hash(password)

						owner.password = password
					else:
						msg = "Password is mismatch"
				else:
					msg = "Password needs to be atleast 6 characters long"
			else:
				if password == "":
					msg = "Please enter a password"
				else:
					msg = "Please confirm your password"

		db.session.commit()

		return { "id": owner.id, "msg": "Owner's info updated" }
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg, "status": status }, 400
		
@app.route("/update_notification_token", methods=["POST"])
def owner_update_notification_token():
	content = request.get_json()

	ownerid = content['ownerid']
	token = content['token']

	owner = Owner.query.filter_by(id=ownerid).first()
	msg = ""
	status = ""

	if owner != None:
		ownerInfo = json.loads(owner.info)
		ownerInfo["pushToken"] = token

		owner.info = json.dumps(ownerInfo)

		db.session.commit()

		return { "msg": "Push token updated" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/add_bankaccount", methods=["POST"])
def add_bankaccount():
	content = request.get_json()

	locationid = content['locationid']
	banktoken = content['banktoken']

	location = Location.query.filter_by(id=locationid).first()
	msg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		stripe.Account.create_external_account(
			accountid,
			external_account=banktoken
		)

		return { "msg": "Added a bank account" }
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/update_bankaccount", methods=["POST"])
def update_bankaccount():
	content = request.get_json()

	locationid = content['locationid']
	oldbanktoken = content['oldbanktoken']
	banktoken = content['banktoken']

	location = Location.query.filter_by(id=locationid).first()
	msg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		stripe.Account.delete_external_account(
			accountid,
			oldbanktoken
		)

		stripe.Account.create_external_account(
			accountid,
			external_account=banktoken
		)

		return { "msg": "Updated a bank account" }
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_accounts/<id>")
def get_accounts(id):
	content = request.get_json()

	location = Location.query.filter_by(id=id).first()
	owners = json.loads(location.owners)
	accounts = []

	for owner in owners:
		info = Owner.query.filter_by(id=owner).first()

		accounts.append({
			"key": "account-" + str(owner), 
			"id": owner, 
			"cellnumber": info.cellnumber,
			"username": info.username,
			"profile": info.profile
		})

	return { "accounts": accounts }

@app.route("/get_bankaccounts/<id>")
def get_bankaccounts(id):
	content = request.get_json()

	location = Location.query.filter_by(id=id).first()
	locationInfo = json.loads(location.info)
	accountid = locationInfo["accountId"]
	bankaccounts = []

	accounts = stripe.Account.list_external_accounts(
		accountid,
		object="bank_account"
	)
	datas = accounts.data

	for k, data in enumerate(datas):
		bankaccounts.append({
			"key": "bankaccount-" + str(k),
			"id": str(k),
			"bankid": data.id,
			"bankname": data.bank_name,
			"number": "****" + str(data.last4),
			"default": data.default_for_currency
		})

	return { "bankaccounts": bankaccounts, "msg": "get bank accounts" }

@app.route("/set_bankaccountdefault", methods=["POST"])
def set_bankaccountdefault():
	content = request.get_json()

	locationid = content['locationid']
	bankid = content['bankid']

	location = Location.query.filter_by(id=locationid).first()
	msg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		stripe.Account.modify_external_account(
			accountid,
			bankid,
			default_for_currency=True
		)

		return { "msg": "Bank account set as default" }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_bankaccount_info", methods=["POST"])
def get_bankaccount_info():
	content = request.get_json()

	locationid = content['locationid']
	bankid = content['bankid']

	location = Location.query.filter_by(id=locationid).first()
	msg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		accounts = stripe.Account.retrieve(accountid)
		datas = accounts.external_accounts.data

		for data in datas:
			if data.id == bankid:
				routing_number = data.routing_number

				transit = routing_number[4:]
				institution = routing_number[1:4]

				info = {
					"account_holder_name": data.account_holder_name,
					"last4": data.last4,
					"transit_number": transit,
					"institution_number": institution
				}

				return { "bankaccountInfo": info }

		msg = "Bank doesn't exist"
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/delete_bankaccount", methods=["POST"])
def delete_bankaccount():
	content = request.get_json()

	locationid = content['locationid']
	bankid = content['bankid']

	location = Location.query.filter_by(id=locationid).first()
	msg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		stripe.Account.delete_external_account(
			accountid,
			bankid
		)

		return { "msg": "Bank account deleted" }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_reset_code/<cellnumber>")
def get_owner_reset_code(cellnumber):
	owner = Owner.query.filter_by(cellnumber=cellnumber).first()
	msg = ""
	status = ""

	if owner != None:
		code = getRanStr()

		if test_sms == False:
			message = client.messages.create(
				body="Your EasyGO reset code is " + code,
				messaging_service_sid=mss,
				to='+1' + str(owner.cellnumber)
			)

		return { "msg": "Reset code sent", "code": code }
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/reset_password", methods=["POST"])
def owner_reset_password():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['newPassword']
	confirmPassword = content['confirmPassword']

	owner = Owner.query.filter_by(cellnumber=cellnumber).first()
	msg = ""
	status = ""

	if owner != None:
		if password != '' and confirmPassword != '':
			if len(password) >= 6:
				if password == confirmPassword:
					password = generate_password_hash(password)

					owner.password = password

					db.session.commit()

					ownerid = owner.id

					data = query("select * from location where owners like '%\"" + str(ownerid) + "\"%'", True)

					if len(data) == 0:
						return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": "", "locationtype": "", "msg": "setup" }
					else:
						data = data[0]

						if data['type'] != "":
							if data['hours'] != "":
								return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": data['id'], "locationtype": data['type'], "msg": "main" }
							else:
								return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": data['id'], "locationtype": data['type'], "msg": "setuphours" }
						else:
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": data['id'], "locationtype": "", "msg": "typesetup" }
				else:
					msg = "Password is mismatch"
			else:
				msg = "Password needs to be atleast 6 characters long"
		else:
			if password == '':
				msg = "Passwod is blank"
			else:
				msg = "Please confirm your password"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400
