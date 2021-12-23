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
	workerId = db.Column(db.Integer)
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

	def __init__(self, userId, workerId, locationId, menuId, serviceId, time, status, cancelReason, nextTime, locationType, customers, note, orders, table, info):
		self.userId = userId
		self.workerId = workerId
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

@app.route("/welcome_services", methods=["GET"])
def welcome_services():
	datas = Location.query.all()
	services = []

	for data in datas:
		services.append(data.id)

	return { "msg": "welcome to services of easygo", "services": services }

@app.route("/get_services", methods=["POST"])
def get_services():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	menuid = content['menuid']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		datas = Service.query.filter_by(locationId=locationid, menuId=menuid).all()
		services = []
		numservices = 0

		if len(datas) > 0:
			for index, data in enumerate(datas):
				schedule = Schedule.query.filter_by(userId=userid, serviceId=data.id).first()

				services.append({
					"key": "service-" + str(data.id),
					"id": data.id,
					"name": data.name,
					"info": data.info,
					"image": data.image,
					"price": data.price,
					"duration": data.duration,
					"scheduleid": schedule.id if schedule != None else None
				})
				numservices += 1

		return { "services": services, "numservices": len(services) }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_service_info/<id>")
def get_service_info(id):
	service = Service.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if service != None:
		info = {
			"name": service.name,
			"info": service.info,
			"image": service.image,
			"price": float(service.price),
			"duration": service.duration
		}

		return { "serviceInfo": info }
	else:
		errormsg = "Service doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_service", methods=["POST"])
def add_service():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	name = request.form['name']
	info = request.form['info']
	imagepath = request.files.get('image', False)
	imageexist = False if imagepath == False else True
	price = request.form['price']
	duration = request.form['duration']
	permission = request.form['permission']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		data = query("select * from service where locationId = " + str(locationid) + " and menuId = '" + str(menuid) + "' and name = '" + name + "'", True)

		if len(data) == 0:
			imagename = ""
			if imageexist == True:
				image = request.files['image']
				imagename = image.filename

				image.save(os.path.join("static", imagename))
			else:
				if permission == "true":
					errormsg = "Please take a good photo"

			if errormsg == "":
				service = Service(locationid, menuid, name, info, imagename, price, duration)

				db.session.add(service)
				db.session.commit()

				return { "id": service.id }
		else:
			errormsg = "Service already exist"
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_service", methods=["POST"])
def update_service():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	serviceid = request.form['serviceid']
	name = request.form['name']
	info = request.form['info']
	imagepath = request.files.get('image', False)
	imageexist = False if imagepath == False else True
	price = request.form['price']
	duration = request.form['duration']
	permission = request.form['permission']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		service = Service.query.filter_by(id=serviceid, locationId=locationid, menuId=menuid).first()

		if service != None:
			service.name = name
			service.info = info
			service.price = price
			service.duration = duration

			if imageexist == True:
				image = request.files['image']
				newimagename = image.filename
				oldimage = service.image

				if oldimage != newimagename:
					if oldimage != "" and os.path.exists("static/" + oldimage):
						os.remove("static/" + oldimage)

					image.save(os.path.join('static', newimagename))
					service.image = newimagename
			else:
				if permission == "true":
					errormsg = "Please take a good photo"

			if errormsg == "":
				db.session.commit()

				return { "msg": "service updated", "id": service.id }
		else:
			errormsg = "Service already exist"
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/remove_service/<id>")
def remove_service(id):
	service = Service.query.filter_by(id=id).first()

	if service != None:
		image = service.image

		if image != "" and os.path.exists("static/" + image):
			os.remove("static/" + image)

		db.session.delete(service)
		db.session.commit()

		return { "msg": "" }

	return { "errormsg": "Service doesn't exist" }

