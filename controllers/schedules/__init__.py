from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql.cursors, json, os
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
cors = CORS(app)

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
	profile = db.Column(db.String(70))
	hours = db.Column(db.Text)
	info = db.Column(db.String(100))

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
	logo = db.Column(db.String(70))
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
	image = db.Column(db.String(70))

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
	image = db.Column(db.String(70))
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.image = image
		self.price = price

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
	time = db.Column(db.String(100))
	status = db.Column(db.String(10))
	cancelReason = db.Column(db.String(200))
	locationType = db.Column(db.String(15))
	customers = db.Column(db.Text)
	note = db.Column(db.String(225))
	orders = db.Column(db.Text)
	table = db.Column(db.String(20))
	info = db.Column(db.String(100))

	def __init__(self, userId, workerId, locationId, menuId, serviceId, userInput, time, status, cancelReason, locationType, customers, note, orders, table, info):
		self.userId = userId
		self.workerId = workerId
		self.locationId = locationId
		self.menuId = menuId
		self.serviceId = serviceId
		self.userInput = userInput
		self.time = time
		self.status = status
		self.cancelReason = cancelReason
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
	image = db.Column(db.String(70))
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
	waitTime = db.Column(db.String(50))

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
				"time": json.loads(data['time']),
				"name": service.name if service != None else userInput['name'] if 'name' in userInput else "",
				"image": json.loads(service.image) if service != None else None,
				"note": data['note'],
				"diners": len(json.loads(data['customers'])) if data['locationType'] == 'restaurant' else False,
				"tablenum": data['table'],
				"status": data['status']
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
		userId = schedule.userId

		client = User.query.filter_by(id=userId).first()

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
			"client": {
				"id": userId,
				"name": client.username
			},
			"locationId": int(locationId), 
			"serviceId": int(serviceId), 
			"time": json.loads(schedule.time), 
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

@app.route("/make_appointment", methods=["POST"])
def make_appointment():
	content = request.get_json()
	errormsg = ""
	status = ""

	userid = content['userid']
	workerid = content['workerid']
	locationid = content['locationid']
	serviceid = content['serviceid']
	serviceinfo = content['serviceinfo']
	time = content['time']
	note = content['note']

	user = User.query.filter_by(id=userid).first()

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
			info = json.loads(location.info)
			type = info["type"]

			sql = "select id, info from owner where "

			if type == "computer":
				sql += "info like '%\"locationId\": \"" + str(location.id) + "\"%' and info like '%\"owner\": true\"%'"
			else:
				sql += "id = " + str(workerid)

			owners = query(sql, True)
			locationInfo = json.loads(location.info)
			receiver = []
			pushids = []

			for owner in owners:
				info = json.loads(owner["info"])

				receiver.append("owner" + str(owner["id"]))

				if info["pushToken"] != "":
					pushids.append(info["pushToken"])

			if schedule != None: # existing schedule
				schedule.time = time
				schedule.status = 'confirmed'
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
						try:
							push(pushmessages)
						except:
							print("")

				worker = Owner.query.filter_by(id=workerid).first()
				speak = { "name": servicename, "time": json.loads(time), "worker": worker.username }

				return { "msg": "appointment remade", "receiver": receiver, "time": time, "speak": speak }
			else: # new schedule
				info = json.dumps({})
				userInput = json.dumps({ "name": serviceinfo, "type": "service" })
				appointment = Schedule(userid, workerid, locationid, menuid, serviceid, userInput, time, 'confirmed', '', location.type, 1, note, '[]', '', info)

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

						try:
							push(pushmessages)
						except:
							print("")

				worker = Owner.query.filter_by(id=workerid).first()
				speak = { "name": servicename, "time": json.loads(time), "worker": worker.username }

				return { "msg": "appointment added", "receiver": receiver, "speak": speak }
		else:
			errormsg = "Location doesn't exist"
			status = "nonexist"
	else:
		errormsg = "User doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/salon_change_appointment", methods=["POST"])
def salon_change_appointment():
	content = request.get_json()
	errormsg = ""
	status = ""

	clientid = content['clientid']
	workerid = content['workerid']
	locationid = content['locationid']
	serviceid = content['serviceid']
	serviceinfo = content['serviceinfo']
	time = content['time']
	note = content['note']

	client = User.query.filter_by(id=clientid).first()

	if client != None:
		location = Location.query.filter_by(id=locationid).first()

		if serviceid != -1:
			service = Service.query.filter_by(id=serviceid).first()
			schedule = Schedule.query.filter_by(userId=clientid, serviceId=serviceid).first()
			servicename = service.name
			menuid = service.menuId
		else:
			schedule = Schedule.query.filter(Schedule.userId==clientid, Schedule.userInput.like("%\"name\": \"" + str(serviceinfo) + "\"%")).first()
			servicename = serviceinfo
			menuid = -1

		if location != None:
			pushids = []

			info = json.loads(client.info)
			pushToken = info["pushToken"]
			receiver = "user" + str(clientid)

			schedule.time = time
			schedule.status = 'confirmed'
			schedule.note = note
			schedule.workerId = workerid

			db.session.commit()

			if pushToken != "":
				pushmessage = pushInfo(
					pushToken, 
					"Appointment remade",
					"A salon requested a different appointment for service: " + servicename,
					content
				)
			
				if send_msg == True:
					try:
						push(pushmessage)
					except:
						print("")

			return { "msg": "appointment remade", "receiver": receiver, "time": time }
		else:
			errormsg = "Location doesn't exist"
			status = "nonexist"
	else:
		errormsg = "User doesn't exist"
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
					message == "appointment"
					message += " with"
					message += " no reason" if reason == "" else " a reason"

					try:
						push(pushInfo(
							info["pushToken"],
							"Appointment cancelled",
							message,
							content
						))
					except:
						print("")
						
			return { "msg": "request cancelled", "receiver": receiver }
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

@app.route("/done_service/<id>")
def done_service(id):
	schedule = Schedule.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if schedule != None:
		booker = schedule.userId

		db.session.delete(schedule)
		db.session.commit()

		return { "msg": "Schedule deleted", "receiver": "user" + str(booker) }
	else:
		errormsg = "Schedule doesn't exist"

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

		serviceName = ""
		if schedule.serviceId == -1:
			userInput = json.loads(schedule.userInput)
			serviceName = userInput["name"]
		else:
			service = Service.query.filter_by(id=schedule.serviceId).first()
			serviceName = service.name

		worker = Owner.query.filter_by(id=schedule.workerId).first()
		speak = { "name": serviceName, "time": json.loads(schedule.time), "worker": worker.username }

		return { "msg": "schedule cancelled", "receivers": receivers, "type": schedule.locationType, "speak": speak }
	else:
		errormsg = "Schedule doens't exist"

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

		charge = price + tip
		paymentInfo = customerPay(charge, userid, schedule.locationId)

		status = paymentInfo["error"]

		if status == "":
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
			errormsg = paymentInfo["error"]
	else:
		errormsg = "Schedule doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_appointments", methods=["POST"])
def get_appointments():
	content = request.get_json()
	
	ownerid = content['ownerid']
	locationid = content['locationid']

	location = Location.query.filter_by(id=locationid).first()
	locationInfo = json.loads(location.info)
	receiveType = locationInfo["type"]

	sql = "select * from schedule where locationId = " + str(locationid) + " and status = 'confirmed'"

	if receiveType == "stylist":
		sql += " and workerId = " + str(ownerid)
		
	sql += " order by time"

	datas = query(sql, True)
	appointments = []

	for data in datas:
		user = User.query.filter_by(id=data['userId']).first()
		service = Service.query.filter_by(id=data['serviceId']).first()
		worker = Owner.query.filter_by(id=data['workerId']).first()
			
		info = json.loads(data["info"])

		client = {
			"id": data['userId'],
			"username": user.username
		}

		worker = {
			"id": worker.id,
			"username": worker.username
		}

		userInput = json.loads(data['userInput'])
		appointments.append({
			"key": "appointment-" + str(data['id']),
			"id": str(data['id']),
			"username": user.username,
			"client": client,
			"worker": worker,
			"time": json.loads(data['time']),
			"serviceid": service.id if service != None else "",
			"name": service.name if service != None else userInput['name'],
			"image": json.loads(service.image) if service != None else None
		})

	return { "appointments": appointments, "numappointments": len(appointments) }

@app.route("/get_cart_orderers/<id>")
def get_cart_orderers(id):
	datas = query("select adder, orderNumber from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by adder, orderNumber", True)
	numCartorderers = query("select count(*) as num from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by adder, orderNumber", True)
	cartOrderers = []

	for k, data in enumerate(datas):
		adder = User.query.filter_by(id=data['adder']).first()
		numOrders = query("select count(*) as num from cart where adder = " + str(data['adder']) + " and locationId = " + str(id) + " and (status = 'checkout' or status = 'inprogress') and orderNumber = '" + data["orderNumber"] + "'", True)
		num = numOrders[0]["num"] if len(numOrders) > 0 else 0

		cartitem = Cart.query.filter_by(orderNumber=data['orderNumber']).first()
		userInput = json.loads(cartitem.userInput)

		cartOrderers.append({
			"key": "cartorderer-" + str(k),
			"id": len(cartOrderers),
			"adder": adder.id,
			"username": adder.username,
			"numOrders": num,
			"orderNumber": data['orderNumber'],
			"type": userInput["type"]
		})

	numCartorderers = numCartorderers[0]["num"] if len(numCartorderers) > 0 else 0

	return { "cartOrderers": cartOrderers, "numCartorderers": numCartorderers }

@app.route("/get_orders", methods=["POST"])
def get_orders():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	ordernumber = content['ordernumber']

	datas = query("select * from cart where adder = " + str(userid) + " and locationId = " + str(locationid) + " and orderNumber = '" + ordernumber + "'", True)
	orders = []
	ready = True
	waitTime = datas[0]["waitTime"] if len(datas) > 0 else ""

	for data in datas:
		product = Product.query.filter_by(id=data['productId']).first()
		quantity = int(data['quantity'])
		options = json.loads(data['options'])
		others = json.loads(data['others'])
		sizes = json.loads(data['sizes'])
		userInput = json.loads(data['userInput'])
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
					if size["selected"] == True:
						cost += float(size["price"])
			else:
				cost += float(product.price)

			for other in others:
				if other["selected"] == True:
					cost += float(other["price"])

		orders.append({
			"key": "cart-item-" + str(data['id']),
			"id": str(data['id']),
			"name": product.name if product != None else userInput['name'],
			"note": data['note'],
			"image": json.loads(product.image) if product != None else None,
			"options": options,
			"others": others,
			"sizes": sizes,
			"quantity": quantity,
			"cost": (cost * quantity) if cost > 0 else None
		})

		if data['status'] == "checkout":
			ready = False

	return { "orders": orders, "ready": ready, "waitTime": waitTime }
