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

def stripeFee(cost):
	return (cost + 0.30) / (1 - 0.029)

def calcTax(cost):
	pst = 0.08 * cost
	hst = 0.05 * cost

	return pst + hst

def pushInfo(to, title, body, data):
	return PushMessage(to=to, title=title, body=body, data=data)

def customerPay(cost, userid, locationid):
	chargecost = stripeFee(cost + calcTax(cost))
	transfercost = cost + calcTax(cost)

	user = User.query.filter_by(id=userid).first()
	info = json.loads(user.info)
	customerid = info["customerId"]

	charge = stripe.Charge.create(
		amount=int(chargecost * 100),
		currency="cad",
		customer=customerid
	)

	if locationid != None:
		location = Location.query.filter_by(id=locationid).first()
		info = json.loads(location.info)
		accountid = info["accountId"]

		transfer = stripe.Transfer.create(
			amount=int(transfercost * 100),
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

@app.route("/welcome_schedules", methods=["GET"])
def welcome_schedules():
	datas = Schedule.query.all()
	schedules = []

	for data in datas:
		schedules.append(data.id)

	return { "msg": "welcome to schedules of easygo", "schedules": schedules }

@app.route("/get_requests", methods=["POST"])
def get_requests():
	content = request.get_json()

	ownerid = content['ownerid']
	locationid = content['locationid']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		# get requested schedules
		datas = query("select * from schedule where locationId = " + str(locationid) + " and (status = 'requested' or status = 'change' or status = 'accepted')", True)
		requests = []

		for data in datas:
			service = {}

			if data['serviceId'] != "":
				service = Service.query.filter_by(id=data['serviceId']).first()

			user = User.query.filter_by(id=data['userId']).first()

			if data['workerId'] > -1:
				owner = Owner.query.filter_by(id=data['workerId']).first()

				worker = {
					"id": data['workerId'],
					"username": owner.username
				}
			else:
				worker = None

			userInput = json.loads(data['userInput'])
			requests.append({
				"key": "request-" + str(data['id']),
				"id": str(data['id']),
				"type": data['locationType'],
				"worker": worker,
				"userId": user.id,
				"username": user.username,
				"time": int(data['nextTime']) if data['nextTime'] != "" else int(data['time']),
				"name": service.name if service != None else userInput['name'] if 'name' in userInput else "",
				"image": service.image if service != None else None,
				"note": data['note'],
				"diners": len(json.loads(data['customers'])) if data['locationType'] == 'restaurant' else False,
				"tablenum": data['table'],
				"status": data['status']
			})

		datas = query("select * from cart where status = 'requested'", True)

		for data in datas:
			userInput = json.loads(data['userInput'])

			requests.append({
				"key": "order-request-" + str(data['id']),
				"id": str(data['id']),
				"product": userInput['name'],
				"quantity": data['quantity']
			})

		return { "requests": requests, "numrequests": len(requests) }
	else:
		errormsg = "Location doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_appointment_info/<id>")
def get_appointment_info(id):
	schedule = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if schedule != None:
		locationId = schedule.locationId
		serviceId = schedule.serviceId

		worker = None
		if schedule.workerId > 0:
			workerInfo = Owner.query.filter_by(id=schedule.workerId).first()

			days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
			hours = json.loads(workerInfo.hours)
			info = {}
			for day in days:
				if hours[day]["working"] == True:
					info[day] = {
						"start": hours[day]["opentime"]["hour"] + ":" + hours[day]["opentime"]["minute"],
						"end": hours[day]["closetime"]["hour"] + ":" + hours[day]["closetime"]["minute"],
						"working": hours[day]["working"]
					}

			worker = { "id": schedule.workerId, "username": workerInfo.username, "profile": workerInfo.profile, "days": info }

		info = { 
			"locationId": int(locationId), 
			"serviceId": int(serviceId), 
			"time": int(schedule.nextTime if schedule.nextTime != "" else schedule.time), 
			"worker": worker
		}

		if serviceId != -1:
			service = Service.query.filter_by(id=serviceId).first()

			if service != None:
				info["name"] = service.name
			else:
				errormsg = "Service doesn't exist"
				status = "nonexist"
		else:
			userInput = json.loads(schedule.userInput)

			info["name"] = userInput["name"]

		if errormsg == "":
			return { "appointmentInfo": info }
	else:
		errormsg = "Appointment doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_reservation_info/<id>")
def get_reservation_info(id):
	schedule = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if schedule != None:
		locationId = schedule.locationId

		location = Location.query.filter_by(id=locationId).first()

		if location != None:
			customers = json.loads(schedule.customers)
			row = []
			rownum = 0
			column = []

			for customer in customers:
				user = User.query.filter_by(id=customer["userid"]).first()

				rownum += 1
				row.append({ "key": "selected-friend-" + str(rownum), "id": user.id, "profile": user.profile })

				if len(row) == 3:
					column.append({ "key": "selected-friend-row-" + str(len(column)), "row": row })
					row = []

			if len(row) > 0:
				column.append({ "key": "selected-friend-row-" + str(len(column)), "row": row })

			info = {
				"locationId": locationId,
				"name": location.name,
				"numdiners": len(json.loads(schedule.customers)),
				"diners": column,
				"note": schedule.note,
				"table": schedule.table,
				"time": int(schedule.nextTime if schedule.nextTime != "" else schedule.time)
			}

			return { "reservationInfo": info }
		else:
			errormsg = "Location doesn't exist"
			status = "nonexist"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/reschedule_appointment", methods=["POST"])
def reschedule_appointment():
	content = request.get_json()

	ownerid = content['ownerid']
	appointmentid = content['appointmentid']
	time = content['time']

	schedule = Schedule.query.filter_by(id=appointmentid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		info = json.loads(schedule.info)
		info["allowpayment"] = False

		schedule.status = "rebook"
		schedule.nextTime = time
		schedule.info = json.dumps(info)
		schedule.workerId = ownerid

		db.session.commit()

		location = Location.query.filter_by(id=schedule.locationId).first()
		service = Service.query.filter_by(id=schedule.serviceId).first()
		user = User.query.filter_by(id=schedule.userId).first()
		userInfo = json.loads(user.info)
		userInput = json.loads(schedule.userInput)

		workerInfo = Owner.query.filter_by(id=ownerid).first()
		worker = {
			"id": ownerid,
			"username": workerInfo.username
		}

		if userInfo["pushToken"] != "":
			if send_msg == True:
				resp = push(pushInfo(
					userInfo["pushToken"],
					"Appointment for service rescheduled",
					location.name + " chose another time for you for service: " + (service.name if service != None else userInput["name"]),
					content
				))
			else:
				resp = { "status": "ok" }
		else:
			resp = { "status": "ok" }

		if resp["status"] == "ok":
			return { "msg": "appointment rescheduled", "receiver": "user" + str(schedule.userId), "worker": worker }
		else:
			errormsg = "Push notification failed"
	else:
		errormsg = "Appointment doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/reschedule_reservation", methods=["POST"])
def reschedule_reservation():
	content = request.get_json()

	scheduleid = content['scheduleid']
	time = content['time']
	table = content['table']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		receiver = []
		diners = json.loads(schedule.customers)

		for diner in diners:
			receiver.append("user" + str(diner["userid"]))

		schedule.status = "rebook"
		schedule.nextTime = time
		schedule.table = table

		db.session.commit()

		return { "msg": "Reservation rescheduled", "receiver": receiver }
	else:
		errormsg = "Reservation doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/make_appointment", methods=["POST"])
def make_appointment():
	content = request.get_json()

	userid = content['userid']
	workerid = content['workerid']
	locationid = content['locationid']
	serviceid = content['serviceid']
	serviceinfo = content['serviceinfo']
	oldtime = content['oldtime']
	time = content['time']
	note = content['note']

	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		location = Location.query.filter_by(id=locationid).first()

		if serviceid != -1:
			service = Service.query.filter_by(id=serviceid).first()
			schedule = Schedule.query.filter_by(userId=userid, serviceId=serviceid).first()
			servicename = service.name
			menuid = service.menuId
		else:
			schedule = Schedule.query.filter(Schedule.userId==userid, Schedule.userInput.like("%\"name\": \"" + str(serviceinfo) + "\"%")).first()
			servicename = serviceinfo
			menuid = -1

		if location != None:
			owners = query("select id, info from owner where info like '%\"locationId\": \"" + str(location.id) + "\"%'", True)
			locationInfo = json.loads(location.info)
			receiver = []
			pushids = []

			for owner in owners:
				info = json.loads(owner["info"])

				receiver.append("owner" + str(owner["id"]))

				if info["pushToken"] != "":
					pushids.append(info["pushToken"])

			if schedule != None: # existing schedule
				info = json.loads(schedule.info)
				info["allowpayment"] = False
				schedule.info = json.dumps(info)
				schedule.time = time
				schedule.nextTime = ''
				schedule.note = note
				schedule.workerId = workerid

				db.session.commit()

				if len(pushids) > 0:
					pushmessages = []
					for pushid in pushids:
						pushmessages.append(pushInfo(
							pushid, 
							"Appointment remade",
							"A client remade an appointment for service: " + servicename,
							content
						))
					
					if send_msg == True:
						resp = push(pushmessages)
					else:
						resp = { "status": "ok" }
				else:
					resp = { "status": "ok" }

				if resp["status"] == "ok":
					return { "msg": "appointment remade", "receiver": receiver, "time": time }
			else: # new schedule
				info = json.dumps({"allowpayment": False,"chargedUser": False,"workerId":0,"cut": locationInfo["cut"]})
				userInput = json.dumps({ "name": serviceinfo })
				appointment = Schedule(userid, workerid, locationid, menuid, serviceid, userInput, time, 'confirmed', '', '', location.type, 1, note, '[]', '', info)

				db.session.add(appointment)
				db.session.commit()

				if len(pushids) > 0:
					if send_msg == True:
						pushmessages = []
						for pushid in pushids:
							pushmessages.append(pushInfo(
								pushid, 
								"Appointment made",
								"A client made an appointment for service: " + servicename,
								content
							))

						resp = push(pushmessages)
					else:
						resp = { "status": "ok" }
				else:
					resp = { "status": "ok" }

				if resp["status"] == "ok":
					return { "msg": "appointment added", "receiver": receiver }
				
				errormsg = "Push notification failed"
		else:
			errormsg = "Location doesn't exist"
			status = "nonexist"
	else:
		errormsg = "User doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/accept_request", methods=["POST"])
def accept_request():
	content = request.get_json()

	scheduleid = content['scheduleid']
	tablenum = content['tablenum']

	appointment = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if appointment != None:
		service = Service.query.filter_by(id=appointment.serviceId).first()
		locationId = str(appointment.locationId)
		location = Location.query.filter_by(id=locationId).first()
		appointment.status = "accepted"
		appointment.table = tablenum
		userInput = json.loads(appointment.userInput)

		if 'ownerid' in content:
			workerId = appointment.workerId

			if workerId == -1:
				appointment.workerId = content['ownerid']

				owner = Owner.query.filter_by(id=content['ownerid']).first()
			else:
				owner = Owner.query.filter_by(id=workerId).first()

			worker = {
				"id": owner.id,
				"username": owner.username
			}
		else:
			worker = None

		if appointment.nextTime != "":
			appointment.time = appointment.nextTime
			appointment.nextTime = ""

		booker = ["user" + str(appointment.userId)]
		receivingUsers = []
		receivingLocations = []
		pushids = []

		if location.type != "restaurant":
			bookerInfo = User.query.filter_by(id=appointment.userId).first()
			info = json.loads(bookerInfo.info)

			if info["pushToken"] != "":
				pushids.append(info["pushToken"])
		else:
			customers = json.loads(appointment.customers)

			for customer in customers:
				user = User.query.filter_by(id=customer["userid"]).first()
				userInfo = json.loads(user.info)

				receivingUsers.append("user" + str(customer["userid"]))

				if userInfo["pushToken"] != "":
					pushids.append(userInfo["pushToken"])

			appointment.customers = json.dumps(customers)

		db.session.commit()

		owners = query("select id from owner where info like '%\"locationId\": \"" + locationId + "\"%'", True)

		for owner in owners:
			receivingLocations.append("owner" + str(owner["id"]))

		receivers = {
			"booker": booker,
			"users": receivingUsers,
			"locations": receivingLocations
		}

		content["receivers"] = receivers
		content["tablenum"] = tablenum

		if len(pushids) > 0:
			if send_msg == True:
				pushmessages = []

				if location.type == "restaurant":
					title = "Reservation accepted"
					message = "The restaurant accepted your reservation"
				else:
					title = "Appointment accepted"
					message = "The salon accepted your appointment for service: " + (service.name if service != None else userInput["name"])
				
				for pushid in pushids:
					pushmessages.append(pushInfo(pushid, title, message, content))

				resp = push(pushmessages)
			else:
				resp = { "status": "ok" }
		else:
			resp = { "status": "ok" }

		if resp["status"] == "ok":
			return { "msg": "Appointment accepted", "receivers": receivers, "worker": worker }

		errormsg = "Push notification failed"
	else:
		errormsg = "Appointment doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/confirm_request", methods=["POST"])
def confirm_request():
	content = request.get_json()

	userid = str(content['userid'])
	scheduleid = content['scheduleid']
	time = int(content['time'])

	appointment = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if appointment != None:
		trialinfo = trialInfo()
		locationId = str(appointment.locationId)
		user = User.query.filter_by(id=userid).first()
		location = Location.query.filter_by(id=locationId).first()
		service = Service.query.filter_by(id=appointment.serviceId).first()
		userInput = json.loads(appointment.userInput)
		chargedUser = False
		pushids = []

		info = json.loads(user.info)
		customerId = info["customerId"]

		if appointment.nextTime != "":
			appointment.time = appointment.nextTime
			appointment.nextTime = ""

		appointment.status = "confirmed"

		if location.type == "restaurant":
			customers = json.loads(appointment.customers)
			receivers = { "users": [], "locations": [] }

			for customer in customers:
				if customer["userid"] == userid:
					customer["status"] = "confirmed"

					booker = User.query.filter_by(id=userid).first()
					info = json.loads(booker.info)

					stripeCustomer = stripe.Customer.list_sources(
						customerId,
						object="card",
						limit=1
					)
					cards = len(stripeCustomer.data)

					if cards > 0 and trialinfo["status"] == "trialover":
						customerPay(0.17, userid, None)
						chargedUser = True

					appointment.customers = json.dumps(customers)

				if customer["userid"] != userid:
					receivers["users"].append("user" + str(customer["userid"]))

			owners = query("select id, info from owner where info like '%\"locationId\": \"" + locationId + "\"%'", True)

			for owner in owners:
				ownerInfo = json.loads(owner["info"])

				if ownerInfo["pushToken"] != "":
					pushids.append(ownerInfo["pushToken"])

				receivers["locations"].append("owner" + str(owner["id"]))
		else:
			info = json.loads(appointment.info)
			receivers = []

			# charge user for first time appointment acceptance
			if info["chargedUser"] == False:
				#info["chargedUser"] = True

				appointment.info = json.dumps(info)
				stripeCustomer = stripe.Customer.list_sources(
					customerId,
					object="card",
					limit=1
				)
				cards = len(stripeCustomer.data)

				if cards > 0 and trialinfo["status"] == "trialover":
					customerPay(0.17, userid, None)

				chargedUser = True

			owners = query("select id, info from owner where info like '%\"locationId\": \"" + locationId + "\"%'", True)

			for owner in owners:
				ownerInfo = json.loads(owner["info"])

				if ownerInfo["pushToken"] != "":
					pushids.append(ownerInfo["pushToken"])

				receivers.append("owner" + str(owner["id"]))

		db.session.commit()

		if len(pushids) > 0:
			if send_msg == True:
				pushmessages = []

				if location.type == "restaurant":
					title = "Reservation confirmed"
					message = "The customer confirmed the reservation"
				else:
					title = "Appointment confirmed"
					message = "The client confirmed the appointment for service: " + (service.name if service != None else userInput["name"])
				
				for pushid in pushids:
					pushmessages.append(pushInfo(pushid, title, message, content))

				resp = push(pushmessages)
			else:
				resp = { "status": "ok" }
		else:
			resp = { "status": "ok" }

		if resp["status"] == "ok":
			return { "msg": "Appointment confirmed", "receivers": receivers, "chargedUser": chargedUser, "time": appointment.time }

		errormsg = "Push notification failed"
	else:
		errormsg = "Appointment doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/cancel_schedule", methods=["POST"])
def cancel_schedule():
	content = request.get_json()

	id = content['scheduleid']
	reason = content['reason']

	appointment = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if appointment != None:
		locationType = appointment.locationType

		if appointment.status == "requested" or appointment.status == "change" or appointment.status == "confirmed":
			appointment.status = "cancel"
			appointment.cancelReason = reason

			db.session.commit()

			receiver = []

			if locationType == "restaurant":
				customers = json.loads(appointment.customers)

				for customer in customers:
					receiver.append("user" + str(customer["userid"]))
			else:
				receiver.append("user" + str(appointment.userId))

			user = User.query.filter_by(id=appointment.userId).first()
			info = json.loads(user.info)

			if send_msg == True:
				if info["pushToken"] != "":
					message = "The "
					message += "restaurant" if locationType == "restaurant" else "salon"
					message += " cancelled your "
					message == "reservation" if locationType == "restaurant" else "appointment"
					message += " with"
					message += " no reason" if reason == "" else " a reason"

					resp = push(pushInfo(
						info["pushToken"],
						("Reservation" if locationType == "restaurant" else "Appointment") + " cancelled",
						message,
						content
					))
				else:
					resp = { "status": "ok" }
			else:
				resp = { "status": "ok" }

			if resp["status"] == "ok":
				return { "msg": "request cancelled", "receiver": receiver }
			else:
				errormsg = "Push notification failed"
		else:
			errormsg = "Action is denied"
	else:
		errormsg = "Appointment doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/close_schedule/<id>")
def close_schedule(id):
	appointment = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if appointment != None:
		locationType = appointment.locationType

		if appointment.status == "cancel" or appointment.status == "rebook":
			if locationType == "restaurant":
				customers = json.loads(appointment.customers)
				receiver = []

				for customer in customers:
					receiver.append("user" + str(customer["userid"]))
			else:
				receiver = ["user" + str(appointment.userId)]

			db.session.delete(appointment)
			db.session.commit()

			return { "msg": "request deleted", "receiver": receiver }

		errormsg = "Action is denied"
	else:
		errormsg = "Appointment doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/cancel_reservation_joining", methods=["POST"])
def cancel_reservation_joining():
	content = request.get_json()

	userid = content['userid']
	scheduleid = content['scheduleid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		diners = json.loads(schedule.customers)

		for k, diner in enumerate(diners):
			if diner['userid'] == userid:
				diners.pop(k)

				schedule.customers = json.dumps(diners)

				db.session.commit()

				return { "msg": "diner removed" }

		errormsg = "Diner doesn't exist"
		status = "nonexist"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/accept_reservation_joining", methods=["POST"])
def accept_reservation_joining():
	content = request.get_json()

	userid = str(content['userid'])
	scheduleid = content['scheduleid']

	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		schedule = Schedule.query.filter_by(id=scheduleid).first()

		if schedule != None:
			locationId = str(schedule.locationId)
			diners = json.loads(schedule.customers)
			confirmed = False
			receiver = ["user" + str(schedule.userId)]
			trialinfo = trialInfo()

			for k, diner in enumerate(diners):
				if diner['userid'] == userid:
					confirmed = True
					diner['status'] = 'confirmed'
					diners[k] = diner

					schedule.customers = json.dumps(diners)

					data = User.query.filter_by(id=userid).first()
					info = json.loads(data.info)

				if diner['status'] == 'confirmed' and diner['userid'] != userid:
					receiver.append("user" + str(diner['userid']))

			db.session.commit()

			if confirmed == True:
				return { "msg": "diner accepted", "receiver": receiver }

			errormsg = "Diner doesn't exist"
			status = "nonexist"
		else:
			errormsg = "Schedule doesn't exist"
			status = "nonexist"
	else:
		errormsg = "User doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_diner", methods=["POST"])
def add_diner():
	content = request.get_json()

	userid = str(content['userid'])
	scheduleid = content['scheduleid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		diners = json.loads(schedule.customers)

		diners.append({ "userid": userid, "status": "waiting" })

		schedule.customers = json.dumps(diners)

		db.session.commit()

		return { "msg": "Diner added" }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/request_payment", methods=["POST"])
def request_payment():
	content = request.get_json()

	scheduleid = content['scheduleid']
	ownerid = content['ownerid']
	serviceprice = content['serviceprice']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	owner = Owner.query.filter_by(id=ownerid).first()

	errormsg = ""
	status = ""

	if schedule != None and owner != None:
		receiver = ["user" + str(schedule.userId)]

		userInput = json.loads(schedule.userInput)
		userInput["price"] = float(serviceprice)

		info = json.loads(schedule.info)
		info["workerId"] = int(owner.id)

		schedule.userInput = json.dumps(userInput)
		schedule.info = json.dumps(info)

		db.session.commit()

		workerInfo = {
			"id": owner.id,
			"username": owner.username,
			"requestprice": float(serviceprice),
			"tip": 0
		}

		return { "msg": "success", "receiver": receiver, "workerInfo": workerInfo }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/done_dining/<id>")
def done_dining(id):
	user_orders = []

	numUnserved = query("select count(*) as num from schedule where ((length(orders) - length(replace(orders, 'making', ''))) / 6 > 0) and id = " + str(id), True)[0]["num"]
	errormsg = ""
	status = ""

	if numUnserved == 0:
		return { "msg": "success" }
	else:
		errormsg = "There's still some unserved orders"
		status = "unserved"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/receive_diners_payments", methods=["POST"])
def receive_diners_payments():
	content = request.get_json()

	scheduleid = content['scheduleid']
	userid = str(content['userid'])
	time = content['time']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""
	info = {}

	if schedule != None:
		location = Location.query.filter_by(id=schedule.locationId).first()

		if location != None:
			locationInfo = json.loads(location.info)
			accountid = locationInfo["accountId"]
			orders = json.loads(schedule.orders)
			charges = orders["charges"]

			if userid in charges:
				user = User.query.filter_by(id=userid).first()

				charge = float(charges[userid]["charge"])
				tip = float(charges[userid]["tip"])
				allowPayment = charges[userid]["allowpayment"]
				paid = charges[userid]["paid"]

				if paid == False:
					if allowPayment == True:
						if charge > 0:
							chargeAmount = charge + tip
							#customerPay(chargeAmount, userid, schedule.locationId)

						charges[userid]["paid"] = True
						charges[userid]["charge"] = None

						orders["charges"] = charges
						schedule.orders = json.dumps(orders)

						# create recents
						groupId = ""

						for k in range(20):
							groupId += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 0))

						for rounds in orders["groups"]:
							for round in rounds:
								if round != "status" and round != "id":
									user_orders = rounds[round]

									for order in user_orders:
										collect = False

										if "\"userid\": \"" + userid + "\"" in json.dumps(order["callfor"]):
											collect = True
										elif round == userid:
											collect = True

										if collect == True:
											product = Product.query.filter_by(id=order['productid']).first()

											userInput = order['userInput']
											quantity = int(order['quantity'])
											options = order['options']
											others = order['others']
											sizes = order['sizes']
											callfor = order['callfor']
											price = 0

											for option in options:
												if "key" in option:
													del option["key"]

											if product != None:
												if len(sizes) > 0:
													for size in sizes:
														if "key" in size:
															del size["key"]

														if size["selected"] == True:
															price = quantity * float(size["price"])
												else:
													price = quantity * float(product.price)
											else:
												price = quantity * float(userInput["price"])

											for other in others:
												if "key" in other:
													del other["key"]

												if other["selected"] == True:
													price += float(other["price"])

											userInput['type'] = 'dining'
											userInput['globalTip'] = charges[round]["tip"]
											transaction = Transaction(groupId, location.id, order['productid'], 0, json.dumps(userInput), quantity, userid, '[]', json.dumps(options), json.dumps(others), json.dumps(sizes), time)

											db.session.add(transaction)
											db.session.commit()
					else:
						errormsg = "Payment unconfirmed"
						status = "paymentunconfirmed"
						info = { "username": user.username }

				if errormsg == "":
					if "\"charge\": \"" not in json.dumps(charges):
						db.session.delete(schedule)
						db.session.commit()

						return { "msg": "payment received" }
					else:
						return { "msg": "" }
			else:
				errormsg = "Diner doesn't exist"
				status = "nonexist"
		else:
			errormsg = "Location doesn't exist"
			status = "nonexist"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status, "info": info }, 400

@app.route("/receive_epayment", methods=["POST"])
def receive_epayment():
	content = request.get_json()

	scheduleid = content['scheduleid']
	ownerid = content['ownerid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		locationid = schedule.locationId
		serviceid = schedule.serviceId
		info = json.loads(schedule.info)

		location = Location.query.filter_by(id=locationid).first()
		service = Service.query.filter_by(id=serviceid).first()

		if location != None and service != None:
			locationInfo = json.loads(location.info)
			clientId = schedule.userId

			client = User.query.filter_by(id=clientId).first()
			clientInfo = json.loads(client.info)
			price = float(service.price)
			tip = float(info["tip"])

			if info["allowpayment"] == True and info["workerId"] == str(ownerid):
				customerid = clientInfo["customerId"]
				accountid = locationInfo["accountId"]

				stripeCustomer = stripe.Customer.list_sources(
					customerid,
					object="card",
					limit=1
				)
				account = stripe.Account.list_external_accounts(
					accountid,
					object="bank_account",
					limit=1
				)

				cards = len(stripeCustomer.data)
				bankaccounts = len(account.data)

				if bankaccounts > 0:
					if cards > 0:
						chargeAmount = price + tip
						customerPay(chargeAmount, clientId, locationid)
					else:
						errormsg = "cardrequired"
						status = "cardrequired"

					if errormsg == "":
						groupId = ""

						for k in range(20):
							groupId += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 0))

						userInput = {"tip": tip, "type": "service"}
						transaction = Transaction(groupId, locationid, 0, schedule.serviceId, json.dumps(userInput), 0, schedule.userId, '[]', '[]', '[]', '[]', schedule.time)

						db.session.add(transaction)
						db.session.delete(schedule)
						db.session.commit()

						user = User.query.filter_by(id=schedule.userId).first()
						userInfo = json.loads(user.info)
						userInput = json.loads(schedule.userInput)

						if userInfo["pushToken"] != "":
							if send_msg == True:
								resp = push(pushInfo(
									userInfo["pushToken"],
									"Payment received by salon",
									location.name + " has received your payment for service: " + (service.name if service != None else userInput["name"]),
									content
								))
							else:
								resp = { "status": "ok" }
						else:
							resp = { "status": "ok" }

						if resp["status"] == "ok":
							receiver = ["user" + str(schedule.userId)]

							return { "msg": "Payment received", "clientName": client.username, "name": service.name, "price": chargeAmount, "receiver": receiver }
						else:
							errormsg = "Push notification failed"
				else:
					errormsg = "Please provide a bank account to receive payment"
					status = "bankaccountrequired"
			else:
				if info["allowpayment"] == False:
					errormsg = "Client hasn't sent payment yet"
					status = "paymentunsent"
				else:
					errormsg = "Only the worker of this client can receive payment"
					status = "wrongworker"
		else:
			errormsg = "Location doesn't exist"
			status = "nonexist"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/receive_inpersonpayment", methods=["POST"])
def receive_inpersonpayment():
	content = request.get_json()

	scheduleid = content['scheduleid']
	ownerid = content['ownerid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		locationid = schedule.locationId
		serviceid = schedule.serviceId
		info = json.loads(schedule.info)

		location = Location.query.filter_by(id=locationid).first()
		service = Service.query.filter_by(id=serviceid).first()

		if location != None and service != None:
			locationInfo = json.loads(location.info)
			clientId = schedule.userId
			workerId = int(info["workerId"])

			client = User.query.filter_by(id=clientId).first()
			clientInfo = json.loads(client.info)
			customerid = clientInfo["customerId"]
			price = float(service.price)

			if workerId > 0:
				if info["workerId"] == str(ownerid):
					groupId = ""

					for k in range(20):
						groupId += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 0))

					transaction = Transaction(groupId, locationid, 0, schedule.serviceId, "{}", 0, schedule.userId, '[]', '[]', '[]', '[]', schedule.time)

					db.session.add(transaction)
					db.session.delete(schedule)
					db.session.commit()

					user = User.query.filter_by(id=schedule.userId).first()
					userInfo = json.loads(user.info)
					userInput = json.loads(schedule.userInput)

					if userInfo["pushToken"] != "":
						if send_msg == True:
							resp = push(pushInfo(
								userInfo["pushToken"],
								"Payment received by salon",
								location.name + " has received your payment for service: " + (service.name if service != None else userInput["name"]),
								content
							))
						else:
							resp = { "status": "ok" }
					else:
						resp = { "status": "ok" }

					if resp["status"] == "ok":
						receiver = ["user" + str(schedule.userId)]

						return { "msg": "Payment received", "clientName": client.username, "name": service.name, "price": service.price, "receiver": receiver }
					else:
						errormsg = "Push notification failed"
				else:
					errormsg = "Only the worker of this client can receive payment"
					status = "wrongworker"
			else:
				errormsg = "The client hasn't allowed payment yet"
				status = "unallowedpayment"
		else:
			errormsg = "Location doesn't exist"
			status = "nonexist"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/cancel_request", methods=["POST"])
def cancel_request():
	content = request.get_json()

	userid = content['userid']
	scheduleid = content['scheduleid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		locationId = str(schedule.locationId)

		owners = query("select id from owner where info like '%\"locationId\": \"" + locationId + "\"%'", True)
		receivers = { "owners": [], "users": [] }

		for owner in owners:
			receivers["owners"].append("owner" + str(owner["id"]))

		if schedule.locationType == "restaurant":
			customers = json.loads(schedule.customers)

			for customer in customers:
				if userid != customer["userid"]:
					receivers["users"].append("user" + str(customer["userid"]))

		db.session.delete(schedule)
		db.session.commit()

		return { "msg": "schedule cancelled", "receivers": receivers, "type": schedule.locationType }
	else:
		errormsg = "Schedule doens't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/can_serve_diners/<id>")
def can_serve_diners(id):
	schedule = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if schedule != None:
		info = json.loads(schedule.info)
		info["dinersseated"] = True

		schedule.info = json.dumps(info)

		db.session.commit()

		receiver = []
		customers = json.loads(schedule.customers)
		for customer in customers:
			if customer["status"] == "confirmed":
				receiver.append("user" + str(customer["userid"]))

		if send_msg == True:
			pushmessages = []
			for info in receiver:
				user = User.query.filter_by(id=info[4:]).first()
				userInfo = json.loads(user.info)

				if userInfo["pushToken"] != "":
					content = { "id": id, "type": "canServeDiners" }
					pushmessages.append(pushInfo(
						userInfo["pushToken"],
						"You are seated",
						"You can start sending your orders now",
						content
					))

			if len(pushmessages) > 0:
				resp = push(pushmessages)
			else:
				resp = { "status": "ok" }
		else:
			resp = { "status": "ok" }

		if resp["status"] == "ok":
			return { "msg": "Diners are seated", "receiver": receiver }

		errormsg = "Push notification failed"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/allow_payment", methods=["POST"])
def allow_payment():
	content = request.get_json()

	scheduleid = content['scheduleid']
	workerid = content['workerid']
	tip = float(content['tip'])

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		info = json.loads(schedule.info)
		info["allowpayment"] = True
		info["workerId"] = str(workerid)
		info["tip"] = tip

		schedule.info = json.dumps(info)

		db.session.commit()

		client = User.query.filter_by(id=schedule.userId).first()
		worker = Owner.query.filter_by(id=workerid).first()
		workerInfo = json.loads(worker.info)

		if workerInfo["pushToken"] != "":
			if send_msg == True:
				resp = push(pushInfo(
					workerInfo["pushToken"],
					"Payment allowed by client: " + client.username,
					"You can now receive your payment",
					content
				))
			else:
				resp = { "status": "ok" }
		else:
			resp = { "status": "ok" }

		if resp["status"] == "ok":
			return { "msg": "" }

		errormsg = "Push notification failed"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/send_dining_payment", methods=["POST"])
def send_dining_payment():
	content = request.get_json()
	errormsg = ""
	status = ""

	userid = str(content['userid'])
	scheduleid = content['scheduleid']

	user = User.query.filter_by(id=userid).first()
	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if user != None and schedule != None:
		userInfo = json.loads(user.info)
		customerId = userInfo["customerId"]

		stripeCustomer = stripe.Customer.list_sources(
			customerId,
			object="card",
			limit=1
		)

		cards = len(stripeCustomer.data)

		if cards > 0:
			if 'getinfo' in content: # 'getinfo' indicates to get payment details
				orders = json.loads(schedule.orders)
				cost = 0.00

				for rounds in orders["groups"]:
					for round in rounds:
						if round != "status" and round != "id" and round == userid:
							user_orders = rounds[round]

							for order in user_orders:
								collect = False

								if "\"userid\": \"" + userid + "\"" in json.dumps(order["callfor"]):
									collect = True
								elif round == userid:
									collect = True

								if collect == True:
									product = Product.query.filter_by(id=order['productid']).first()

									quantity = int(order['quantity'])
									others = order['others']
									sizes = order['sizes']
									callfor = order['callfor']
									userInput = order['userInput']

									if len(sizes) > 0:
										for size in sizes:
											if size["selected"] == True:
												cost += quantity * float(size["price"])
									else:
										cost += quantity * float(product.price if product != None else (userInput["price"] if "price" in userInput else 13.99))

									for other in others:
										if other["selected"] == True:
											cost += float(other["price"])

				return { "msg": "Cost received", "cost": cost }
			else:
				locationId = str(schedule.locationId)
				orders = json.loads(schedule.orders)

				if str(userid) not in orders["charges"]:
					orders["charges"][str(userid)] = {}

				orders["charges"][str(userid)]["allowpayment"] = True
				orders["charges"][str(userid)]["tip"] = float(content['tip'])

				schedule.orders = json.dumps(orders)

				db.session.commit()

				owners = query("select id from owner where info like '%\"locationId\": \"" + locationId + "\"%'", True)
				receiver = []
				for owner in owners:
					receiver.append("owner" + str(owner["id"]))

				return { "msg": "Payment sent", "receiver": receiver }
		else:
			errormsg = "Payment required"
			status = "cardrequired"
	else:
		if user == None:
			errormsg = "User doesn't exist"
		else:
			errormsg = "Schedule doesn't exist"

		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/send_service_payment", methods=["POST"])
def send_service_payment():
	content = request.get_json()

	scheduleid = content['scheduleid']
	userid = content['userid']
	service = content['service']
	workerinfo = content['workerInfo']

	user = User.query.filter_by(id=userid).first()
	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if user != None and schedule != None:
		price = float(workerinfo["requestprice"])
		tip = float(workerinfo["tip"])
		info = json.loads(user.info)

		customerId = info["customerId"]
		stripeCustomer = stripe.Customer.list_sources(
			customerId,
			object="card",
			limit=1
		)
		cards = len(stripeCustomer.data)

		if cards > 0:
			charge = price + tip
			customerPay(charge, userid, schedule.locationId)

			groupId = ""

			for k in range(20):
				groupId += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 0))

			userInput = json.dumps({ "name": service, "price": price, "tip": tip, "type": "service" })
			transaction = Transaction(groupId, schedule.locationId, 0, schedule.serviceId, userInput, 0, schedule.userId, '[]', '[]', '[]', '[]', schedule.time)

			db.session.add(transaction)
			db.session.delete(schedule)
			db.session.commit()

			return { "msg": "success" }
		else:
			errormsg = "cardrequired"
			status = "cardrequired"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_appointments", methods=["POST"])
def get_appointments():
	content = request.get_json()

	ownerid = content['ownerid']
	locationid = content['locationid']

	datas = query("select * from schedule where locationId = " + str(locationid) + " and status = 'confirmed' and (workerId = -1 or workerId = " + str(ownerid) + ")", True)
	appointments = []

	for data in datas:
		user = User.query.filter_by(id=data['userId']).first()
		service = Service.query.filter_by(id=data['serviceId']).first()
			
		info = json.loads(data["info"])

		client = {
			"id": data['userId'],
			"username": user.username
		}

		userInput = json.loads(data['userInput'])
		appointments.append({
			"key": "appointment-" + str(data['id']),
			"id": str(data['id']),
			"username": user.username,
			"client": client,
			"time": int(data['time']),
			"serviceid": service.id if service != None else "",
			"name": service.name if service != None else userInput['name'],
			"image": service.image if service != None else None,
			"gettingPayment": False,
			"allowPayment": info["allowpayment"]
		})

	return { "appointments": appointments, "numappointments": len(appointments) }

@app.route("/search_customers", methods=["POST"])
def search_customers():
	content = request.get_json()

	locationid = content['locationid']
	searchingusername = content['username']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		datas = Schedule.query.filter_by(locationId=locationid).all()
		appointments = []

		for data in datas:
			user = User.query.filter_by(id=data.userId).first()
			username = user.username

			if searchingusername.lower() in username.lower():
				service = Service.query.filter_by(id=data.serviceId).first()

				appointments.append({
					"key": "appointment-" + str(data.id),
					"id": str(data.id),
					"username": user.username,
					"time": int(data.time),
					"name": service.name,
					"image": service.image,
					"gettingPayment": False
				})

		return { "appointments": appointments, "numappointments": len(appointments) }
	else:
		errormsg = "Location doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_cart_orderers/<id>")
def get_cart_orderers(id):
	datas = query("select adder, orderNumber from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'ready') group by adder, orderNumber", True)
	numCartorderers = query("select count(*) as num from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'ready') group by adder, orderNumber", True)
	cartOrderers = []

	for k, data in enumerate(datas):
		adder = User.query.filter_by(id=data['adder']).first()
		orders = query("select * from cart where adder = " + str(data['adder']) + " and locationId = " + str(id) + " and (status = 'checkout' or status = 'ready')", True)
		numOrders = 0

		for order in orders:
			callfor = json.loads(order['callfor'])

			if len(callfor) > 0:
				numOrders += len(callfor)
			else:
				numOrders += 1

		cartOrderers.append({
			"key": "cartorderer-" + str(k),
			"id": len(cartOrderers),
			"adder": adder.id,
			"username": adder.username,
			"profile": adder.profile,
			"numOrders": numOrders,
			"orderNumber": data['orderNumber']
		})

	if len(numCartorderers) > 0:
		numCartorderers = len(numCartorderers)
	else:
		numCartorderers = 0

	return { "cartOrderers": cartOrderers, "numCartorderers": numCartorderers }

@app.route("/see_user_orders", methods=["POST"])
def see_user_orders():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	ordernumber = content['ordernumber']

	datas = query("select * from cart where adder = " + str(userid) + " and locationId = " + str(locationid) + " and orderNumber = '" + ordernumber + "' and (status='checkout' or status='ready')", True)
	orders = []
	totaloverallcost = 0
	ready = True

	for data in datas:
		product = Product.query.filter_by(id=data['productId']).first()
		quantity = int(data['quantity'])
		callfor = json.loads(data['callfor'])
		options = json.loads(data['options'])
		others = json.loads(data['others'])
		sizes = json.loads(data['sizes'])
		userInput = json.loads(data['userInput'])
		row = []
		cost = 0

		for k, option in enumerate(options):
			option['key'] = "option-" + str(k)

		for k, other in enumerate(others):
			other['key'] = "other-" + str(k)

		for k, size in enumerate(sizes):
			size['key'] = "size-" + str(k)

		if len(callfor) == 0:
			if product != None:
				if product.price == "":
					for size in sizes:
						if size['selected'] == True:
							cost += quantity * float(size['price'])
							totaloverallcost += quantity * float(size['price'])
				else:
					cost += quantity * float(product.price if product != None else (userInput["price"] if "price" in userInput else 13.99))
					totaloverallcost += quantity * float(product.price if product != None else (userInput["price"] if "price" in userInput else 13.99))
			else:
				cost += quantity * float(product.price if product != None else (userInput["price"] if "price" in userInput else 13.99))
				totaloverallcost += quantity * float(product.price if product != None else (userInput["price"] if "price" in userInput else 13.99))

			for other in others:
				if other['selected'] == True:
					cost += float(other['price'])
					totaloverallcost += float(other['price'])

		if len(datas) == 1:
			pst = cost * 0.08
			hst = cost * 0.05
			totalcost = stripeFee(cost + pst + hst)
			nofee = cost + pst + hst
			fee = totalcost - nofee
		else:
			pst = 0.00
			hst = 0.00
			totalcost = cost
			nofee = 0.00
			fee = 0.00

		orders.append({
			"key": "cart-item-" + str(data['id']),
			"id": str(data['id']),
			"name": product.name if product != None else userInput['name'],
			"productId": product.id if product != None else "",
			"note": data['note'],
			"image": product.image if product != None else None,
			"options": options,
			"others": others,
			"sizes": sizes,
			"quantity": quantity,
			"price": cost,
			"pst": pst,
			"hst": hst,
			"totalcost": totalcost,
			"nofee": nofee,
			"fee": fee,
			"orderers": len(callfor)
		})

		if data['status'] == "checkout":
			ready = False

	totalcost = {}
	totalcost["price"] = totaloverallcost
	totalcost["pst"] = totaloverallcost * 0.08
	totalcost["hst"] = totaloverallcost * 0.05
	totalcost["cost"] = stripeFee(totaloverallcost + totalcost["pst"] + totalcost["hst"])
	totalcost["nofee"] = totaloverallcost + totalcost["pst"] + totalcost["hst"]
	totalcost["fee"] = totalcost["cost"] - totalcost["nofee"]

	return { "orders": orders, "totalcost": totalcost, "ready": ready }

@app.route("/get_diners_orders/<id>")
def get_diners_orders(id):
	schedule = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if schedule != None:
		orders = json.loads(schedule.orders)
		customers = json.loads(schedule.customers)
		groups = orders["groups"]
		charges = orders["charges"]

		user_charges = {}

		if str(schedule.userId) in charges:
			allowPayment = charges[str(schedule.userId)]["allowpayment"] if str(schedule.userId) in charges else False
			tip = charges[str(schedule.userId)]["tip"] if str(schedule.userId) in charges else 0
			paid = charges[str(schedule.userId)]["paid"] if str(schedule.userId) in charges else False

			user_charges[str(schedule.userId)] = {
				"charge": 0.00,
				"allowpayment": allowPayment,
				"paid": paid,
				"tip": tip
			}

		for customer in customers:
			if customer["status"] == "confirmed":
				allowPayment = charges[customer["userid"]]["allowpayment"] if customer["userid"] in charges else False
				tip = charges[customer["userid"]]["tip"] if customer["userid"] in charges else 0
				paid = charges[customer["userid"]]["paid"] if customer["userid"] in charges else False

				user_charges[customer["userid"]] = {
					"charge": 0.00,
					"allowpayment": allowPayment,
					"paid": paid,
					"tip": tip
				}

		diners = []
		total = 0.00

		for rounds in groups:
			for round in rounds:
				if round != "status" and round != "id":
					for orderer in rounds[round]:
						product = Product.query.filter_by(id=orderer['productid']).first()

						userInput = orderer['userInput']
						quantity = int(orderer['quantity'])
						sizes = orderer['sizes']
						others = orderer['others']
						callfor = orderer['callfor']
						price = 0

						if len(sizes) > 0:
							for size in sizes:
								if size["selected"] == True:
									price = quantity * float(size["price"])
						else:
							price = quantity * float(product.price if product != None else (userInput["price"] if "price" in userInput else 13.99))

						for other in others:
							if other["selected"] == True:
								price += float(other["price"])

						if len(callfor) > 0:
							for info in callfor:
								user_charges[str(info["userid"])]["charge"] = float(user_charges[str(info["userid"])]["charge"])
								user_charges[str(info["userid"])]["charge"] += price
								user_charges[str(info["userid"])]["charge"] = str(user_charges[str(info["userid"])]["charge"])
						else:
							user_charges[round]["charge"] = float(user_charges[round]["charge"])
							user_charges[round]["charge"] += price
							user_charges[round]["charge"] = str(user_charges[round]["charge"])

			orders["charges"] = user_charges

			schedule.orders = json.dumps(orders)

			db.session.commit()

		for index, charge in enumerate(user_charges):
			user = User.query.filter_by(id=charge).first()
			cost = float(user_charges[charge]["charge"])

			user_charges[charge]["key"] = "user-" + str(index)
			user_charges[charge]["userId"] = user.id
			user_charges[charge]["username"] = user.username
			user_charges[charge]["profile"] = user.profile
			user_charges[charge]["payed"] = False
			user_charges[charge]["paying"] = False

			if cost > 0:
				user_charges[charge]["charge"] = stripeFee(cost + calcTax(cost))
				total += float(user_charges[charge]["charge"]) + float(user_charges[charge]["tip"])

				diners.append(user_charges[charge])

		return { "diners": diners, "total": total }
	else:
		errormsg = "Reservation doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_reservations/<id>")
def get_reservations(id):
	datas = Schedule.query.filter_by(locationId=id, status='confirmed').all()
	reservations = []

	for data in datas:
		user = User.query.filter_by(id=data.userId).first()
		location = Location.query.filter_by(id=data.locationId).first()

		# get number of making orders
		orders = data.orders
		info = json.loads(data.info)
		newOrders = orders.replace("\"status\": \"making\"", "")
		numMakings = (len(orders) - len(newOrders)) / len("\"status\": \"making\"")

		reservations.append({
			"key": "reservation-" + str(data.id),
			"id": str(data.id),
			"userId": user.id,
			"username": user.username,
			"time": int(data.time),
			"name": location.name,
			"image": location.logo,
			"diners": len(json.loads(data.customers)),
			"table": data.table,
			"numMakings": numMakings,
			"gettingPayment": False,
			"seated": info["dinersseated"]
		})

	return { "reservations": reservations, "numreservations": len(reservations) }

@app.route("/get_schedule_info/<id>")
def get_schedule_info(id):
	schedule = Schedule.query.filter_by(id=id, status="confirmed").first()
	errormsg = ""
	status = ""

	if schedule != None:
		info = json.loads(schedule.info)
		location = Location.query.filter_by(id=schedule.locationId).first()

		info = {
			"name": location.name,
			"locationId": schedule.locationId,
			"time": schedule.time,
			"table": schedule.table,
			"numdiners": len(json.loads(schedule.customers)),
			"seated": info["dinersseated"] if "dinersseated" in info else None
		}

		return { "scheduleInfo": info }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_item_to_order", methods=["POST"])
def add_item_to_order():
	def getRanStr():
		while True:
			strid = ""
			numlength = randint(5, 20)

			for k in range(numlength):
				strid += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 9))

			numsame = query("select count(*) as num from schedule where orders like '%\"" + strid + "\"%'", True)[0]["num"]

			if numsame == 0:
				return strid

	content = request.get_json()

	userid = str(content['userid'])
	scheduleid = content['scheduleid']
	productid = content['productid']
	name = content['name']
	quantity = content['quantity']
	callfor = content['callfor']
	options = content['options']
	others = content['others']
	sizes = content['sizes']
	note = content['note']

	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		product = Product.query.filter_by(id=productid).first()

		if product != None or name != '':
			if product != None:
				if product.price == '':
					if "true" not in json.dumps(sizes):
						errormsg = "Please choose a size"

			if errormsg == "":
				schedule = Schedule.query.filter_by(id=scheduleid).first()

				if schedule != None:
					customers = json.loads(schedule.customers)
					orders = json.loads(schedule.orders)

					groups = orders['groups']

					if len(groups) > 0:
						first_group = groups[0]

						if first_group['status'] == "served" or first_group['status'] == "making":
							groups.insert(0, { "id": getRanStr(), "status": "ordering" })

							first_group = groups[0]
					else:
						groups.insert(0, { "id": getRanStr(), "status": "ordering" })

						first_group = groups[0]

					receiver = []
					for info in callfor:
						receiver.append("user" + str(info["userid"]))

					if userid in first_group:
						first_group[userid].append({ "id": getRanStr(), "productid": productid, "userInput": {"name": name}, "options": options, "others": others, "sizes": sizes, "quantity": quantity, "note": note, "callfor": callfor })
					else:
						first_group[userid] = [{ "id": getRanStr(), "productid": productid, "userInput": {"name": name}, "options": options, "others": others, "sizes": sizes, "quantity": quantity, "note": note, "callfor": callfor }]

					groups[0] = first_group
					orders['groups'] = groups
					schedule.orders = json.dumps(orders)

					db.session.commit()

					if send_msg == True:
						pushids = []
						for info in callfor:
							userInfo = User.query.filter_by(id=info["userid"]).first()
							info = json.loads(userInfo.info)

						if info["pushToken"] != "":
							pushids.append(info["pushToken"])

						if len(pushids) > 0:
							pushmessages = []
							for pushid in pushids:
								pushmessages.append(pushInfo(
									pushid,
									"An order for you",
									user.username + " made an order call for you\nPlease reject or accept it",
									content
								))

							resp = push(pushmessages)
						else:
							resp = { "status": "ok" }
					else:
						resp = { "status": "ok" }

					if resp["status"] == "ok":
						return { "orders": orders, "msg": "item added to list", "receiver": receiver }
					
					errormsg = "Push notification failed"
				else:
					errormsg = "Schedule doesn't exist"
					status = "nonexist"
		else:
			errormsg = "Product doesn't exist"
			status = "nonexist"
	else:
		errormsg = "User doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/see_dining_orders/<id>")
def see_dining_orders(id):
	schedule = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if schedule != None:
		orderer = schedule.userId
		orders = json.loads(schedule.orders)
		info = json.loads(schedule.info)

		groups = orders['groups']
		donedining = info['donedining']
		dinersseated = info['dinersseated']
		each_rounds = []
		each_orderers = []
		each_orders = []

		each_order_num = 0
		each_orderer_num = 0
		each_round_num = 0
		each_callfor_num = 0

		for rounds in groups:
			for orderer in rounds:
				if orderer != "status" and orderer != "id":
					ordererInfo = User.query.filter_by(id=orderer).first()
					orders = rounds[orderer]
					ordererid = orderer

					for order in orders:
						product = Product.query.filter_by(id=order['productid']).first()
						callfor = order['callfor']

						orderers = []
						row = []
						numorderers = 0

						for k, info in enumerate(callfor):
							info = callfor[k]

							orderer = User.query.filter_by(id=info["userid"]).first()

							row.append({
								"key": "orderer-" + str(each_callfor_num),
								"id": orderer.id,
								"username": orderer.username,
								"profile": orderer.profile,
								"status": info["status"]
							})
							each_callfor_num += 1
							numorderers += 1

							if len(row) == 4 or (len(callfor) - 1 == k and len(row) > 0):
								if len(callfor) - 1 == k and len(row) > 0:
									leftover = 4 - len(row)

									for k in range(leftover):
										row.append({ "key": "orderer-" + str(each_callfor_num) })
										each_callfor_num += 1

								orderers.append({ "key": "orderer-row-" + str(len(orderers)), "row": row })
								row = []

						options = order['options']
						others = order['others']
						sizes = order['sizes']
						quantity = int(order['quantity'])
						userInput = order['userInput']
						cost = 0

						for k, option in enumerate(options):
							option['key'] = "option-" + str(k)

						for k, other in enumerate(others):
							other['key'] = "other-" + str(k)

						for k, size in enumerate(sizes):
							size['key'] = "size-" + str(k)

						if product != None:
							if product.price == "":
								for size in sizes:
									if size['selected'] == True:
										cost += quantity * float(size['price'])
							else:
								cost += quantity * float(product.price)
						else:
							cost += quantity * (float(userInput["price"]) if "price" in userInput else 0)

						for other in others:
							if other['selected'] == True:
								cost += float(other['price'])

						orderer = User.query.filter_by(id=ordererid).first()
						userInput = order["userInput"]
						each_orders.append({
							"id": order['id'],
							"image": product.image if product != None else None,
							"key": "meal-" + order['id'],
							"name": product.name if product != None else userInput["name"],
							"note": order['note'],
							"options": options,
							"others": others,
							"sizes": sizes,
							"quantity": quantity,
							"cost": cost,
							"orderers": orderers,
							"orderer": { "id": ordererid, "username": orderer.username },
							"numorderers": numorderers,
							"priceUnset": False if product != None or "price" in userInput else True
						})
						each_callfor_num = 0
						each_order_num += 1

					if len(each_orders) > 0:
						each_orderers.append({
							"key": "orders-" + str(each_orderer_num),
							"orders": each_orders
						})
						each_order_num = 0
						each_orderer_num += 1
						each_orders = []

			if len(each_orderers) > 0:
				each_rounds.append({
					"key": "round-" + str(each_round_num),
					"round": each_orderers,
					"id": rounds["id"],
					"status": rounds["status"]
				})
				each_round_num += 1
				each_orderers = []

		return { "rounds": each_rounds, "dinersseated": dinersseated }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/edit_diners/<id>")
def edit_diners(id):
	schedule = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if schedule != None:
		customers = json.loads(schedule.customers)
		diners = []
		row = []
		key = 0
		numdiners = 0

		for k, customer in enumerate(customers):
			diner = User.query.filter_by(id=customer['userid']).first()

			row.append({
				"key": "diner-" + str(key),
				"id": diner.id,
				"profile": diner.profile,
				"username": diner.username,
				"status": customer['status']
			})
			key += 1
			numdiners += 1

			if len(row) == 4 or (len(customers) - 1 == k and len(row) > 0):
				if len(customers) - 1 == k and len(row) > 0:
					leftover = 4 - len(row)

					for k in range(leftover):
						row.append({ "key": "diner-" + str(key) })
						key += 1

				diners.append({ "key": "diner-row-" + str(len(diners)), "row": row })
				row = []

		return { "diners": diners, "numdiners": numdiners }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_dining_orders/<id>")
def get_dining_orders(id):
	schedule = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if schedule != None:
		data = query("select * from schedule where id = " + str(id) + " and orders like '%\"making\"%'", True)
		each_rounds = []

		if len(data) == 1:
			orders = json.loads(data[0]['orders'])

			groups = orders['groups']

			each_orderers = []
			each_orders = []

			each_order_num = 0
			each_orderer_num = 0
			each_round_num = 0
			each_callfor_num = 0

			for rounds in groups:
				for orderer in rounds:
					if (orderer != "status" and orderer != "id") and rounds["status"] == "making":
						ordererInfo = User.query.filter_by(id=orderer).first()
						orders = rounds[orderer]

						for order in orders:
							product = Product.query.filter_by(id=order['productid']).first()
							options = order['options']
							others = order['others']
							sizes = order['sizes']
							quantity = int(order['quantity'])

							for k, option in enumerate(options):
								option["key"] = "option-" + str(k)

							for k, other in enumerate(others):
								other["key"] = "other-" + str(k)

							for k, size in enumerate(sizes):
								size["key"] = "size-" + str(k)

							userInput = order["userInput"]
							each_orders.append({
								"id": order['id'],
								"image": product.image if product != None else "",
								"key": "meal-" + order['id'],
								"name": product.name if product != None else userInput["name"],
								"note": order['note'],
								"options": options, "others": others, "sizes": sizes,
								"quantity": quantity,
								"callfor": len(order['callfor']),
								"priceUnset": False if product != None or "price" in userInput else True
							})
							each_callfor_num = 0
							each_order_num += 1

						each_orderers.append({
							"key": "orders-" + str(each_orderer_num),
							"orders": each_orders
						})
						each_order_num = 0
						each_orderer_num += 1
						each_orders = []

				if len(each_orderers) > 0:
					each_rounds.append({
						"id": rounds["id"],
						"key": "round-" + str(each_round_num),
						"round": each_orderers
					})
					each_round_num += 1
					each_orderers = []

		return { "rounds": each_rounds }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/serve_round", methods=["POST"])
def serve_round():
	content = request.get_json()

	ownerid = content['ownerid']
	scheduleid = content['scheduleid']
	roundid = content['roundid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		customers = json.loads(schedule.customers)
		orders = json.loads(schedule.orders)

		receiver = ["user" + str(schedule.userId)]
		for customer in customers:
			if customer["status"] == "confirmed":
				receiver.append("user" + str(customer["userid"]))

		owners = query("select id from owner where info like '%\"locationId\": \"" + str(schedule.locationId) + "\"%'", True)
		for owner in owners:
			if str(owner["id"]) != str(ownerid):
				receiver.append("owner" + str(owner["id"]))

		groups = orders['groups']
		invalid = False

		for rounds in groups:
			if rounds['id'] == roundid:
				for orderer in rounds:
					if orderer != "status" and orderer != "id":
						roundOrders = rounds[orderer]

						for order in roundOrders:
							price = 0.00

							if order['productid'] > -1:
								product = Product.query.filter_by(id=order['productid']).first()
								options = json.loads(product.others)
								others = json.loads(product.others)
								sizes = json.loads(product.sizes)

								if product.price == "":
									if product.price == "":
										for size in sizes:
											if size['selected'] == True:
												cost += quantity * float(size['price'])
									else:
										cost += quantity * float(product.price)

									for other in others:
										if other['selected'] == True:
											cost += float(other['price'])
								else:
									price = float(product.price)
							else:
								userInput = order['userInput']
								price = float(userInput['price']) if 'price' in userInput else 0

							if price == 0.00:
								invalid = True

				if invalid == False:
					rounds['status'] = 'served'

		if invalid == False:
			orders['groups'] = groups

			schedule.orders = json.dumps(orders)

			db.session.commit()

			return { "msg": "round served", "receiver": receiver }
		else:
			errormsg = "Some price not set"
			status = "unsetprices"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/set_order_price", methods=["POST"])
def set_order_price():
	content = request.get_json()
	errormsg = ""
	status = ""

	orderid = content['orderid']
	name = content['name']
	price = content['price']

	reservation = Schedule.query.filter(Schedule.orders.like("%\"id\": \"" + str(orderid) + "\"%")).first()

	if reservation != None:
		orders = json.loads(reservation.orders)
		groups = orders['groups']
		receiver = []

		for rounds in groups:
			for k in rounds:
				if k != "status" and k != "id":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							userInput = orderer['userInput']

							userInput['price'] = float(price)
							receiver = ["user" + str(k)]

		reservation.orders = json.dumps(orders)

		db.session.commit()

		return { "msg": "success", "receiver": receiver }
	else:
		errormsg = "Reservation doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/send_orders/<id>")
def send_orders(id):
	schedule = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if schedule != None:
		locationId = str(schedule.locationId)
		orders = json.loads(schedule.orders)
		customers = json.loads(schedule.customers)
		receiverLocations = []
		receiverDiners = ["user" + str(schedule.userId)]
		orderid = ""
		ordererid = ""

		owners = query("select id from owner where info like '%\"locationId\": \"" + locationId + "\"%'", True)
		for owner in owners:
			receiverLocations.append("owner" + str(owner["id"]))

		for customer in customers:
			if customer["status"] == "confirmed":
				receiverDiners.append("user" + str(customer["userid"]))

		groups = orders['groups']

		first_group = groups[0]
		confirmed = True

		if first_group['status'] == "ordering":
			for k in first_group:
				if k != "status" and k != "id":
					for orderer in first_group[k]:
						for info in orderer["callfor"]:
							if info["status"] == "confirmawaits":
								confirmed = False

								errormsg = "unconfirm orders"
								status = "unconfirmedorders"

			if confirmed == True:
				first_group['status'] = "making"

				groups[0] = first_group

				orders['groups'] = groups

				schedule.orders = json.dumps(orders)

				db.session.commit()

				return { "msg": "order sent", "receiverLocations": receiverLocations, "receiverDiners": receiverDiners }
		else:
			return { "msg": "order sent" }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/edit_order", methods=["POST"])
def edit_order():
	content = request.get_json()

	scheduleid = content['scheduleid']
	orderid = content['orderid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		orders = json.loads(schedule.orders)
		groups = orders['groups']

		for rounds in groups:
			for k in rounds:
				if k != "status" and k != "id":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							product = Product.query.filter_by(id=orderer['productid']).first()

							options = orderer['options']
							others = orderer['others']
							sizes = orderer['sizes']
							quantity = int(orderer['quantity'])
							userInput = orderer['userInput']
							cost = 0

							for k, option in enumerate(options):
								option['key'] = "option-" + str(k)

							for k, other in enumerate(others):
								other['key'] = "other-" + str(k)

							for k, size in enumerate(sizes):
								size['key'] = "size-" + str(k)

							if product != None:
								if product.price == "":
									for size in sizes:
										if size['selected'] == True:
											cost += quantity * float(size['price'])
								else:
									cost += quantity * float(product.price)
							else:
								cost += quantity * (float(userInput["price"]) if "price" in userInput else 0)

							for other in others:
								if other['selected'] == True:
									cost += float(other['price'])

							userInput = orderer['userInput']
							info = {
								"name": product.name if product != None else userInput["name"],
								"info": product.info if product != None else orderer["note"],
								"image": product.image if product != None else "",
								"quantity": quantity,
								"options": options, "others": others, "sizes": sizes,
								"note": orderer['note'],
								"price": float(product.price) if product != None else (userInput["price"] if "price" in userInput else 0),
								"cost": cost
							}

							return { "orderInfo": info, "msg": "order info fetched" }

		errormsg = "Order doesn't exist"
		status = "nonexist"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_order", methods=["POST"])
def update_order():
	content = request.get_json()

	scheduleid = content['scheduleid']
	orderid = content['orderid']
	quantity = content['quantity']
	options = content['options']
	others = content['others']
	sizes = content['sizes']
	note = content['note']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		orders = json.loads(schedule.orders)

		groups = orders['groups']

		for rounds in groups:
			for k in rounds:
				if k != "status" and k != "id":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							orderer['options'] = options
							orderer['others'] = others
							orderer['sizes'] = sizes
							orderer['quantity'] = quantity
							orderer['note'] = note

		orders['groups'] = groups
		schedule.orders = json.dumps(orders)

		db.session.commit()

		return { "msg": "order updated" }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/delete_order", methods=["POST"])
def delete_order():
	content = request.get_json()

	scheduleid = content['scheduleid']
	orderid = content['orderid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		orders = json.loads(schedule.orders)

		groups = orders['groups']
		callfor = []

		for rounds in groups:
			for k in rounds:
				if k != "status" and k != "id":
					for m, data in enumerate(rounds[k]):
						if data['id'] == orderid:
							callfor = data['callfor']
							del rounds[k][m]

		orders['groups'] = groups
		schedule.orders = json.dumps(orders)

		db.session.commit()

		receiver = []
		for info in callfor:
			receiver.append("user" + info["userid"])

		return { "msg": "order deleted", "receiver": receiver }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_diners", methods=["POST"])
def add_diners():
	content = request.get_json()

	scheduleid = content['scheduleid']
	newdiners = content['diners']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	location = Location.query.filter_by(id=schedule.locationId).first()
	errormsg = ""
	status = ""

	if schedule != None:
		booker = str(schedule.userId)

		schedule.customers = json.dumps(newdiners)

		db.session.commit()

		receiver = []
		pushids = []
		for diner in newdiners:
			receiver.append("user" + str(diner["userid"]))

			if diner["status"] == "waiting":
				user = User.query.filter_by(id=diner["userid"]).first()
				info = json.loads(user.info)

				if info["pushToken"] != "":
					pushids.append(info["pushToken"])

		if send_msg == True:
			if len(pushids) > 0:
				pushmessages = []
				for pushid in pushids:
					pushmessages.append(pushInfo(
						pushid,
						"Join a reservation",
						"You have been added to a reservation at " + location.name,
						content
					))

				resp = push(pushmessages)
			else:
				resp = { "status": "ok" }
		else:
			resp = { "status": "ok" }

		if resp["status"] == "ok":
			return { "msg": "New diners added", "receiver": receiver }
		
		errormsg = "Push notification failed"
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/edit_order_callfor", methods=["POST"])
def edit_order_callfor():
	content = request.get_json()

	scheduleid = content['scheduleid']
	orderid = content['orderid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		orders = json.loads(schedule.orders)
		groups = orders['groups']

		for rounds in groups:
			for k in rounds:
				if k != "status" and k != "id":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							callfor = orderer['callfor']
							product = Product.query.filter_by(id=orderer['productid']).first()
							searcheddiners = []
							row = []
							key = 0
							numsearcheddiners = 0

							for k, info in enumerate(callfor):
								user = User.query.filter_by(id=info["userid"]).first()

								row.append({
									"key": "selected-friend-" + str(key),
									"id": user.id,
									"profile": user.profile,
									"username": user.username,
									"status": info["status"]
								})
								key += 1
								numsearcheddiners += 1

								if len(row) == 4 or (len(callfor) - 1 == k and len(row) > 0):
									if len(callfor) - 1 == k and len(row) > 0:
										leftover = 4 - len(row)

										for k in range(leftover):
											row.append({ "key": "selected-friend-" + str(key) })
											key += 1

									searcheddiners.append({ "key": "selected-friend-row-" + str(len(searcheddiners)), "row": row })
									row = []

							options = orderer['options']
							others = orderer['others']
							sizes = orderer['sizes']
							quantity = int(orderer['quantity'])
							userInput = orderer['userInput']
							cost = 0

							for k, option in enumerate(options):
								option['key'] = "option-" + str(k)

							for k, other in enumerate(others):
								other['key'] = "other-" + str(k)

							for k, size in enumerate(sizes):
								size['key'] = "size-" + str(k)

							if product != None:
								if product.price == "":
									for size in sizes:
										if size['selected'] == True:
											cost += quantity * float(size['price'])
								else:
									cost += quantity * float(product.price)
							else:
								cost += quantity * (float(userInput["price"]) if "price" in userInput else 0)

							for other in others:
								if other['selected'] == True:
									cost += float(other['price'])

							userInput = orderer['userInput']
							orderingItem = {
								"name": product.name if product != None else userInput["name"],
								"image": product.image if product != None else "",
								"options": options, "others": others, "sizes": sizes,
								"quantity": int(orderer['quantity']),
								"cost": cost
							}

							return { "searchedDiners": searcheddiners, "numSearchedDiners": numsearcheddiners, "orderingItem": orderingItem }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/diner_is_removable", methods=["POST"])
def diner_is_removable():
	content = request.get_json()

	scheduleid = content['scheduleid']
	userid = str(content['userid'])

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		orders = schedule.orders

		if "\"" + userid + "\"" in orders:
			user = User.query.filter_by(id=userid).first()

			return { "removable": False, "username": user.username }

		return { "removable": True }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/diner_is_selectable", methods=["POST"])
def diner_is_selectable():
	content = request.get_json()

	scheduleid = content['scheduleid']
	userid = str(content['userid'])

	num = query("select count(*) as num from schedule where id = " + str(scheduleid) + " and customers like '%\"" + userid + "\"%'", True)[0]["num"]
	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""
	info = {}

	if user != None:
		schedule = Schedule.query.filter_by(id=scheduleid).first()
		info = json.loads(user.info)

		paymentStatus = info["paymentStatus"]

		# whether the diner is confirmed
		sql = "select count(*) as num from schedule where id = " + str(scheduleid) + " and ("
		sql += "customers like '%\"userid\": \"" + userid + "\", \"status\": \"confirmed\"%'"
		sql += " or "
		sql += "customers like '%\"status\": \"confirmed\", \"userid\": \"" + userid + "\"%'"
		sql += ")"
		confirmed = query(sql, True)[0]["num"] == 1

		if (paymentStatus == "filled" and confirmed == True) or str(schedule.userId) == str(userid):
			return { "selectable": True, "username": user.username }

		errormsg = "paymentrequired" if paymentStatus == "required" else "unconfirmeddiner"

		info = { "selectable": False, "username": user.username }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status, "info": info }, 400

@app.route("/cancel_dining_order", methods=["POST"])
def cancel_dining_order():
	content = request.get_json()

	orderid = content['orderid']
	ordererid = content['ordererid']

	data = query("select customers, orders from schedule where orders like '%\"" + str(orderid) + "\"%'", True)
	errormsg = ""
	status = ""

	if len(data) == 1:
		data = data[0]
		customers = json.loads(data["customers"])
		orders = json.loads(data["orders"])
		receiver = []
		numCallfor = 0

		for customer in customers:
			receiver.append("user" + str(customer["userid"]))

		for rounds in orders["groups"]:
			for k in rounds:
				if k != "status" and k != "id":
					for index, orderer in enumerate(rounds[k]):
						if orderer['id'] == orderid:
							for index, info in enumerate(orderer['callfor']):
								if info["userid"] == str(ordererid):
									if len(orderer['callfor']) == 1:
										del rounds[k][index]
									else:
										del orderer["callfor"][index]

									numCallfor = len(orderer['callfor']) - 1

		query("update schedule set orders = '" + json.dumps(orders) + "' where orders like '%\"" + str(ordererid) + "\"%'", False)

		return { "msg": "user order cancelled", "receiver": receiver, "numCallfor": numCallfor }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/confirm_dining_order", methods=["POST"])
def confirm_dining_order():
	content = request.get_json()

	orderid = content['orderid']
	ordererid = content['ordererid']

	data = query("select orders from schedule where orders like '%\"" + str(orderid) + "\"%'", True)
	errormsg = ""
	status = ""

	if len(data) == 1:
		data = data[0]
		orders = json.loads(data["orders"])
		receiver = []

		for rounds in orders["groups"]:
			for k in rounds:
				if k != "status" and k != "id":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							for info in orderer['callfor']:
								if info["userid"] == str(ordererid):
									info["status"] = "confirmed"
									receiver.append("user" + str(k))

		query("update schedule set orders = '" + json.dumps(orders) + "' where orders like '%\"" + str(ordererid) + "\"%'", False)

		return { "msg": "user order confirmed", "receiver": receiver }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_order_callfor", methods=["POST"])
def update_order_callfor():
	content = request.get_json()

	scheduleid = content['scheduleid']
	orderid = content['orderid']
	callfor = content['callfor']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		orders = json.loads(schedule.orders)
		groups = orders['groups']

		for rounds in groups:
			for k in rounds:
				if k != "status" and k != "id":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							orderer['callfor'] = callfor

		orders['groups'] = groups

		schedule.orders = json.dumps(orders)

		db.session.commit()

		return { "msg": "call for updated" }
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400
