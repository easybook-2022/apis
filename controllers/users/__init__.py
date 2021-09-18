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
test_sms = True

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
def welcome_users():
	datas = query("select * from user", True)
	users = []

	for data in datas:
		users.append({
			"id": data["id"]
		})

	return { "msg": "welcome to users of easygo", "users": users }

@app.route("/login", methods=["POST"])
def login():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']

	if cellnumber != '' and password != '':
		user = User.query.filter_by(cellnumber=cellnumber).first()

		if user != None:
			if check_password_hash(user.password, password):
				userid = user.id

				password = generate_password_hash(password)

				user.password = password

				db.session.commit()

				if user.username == '':
					return { "id": userid, "msg": "setup" }
				else:
					return { "id": userid, "msg": "main" }
			else:
				msg = "Password is incorrect"
		else:
			msg = "User doesn't exist"
	else:
		if cellnumber == '':
			msg = "Phone number is blank"
		else:
			msg = "Password is blank"

	return { "errormsg": msg }

@app.route("/verify/<cellnumber>")
def verify(cellnumber):
	verifycode = getRanStr()

	user = User.query.filter_by(cellnumber=cellnumber).first()

	if user == None:
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

	if cellnumber != '' and password != '' and confirmPassword != '':
		if len(password) >= 6:
			if password == confirmPassword:
				user = User.query.filter_by(cellnumber=cellnumber).first()

				if user == None:
					password = generate_password_hash(password)

					customer = stripe.Customer.create(
						phone=cellnumber
					)
					info = json.dumps({"customerId": customer.id, "status": "required"})

					user = User(cellnumber, password, '', '', info)
					db.session.add(user)
					db.session.commit()

					return { "id": user.id }
				else:
					msg = "User already exist"
			else:
				msg = "Password is mismatch"
		else:
			msg = "Password needs to be atleast 6 characters long"
	else:
		if cellnumber == '':
			msg = "Phone number is blank"
		elif password == '':
			msg = "Passwod is blank"
		else:
			msg = "Please confirm your password"

	return { "errormsg": msg }

@app.route("/setup", methods=["POST"])
def setup():
	userid = request.form['userid']
	username = request.form['username']
	profile = request.files['profile']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		user.username = username
		user.profile = profile.filename

		stripe.Customer.modify(
			customerid,
			name=username
		)

		profile.save(os.path.join('static', profile.filename))

		db.session.commit()

		return { "msg": "" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/update", methods=["POST"])
def update():
	userid = request.form['userid']
	username = request.form['username']
	cellnumber = request.form['cellnumber']
	filepath = request.files.get('profile', False)
	fileexist = False if filepath == False else True

	if fileexist == True:
		profile = request.files['profile']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		if fileexist == True:
			if user.profile != None:
				oldprofile = user.profile

				if oldprofile != "" and os.path.exists("static/" + oldprofile):
					os.remove("static/" + oldprofile)

			profile.save(os.path.join('static', profile.filename))

			user.profile = profile.filename

		user.username = username
		user.cellnumber = cellnumber

		info = json.loads(user.info)
		customerid = info["customerId"]

		stripe.Customer.modify(
			customerid,
			phone=cellnumber,
			name=username
		)

		db.session.commit()

		return { "msg": "" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_user_info/<id>")
def get_user_info(id):
	user = User.query.filter_by(id=id).first()

	info = {
		"username": user.username,
		"cellnumber": user.cellnumber,
		"profile": user.profile
	}

	return { "userInfo": info }

@app.route("/add_paymentmethod", methods=["POST"])
def add_paymentmethod():
	content = request.get_json()

	userid = content['userid']
	cardtoken = content['cardtoken']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		stripe.Customer.create_source(
			customerid,
			source=cardtoken
		)

		info["status"] = "filled"

		user.info = json.dumps(info)

		db.session.commit()

		return { "msg": "Added a payment method" }
	else:
		msg = ""

@app.route("/update_paymentmethod", methods=["POST"])
def update_paymentmethod():
	content = request.get_json()

	userid = content['userid']
	oldcardtoken = content['oldcardtoken']
	cardtoken = content['cardtoken']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		stripe.Customer.delete_source(
			customerid,
			oldcardtoken
		)

		stripe.Customer.create_source(
			customerid,
			source=cardtoken
		)

		return { "msg": "Updated a payment method" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_payment_methods/<id>")
def get_payment_methods(id):
	user = User.query.filter_by(id=id).first()

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		customer = stripe.Customer.retrieve(customerid)
		default_card = customer.default_source

		cards = stripe.Customer.list_sources(
			customerid,
			object="card"
		)
		datas = cards.data
		cards = []

		for k, data in enumerate(datas):
			cards.append({
				"key": "card-" + str(k),
				"id": str(k),
				"cardid": data.id,
				"cardname": data.brand,
				"default": data.id == default_card,
				"number": "****" + str(data.last4)
			})

		return { "cards": cards }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/set_paymentmethoddefault", methods=["POST"])
def set_paymentmethoddefault():
	content = request.get_json()

	userid = content['userid']
	cardid = content['cardid']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		stripe.Customer.modify(
			customerid,
			default_source=cardid
		)

		return { "msg": "Payment method set as default" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_paymentmethod_info", methods=["POST"])
def get_paymentmethod_info():
	content = request.get_json()

	userid = content['userid']
	cardid = content['cardid']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		card = stripe.Customer.retrieve_source(
			customerid,
			cardid
		)

		info = {
			"exp_month": card.exp_month,
			"exp_year": card.exp_year,
			"last4": card.last4
		}

		return { "paymentmethodInfo": info }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/delete_paymentmethod", methods=["POST"])
def delete_paymentmethod():
	content = request.get_json()

	userid = content['userid']
	cardid = content['cardid']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		stripe.Customer.delete_source(
			customerid,
			cardid
		)

		return { "msg": "Payment method deleted"}
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_notifications/<id>")
def get_notifications(id):
	user = User.query.filter_by(id=id).first()

	if user != None:
		userId = user.id
		notifications = []

		# cart orders called for self
		sql = "select * from cart where adder = " + str(id)
		datas = query(sql, True)

		for data in datas:
			adder = User.query.filter_by(id=data['adder']).first()
			product = Product.query.filter_by(id=data['productId']).first()
			options = json.loads(data['options'])
			others = json.loads(data['others'])
			sizes = json.loads(data['sizes'])

			for k, option in enumerate(options):
				option["key"] = "option-" + str(k)

			for k, other in enumerate(others):
				other["key"] = "other-" + str(k)

			for k, size in enumerate(sizes):
				size["key"] = "size-" + str(k)

			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "cart-order-self",
				"id": str(data['id']),
				"name": product.name,
				"image": product.image,
				"options": options,
				"others": others,
				"sizes": sizes,
				"quantity": int(data['quantity']),
				"adder": { "username": adder.username, "profile": adder.profile },
				"price": int(data['quantity']) * float(product.price) if product.price != "" else "",
				"orderNumber": data['orderNumber'],
				"status": data['status']
			})
		
		# cart orders called for other user(s)
		sql = "select * from cart where callfor like '%\"userid\": \"" + str(id) + "\", \"status\": \"waiting\"%'"
		datas = query(sql, True)

		for data in datas:
			adder = User.query.filter_by(id=data['adder']).first()
			product = Product.query.filter_by(id=data['productId']).first()
			callfor = json.loads(data['callfor'])
			options = json.loads(data['options'])
			others = json.loads(data['others'])
			sizes = json.loads(data['sizes'])
			friends = []

			for info in callfor:
				friend = User.query.filter_by(id=info['userid']).first()

				friends.append({
					"key": str(data['id']) + "-" + str(friend.id),
					"username": friend.username,
					"profile": friend.profile
				})

			for k, option in enumerate(options):
				option["key"] = "option-" + str(k)

			for k, other in enumerate(others):
				other["key"] = "other-" + str(k)

			for k, size in enumerate(sizes):
				size["key"] = "size-" + str(k)

			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "cart-order-other",
				"id": str(data['id']),
				"name": product.name,
				"image": product.image,
				"options": options,
				"others": others,
				"sizes": sizes,
				"quantity": int(data['quantity']),
				"orderers": friends,
				"adder": { "username": adder.username, "profile": adder.profile },
				"price": int(data['quantity']) * float(product.price) if product.price != "" else ""
			})

		# dining orders called for user
		sql = "select * from schedule where orders like '%\"userid\": \"" + str(id) + "\", \"status\": \"confirmawaits\"%'"
		datas = query(sql, True)

		for data in datas:
			orders = json.loads(data['orders'])
			groups = orders['groups']

			for rounds in groups:
				for k in rounds:
					if k != "status" and k != "id":
						for orderer in rounds[k]:
							if {"userid": str(id), "status": "confirmawaits"} in orderer['callfor']:
								callfor = orderer['callfor']
								product = Product.query.filter_by(id=orderer['productid']).first()
								adder = User.query.filter_by(id=k).first()
								options = orderer['options']
								others = orderer['others']
								sizes = orderer['sizes']

								notifications.append({
									"key": "order-" + str(len(notifications)),
									"type": "dining-order",
									"orderid": str(orderer['id']),
									"name": product.name,
									"image": product.image,
									"options": options,
									"others": others,
									"sizes": sizes,
									"quantity": int(orderer['quantity']),
									"adder": { "username": adder.username, "profile": adder.profile },
									"price": int(orderer['quantity']) * float(product.price) if product.price != "" else ""
								})

		# get requested payment method to order for
		sql = "select * from cart where callfor like '%\"userid\": \"" + str(id) + "\", \"status\": \"paymentrequested\"%'"
		datas = query(sql, True)

		for data in datas:
			adder = User.query.filter_by(id=data['adder']).first()
			product = Product.query.filter_by(id=data['productId']).first()
			callfor = json.loads(data['callfor'])
			options = json.loads(data['options'])
			others = json.loads(data['others'])
			sizes = json.loads(data['sizes'])
			friends = []

			for info in callfor:
				friend = User.query.filter_by(id=info['userid']).first()

				friends.append({
					"key": str(data['id']) + "-" + str(friend.id),
					"username": friend.username,
					"profile": friend.profile
				})

			for k, option in enumerate(options):
				option["key"] = "option-" + str(k)

			for k, other in enumerate(others):
				other["key"] = "other-" + str(k)

			for k, size in enumerate(sizes):
				size["key"] = "size-" + str(k)

			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "paymentrequested",
				"id": str(data['id']),
				"name": product.name,
				"image": product.image,
				"options": options,
				"others": others,
				"sizes": sizes,
				"quantity": int(data['quantity']),
				"orderers": friends,
				"adder": { "username": adder.username, "profile": adder.profile },
				"price": int(data['quantity']) * float(product.price) if product.price != "" else ""
			})

		# get reservation requests
		sql = "select * from schedule where "
		sql += "(userId = " + str(id) + " and (status = 'requested' or status = 'rebook' or status = 'cancel' or status = 'accepted'))"
		sql += " or customers like '%{\"userid\": \"" + str(id) + "\", \"status\": \"waiting\"}%'"
		sql += " or (status = 'accepted' and customers like '%{\"userid\": \"" + str(id) + "\", \"status\": \"confirmed\"}%')"
		datas = query(sql, True)

		for data in datas:
			location = None
			service = None

			if data['locationId'] != "":
				location = Location.query.filter_by(id=data['locationId']).first()

			if data['serviceId'] != "":
				service = Service.query.filter_by(id=data['serviceId']).first()

			booker = User.query.filter_by(id=data['userId']).first()
			confirm = False
			info = json.loads(data['info'])

			if data["locationType"] == 'restaurant':
				customers = json.loads(data['customers'])
				
				for customer in customers:
					if customer['userid'] == id:
						confirm = customer['status'] == 'confirmed'

				if str(data['userId']) == id:
					confirm = data["status"] == 'accepted'

				customers = len(customers)
			else:
				customers = int(data['customers'])

			if data["locationType"] != 'restaurant':
				paymentSent = info["paymentsent"]
			else:
				orders = json.loads(data["orders"])
				charges = orders["charges"]

				paymentSent = charges[str(userId)]["paymentsent"]

			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "service",
				"id": str(data['id']),
				"locationid": data['locationId'],
				"location": location.name,
				"menuid": int(data['menuId']) if data['menuId'] != "" else "",
				"serviceid": int(data['serviceId']) if data['serviceId'] != "" else "",
				"service": service.name if service != None else "",
				"locationimage": location.logo,
				"locationtype": location.type,
				"serviceimage": service.image if service != None else "",
				"time": int(data['time']),
				"action": data['status'],
				"nextTime": int(data['nextTime']) if data['status'] == 'rebook' else 0,
				"reason": data['cancelReason'],
				"table": data['table'],
				"booker": userId == data['userId'],
				"bookerName": booker.username,
				"diners": customers,
				"confirm": confirm,
				"paymentSent": paymentSent
			})

		return { "notifications": notifications }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_num_updates", methods=["POST"])
def get_num_updates():
	content = request.get_json()

	userid = content['userid']
	time = content['time']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		num = 0

		# cart orders called for self
		sql = "select count(*) as num from cart where adder = " + str(userid)
		num += query(sql, True)[0]["num"]

		# cart orders called for other user(s)
		sql = "select count(*) as num from cart where callfor like '%\"userid\": \"" + str(userid) + "\", \"status\": \"waiting\"%'"
		num += query(sql, True)[0]["num"]

		# dining orders called for user
		sql = "select count(*) as num from schedule where orders like '%\"userid\": \"" + str(userid) + "\", \"status\": \"confirmawaits\"%'"
		num += query(sql, True)[0]["num"]

		# requested payment method for order for
		sql = "select count(*) as num from cart where callfor like '%\"userid\": \"" + str(userid) + "\", \"status\": \"paymentrequested\"%'"
		num += query(sql, True)[0]["num"]

		# get reservation requests
		sql = "select count(*) as num from schedule where "
		sql += "(userId = " + str(userid) + " and (status = 'requested' or status = 'rebook' or status = 'cancel' or status = 'accepted'))"
		sql += " or customers like '%{\"userid\": \"" + str(userid) + "\", \"status\": \"waiting\"}%'"
		sql += " or (status = 'accepted' and customers like '%{\"userid\": \"" + str(userid) + "\", \"status\": \"confirmed\"}%')"
		num += query(sql, True)[0]["num"]

		return { "numNotifications": num }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/search_friends", methods=["POST"])
def search_friends():
	content = request.get_json()

	userid = content['userid']
	searchusername = content['username']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		searchedfriends = []
		numSearchedFriends = 0

		if searchusername != "":
			datas = query("select id, profile, username from user where username like '%" + searchusername + "%' and not id = " + str(userid), True)
			row = []
			rownum = 0

			for k, data in enumerate(datas):
				row.append({
					"key": "friend-" + str(data['id']),
					"id": data['id'],
					"profile": data['profile'],
					"username": data['username']
				})
				numSearchedFriends += 1

				if len(row) == 4 or (len(datas) - 1 == k and len(row) > 0):
					if len(datas) - 1 == k and len(row) > 0:
						key = data['id'] + 1

						leftover = 4 - len(row)

						for k in range(leftover):
							row.append({ "key": "friend-" + str(key) })
							key += 1
					
					searchedfriends.append({ "key": "friend-row-" + str(len(searchedfriends)), "row": row })
					row = []

		return { "searchedFriends": searchedfriends, "numSearchedFriends": numSearchedFriends }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/search_diners", methods=["POST"])
def search_diners():
	content = request.get_json()

	userid = str(content['userid'])
	scheduleid = content['scheduleid']
	searchusername = content['username']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		datas = json.loads(schedule.customers)
		customers = [str(schedule.userId)]

		for data in datas:
			customers.append(data["userid"])

		if userid in customers:
			customers.remove(userid)

		datas = query("select id, profile, username from user where username like '%" + searchusername + "%' and id in (" + json.dumps(customers)[1:-1] + ")", True)
		row = []
		searcheddiners = []
		rownum = 0
		numSearchedDiners = 0

		for k, data in enumerate(datas):
			row.append({
				"key": "diner-" + str(data['id']),
				"id": data['id'],
				"profile": data['profile'],
				"username": data['username']
			})
			numSearchedDiners += 1

			if len(row) == 4 or (len(datas) - 1 == k and len(row) > 0):
				if len(datas) - 1 == k and len(row) > 0:
					key = data['id'] + 1

					leftover = 4 - len(row)

					for k in range(leftover):
						row.append({ "key": "diner-" + str(key) })
						key += 1

				searcheddiners.append({ "key": "diner-row-" + str(len(searcheddiners)), "row": row })
				row = []

		return { "searchedDiners": searcheddiners, "numSearchedDiners": numSearchedDiners }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/select_user/<id>")
def select_user(id):
	user = User.query.filter_by(id=id).first()

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]
		customer = stripe.Customer.list_sources(
			customerid,
			object="card",
			limit=1
		)
		cards = len(customer.data)

		return { "username": user.username, "cards": cards }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/request_user_payment_method/<id>")
def request_user_payment_method(id):
	user = User.query.filter_by(id=id).first()

	if user != None:
		info = json.loads(user.info)

		info["status"] = "requested"

		user.info = json.dumps(info)

		db.session.commit()

		return { "msg": "Card requested" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_reset_code/<phonenumber>")
def get_reset_code(phonenumber):
	user = User.query.filter_by(cellnumber=phonenumber).first()

	if user != None:
		code = getRanStr()

		if test_sms == False:
			message = client.messages.create(
				body="Your EasyGO reset code is " + code,
				messaging_service_sid=mss,
				to='+1' + str(user.cellnumber)
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

	user = User.query.filter_by(cellnumber=cellnumber).first()

	if user != None:
		if password != '' and confirmPassword != '':
			if len(password) >= 6:
				if password == confirmPassword:
					password = generate_password_hash(password)

					user.password = password

					db.session.commit()

					if user.username == '':
						return { "id": user.id, "msg": "setup" }
					else:
						return { "id": user.id, "msg": "main" }
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
