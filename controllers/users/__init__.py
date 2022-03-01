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
	image = db.Column(db.String(20))

	def __init__(self, locationId, parentMenuId, name, image):
		self.locationId = locationId
		self.parentMenuId = parentMenuId
		self.name = name
		self.image = image

	def __repr__(self):
		return '<Menu %r>' % self.name

class Service(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	name = db.Column(db.String(20))
	image = db.Column(db.String(20))
	price = db.Column(db.String(10))
	duration = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, price, duration):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
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
	note = db.Column(db.String(225))
	orders = db.Column(db.Text)
	table = db.Column(db.String(20))
	info = db.Column(db.String(100))

	def __init__(self, userId, workerId, locationId, menuId, serviceId, userInput, time, status, cancelReason, nextTime, locationType, note, orders, table, info):
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
	image = db.Column(db.String(20))
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(150))
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, options, others, sizes, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
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
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(225))
	note = db.Column(db.String(100))
	status = db.Column(db.String(10))
	orderNumber = db.Column(db.String(10))
	waitTime = db.Column(db.String(2))

	def __init__(self, locationId, productId, userInput, quantity, adder, options, others, sizes, note, status, orderNumber, waitTime):
		self.locationId = locationId
		self.productId = productId
		self.userInput = userInput
		self.quantity = quantity
		self.adder = adder
		self.options = options
		self.others = others
		self.sizes = sizes
		self.note = note
		self.status = status
		self.orderNumber = orderNumber
		self.waitTime = waitTime

	def __repr__(self):
		return '<Cart %r>' % self.productId

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

	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['password']
	errormsg = ""
	status = ""

	if cellnumber != '' and password != '':
		user = User.query.filter_by(cellnumber=cellnumber).first()

		if user != None:
			if check_password_hash(user.password, password):
				userid = user.id

				user.password = generate_password_hash(password)

				db.session.commit()

				if user.username == '':
					return { "id": userid, "msg": "setup" }
				else:
					return { "id": userid, "msg": "main" }
			else:
				errormsg = "Password is incorrect"
		else:
			errormsg = "User doesn't exist"
	else:
		if cellnumber == '':
			errormsg = "Cell number is blank"
		else:
			errormsg = "Password is blank"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/verify/<cellnumber>")
def user_verify(cellnumber):
	verifycode = getRanStr()

	cellnumber = cellnumber.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	user = User.query.filter_by(cellnumber=cellnumber).first()
	errormsg = ""
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
		errormsg = "Cell number already used"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/register", methods=["POST"])
def user_register():
	content = request.get_json()

	username = content['username']
	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['password']
	confirmPassword = content['confirmPassword']
	errormsg = ""
	status = ""

	if username != "" and cellnumber != '' and password != '' and confirmPassword != '':
		if len(password) >= 6:
			if password == confirmPassword:
				user = User.query.filter_by(cellnumber=cellnumber).first()

				if user == None:
					password = generate_password_hash(password)

					userInfo = json.dumps({"pushToken": ""})

					user = User(cellnumber, password, username, userInfo)
					db.session.add(user)
					db.session.commit()

					return { "id": user.id }
				else:
					errormsg = "User already exist"
			else:
				errormsg = "Password is mismatch"
		else:
			errormsg = "Password needs to be atleast 6 characters long"
	else:
		if username == '':
			errormsg = "Please enter your name"
		elif cellnumber == '':
			errormsg = "Cell number is blank"
		elif password == '':
			errormsg = "Password is blank"
		else:
			errormsg = "Please confirm your password"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_user", methods=["POST"])
def update_user():
	userid = request.form['userid']
	username = request.form['username']
	cellnumber = request.form['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")

	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		if username != "":
			if user.username != username:
				exist_username = User.query.filter_by(username=username).count()

				if exist_username == 0:
					user.username = username
				else:
					errormsg = "This username is already taken"
					status = "sameusername"

		if cellnumber != "":
			if user.cellnumber != cellnumber:
				exist_cellnumber = User.query.filter_by(cellnumber=cellnumber).first()

				if exist_cellnumber == 0:
					user.cellnumber = cellnumber
				else:
					errormsg = "This cell number is already taken"
					status = "samecellnumber"

		info = json.loads(user.info)

		if errormsg == "":
			db.session.commit()

			return { "msg": "update successfully" }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_notification_token", methods=["POST"])
def user_update_notification_token():
	content = request.get_json()

	userid = content['userid']
	token = content['token']

	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		info["pushToken"] = token

		user.info = json.dumps(info)

		db.session.commit()

		return { "msg": "Push token updated" }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_user_info/<id>")
def get_user_info(id):
	user = User.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if user != None:
		cellnumber = user.cellnumber

		f3 = str(cellnumber[0:3])
		s3 = str(cellnumber[3:6])
		l4 = str(cellnumber[6:len(cellnumber)])

		cellnumber = "(" + f3 + ") " + s3 + "-" + l4

		info = {
			"id": id,
			"username": user.username,
			"cellnumber": cellnumber
		}

		return { "userInfo": info }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_num_notifications", methods=["POST"])
def get_num_notifications():
	content = request.get_json()

	userid = str(content['userid'])

	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		num = 0

		# cart orders called for self
		sql = "select count(*) as num from cart where adder = " + userid + " and (status = 'checkout' or status = 'ready') group by adder, orderNumber"
		numCartorderers = query(sql, True)
		num += numCartorderers[0]["num"] if len(numCartorderers) > 0 else 0

		# get schedules
		sql = "select count(*) as num from schedule where userId = " + userid + " and (status = 'cancel' or status = 'confirmed')"
		num += query(sql, True)[0]["num"]

		return { "numNotifications": num }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_notifications/<id>")
def get_notifications(id):
	user = User.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if user != None:
		userId = user.id
		notifications = []

		# cart orders called for self
		sql = "select orderNumber from cart where adder = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by orderNumber"
		datas = query(sql, True)

		for data in datas:
			cartitem = Cart.query.filter_by(orderNumber=data["orderNumber"]).first()
			numCartitems = Cart.query.filter_by(orderNumber=data["orderNumber"]).count()

			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "cart-order-self",
				"orderNumber": data['orderNumber'],
				"numOrders": numCartitems,
				"status": cartitem.status,
				"waitTime": cartitem.waitTime
			})

		# get schedules
		sql = "select * from schedule where "
		sql += "(userId = " + str(id) + " and (status = 'cancel' or status = 'confirmed'))"
		datas = query(sql, True)

		for data in datas:
			location = None
			service = None

			if data['locationId'] != "":
				location = Location.query.filter_by(id=data['locationId']).first()

			if data['serviceId'] != -1:
				service = Service.query.filter_by(id=data['serviceId']).first()

			booker = User.query.filter_by(id=data['userId']).first()
			confirm = False
			info = json.loads(data['info'])

			if data["locationType"] == 'restaurant':
				orders = json.loads(data["orders"])
				charges = orders["charges"]
				
			if data["workerId"] > -1:
				owner = Owner.query.filter_by(id=data["workerId"]).first()

				worker = {
					"id": data["workerId"],
					"username": owner.username
				}
			else:
				worker = None

			orders = json.loads(data["orders"])
			numOrders = None

			if "groups" in orders:
				groups = orders["groups"]
				
				for rounds in groups:
					for k in rounds:
						if k != "status" and k != "id" and k == str(id):
							numOrders = len(rounds[k])

			userInput = json.loads(data['userInput'])
			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "service",
				"id": str(data['id']),
				"locationid": data['locationId'],
				"location": location.name,
				"worker": worker,
				"menuid": int(data['menuId']) if data['menuId'] != "" else "",
				"serviceid": int(data['serviceId']) if data['serviceId'] != -1 else "",
				"service": service.name if service != None else userInput['name'] if 'name' in userInput else "",
				"locationimage": location.logo,
				"locationtype": location.type,
				"serviceimage": service.image if service != None else "",
				"serviceprice": float(service.price) if service != None else float(userInput['price']) if 'price' in userInput else "",
				"time": int(data['time']),
				"action": data['status'],
				"nextTime": int(data['nextTime']) if data['nextTime'] != "" else "",
				"reason": data['cancelReason'],
				"table": data['table'],
				"booker": userId == data['userId'],
				"bookerName": booker.username,
				"confirm": confirm,
				"numOrders": numOrders,
				"seated": info["dinersseated"] if "dinersseated" in info else None,
				"requestPayment": True if "price" in userInput else False,
				"workerInfo": {
					"id": owner.id,
					"username": owner.username,
					"requestprice": float(userInput["price"]) if "price" in userInput else 0,
					"tip": 0
				} if data["workerId"] > -1 else {}
			})

		return { "notifications": notifications }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_reset_code/<phonenumber>")
def get_user_reset_code(phonenumber):
	user = User.query.filter_by(cellnumber=phonenumber).first()
	errormsg = ""
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
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/reset_password", methods=["POST"])
def user_reset_password():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['newPassword']
	confirmPassword = content['confirmPassword']

	user = User.query.filter_by(cellnumber=cellnumber).first()
	errormsg = ""
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
					errormsg = "Password is mismatch"
			else:
				errormsg = "Password needs to be atleast 6 characters long"
		else:
			if password == '':
				errormsg = "Password is blank"
			else:
				errormsg = "Please confirm your password"
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
