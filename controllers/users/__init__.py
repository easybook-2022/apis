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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + user + ':' + password + '@' + host + '/' + database
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
				del info["trialstart"]

				user.info = json.dumps(info)

				db.session.commit()

				status = "cardrequired"
			else:
				status = "trialover"
		else:
			days = 30 - int((time - info["trialstart"]) / (86400000 * 30))
			status = "notover"
	else:
		if cards > 0:
			status = "cardrequired"
		else:
			status = "trialover"

	return { "days": days, "status": status }

def getRanStr():
	strid = ""

	for k in range(6):
		strid += str(randint(0, 9))

	return strid

def stripeFee(amount, add):
	if add == True:
		amount = (amount + 0.30) / (1 - 0.029)
	else:
		amount = (amount * (1 - 0.029) - 0.30)

	return amount

def calcTax(amount):
	pst = 0.08 * amount
	hst = 0.05 * amount

	return pst + hst

def pushInfo(to, title, body, data):
	return PushMessage(to=to, title=title, body=body, data=data)

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

@app.route("/welcome_users", methods=["GET"])
def welcome_users():
	datas = User.query.all()
	users = []

	for data in datas:
		users.append(data.id)

	return { "msg": "welcome to users of easygo", "users": users }

@app.route("/login", methods=["POST"])
def user_login():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']
	msg = ""
	status = ""

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
			msg = "Cell number is blank"
		else:
			msg = "Password is blank"

	return { "errormsg": msg, "status": status }, 400

@app.route("/verify/<cellnumber>")
def user_verify(cellnumber):
	verifycode = getRanStr()

	user = User.query.filter_by(cellnumber=cellnumber).first()
	msg = ""
	status = ""

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/register", methods=["POST"])
def user_register():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']
	confirmPassword = content['confirmPassword']
	msg = ""
	status = ""

	if cellnumber != '' and password != '' and confirmPassword != '':
		if len(password) >= 6:
			if password == confirmPassword:
				user = User.query.filter_by(cellnumber=cellnumber).first()

				if user == None:
					password = generate_password_hash(password)

					customer = stripe.Customer.create(
						phone=cellnumber
					)
					customerid = customer.id

					userInfo = json.dumps({"customerId": customerid, "paymentStatus": "required", "pushToken": ""})

					user = User(cellnumber, password, '', '', userInfo)
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
			msg = "Cell number is blank"
		elif password == '':
			msg = "Password is blank"
		else:
			msg = "Please confirm your password"

	return { "errormsg": msg, "status": status }, 400

@app.route("/setup", methods=["POST"])
def setup():
	userid = request.form['userid']
	username = request.form['username']
	profilepath = request.files.get('profile', False)
	profileexist = False if profilepath == False else True
	permission = request.form['permission']
	time = int(request.form['time'])

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		user.username = username

		if profileexist == True:
			profile = request.files['profile']
			profilename = profile.filename

			profile.save(os.path.join('static', profilename))
			user.profile = profilename
		else:
			if permission == "true":
				msg = "Please take a photo of yourself for identification purpose"

		info["trialstart"] = time
		user.info = json.dumps(info)

		if msg == "":
			stripe.Customer.modify(
				customerid,
				name=username
			)
			
			db.session.commit()

			return { "msg": "User setup" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/update_user", methods=["POST"])
def update_user():
	userid = request.form['userid']
	username = request.form['username']
	cellnumber = request.form['cellnumber']
	profilepath = request.files.get('profile', False)
	profileexist = False if profilepath == False else True
	permission = request.form['permission']

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

	if user != None:
		if profileexist == True:
			profile = request.files['profile']
			newprofilename = profile.filename
			oldprofile = user.profile

			if oldprofile != "" and os.path.exists("static/" + oldprofile):
				os.remove("static/" + oldprofile)

			profile.save(os.path.join('static', newprofilename))
			user.profile = newprofilename

		exist_username = User.query.filter_by(username=username).count()

		if exist_username == 0:
			user.username = username
		else:
			msg = "This username is already taken"
			status = "sameusername"

		exist_cellnumber = User.query.filter_by(cellnumber=cellnumber).count()

		if exist_cellnumber == 0:
			user.cellnumber = cellnumber
		else:
			msg = "This cell number is already taken"
			status = "samecellnumber"

		info = json.loads(user.info)
		customerid = info["customerId"]

		if msg == "":
			stripe.Customer.modify(
				customerid,
				phone=cellnumber,
				name=username
			)

			db.session.commit()

			return { "msg": "update successfully" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/update_notification_token", methods=["POST"])
def user_update_notification_token():
	content = request.get_json()

	userid = content['userid']
	token = content['token']

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		info["pushToken"] = token

		user.info = json.dumps(info)

		db.session.commit()

		return { "msg": "Push token updated" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_user_info/<id>")
def get_user_info(id):
	user = User.query.filter_by(id=id).first()
	msg = ""
	status = ""

	if user != None:
		info = {
			"username": user.username,
			"cellnumber": user.cellnumber,
			"profile": user.profile
		}

		return { "userInfo": info }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_trial_info", methods=["POST"])
def get_trial_info():
	content = request.get_json()

	userid = str(content['userid'])
	time = int(content['time'])

	trialinfo = trialInfo(userid, time)
	days = trialinfo["days"]
	status = trialinfo["status"]

	if status != "cardrequired":
		return { "days": days, "status": status }

	return { "errormsg": "", "status": status }, 400

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

		info["paymentStatus"] = "filled"

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
	msg = ""
	status = ""

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_payment_methods/<id>")
def get_payment_methods(id):
	user = User.query.filter_by(id=id).first()
	msg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]
		cards = []

		customer = stripe.Customer.retrieve(customerid)
		default_card = customer.default_source

		methods = stripe.Customer.list_sources(
			customerid,
			object="card"
		)
		datas = methods.data

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/set_paymentmethoddefault", methods=["POST"])
def set_paymentmethoddefault():
	content = request.get_json()

	userid = content['userid']
	cardid = content['cardid']

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_paymentmethod_info", methods=["POST"])
def get_paymentmethod_info():
	content = request.get_json()

	userid = content['userid']
	cardid = content['cardid']

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/delete_paymentmethod", methods=["POST"])
def delete_paymentmethod():
	content = request.get_json()

	userid = content['userid']
	cardid = content['cardid']

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_num_updates", methods=["POST"])
def get_num_updates():
	content = request.get_json()

	userid = str(content['userid'])
	time = content['time']

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

	if user != None:
		num = 0

		# cart orders called for self
		sql = "select count(*) as num from cart where adder = " + userid + " and callfor = '[]' and not status = 'unlisted'"
		num += query(sql, True)[0]["num"]

		# cart orders called for other user(s)
		sql = "select count(*) as num from cart where "
		sql += "("
		sql += "callfor like '%\"userid\": \"" + userid + "\", \"status\": \"waiting\"%'"
		sql += " or "
		sql += "callfor like '%\"status\": \"waiting\", \"userid\": \"" + userid + "\"%'"
		sql += ") or "
		sql += "(adder = " + userid + " and not callfor = '[]' and status = 'checkout') or "
		sql += "(not callfor = '[]' and status = 'ready')"
		num += query(sql, True)[0]["num"]

		# dining orders called for user
		sql = "select count(*) as num from schedule where "
		sql += "("
		sql += "orders like '%\"userid\": \"" + userid + "\", \"status\": \"confirmawaits\"%'"
		sql += " or "
		sql += "orders like '%\"status\": \"confirmawaits\", \"userid\": \"" + userid + "\"%'"
		sql += ")"
		num += query(sql, True)[0]["num"]

		# requested payment method for order for
		sql = "select count(*) as num from cart where "
		sql += "("
		sql += "callfor like '%\"userid\": \"" + userid + "\", \"status\": \"paymentrequested\"%'"
		sql += " or "
		sql += "callfor like '%\"status\": \"paymentrequested\", \"userid\": \"" + userid + "\"%'"
		sql += ")"
		num += query(sql, True)[0]["num"]

		# get reservation requests
		sql = "select count(*) as num from schedule where "
		sql += "(userId = " + userid + " and (status = 'requested' or status = 'rebook' or status = 'cancel' or status = 'accepted' or status = 'change' or status = 'confirmed')) or "
		sql += "(customers like '%\"userid\": \"" + userid + "\"%')"
		num += query(sql, True)[0]["num"]

		return { "numNotifications": num }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_notifications/<id>")
def get_notifications(id):
	user = User.query.filter_by(id=id).first()
	msg = ""
	status = ""

	if user != None:
		userId = user.id
		notifications = []

		# cart orders called for self
		sql = "select * from cart where adder = " + str(id) + " and callfor = '[]' and not status = 'unlisted'"
		datas = query(sql, True)

		for data in datas:
			adder = User.query.filter_by(id=data['adder']).first()
			product = Product.query.filter_by(id=data['productId']).first()
			options = json.loads(data['options'])
			others = json.loads(data['others'])
			sizes = json.loads(data['sizes'])

			for k, option in enumerate(options):
				option["key"] = "option-" + str(len(notifications)) + "-" + str(k)

			for k, other in enumerate(others):
				other["key"] = "other-" + str(len(notifications)) + "-" + str(k)

			for k, size in enumerate(sizes):
				size["key"] = "size-" + str(len(notifications)) + "-" + str(k)

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
		sql = "select * from cart where "
		sql += "("
		sql += "callfor like '%\"userid\": \"" + str(id) + "\", \"status\": \"waiting\"%'"
		sql += " or "
		sql += "callfor like '%\"status\": \"waiting\", \"userid\": \"" + str(id) + "\"%'"
		sql += ") or "
		sql += "(adder = " + str(id) + " and not callfor = '[]' and status = 'checkout') or "
		sql += "(not callfor = '[]' and status = 'ready')"
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
				option["key"] = "option-" + str(len(notifications)) + "-" + str(k)

			for k, other in enumerate(others):
				other["key"] = "other-" + str(len(notifications)) + "-" + str(k)

			for k, size in enumerate(sizes):
				size["key"] = "size-" + str(len(notifications)) + "-" + str(k)

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
				"price": int(data['quantity']) * float(product.price) if product.price != "" else "",
				"status": data['status'],
				"orderNumber": data['orderNumber']
			})

		# dining orders called for user
		sql = "select * from schedule where "
		sql += "("
		sql += "orders like '%\"userid\": \"" + str(id) + "\", \"status\": \"confirmawaits\"%'"
		sql += " or "
		sql += "orders like '%\"status\": \"confirmawaits\", \"userid\": \"" + str(id) + "\"%'"
		sql += ")"
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

								for k, option in enumerate(options):
									option["key"] = "option-" + str(len(notifications)) + "-" + str(k)

								for k, other in enumerate(others):
									other["key"] = "other-" + str(len(notifications)) + "-" + str(k)

								for k, size in enumerate(sizes):
									size["key"] = "size-" + str(len(notifications)) + "-" + str(k)

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
									"price": int(orderer['quantity']) * float(product.price) if product.price != "" else "",
									"status": "unlisted"
								})

		# get requested payment method to order for
		sql = "select * from cart where "
		sql += "("
		sql += "callfor like '%\"userid\": \"" + str(id) + "\", \"status\": \"paymentrequested\"%'"
		sql += " or "
		sql += "callfor like '%\"status\": \"paymentrequested\", \"userid\": \"" + str(id) + "\"%'"
		sql += ")"
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
				option["key"] = "option-" + str(len(notifications)) + "-" + str(k)

			for k, other in enumerate(others):
				other["key"] = "other-" + str(len(notifications)) + "-" + str(k)

			for k, size in enumerate(sizes):
				size["key"] = "size-" + str(len(notifications)) + "-" + str(k)

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

		# get requests
		sql = "select * from schedule where "
		sql += "(userId = " + str(id) + " and (status = 'requested' or status = 'rebook' or status = 'cancel' or status = 'accepted' or status = 'change' or status = 'confirmed')) or "
		sql += "(customers like '%\"userid\": \"" + str(id) + "\"%')"
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
			chargedUser = False
			info = json.loads(data['info'])

			if data["locationType"] == 'restaurant':
				customers = json.loads(data['customers'])
				
				for customer in customers:
					if customer['userid'] == id:
						confirm = customer['status'] == 'confirmed'

				customers = len(customers)
			else:
				customers = int(data['customers'])
				chargedUser = info["chargedUser"]

			if data["locationType"] != 'restaurant':
				allowPayment = info["allowpayment"]
			else:
				orders = json.loads(data["orders"])
				charges = orders["charges"]
				allowPayment = charges[str(userId)]["allowpayment"] if str(userId) in charges else False


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
				"serviceprice": float(service.price) if service != None else "",
				"time": int(data['time']),
				"action": data['status'],
				"nextTime": int(data['nextTime']) if data['nextTime'] != "" else "",
				"reason": data['cancelReason'],
				"table": data['table'],
				"booker": userId == data['userId'],
				"bookerName": booker.username,
				"diners": customers,
				"confirm": confirm,
				"chargedUser": chargedUser,
				"allowPayment": allowPayment,
				"seated": info["dinersseated"] if "dinersseated" in info else None
			})

		return { "notifications": notifications }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/search_friends", methods=["POST"])
def search_friends():
	content = request.get_json()

	userid = content['userid']
	searchusername = content['username']

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/search_diners", methods=["POST"])
def search_diners():
	content = request.get_json()

	userid = str(content['userid'])
	scheduleid = content['scheduleid']
	searchusername = content['username']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	msg = ""
	status = ""

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/select_user/<id>")
def select_user(id):
	user = User.query.filter_by(id=id).first()
	msg = ""
	status = ""

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/request_user_payment_method/<id>")
def request_user_payment_method(id):
	user = User.query.filter_by(id=id).first()
	msg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)

		info["paymentStatus"] = "requested"

		user.info = json.dumps(info)

		db.session.commit()

		return { "msg": "Card requested" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_reset_code/<phonenumber>")
def get_user_reset_code(phonenumber):
	user = User.query.filter_by(cellnumber=phonenumber).first()
	msg = ""
	status = ""

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

	return { "errormsg": msg, "status": status }, 400

@app.route("/reset_password", methods=["POST"])
def user_reset_password():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['newPassword']
	confirmPassword = content['confirmPassword']

	user = User.query.filter_by(cellnumber=cellnumber).first()
	msg = ""
	status = ""

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
				msg = "Password is blank"
			else:
				msg = "Please confirm your password"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400
