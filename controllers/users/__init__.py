from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, os, json, stripe
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
stripe.api_key = "sk_test_lft1B76yZfF2oEtD5rI3y8dz"

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(10), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	profile = db.Column(db.String(25))
	customerid = db.Column(db.String(25))

	def __init__(self, cellnumber, password, username, profile, customerid):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.profile = profile
		self.customerid = customerid

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
	accountid = db.Column(db.String(25))

	def __init__(
		self, 
		name, addressOne, addressTwo, city, province, postalcode, phonenumber, logo, 
		longitude, latitude, owners, type, hours, accountid
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
		self.accountid = accountid

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
	seaters = db.Column(db.Integer)

	def __init__(self, userId, locationId, menuId, serviceId, time, status, cancelReason, nextTime, locationType, seaters):
		self.userId = userId
		self.locationId = locationId
		self.menuId = menuId
		self.serviceId = serviceId
		self.time = time
		self.status = status
		self.cancelReason = cancelReason
		self.nextTime = nextTime
		self.locationType = locationType
		self.seaters = seaters

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

@app.route("/", methods=["GET"])
def welcome_users():
	return { "msg": "welcome to users of easygo" }

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

				if user.username == '':
					return { "userid": userid, "msg": "setup" }
				else:
					return { "userid": userid, "msg": "main" }
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

					user = User(cellnumber, password, '', '', customer.id)
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
		customerid = user.customerid

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

				if os.path.exists("static/" + oldprofile):
					os.remove("static/" + oldprofile)

			profile.save(os.path.join('static', profile.filename))

			user.profile = profile.filename

		user.username = username
		user.cellnumber = cellnumber

		customerid = user.customerid

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
		customerid = user.customerid

		stripe.Customer.create_source(
			customerid,
			source=cardtoken
		)

		return { "msg": "Added a payment method" }
	else:
		msg = ""

@app.route("/update_paymentmethod", methods=["POST"])
def update_paymentmethod():
	content = request.get_json()

	userid = content['userid']
	cardid = content['cardid']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		customerid = user.customerid

		stripe.Customer.modify_source(
			customerid,
			cardid
		)
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_payment_methods/<id>")
def get_payment_methods(id):
	user = User.query.filter_by(id=id).first()

	if user != None:
		customerid = user.customerid

		customer = stripe.Customer.retrieve(customerid)
		default_card = customer.default_source

		cards = stripe.Customer.list_sources(
			customerid,
			object="card"
		)
		datas = cards.data
		cards = []

		for k in range(len(datas)):
			data = datas[k]

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
		customerid = user.customerid

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
		customerid = user.customerid

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
		customerid = user.customerid

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
		notifications = []
		
		# get orders
		sql = "select * from cart where callfor like '%\"userid\": " + str(id) + ", \"status\": \"waiting\"%'"
		datas = query(sql, True)

		for data in datas:
			adder = User.query.filter_by(id=data['adder']).first()
			product = Product.query.filter_by(id=data['productId']).first()
			callfor = json.loads(data['callfor'])
			friends = []

			for info in callfor:
				friend = User.query.filter_by(id=info['userid']).first()

				friends.append({
					"key": str(data['id']) + "-" + str(friend.id),
					"username": friend.username,
					"profile": friend.profile
				})

			notifications.append({
				"key": "order-" + str(data['id']),
				"type": "order",
				"id": str(data['id']),
				"name": product.name,
				"image": product.image,
				"options": json.loads(data['options']),
				"quantity": int(data['quantity']),
				"price": int(data['quantity']) * float(product.price),
				"orderers": friends,
				"adder": {
					"username": adder.username,
					"profile": adder.profile
				}
			})

		sql = "select * from schedule where userId = " + str(id) + " and (status = 'accepted' or status = 'rebook' or status = 'cancel')"
		datas = query(sql, True)

		for data in datas:
			location = None
			service = None

			if data['locationId'] != "":
				location = Location.query.filter_by(id=data['locationId']).first()

			if data['serviceId'] != "":
				service = Service.query.filter_by(id=data['serviceId']).first()

			notifications.append({
				"key": "order-" + str(data['id']),
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
				"reason": data['cancelReason']
			})

		return { "notifications": notifications }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_updates", methods=["POST"])
def get_updates():
	content = request.get_json()

	userid = content['userid']
	time = content['time']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		num = 0

		# delete passed schedules
		schedules = query("select id from schedule where userId = " + str(userid) + " and status = 'accepted' and " + str(time) + " > time", True)

		for data in schedules:
			query("delete from schedule where id = " + str(data['id']), False)

		sql = "select count(*) as num from cart where callfor like '%\"userid\": " + str(userid) + ",%'"
		num += query(sql, True)[0]["num"]

		sql = "select count(*) as num from schedule where userId = " + str(userid) + " and (status = 'accepted' or status = 'rebook')"
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
		row = []
		column = []
		rownum = 0
		numSearchedFriends = 0

		if searchusername != "":
			datas = query("select id, profile, username from user where username like '%" + searchusername + "%' and not id = " + str(userid), True)

			for k in range(len(datas)):
				data = datas[k]

				row.append({
					"key": "friend-" + str(data['id']),
					"id": data['id'],
					"profile": data['profile'],
					"username": data['username']
				})
				numSearchedFriends += 1

				if len(row) == 4 or (len(datas) - 1 == k and len(row) > 0):
					column.append({ "key": "friend-row-" + str(len(column)), "row": row })
					row = []

		return { "searchedFriends": column, "numSearchedFriends": numSearchedFriends }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }
