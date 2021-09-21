from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, json, pymysql.cursors, os, stripe
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
test_sms = True
run_stripe = True

account_sid = "ACc2195555d01f8077e6dcd48adca06d14" if test_sms == True else "AC8c3cd78674e391f0834a086891304e52"
auth_token = "244371c21d9c8e735f0e08dd4c29249a" if test_sms == True else "b7f9e3b46ac445302a4a0710e95f44c1"
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

	def __init__(
		self, 
		name, addressOne, addressTwo, city, province, postalcode, phonenumber, logo, 
		longitude, latitude, owners, type, hours, accountId
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
	info = db.Column(db.String(80))

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
	sizes = db.Column(db.String(150))
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

def getRanStr():
	strid = ""

	for k in range(6):
		strid += str(randint(0, 9))

	return strid

@app.route("/", methods=["GET"])
def welcome_owners():
	datas = query("select * from owner", True)
	owners = []

	for data in datas:
		owners.append({
			"id": data["id"]
		})

	return { "msg": "welcome to owners of easygo", "owners": owners }

@app.route("/login", methods=["POST"])
def login():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']

	if cellnumber != "" and password != "":
		data = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True)

		if len(data) > 0:
			owner = data[0]

			if check_password_hash(owner['password'], password):
				ownerid = owner['id']

				data = query("select * from location where owners like '%\"" + str(ownerid) + "\"%'", True)
				logo = data[0]["logo"] if len(data) > 0 else ""

				if len(data) == 0 or logo == "":
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

	return { "errormsg": msg }

@app.route("/verify/<cellnumber>")
def verify(cellnumber):
	verifycode = getRanStr()

	owner = Owner.query.filter_by(cellnumber=cellnumber).first()

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

	return { "errormsg": msg }

@app.route("/register", methods=["POST"])
def register():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']
	confirmPassword = content['confirmPassword']

	if cellnumber != "" and password != "" and confirmPassword != "":
		if len(password) >= 6:
			if password == confirmPassword:
				data = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True)

				if len(data) == 0:
					password = generate_password_hash(password)

					owner = Owner(cellnumber, password, 0)
					db.session.add(owner)
					db.session.commit()

					return { "id": owner.id }
				else:
					msg = "Owner already exist"
			else:
				msg = "Password is mismatch"
		else:
			msg = "Password needs to be atleast 6 characters long"
	else:
		if cellnumber == "":
			msg = "Phone number is blank"
		elif password == "":
			msg = "Passwod is blank"
		else:
			msg = "Please confirm your password"

	return { "errormsg": msg }

@app.route("/add_owner", methods=["POST"])
def add_owner():
	content = request.get_json()

	ownerid = content['ownerid']
	cellnumber = content['cellnumber']
	password = content['password']
	confirmPassword = content['confirmPassword']

	if cellnumber != "" and password != "" and confirmPassword != "":
		if len(password) >= 6:
			if password == confirmPassword:
				data = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True)

				if len(data) == 0:
					password = generate_password_hash(password)

					owner = Owner.query.filter_by(id=ownerid).first()

					if owner != None:
						locationId = owner.locationId

						owner = Owner(cellnumber, password, owner.locationId)
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
			else:
				msg = "Password is mismatch"
		else:
			msg = "Password needs to be atleast 6 characters long"
	else:
		if cellnumber == "":
			msg = "Phone number is blank"
		elif password == "":
			msg = "Please confirm your password"
		else:
			msg = "Please confirm your password"

	return { "errormsg": msg }

@app.route("/update_owner", methods=["POST"])
def update_owner():
	content = request.get_json()

	ownerid = content['ownerid']
	cellnumber = content['cellnumber']
	password = content['password']
	confirmPassword = content['confirmPassword']
	errormsg = ""

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		if cellnumber != "":
			owner.cellnumber = cellnumber

		if password != "" or confirmPassword != "":
			if password != "" and confirmPassword != "":
				if len(password) >= 6:
					if password == confirmPassword:
						password = generate_password_hash(password)

						owner.password = password
					else:
						errormsg = "Password is mismatch"
				else:
					errormsg = "Password needs to be atleast 6 characters long"
			else:
				if password == "":
					errormsg = "Please confirm your password"
				else:
					errormsg = "Please confirm your password"

		db.session.commit()
	else:
		errormsg = "Owner doesn't exist"

	if errormsg != "":
		return { "errormsg": errormsg }
	else:
		return { "id": owner.id, "msg": "Owner's info updated" }

@app.route("/add_bankaccount", methods=["POST"])
def add_bankaccount():
	content = request.get_json()

	locationid = content['locationid']
	banktoken = content['banktoken']

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		accountid = location.accountId

		if run_stripe == True:
			stripe.Account.create_external_account(
				accountid,
				external_account=banktoken
			)

		return { "msg": "Added a bank account" }
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg }

@app.route("/update_bankaccount", methods=["POST"])
def update_bankaccount():
	content = request.get_json()

	locationid = content['locationid']
	oldbanktoken = content['oldbanktoken']
	banktoken = content['banktoken']

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		accountid = location.accountId

		if run_stripe == True:
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

	return { "errormsg": msg }

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
			"cellnumber": info.cellnumber
		})

	return { "accounts": accounts }

@app.route("/get_bankaccounts/<id>")
def get_bankaccounts(id):
	content = request.get_json()

	location = Location.query.filter_by(id=id).first()
	accountid = location.accountId
	bankaccounts = []

	if run_stripe == True:
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

	if location != None:
		accountid = location.accountId

		if run_stripe == True:
			stripe.Account.modify_external_account(
				accountid,
				bankid,
				default_for_currency=True
			)

		return { "msg": "Bank account set as default" }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }

@app.route("/get_bankaccount_info", methods=["POST"])
def get_bankaccount_info():
	content = request.get_json()

	locationid = content['locationid']
	bankid = content['bankid']

	location = Location.query.filter_by(id=locationid).first()
	msg = ""

	if location != None:
		accountid = location.accountId

		if run_stripe == True:
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

	return { "errormsg": msg }, 400

@app.route("/delete_bankaccount", methods=["POST"])
def delete_bankaccount():
	content = request.get_json()

	locationid = content['locationid']
	bankid = content['bankid']

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		accountid = location.accountId

		if run_stripe == True:
			stripe.Account.delete_external_account(
				accountid,
				bankid
			)

		return { "msg": "Bank account deleted" }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }

@app.route("/get_reset_code/<cellnumber>")
def get_reset_code(cellnumber):
	owner = Owner.query.filter_by(cellnumber=cellnumber).first()

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

	return { "errormsg": msg }

@app.route("/reset_password", methods=["POST"])
def reset_password():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['newPassword']
	confirmPassword = content['confirmPassword']

	owner = Owner.query.filter_by(cellnumber=cellnumber).first()

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

	return { "errormsg": msg }
