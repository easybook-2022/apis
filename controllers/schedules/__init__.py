from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, os, math, json
from haversine import haversine, Unit
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
def welcome_schedules():
	return { "msg": "welcome to schedules of easygo" }

@app.route("/get_requests", methods=["POST"])
def get_requests():
	content = request.get_json()

	ownerid = content['ownerid']
	locationid = content['locationid']

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			datas = query("select * from schedule where status = 'requested'", True)
			requests = []

			for data in datas:
				service = None

				if data['serviceId'] != "":
					service = Service.query.filter_by(id=data['serviceId']).first()

				user = User.query.filter_by(id=data['userId']).first()

				requests.append({
					"key": "request-" + str(data['id']),
					"id": str(data['id']),
					"userId": user.id,
					"username": user.username,
					"time": int(data['time']),
					"name": service.name if service != None else location.name,
					"image": service.image if service != None else location.logo
				})

			return { "requests": requests }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg }

@app.route("/get_appointment_info/<id>")
def get_appointment_info(id):
	schedule = Schedule.query.filter_by(id=id).first()

	if schedule != None:
		locationId = schedule.locationId
		serviceId = schedule.serviceId

		service = Service.query.filter_by(id=serviceId).first()

		if service != None:
			info = {
				"locationId": int(locationId),
				"name": service.name,
			}

			return { "appointmentInfo": info }
		else:
			msg = "Service doesn't exist"
	else:
		msg = "Appointment doesn't exist"

	return { "errormsg": msg }

@app.route("/get_reservation_info/<id>")
def get_reservation_info(id):
	schedule = Schedule.query.filter_by(id=id).first()

	if schedule != None:
		locationId = schedule.locationId

		location = Location.query.filter_by(id=locationId).first()

		if location != None:
			info = {
				"locationId": locationId,
				"name": location.name,
				"seaters": schedule.seaters
			}

			return { "reservationInfo": info }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Reservation doesn't exist"

	return { "errormsg": msg }

@app.route("/reschedule_appointment", methods=["POST"])
def reschedule_appointment():
	content = request.get_json()

	appointmentid = content['appointmentid']
	time = content['time']

	schedule = Schedule.query.filter_by(id=appointmentid).first()

	if schedule != None:
		schedule.status = "rebook"
		schedule.nextTime = time

		db.session.commit()

		return { "msg": "" }
	else:
		msg = "Appointment doesn't exist"

	return { "errormsg": msg }

@app.route("/reschedule_reservation", methods=["POST"])
def reschedule_reservation():
	content = request.get_json()

	reservationid = content['reservationid']
	time = content['time']

	schedule = Schedule.query.filter_by(id=reservationid).first()

	if schedule != None:
		schedule.status = "rebook"
		schedule.nextTime = time

		db.session.commit()

		return { "msg": "" }
	else:
		msg = "Reservation doesn't exist"

	return { "errormsg": msg }

@app.route("/request_appointment", methods=["POST"])
def request_appointment():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	menuid = content['menuid']
	serviceid = content['serviceid']
	time = content['time']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			menu = Menu.query.filter_by(id=menuid).first()

			if menu != None:
				service = Service.query.filter_by(id=serviceid).first()

				if service != None:
					serviceName = service.name

					requested_appointment = Schedule.query.filter_by(
						locationId=locationid,
						menuId=menuid,
						serviceId=serviceid,
						userId=userid,
						status='requested'
					).first()
					rebooked_appointment = Schedule.query.filter_by(
						locationId=locationid,
						menuId=menuid,
						serviceId=serviceid,
						userId=userid,
						status='rebook'
					).first()

					if requested_appointment == None and rebooked_appointment == None: # nothing created yet
						appointment = Schedule(userid, locationid, menuid, serviceid, time, "requested", '', '', location.type, 1)

						db.session.add(appointment)
						db.session.commit()

						msg = "appointment added"

						return { "msg": msg }
					else:
						if rebooked_appointment != None:
							rebooked_appointment.status = 'requested'
							rebooked_appointment.time = time

							db.session.commit()

							msg = "appointment re-requested"

							return { "msg": msg }
						else:
							msg = "Appointment already requested"
				else:
					msg = "Service doesn't exist"
			else:
				msg = "Menu doesn't exist"
		else:
			msg = "Location doesn't exist"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/accept_request/<id>")
def accept_request(id):
	appointment = Schedule.query.filter_by(id=id).first()

	if appointment != None:
		appointment.status = "accepted"

		db.session.commit()

		return { "msg": "Appointment accepted" }
	else:
		msg = "Appointment doesn't exist"

	return { "errormsg": msg }

@app.route("/cancel_request", methods=["POST"])
def cancel_request():
	content = request.get_json()

	id = content['id']
	reason = content['reason']

	appointment = Schedule.query.filter_by(id=id).first()

	if appointment != None:
		appointment.status = "cancel"
		appointment.cancelReason = reason

		db.session.commit()

		return { "msg": "" }
	else:
		msg = "Appointment doesn't exist"

	return { "errormsg": msg }

@app.route("/close_request/<id>")
def close_request(id):
	appointment = Schedule.query.filter_by(id=id).first()

	if appointment != None:
		db.session.delete(appointment)
		db.session.commit()

		return { "msg": "" }
	else:
		msg = "Appointment doesn't exist"

	return { "errormsg": msg }

@app.route("/get_appointments/<id>")
def get_appointments(id):
	datas = Schedule.query.filter_by(locationId=id, status='accepted').all()
	appointments = []

	for data in datas:
		user = User.query.filter_by(id=data.userId).first()
		service = Service.query.filter_by(id=data.serviceId).first()

		appointments.append({
			"key": "appointment-" + str(data.id),
			"id": str(data.id),
			"username": user.username,
			"time": int(data.time),
			"name": service.name,
			"image": service.image
		})

	return { "appointments": appointments, "numappointments": len(appointments) }

@app.route("/get_reservations/<id>")
def get_reservations(id):
	datas = Schedule.query.filter_by(locationId=id, status='accepted').all()
	reservations = []

	for data in datas:
		user = User.query.filter_by(id=data.userId).first()
		location = Location.query.filter_by(id=data.locationId).first()

		reservations.append({
			"key": "reservation-" + str(data.id),
			"id": str(data.id),
			"username": user.username,
			"time": int(data.time),
			"name": location.name,
			"image": location.logo,
			"seaters": data.seaters
		})

	return { "reservations": reservations, "numreservations": len(reservations) }
