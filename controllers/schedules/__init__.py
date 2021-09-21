from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, os, math, json, stripe
from haversine import haversine, Unit
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint

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
run_stripe = True

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
	state = db.Column(db.String(6))

	def __init__(
		self, 
		name, addressOne, addressTwo, city, province, postalcode, phonenumber, logo, 
		longitude, latitude, owners, type, hours, accountId, state
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
		self.state = state

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

@app.route("/", methods=["GET"])
def welcome_schedules():
	return { "msg": "welcome to schedules of easygo" }

@app.route("/get_requests/<id>")
def get_requests(id):
	location = Location.query.filter_by(id=id).first()

	if location != None:
		datas = query("select * from schedule where locationId = " + str(id) + " and status = 'requested'", True)
		requests = []

		for data in datas:
			service = None

			if data['serviceId'] != "":
				service = Service.query.filter_by(id=data['serviceId']).first()

			user = User.query.filter_by(id=data['userId']).first()

			requests.append({
				"key": "request-" + str(data['id']),
				"id": str(data['id']),
				"type": data['locationType'],
				"userId": user.id,
				"username": user.username,
				"time": int(data['time']),
				"name": service.name if service != None else location.name,
				"image": service.image if service != None else location.logo,
				"note": data['note'],
				"diners": len(json.loads(data['customers'])) if data['locationType'] == 'restaurant' else False,
				"tablenum": data['table']
			})

		return { "requests": requests }
	else:
		msg = "Location doesn't exist"

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
				"diners": len(json.loads(schedule.customers)),
				"note": schedule.note,
				"table": schedule.table
			}

			return { "reservationInfo": info }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Reservation doesn't exist"

	return { "errormsg": msg }, 400

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
	table = content['table']

	schedule = Schedule.query.filter_by(id=reservationid).first()

	if schedule != None:
		schedule.status = "rebook"
		schedule.nextTime = time
		schedule.table = table

		db.session.commit()

		return { "msg": "Reservation rescheduled" }
	else:
		msg = "Reservation doesn't exist"

	return { "errormsg": msg }

@app.route("/request_appointment", methods=["POST"])
def request_appointment():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	scheduleid = content['scheduleid']
	serviceid = content['serviceid']
	time = content['time']
	note = content['note']

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		customerid = info['customerId']

		if run_stripe == True:
			customer = stripe.Customer.list_sources(
				customerid,
				object="card",
				limit=1
			)
			cards = len(customer.data)
		else:
			cards = 1

		if cards > 0:
			location = Location.query.filter_by(id=locationid).first()

			if location != None:
				if scheduleid == None:
					appointment = Schedule.query.filter_by(userId=userid, serviceId=serviceid).first()

					if appointment == None:
						service = Service.query.filter_by(id=serviceid).first()
						info = json.dumps({"paymentsent": False,"customer_cancel": False,"salon_cancel": False})
						appointment = Schedule(userid, locationid, service.menuId, serviceid, time, "requested", '', '', location.type, 1, note, '[]', '', info)

						db.session.add(appointment)
						db.session.commit()

						return { "msg": "appointment added" }
					else:
						msg = "Appointment already made"
						status = "existed"
				else:
					appointment = Schedule.query.filter_by(id=scheduleid).first()

					if appointment != None:
						appointment.status = 'requested'
						appointment.time = time
						appointment.note = note

						db.session.commit()

						return { "msg": "appointment re-requested" }
					else:
						msg = "Appointment doesn't exist"
			else:
				msg = "Location doesn't exist"
		else:
			msg = "A payment method is required"
			status = "cardrequired"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/accept_request", methods=["POST"])
def accept_request():
	content = request.get_json()

	requestid = content['requestid']
	tablenum = content['tablenum']

	appointment = Schedule.query.filter_by(id=requestid).first()

	if appointment != None:
		appointment.status = "accepted"
		appointment.table = tablenum

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

		return { "msg": "success" }
	else:
		msg = "Appointment doesn't exist"

	return { "errormsg": msg }

@app.route("/cancel_reservation_joining", methods=["POST"])
def cancel_reservation_joining():
	content = request.get_json()

	userid = content['userid']
	scheduleid = content['scheduleid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		diners = json.loads(schedule.customers)

		for k, diner in enumerate(diners):
			if diner['userid'] == userid:
				diners.pop(k)

				schedule.customers = json.dumps(diners)

				db.session.commit()

				return { "msg": "diner removed" }

		msg = "Diner doesn't exist"
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/accept_reservation_joining", methods=["POST"])
def accept_reservation_joining():
	content = request.get_json()

	userid = content['userid']
	scheduleid = content['scheduleid']

	user = User.query.filter_by(id=userid).first()
	msg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		if run_stripe == True:
			customer = stripe.Customer.list_sources(
				customerid,
				object="card",
				limit=1
			)
			cards = len(customer.data)
		else:
			cards = 1

		if cards > 0:
			schedule = Schedule.query.filter_by(id=scheduleid).first()

			if schedule != None:
				diners = json.loads(schedule.customers)

				for k, diner in enumerate(diners):
					if diner['userid'] == userid:
						diner['status'] = 'confirmed'
						diners[k] = diner

						schedule.customers = json.dumps(diners)

						db.session.commit()

						return { "msg": "diner accepted" }

				msg = "Diner doesn't exist"
			else:
				msg = "Schedule doesn't exist"
		else:
			msg = "A payment method is required"
			status = "cardrequired"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/add_diner", methods=["POST"])
def add_diner():
	content = request.get_json()

	userid = str(content['userid'])
	scheduleid = content['scheduleid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		diners = json.loads(schedule.customers)

		diners.append({ "userid": userid, "status": "waiting" })

		schedule.customers = json.dumps(diners)

		db.session.commit()

		return { "msg": "Diner added" }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/done_dining/<id>")
def done_dining(id):
	user_orders = []

	numUnserved = query("select count(*) as num from schedule where ((length(orders) - length(replace(orders, 'making', ''))) / 6 > 0) and id = " + str(id), True)[0]["num"]
	msg = ""
	status = ""

	if numUnserved == 0:
		return { "msg": "success" }
	else:
		msg = "There's still some unserved orders"
		status = "unserved"

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_diners_payments", methods=["POST"])
def get_diners_payments():
	content = request.get_json()

	scheduleid = content['scheduleid']
	userid = str(content['userid'])
	time = content['time']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		location = Location.query.filter_by(id=schedule.locationId).first()

		if location != None:
			accountid = location.accountId
			orders = json.loads(schedule.orders)
			charges = orders["charges"]

			if userid in charges:
				user = User.query.filter_by(id=userid).first()

				charge = charges[userid]["charge"]
				paymentSent = charges[userid]["paymentsent"]
				paid = charges[userid]["paid"]

				if charge > 0 and paid == False:
					if paymentSent == True:
						info = json.loads(user.info)

						customerid = info["customerId"]

						if run_stripe == True:
							stripe.Charge.create(
								amount=int(charge * 100),
								currency="cad",
								customer=customerid,
								transfer_data={
									"destination": accountid
								}
							)

						charges[userid]["paid"] = True

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

											quantity = int(order['quantity'])
											options = order['options']
											others = order['others']
											sizes = order['sizes']
											callfor = order['callfor']
											price = 0

											if len(sizes) > 0:
												for size in sizes:
													if size["selected"] == True:
														price = quantity * float(size["price"])
											else:
												price = quantity * float(product.price)

											for other in others:
												if other["selected"] == True:
													price += float(other["price"])

											transaction = Transaction(groupId, location.id, order['productid'], 0, userid, '[]', json.dumps(options), json.dumps(others), json.dumps(sizes), time)

											db.session.add(transaction)
											db.session.commit()
					else:
						return { "errormsg": "Payment unconfirmed", "status": "paymentunconfirmed", "username": user.username }, 400

				if "\"paid\": false" not in json.dumps(charges):
					db.session.delete(schedule)

				db.session.commit()

				return { "msg": "payment received" }
			else:
				msg = "Diner doesn't exist"
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }, 400

@app.route("/done_service", methods=["POST"])
def done_service():
	content = request.get_json()

	scheduleid = content['scheduleid']
	time = content['time']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	msg = ""
	status = ""

	if schedule != None:
		locationid = schedule.locationId
		serviceid = schedule.serviceId
		info = json.loads(schedule.info)

		location = Location.query.filter_by(id=locationid).first()
		service = Service.query.filter_by(id=serviceid).first()

		if location != None and service != None:
			accountid = location.accountId

			if run_stripe == True:
				account = stripe.Account.list_external_accounts(
					accountid,
					object="bank_account",
					limit=1
				)
				bankaccounts = len(account.data)
			else:
				bankaccounts = 1

			if bankaccounts > 0:
				clientId = schedule.userId

				client = User.query.filter_by(id=clientId).first()
				clientInfo = json.loads(client.info)
				customerid = clientInfo["customerId"]
				price = float(service.price)

				if info["paymentsent"] == True:
					if run_stripe == True:
						stripe.Charge.create(
							amount=int(price * 100),
							currency="cad",
							customer=customerid,
							transfer_data={
								"destination": accountid
							}
						)

					groupId = ""

					for k in range(20):
						groupId += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 0))

					transaction = Transaction(groupId, locationid, 0, schedule.serviceId, schedule.userId, '[]', '[]', '[]', '[]', time)

					db.session.add(transaction)
					db.session.delete(schedule)
					db.session.commit()

					return { "msg": "Payment received", "clientName": client.username, "name": service.name, "price": service.price }
				else:
					msg = "Client hasn't sent payment yet"
					status = "paymentunsent"
			else:
				msg = "Please provide a bank account to receive payment"
				status = "bankaccountrequired"
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/cancel_service", methods=["POST"])
def cancel_service():
	content = request.get_json()

	scheduleid = content['scheduleid']
	type = content['type']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		info = json.loads(schedule.info)
		salon_cancel = info['salon_cancel']
		customer_cancel = info['customer_cancel']
		delete_service = False

		if type == "salon":
			if customer_cancel == True:
				delete_service = True
		elif type == "customer":
			if salon_cancel == True:
				delete_service = True

		if delete_service == True:
			db.session.delete(schedule)
		else:
			info[type + '_cancel'] = True

			schedule.info = json.dumps(info)

		db.session.commit()

		return { "msg": "appointment cancelled", "delete": delete_service }
	else:
		msg = "Schedule doens't exist"

	return { "errormsg": msg }, 400

@app.route("/send_service_payment/<id>")
def send_service_payment(id):
	schedule = Schedule.query.filter_by(id=id).first()

	if schedule != None:
		info = json.loads(schedule.info)
		info["paymentsent"] = True

		schedule.info = json.dumps(info)

		db.session.commit()

		return { "msg": "Payment sent" }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }, 400

@app.route("/send_dining_payment", methods=["POST"])
def send_dining_payment():
	content = request.get_json()

	userid = content['userid']
	scheduleid = content['scheduleid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		orders = json.loads(schedule.orders)
		orders["charges"][str(userid)]["paymentsent"] = True

		schedule.orders = json.dumps(orders)

		db.session.commit()

		return { "msg": "Payment sent" }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }, 400

@app.route("/get_appointments/<id>")
def get_appointments(id):
	datas = query("select * from schedule where locationId = " + str(id) + " and status = 'accepted'", True)
	appointments = []

	for data in datas:
		user = User.query.filter_by(id=data['userId']).first()
		service = Service.query.filter_by(id=data['serviceId']).first()

		appointments.append({
			"key": "appointment-" + str(data['id']),
			"id": str(data['id']),
			"username": user.username,
			"time": int(data['time']),
			"name": service.name,
			"image": service.image,
			"gettingPayment": False
		})

	return { "appointments": appointments, "numappointments": len(appointments) }

@app.route("/search_customers", methods=["POST"])
def search_customers():
	content = request.get_json()

	locationid = content['locationid']
	searchingusername = content['username']

	location = Location.query.filter_by(id=locationid).first()

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
		msg = "Location doesn't exist"

	return { "errormsg": msg }

@app.route("/get_cart_orderers/<id>")
def get_cart_orderers(id):
	datas = query("select adder, orderNumber from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'ready') group by adder, orderNumber", True)
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
			"id": adder.id,
			"username": adder.username,
			"profile": adder.profile,
			"numOrders": numOrders,
			"orderNumber": data['orderNumber']
		})

	return { "cartOrderers": cartOrderers }

@app.route("/see_user_orders", methods=["POST"])
def see_user_orders():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	ordernumber = content['ordernumber']

	datas = query("select * from cart where adder = " + str(userid) + " and locationId = " + str(locationid) + " and orderNumber = '" + ordernumber + "' and (status='checkout' or status='ready')", True)
	orders = []
	totalcost = 0
	ready = True

	for data in datas:
		product = Product.query.filter_by(id=data['productId']).first()
		quantity = int(data['quantity'])
		callfor = json.loads(data['callfor'])
		options = json.loads(data['options'])
		others = json.loads(data['others'])
		sizes = json.loads(data['sizes'])
		row = []
		cost = 0

		for k, option in enumerate(options):
			option['key'] = "option-" + str(k)

		for k, other in enumerate(others):
			other['key'] = "other-" + str(k)

		for k, size in enumerate(sizes):
			size['key'] = "size-" + str(k)

		if product.price == "":
			for size in sizes:
				if size['selected'] == True:
					cost += quantity * float(size['price'])
					totalcost += quantity * float(size['price'])
		else:
			cost += quantity * float(product.price)
			totalcost += quantity * float(product.price)

		for other in others:
			if other['selected'] == True:
				cost += float(other['price'])
				totalcost += float(other['price'])

		orders.append({
			"key": "cart-item-" + str(data['id']),
			"id": str(data['id']),
			"name": product.name,
			"productId": product.id,
			"note": data['note'],
			"image": product.image,
			"options": options,
			"others": others,
			"sizes": sizes,
			"quantity": quantity,
			"cost": cost,
			"orderers": len(callfor)
		})

		if data['status'] == "checkout":
			ready = False

	return { "orders": orders, "totalcost": totalcost, "ready": ready }

@app.route("/get_diners_orders/<id>")
def get_diners_orders(id):
	schedule = Schedule.query.filter_by(id=id).first()

	if schedule != None:
		orders = json.loads(schedule.orders)
		customers = json.loads(schedule.customers)
		groups = orders["groups"]
		charges = orders["charges"]

		user_charges = {}

		if str(schedule.userId) in charges:
			user_charges[str(schedule.userId)] = {
				"charge": 0,
				"paymentsent": charges[str(schedule.userId)]["paymentsent"],
				"paid": charges[str(schedule.userId)]["paid"]
			}

		for customer in customers:
			user_charges[customer["userid"]] = {
				"charge": 0,
				"paymentsent": charges[customer["userid"]]["paymentsent"],
				"paid": charges[customer["userid"]]["paid"]
			}

		diners = []
		total = 0

		for rounds in groups:
			for round in rounds:
				if round != "status" and round != "id":
					for orderer in rounds[round]:
						product = Product.query.filter_by(id=orderer['productid']).first()

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
							price = quantity * float(product.price)

						for other in others:
							if other["selected"] == True:
								price += float(other["price"])

						if len(callfor) > 0:
							for info in callfor:
								user_charges[str(info["userid"])]["charge"] += price
						else:
							user_charges[round]["charge"] += price

			orders["charges"] = user_charges

			schedule.orders = json.dumps(orders)

			db.session.commit()

		for index, charge in enumerate(user_charges):
			user = User.query.filter_by(id=charge).first()

			user_charges[charge]["key"] = "user-" + str(index)
			user_charges[charge]["userId"] = user.id
			user_charges[charge]["username"] = user.username
			user_charges[charge]["profile"] = user.profile
			user_charges[charge]["payed"] = False
			user_charges[charge]["paying"] = False

			total += user_charges[charge]["charge"]

			diners.append(user_charges[charge])

		return { "diners": diners, "total": total }
	else:
		msg = "Reservation doesn't exist"

	return { "errormsg": msg }, 400

@app.route("/get_reservations/<id>")
def get_reservations(id):
	datas = Schedule.query.filter_by(locationId=id, status='accepted').all()
	reservations = []

	for data in datas:
		user = User.query.filter_by(id=data.userId).first()
		location = Location.query.filter_by(id=data.locationId).first()

		# get number of making orders
		orders = data.orders
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
			"gettingPayment": False
		})

	return { "reservations": reservations, "numreservations": len(reservations) }

@app.route("/get_schedule_info/<id>")
def get_schedule_info(id):
	schedule = Schedule.query.filter_by(id=id, status="accepted").first()

	if schedule != None:
		location = Location.query.filter_by(id=schedule.locationId).first()

		info = {
			"name": location.name,
			"locationId": schedule.locationId,
			"time": schedule.time,
			"table": schedule.table,
			"numdiners": len(json.loads(schedule.customers)) + 1
		}

		return { "scheduleInfo": info, "msg": "" }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

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
	quantity = content['quantity']
	callfor = content['callfor']
	options = content['options']
	others = content['others']
	sizes = content['sizes']
	note = content['note']

	user = User.query.filter_by(id=userid).first()
	msg = ""

	if user != None:
		product = Product.query.filter_by(id=productid).first()

		if product != None:
			if product.price == '':
				if "true" not in json.dumps(sizes):
					msg = "Please choose a size"

			if msg == "":
				schedule = Schedule.query.filter_by(id=scheduleid).first()

				if schedule != None:
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

					if userid in first_group:
						first_group[userid].append({ "id": getRanStr(), "productid": productid, "options": options, "others": others, "sizes": sizes, "quantity": quantity, "note": note, "callfor": callfor })
					else:
						first_group[userid] = [{ "id": getRanStr(), "productid": productid, "options": options, "others": others, "sizes": sizes, "quantity": quantity, "note": note, "callfor": callfor }]

					groups[0] = first_group
					orders['groups'] = groups
					schedule.orders = json.dumps(orders)

					db.session.commit()

					return { "orders": orders, "msg": "item added to list" }
				else:
					msg = "Schedule doesn't exist"
		else:
			msg = "Product doesn't exist"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/see_dining_orders/<id>")
def see_dining_orders(id):
	schedule = Schedule.query.filter_by(id=id).first()

	if schedule != None:
		orderer = schedule.userId
		data = json.loads(schedule.orders)

		groups = data['groups']
		donedining = data['donedining']
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
						cost = 0

						for k, option in enumerate(options):
							option['key'] = "option-" + str(k)

						for k, other in enumerate(others):
							other['key'] = "other-" + str(k)

						for k, size in enumerate(sizes):
							size['key'] = "size-" + str(k)

						if product.price == "":
							for size in sizes:
								if size['selected'] == True:
									cost += quantity * float(size['price'])
						else:
							cost += quantity * float(product.price)

						for other in others:
							if other['selected'] == True:
								cost += float(other['price'])

						orderer = User.query.filter_by(id=ordererid).first()

						each_orders.append({
							"id": order['id'],
							"image": product.image,
							"key": "meal-" + order['id'],
							"name": product.name,
							"note": order['note'],
							"options": options,
							"others": others,
							"sizes": sizes,
							"quantity": quantity,
							"cost": cost,
							"orderers": orderers,
							"orderer": { "id": ordererid, "username": orderer.username },
							"numorderers": numorderers
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
					"status": rounds["status"]
				})
				each_round_num += 1
				each_orderers = []

		return { "rounds": each_rounds }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/edit_diners/<id>")
def edit_diners(id):
	schedule = Schedule.query.filter_by(id=id).first()

	if schedule != None:
		customers = json.loads(schedule.customers)
		customers.append({ "userid": str(schedule.userId), "status": "confirmed" })
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
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/get_dining_orders/<id>")
def get_dining_orders(id):
	schedule = Schedule.query.filter_by(id=id).first()

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

							each_orders.append({
								"id": order['id'],
								"image": product.image,
								"key": "meal-" + order['id'],
								"name": product.name,
								"note": order['note'],
								"options": options, "others": others, "sizes": sizes,
								"quantity": quantity,
								"callfor": len(order['callfor'])
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
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/deliver_round", methods=["POST"])
def deliver_round():
	content = request.get_json()

	scheduleid = content['scheduleid']
	roundid = content['roundid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		orders = json.loads(schedule.orders)

		groups = orders['groups']

		for rounds in groups:
			if rounds['id'] == roundid:
				rounds['status'] = 'served'

		orders['groups'] = groups

		schedule.orders = json.dumps(orders)

		db.session.commit()

		return { "msg": "round served" }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/send_orders/<id>")
def send_orders(id):
	schedule = Schedule.query.filter_by(id=id).first()
	msg = ""
	status = ""

	if schedule != None:
		orders = json.loads(schedule.orders)

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

								msg = "unconfirm orders"
								status = "unconfirmedorders"

			if confirmed == True:
				first_group['status'] = "making"

				groups[0] = first_group

				orders['groups'] = groups

				schedule.orders = json.dumps(orders)

				db.session.commit()

				return { "msg": "order sent" }
		else:
			msg = "Orders already sent"
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/edit_order", methods=["POST"])
def edit_order():
	content = request.get_json()

	scheduleid = content['scheduleid']
	orderid = content['orderid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

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
							cost = 0

							for k, option in enumerate(options):
								option['key'] = "option-" + str(k)

							for k, other in enumerate(others):
								other['key'] = "other-" + str(k)

							for k, size in enumerate(sizes):
								size['key'] = "size-" + str(k)

							if product.price == "":
								for size in sizes:
									if size['selected'] == True:
										cost += quantity * float(size['price'])
							else:
								cost += quantity * float(product.price)

							for other in others:
								if other['selected'] == True:
									cost += float(other['price'])

							info = {
								"name": product.name,
								"info": product.info,
								"image": product.image,
								"quantity": quantity,
								"options": options, "others": others, "sizes": sizes,
								"note": orderer['note'],
								"price": float(product.price) if product.price != "" else 0,
								"cost": cost
							}

							return { "orderInfo": info, "msg": "order info fetched" }

		msg = "Order doesn't exist"
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

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
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/delete_order", methods=["POST"])
def delete_order():
	content = request.get_json()

	scheduleid = content['scheduleid']
	orderid = content['orderid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		orders = json.loads(schedule.orders)

		groups = orders['groups']

		for rounds in groups:
			for k in rounds:
				if k != "status" and k != "id":
					for m, data in enumerate(rounds[k]):
						if data['id'] == orderid:
							del rounds[k][m]

		orders['groups'] = groups
		schedule.orders = json.dumps(orders)

		db.session.commit()

		return { "msg": "order deleted" }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/add_diners", methods=["POST"])
def add_diners():
	content = request.get_json()

	scheduleid = content['scheduleid']
	newdiners = content['diners']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		booker = str(schedule.userId)

		for k, newdiner in enumerate(newdiners):
			if newdiner["userid"] == booker: # remove booker from diners
				del newdiners[k]

		schedule.customers = json.dumps(newdiners)

		db.session.commit()

		return { "msg": "New diners added" }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/edit_order_callfor", methods=["POST"])
def edit_order_callfor():
	content = request.get_json()

	scheduleid = content['scheduleid']
	orderid = content['orderid']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

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
							cost = 0

							for k, option in enumerate(options):
								option['key'] = "option-" + str(k)

							for k, other in enumerate(others):
								other['key'] = "other-" + str(k)

							for k, size in enumerate(sizes):
								size['key'] = "size-" + str(k)

							if product.price == "":
								for size in sizes:
									if size['selected'] == True:
										cost += quantity * float(size['price'])
							else:
								cost += quantity * float(product.price)

							for other in others:
								if other['selected'] == True:
									cost += float(other['price'])

							orderingItem = {
								"name": product.name,
								"image": product.image,
								"options": options, "others": others, "sizes": sizes,
								"quantity": int(orderer['quantity']),
								"cost": cost
							}

							return { "searchedDiners": searcheddiners, "numSearchedDiners": numsearcheddiners, "orderingItem": orderingItem }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/diner_is_removable", methods=["POST"])
def diner_is_removable():
	content = request.get_json()

	scheduleid = content['scheduleid']
	userid = str(content['userid'])

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		orders = schedule.orders

		if "\"" + userid + "\"" in orders:
			user = User.query.filter_by(id=userid).first()

			return { "removable": False, "username": user.username }

		return { "removable": True }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/diner_is_selectable", methods=["POST"])
def diner_is_selectable():
	content = request.get_json()

	scheduleid = content['scheduleid']
	userid = str(content['userid'])

	num = query("select count(*) as num from schedule where id = " + str(scheduleid) + " and customers like '%%'", True)[0]["num"]
	user = User.query.filter_by(id=userid).first()

	if user != None:
		info = json.loads(user.info)

		status = info["status"]

		isconfirmed = True if query("select count(*) as num from schedule where id = " + str(scheduleid) + " and customers like '%\"userid\": \"" + userid + "\", \"status\": \"confirmed\"%'", True)[0]["num"] > 0 else False

		if status == "filled" and isconfirmed == True:
			return { "selectable": True, "username": user.username }

		msg = "paymentrequired" if status == "required" else "unconfirmeddiner"

		return { "selectable": False, "username": user.username, "msg": msg }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/cancel_dining_order", methods=["POST"])
def cancel_dining_order():
	content = request.get_json()

	orderid = content['orderid']
	ordererid = content['ordererid']

	data = query("select orders from schedule where orders like '%\"" + str(orderid) + "\"%'", True)

	if len(data) == 1:
		data = data[0]
		orders = json.loads(data["orders"])

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

		query("update schedule set orders = '" + json.dumps(orders) + "' where orders like '%\"" + str(ordererid) + "\"%'", False)

		return { "msg": "user order cancelled" }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/confirm_dining_order", methods=["POST"])
def confirm_dining_order():
	content = request.get_json()

	orderid = content['orderid']
	ordererid = content['ordererid']

	data = query("select orders from schedule where orders like '%\"" + str(orderid) + "\"%'", True)

	if len(data) == 1:
		data = data[0]
		orders = json.loads(data["orders"])

		for rounds in orders["groups"]:
			for k in rounds:
				if k != "status" and k != "id":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							for info in orderer['callfor']:
								if info["userid"] == str(ordererid):
									info["status"] = "confirmed"

		query("update schedule set orders = '" + json.dumps(orders) + "' where orders like '%\"" + str(ordererid) + "\"%'", False)

		return { "msg": "user order confirmed" }
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

@app.route("/update_order_callfor", methods=["POST"])
def update_order_callfor():
	content = request.get_json()

	scheduleid = content['scheduleid']
	orderid = content['orderid']
	callfor = content['callfor']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

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
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }
