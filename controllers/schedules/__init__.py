from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, os, math, json
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
	customers = db.Column(db.String(255))
	note = db.Column(db.String(225))
	orders = db.Column(db.Text)
	table = db.Column(db.String(20))

	def __init__(self, userId, locationId, menuId, serviceId, time, status, cancelReason, nextTime, locationType, customers, note, orders, table):
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
	productId = db.Column(db.Integer)
	quantity = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(150))
	note = db.Column(db.String(100))

	def __init__(self, productId, quantity, adder, callfor, options, others, sizes, note):
		self.productId = productId
		self.quantity = quantity
		self.adder = adder
		self.callfor = callfor
		self.options = options
		self.others = others
		self.sizes = sizes
		self.note = note

	def __repr__(self):
		return '<Cart %r>' % self.productId

class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	groupId = db.Column(db.String(20)) # same for each cart
	productId = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(150))
	time = db.Column(db.String(15))

	def __init__(self, groupId, productId, adder, callfor, options, others, sizes, time):
		self.groupId = groupId
		self.productId = productId
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

@app.route("/get_requests", methods=["POST"])
def get_requests():
	content = request.get_json()

	ownerid = content['ownerid']
	locationid = content['locationid']

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			datas = query("select * from schedule where locationId = " + str(locationid) + " and status = 'requested'", True)
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
					"diners": len(json.loads(data['customers'])) if data['locationType'] != 'nail' else False
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
				"diners": len(json.loads(schedule.customers))
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

@app.route("/accept_appointment", methods=["POST"])
def accept_appointment():
	content = request.get_json()

	requestid = content['requestid']
	tablenum = content['tablenum']

	return { "msg": "" }

@app.route("/request_appointment", methods=["POST"])
def request_appointment():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	menuid = content['menuid']
	serviceid = content['serviceid']
	time = content['time']
	note = content['note']

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
						appointment = Schedule(userid, locationid, menuid, serviceid, time, "requested", '', '', location.type, 1, note, '[]', '')

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

		return { "msg": "" }
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

		for k in range(len(diners)):
			diner = diners[k]

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

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		diners = json.loads(schedule.customers)

		for k in range(len(diners)):
			diner = diners[k]

			if diner['userid'] == userid:
				diner['status'] = 'confirm'
				diners[k] = diner

				schedule.customers = json.dumps(diners)

				db.session.commit()

				return { "msg": "diner accepted" }

		msg = "Diner doesn't exist"
	else:
		msg = "Schedule doesn't exist"

	return { "errormsg": msg }

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

@app.route("/done_dining", methods=["POST"])
def done_dining():
	content = request.get_json()

	userid = str(content['userid'])
	scheduleid = content['scheduleid']
	user_orders = []

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		datas = json.loads(schedule.customers)
		diners = []

		for data in datas:
			diners.append(str(data['userid']))

		if userid not in diners:
			diners.append(userid)

		for diner in diners:
			if diner == userid:
				# submit diner's payment to location
				orders = json.loads(schedule.orders)

				groups = orders['groups']

				for rounds in groups:
					for round in rounds:
						if round != "status":
							for orderer in rounds[round]:
								if (round == userid and len(orderer['callfor']) == 0) or (round != userid and userid in orderer['callfor']):
									product = Product.query.filter_by(id=orderer['productid']).first()

									price = float(product.price)
									quantity = int(orderer['quantity'])
									callfor = orderer['callfor']

									user_orders.append({
										"id": orderer['id'],
										"quantity": quantity,
										"price": price,
										"name": product.name
									})

							schedule.customers = json.dumps(diners)

							db.session.commit()

		return { "orders": user_orders }
	else:
		msg = "Schedule doesn't exist"

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
			"numMakings": numMakings
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
			"table": schedule.table
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
	note = content['note']

	user = User.query.filter_by(id=userid).first()
	msg = ""

	if user != None:
		product = Product.query.filter_by(id=productid).first()

		if product != None:
			for option in options:
				if option['type'] == 'size' and option['selected'] == '':
					msg = "Please choose a size"

			if msg == "":
				schedule = Schedule.query.filter_by(id=scheduleid).first()

				if schedule != None:
					orders = json.loads(schedule.orders)

					groups = orders['groups']

					if len(groups) > 0:
						first_group = groups[0]

						if first_group['status'] == "making":
							groups.insert(0, { "id": getRanStr(), "status": "ordering" })

							first_group = groups[0]
					else:
						groups.insert(0, { "id": getRanStr(), "status": "ordering" })

						first_group = groups[0]

					if userid in first_group:
						first_group[userid].append({ "id": getRanStr(), "productid": productid, "options": options, "quantity": quantity, "note": note, "callfor": callfor })
					else:
						first_group[userid] = [{ "id": getRanStr(), "productid": productid, "options": options, "quantity": quantity, "note": note, "callfor": callfor }]

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

@app.route("/see_orders/<id>")
def see_orders(id):
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
				if orderer != "status":
					ordererInfo = User.query.filter_by(id=orderer).first()
					orders = rounds[orderer]

					for order in orders:
						product = Product.query.filter_by(id=order['productid']).first()
						callfor = order['callfor']

						orderers = []
						row = []

						for k in range(len(callfor)):
							info = callfor[k]

							orderer = User.query.filter_by(id=info).first()

							row.append({
								"key": "orderer-" + str(each_callfor_num),
								"id": orderer.id,
								"username": orderer.username,
								"profile": orderer.profile
							})
							each_callfor_num += 1

							if len(row) == 4 or (len(callfor) - 1 == k and len(row) > 0):
								if len(callfor) - 1 == k and len(row) > 0:
									key = orderer.id + 1

									leftover = 4 - len(row)

									for k in range(leftover):
										row.append({ "key": "orderer-" + str(key) })
										key += 1

								orderers.append({ "key": "orderer-row-" + str(len(orderers)), "row": row })
								row = []

						each_orders.append({
							"id": order['id'],
							"image": product.image,
							"key": "meal-" + order['id'],
							"name": product.name,
							"note": order['note'],
							"options": order['options'],
							"quantity": order['quantity'],
							"price": float(product.price),
							"orderers": orderers,
							"numorderers": each_callfor_num
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

@app.route("/get_orders/<id>")
def get_orders(id):
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

							each_orders.append({
								"id": order['id'],
								"image": product.image,
								"key": "meal-" + order['id'],
								"name": product.name,
								"note": order['note'],
								"options": order['options'],
								"quantity": order['quantity'],
								"price": float(product.price)
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

	if schedule != None:
		orders = json.loads(schedule.orders)

		groups = orders['groups']

		first_group = groups[0]

		if first_group['status'] == "ordering":
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

	return { "errormsg": msg }

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
				if k != "status":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							product = Product.query.filter_by(id=orderer['productid']).first()

							options = orderer['options']

							for k in range(len(options)):
								option = options[k]

								if option['type'] == 'size':
									option['options'] = [
										{ "key": "info-opt-0", "header": "small" },
										{ "key": "info-opt-1", "header": "medium" },
										{ "key": "info-opt-2", "header": "large" },
										{ "key": "info-opt-3", "header": "extra large" }
									]

								option['key'] = "info-" + str(k)

							info = {
								"name": product.name,
								"info": product.info,
								"image": product.image,
								"quantity": orderer['quantity'],
								"options": options,
								"note": orderer['note'],
								"price": float(product.price)
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
	note = content['note']

	schedule = Schedule.query.filter_by(id=scheduleid).first()

	if schedule != None:
		orders = json.loads(schedule.orders)

		groups = orders['groups']

		for rounds in groups:
			for k in rounds:
				if k != "status":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							orderer['options'] = options
							orderer['quantity'] = quantity
							orderer['note'] = note

		orders['groups'] = groups
		schedule.orders = json.dumps(orders)

		db.session.commit()

		return { "msg": "order updated" }
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
		diners = json.loads(schedule.customers)

		diners += newdiners

		schedule.customers = json.dumps(diners)

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
				if k != "status":
					for orderer in rounds[k]:
						if orderer['id'] == orderid:
							callfor = orderer['callfor']
							product = Product.query.filter_by(id=orderer['productid']).first()
							searcheddiners = []
							row = []
							numsearcheddiners = 0

							for k in range(len(callfor)):
								info = callfor[k]

								user = User.query.filter_by(id=info).first()

								row.append({
									"key": "selected-friend-" + str(user.id),
									"id": user.id,
									"profile": user.profile,
									"username": user.username
								})
								numsearcheddiners += 1

								if len(row) == 4 or (len(callfor) - 1 == k and len(row) > 0):
									if len(callfor) - 1 == k and len(row) > 0:
										key = user.id + 1

										leftover = 4 - len(row)

										for k in range(leftover):
											row.append({ "key": "selected-friend-" + str(key) })
											key += 1

									searcheddiners.append({ "key": "selected-friend-row-" + str(len(searcheddiners)), "row": row })

							options = orderer['options']

							for k in range(len(options)):
								options[k]['key'] = 'opt-' + str(k)

							orderingItem = {
								"name": product.name,
								"image": product.image,
								"options": options,
								"quantity": orderer['quantity'],
								"cost": float(orderer['quantity'] * float(product.price))
							}

							return { "searchedDiners": searcheddiners, "numSearchedDiners": numsearcheddiners, "orderingItem": orderingItem }
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
				if k != "status":
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
