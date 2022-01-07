from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, json, os
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from haversine import haversine
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

@app.route("/welcome_locations", methods=["GET"])
def welcome_locations():
	datas = Location.query.all()
	locations = []

	for data in datas:
		locations.append(data.id)

	return { "msg": "welcome to locations of easygo", "locations": locations }

@app.route("/setup_location", methods=["POST"])
def setup_location():
	name = request.form['storeName']
	phonenumber = request.form['phonenumber']
	addressOne = request.form['addressOne']
	addressTwo = request.form['addressTwo']
	city = request.form['city']
	province = request.form['province']
	postalcode = request.form['postalcode']
	hours = request.form['hours']
	type = request.form['type']
	logopath = request.files.get('logo', False)
	logoexist = False if logopath == False else True
	longitude = request.form['longitude']
	latitude = request.form['latitude']
	ownerid = request.form['ownerid']
	time = request.form['time']
	ipAddress = request.form['ipAddress']
	permission = request.form['permission']
	trialtime = int(request.form['trialtime'])

	owner = Owner.query.filter_by(id=ownerid).first()
	errormsg = ""
	status = ""

	if owner != None:
		location = Location.query.filter_by(phonenumber=phonenumber).first()

		if location == None:
			logoname = ""
			if logoexist == True:
				logo = request.files['logo']
				logoname = logo.filename

				logo.save(os.path.join('static', logoname))
			else:
				logoname = ""

			if errormsg == "":
				# create a connected account
				connectedaccount = stripe.Account.create(
					type="custom",
					country="CA",
					business_type="company",
					business_profile={
						"name": name
					},
					company={
						"address": {
							"city": city,
							"line1": addressOne,
							"line2": addressTwo,
							"postal_code": postalcode,
							"state": province 
						},
						"name": name,
						"phone": phonenumber,
					},
					capabilities={
						"transfers": {"requested": True},
						"card_payments": {"requested": True}
					},
					tos_acceptance={
						"date": time,
						"ip": str(ipAddress)
					}
				)
				stripe.Account.create_person(
					connectedaccount.id,
					first_name=name,
					last_name=" ",
					address={
						"city": city,
						"line1": addressOne,
						"line2": addressTwo,
						"postal_code": postalcode,
						"state": province 
					},
					dob={
						"day": 30,
						"month": 7,
						"year": 1996
					},
					relationship={
						"representative": True
					}
				)

				accountid = connectedaccount.id

				locationInfo = json.dumps({"accountId": str(accountid), "listed": False, "cut": 100, "trialstart": trialtime })
				location = Location(
					name, addressOne, addressTwo, 
					city, province, postalcode, phonenumber, logoname,
					longitude, latitude, '["' + str(ownerid) + '"]',
					type, hours, locationInfo
				)
				db.session.add(location)
				db.session.commit()

				ownerInfo = json.loads(owner.info)
				ownerInfo["locationId"] = str(location.id)
				owner.info = json.dumps(ownerInfo)
				owner.hours = json.dumps({"notrequired": True}) if type == "restaurant" else "{}"

				db.session.commit()

				return { "msg": "location setup", "id": location.id }
		else:
			errormsg = "Location phone number already taken"
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_location", methods=["POST"])
def update_location():
	name = request.form['storeName']
	phonenumber = request.form['phonenumber']
	addressOne = request.form['addressOne']
	addressTwo = request.form['addressTwo']
	city = request.form['city']
	province = request.form['province']
	postalcode = request.form['postalcode']
	logopath = request.files.get('logo', False)
	logoexist = False if logopath == False else True
	longitude = request.form['longitude']
	latitude = request.form['latitude']
	ownerid = request.form['ownerid']
	time = request.form['time']
	ipAddress = request.form['ipAddress']
	permission = request.form['permission']

	owner = Owner.query.filter_by(id=ownerid).first()
	errormsg = ""
	status = ""

	if owner != None:
		ownerInfo = json.loads(owner.info)
		locationid = ownerInfo["locationId"]

		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			locationInfo = json.loads(location.info)
			accountid = locationInfo["accountId"]

			person = stripe.Account.list_persons(accountid)
			personid = person.data[0].id

			stripe.Account.modify(
				accountid,
				business_profile={
					"name": name
				},
				company={
					"address": {
						"city": city,
						"line1": addressOne,
						"line2": addressTwo,
						"postal_code": postalcode,
						"state": province 
					},
					"name": name,
					"phone": phonenumber,
				},
				tos_acceptance={
					"date": time,
					"ip": str(ipAddress)
				}
			)
			stripe.Account.modify_person(
				accountid,
				personid,
				first_name=name,
				address={
					"city": city,
					"line1": addressOne,
					"line2": addressTwo,
					"postal_code": postalcode,
					"state": province 
				}
			)

			location.name = name
			location.addressOne = addressOne
			location.addressTwo = addressTwo
			location.city = city
			location.province = province
			location.postalcode = postalcode
			location.phonenumber = phonenumber
			location.longitude = longitude
			location.latitude = latitude

			if logoexist == True:
				logo = request.files['logo']
				newlogoname = logo.filename
				oldlogo = location.logo

				if newlogoname != oldlogo:
					if oldlogo != "" and oldlogo != None and os.path.exists("static/" + oldlogo):
						os.remove("static/" + oldlogo)

					logo.save(os.path.join('static', newlogoname))
					location.logo = newlogoname

			db.session.commit()

			return { "msg": "location updated", "id": location.id }
		else:
			errormsg = "Location doesn't exist"
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/fetch_num_requests/<id>")
def fetch_num_requests(id):
	numRequests = query("select count(*) as num from schedule where locationId = " + str(id) + " and (status = 'requested' or status = 'change' or status = 'accepted')", True)[0]["num"]

	return { "numRequests": numRequests }

@app.route("/fetch_num_appointments/<id>")
def fetch_num_appointments(id):
	numAppointments = query("select count(*) as num from schedule where locationId = " + str(id) + " and status = 'confirmed'", True)[0]["num"]

	return { "numAppointments": numAppointments }

@app.route("/fetch_num_cartorderers/<id>")
def fetch_num_cartorderers(id):
	numCartorderers = query("select count(*) as num from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'ready') group by adder, orderNumber", True)

	if len(numCartorderers) > 0:
		numCartorderers = len(numCartorderers)
	else:
		numCartorderers = 0

	return { "numCartorderers": numCartorderers }

@app.route("/fetch_num_reservations/<id>")
def fetch_num_reservations(id):
	numReservations = Schedule.query.filter_by(locationId=id, status='confirmed').count()

	return { "numReservations": numReservations }

@app.route("/set_type", methods=["POST"])
def set_type():
	content = request.get_json()

	ownerid = content['ownerid']
	locationid = content['locationid']
	type = content['type']

	owner = Owner.query.filter_by(id=ownerid).first()
	errormsg = ""
	status = ""

	if owner != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			location.type = type

			db.session.commit()

			return { "msg": "" }
		else:
			errormsg = "Location doesn't exist"
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/set_hours", methods=["POST"])
def set_hours():
	content = request.get_json()

	locationid = content['locationid']
	hours = content['hours']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		location.hours = json.dumps(hours)

		db.session.commit()

		return { "msg": "hours updated" }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_locations", methods=["POST"])
def get_locations():
	content = request.get_json()

	longitude = content['longitude']
	latitude = content['latitude']
	name = content['locationName']
	day = content['day']
	errormsg = ""
	status = ""

	if longitude != None and latitude != None:
		longitude = float(longitude)
		latitude = float(latitude)

		locations = [
			{ "key": "0", "service": "restaurant", "header": "Restaurant(s)", "locations": [], "loading": True, "index": 0, "max": 0 },
			{ "key": "1", "service": "hair", "header": "Hair Salon(s)", "locations": [], "loading": True, "index": 0, "max": 0 },
			{ "key": "2", "service": "nail", "header": "Nail Salon(s)", "locations": [], "loading": True, "index": 0, "max": 0 }
		]
		orderQuery = "and name like '%" + name + "%' " if name != "" else ""
		orderQuery += "order by ST_Distance_Sphere(point(" + str(longitude) + ", " + str(latitude) + "), point(longitude, latitude))"

		point1 = (longitude, latitude)

		# get restaurants
		sql = "select * from location where type = 'restaurant' and info like '%\"listed\": true%' " + orderQuery + " limit 0, 10"
		maxsql = "select count(*) as num from location where type = 'restaurant' and info like '%\"listed\": true%' " + orderQuery
		datas = query(sql, True)
		maxdatas = query(maxsql, True)[0]["num"]
		for data in datas:
			lon2 = float(data['longitude'])
			lat2 = float(data['latitude'])

			point2 = (lon2, lat2)
			distance = haversine(point1, point2)

			if distance < 1:
				distance *= 1000
				distance = str(round(distance, 1)) + " m"
			else:
				distance = str(round(distance, 1)) + " km"

			hours = json.loads(data['hours'])

			locations[0]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": data['logo'],
				"nav": "restaurantprofile",
				"name": data['name'],
				"distance": distance,
				"opentime": hours[day]["opentime"],
				"closetime": hours[day]["closetime"]
			})

		locations[0]["index"] += len(datas)

		# get hair salons
		sql = "select * from location where type = 'hair' and info like '%\"listed\": true%' " + orderQuery + " limit 0, 10"
		maxsql = "select count(*) as num from location where type = 'hair' and info like '%\"listed\": true%' " + orderQuery
		datas = query(sql, True)
		maxdatas = query(maxsql, True)[0]["num"]
		for data in datas:
			lon2 = float(data['longitude'])
			lat2 = float(data['latitude'])

			point2 = (lon2, lat2)
			distance = haversine(point1, point2)

			if distance < 1:
				distance *= 1000
				distance = str(round(distance, 1)) + " m"
			else:
				distance = str(round(distance, 1)) + " km"

			hours = json.loads(data['hours'])

			locations[1]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": data['logo'],
				"nav": "salonprofile",
				"name": data['name'],
				"distance": distance,
				"opentime": hours[day]["opentime"],
				"closetime": hours[day]["closetime"]
			})

		locations[1]["index"] += len(datas)

		# get nail salons
		sql = "select * from location where type = 'nail' and info like '%\"listed\": true%' " + orderQuery + " limit 0, 10"
		maxsql = "select count(*) as num from location where type = 'nail' and info like '%\"listed\": true%' " + orderQuery
		datas = query(sql, True)
		maxdatas = query(maxsql, True)[0]["num"]
		for data in datas:
			lon2 = float(data['longitude'])
			lat2 = float(data['latitude'])

			point2 = (lon2, lat2)
			distance = haversine(point1, point2)

			if distance < 1:
				distance *= 1000
				distance = str(round(distance, 1)) + " m"
			else:
				distance = str(round(distance, 1)) + " km"

			hours = json.loads(data['hours'])

			locations[2]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": data['logo'],
				"nav": "salonprofile",
				"name": data['name'],
				"distance": distance,
				"opentime": hours[day]["opentime"],
				"closetime": hours[day]["closetime"]
			})

		locations[2]["index"] += len(datas)
		
		return { "locations": locations }
	else:
		errormsg = "Coordinates is unknown"
		status = "unknowncoords"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_more_locations", methods=["POST"])
def get_more_locations():
	content = request.get_json()

	longitude = float(content['longitude'])
	latitude = float(content['latitude'])
	name = content['locationName']
	type = content['type']
	index = str(content['index'])
	day = content['day']

	locations = []
	orderQuery = "and name like '%" + name + "%' " if name != "" else ""
	orderQuery += "order by st_distance_sphere(point(" + str(longitude) + ", " + str(latitude) + "), point(longitude, latitude))"
	lon1 = longitude
	lat1 = latitude

	# get locations
	sql = "select * from location where type = '" + type + "' and info like '%\"listed\": true%' " + orderQuery + " limit " + index + ", 10"
	maxsql = "select count(*) as num from location where type = '" + type + "' and info like '%\"listed\": true%' " + orderQuery
	datas = query(sql, True)
	maxdatas = query(maxsql, True)[0]["num"]
	for data in datas:
		lon2 = float(data['longitude'])
		lat2 = float(data['latitude'])

		point1 = (lon1, lat1)
		point2 = (lon2, lat2)
		distance = haversine(point1, point2)

		if distance < 1:
			distance *= 1000
			distance = str(round(distance, 1)) + " m"
		else:
			distance = str(round(distance, 1)) + " km"

		hours = json.loads(data['hours'])

		locations.append({
			"key": "l-" + str(data['id']),
			"id": data['id'],
			"logo": data['logo'],
			"nav": ("restaurant" if type == "restaurant" else "salon") + "profile",
			"name": data['name'],
			"distance": distance,
			"opentime": hours[day]["opentime"],
			"closetime": hours[day]["closetime"]
		})

	return { "newlocations": locations, "index": len(datas), "max": maxdatas }
	
@app.route("/get_location_profile", methods=["POST"])
def get_location_profile():
	content = request.get_json()

	locationid = str(content['locationid'])

	if 'longitude' in content:
		if content['longitude'] != None:
			longitude = float(content['longitude'])
			latitude = float(content['latitude'])
		else:
			longitude = content['longitude']
			latitude = content['latitude']
	else:
		longitude = None
		latitude = None

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)

		if longitude != None:
			point1 = (longitude, latitude)
			point2 = (float(location.longitude), float(location.latitude))
			distance = haversine(point1, point2)

			if distance < 1:
				distance *= 1000
				distance = str(round(distance, 1)) + " m away"
			else:
				distance = str(round(distance, 1)) + " km away"
		else:
			distance = None

		hours = [
			{ "key": "0", "header": "Sunday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "close": False },
			{ "key": "1", "header": "Monday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "close": False },
			{ "key": "2", "header": "Tuesday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "close": False },
			{ "key": "3", "header": "Wednesday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "close": False },
			{ "key": "4", "header": "Thursday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "close": False },
			{ "key": "5", "header": "Friday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "close": False },
			{ "key": "6", "header": "Saturday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "close": False }
		]

		if location.hours != '':
			data = json.loads(location.hours)
			day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

			for k, info in enumerate(hours):
				openhour = int(data[day[k][:3]]["opentime"]["hour"])
				closehour = int(data[day[k][:3]]["closetime"]["hour"])
				close = data[day[k][:3]]["close"]

				openperiod = "PM" if openhour > 12 else "AM"
				openhour = int(openhour)

				if openhour == 0:
					openhour = "12"
				elif openhour < 10:
					openhour = "0" + str(openhour)
				elif openhour > 12:
					openhour -= 12
					openhour = str(openhour)

				closeperiod = "PM" if closehour > 12 else "AM"
				closehour = int(closehour)

				if closehour == 0:
					closehour = "12"
				elif closehour < 10:
					closehour = "0" + str(closehour)
				elif closehour > 12:
					closehour -= 12
					closehour = str(closehour)

				info["opentime"]["hour"] = openhour
				info["opentime"]["minute"] = data[day[k][:3]]["opentime"]["minute"]
				info["opentime"]["period"] = openperiod

				info["closetime"]["hour"] = closehour
				info["closetime"]["minute"] = data[day[k][:3]]["closetime"]["minute"]
				info["closetime"]["period"] = closeperiod
				info["close"] = close

				hours[k] = info

		info = {
			"id": location.id,
			"name": location.name,
			"addressOne": location.addressOne,
			"addressTwo": location.addressTwo,
			"city": location.city,
			"province": location.province,
			"postalcode": location.postalcode,
			"phonenumber": location.phonenumber,
			"distance": distance,
			"logo": location.logo,
			"longitude": float(location.longitude),
			"latitude": float(location.latitude),
			"hours": hours,
			"type": "restaurant" if location.type == "restaurant" else "salon",
			"listed": locationInfo["listed"],
			"fullAddress": location.addressOne + ", " + (location.addressOne if location.addressTwo != "" else "") + location.city + ", " + location.province + ", " + location.postalcode
		}

		return { "info": info }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/make_reservation", methods=["POST"])
def make_reservation():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	scheduleid = content['scheduleid']
	oldtime = content['oldtime']
	time = content['time']
	customers = content['diners']
	note = content['note']

	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		customerid = info['customerId']

		customer = stripe.Customer.list_sources(
			customerid,
			object="card",
			limit=1
		)
		cards = len(customer.data)

		if cards > 0:
			location = Location.query.filter_by(id=locationid).first()

			if location != None:
				info = json.loads(location.info)

				receivingUsers = []
				receivingLocations = []

				owners = query("select id from owner where info like '%\"locationId\": \"" + str(locationid) + "\"%'", True)
				
				for owner in owners:
					receivingLocations.append("owner" + str(owner["id"]))

				if scheduleid != None: # existing schedule
					sql = "select * from schedule where locationId = " + str(locationid)
					sql += " and (userId = " + str(userid) + " or customers like '%\"userid\": \"" + str(userid) + "\"%')"
					data = query(sql, True)

					if data != None:
						schedule = data[0]

						customers = json.loads(schedule["customers"])

						for customer in customers:
							receivingUsers.append("user" + str(customer["userid"]))

						if schedule["status"] == 'accepted': # reschedule
							if oldtime == 0: # get old time
								return {
									"msg": "reservation already made",
									"status": "existed",
									"oldtime": int(schedule["time"]),
									"note": schedule["note"]
								}
							else:
								sql = "update schedule set status = 'change', nextTime = '" + str(time) + "', "
								sql += "note = '" + note + "', userId = " + str(userid) + " where id = " + str(schedule["id"])

								query(sql, False)

								return { "msg": "reservation updated", "status": "updated", "receivingUsers": receivingUsers, "receivingLocations": receivingLocations }
						else:
							sql = "update schedule set status = 'requested', time = '" + str(time) + "', nextTime = '', "
							sql += "note = '" + note + "', userId = " + str(userid) + " where id = " + str(schedule["id"])

							query(sql, False)

							return { "msg": "reservation re-requested", "status": "requested", "receivingUsers": receivingUsers, "receivingLocations": receivingLocations }
					else:
						errormsg = "Schedule doesn't exist"
				else: # new schedule
					for customer in customers:
						receivingUsers.append("user" + str(customer["userid"]))

					charges = { str(str(userid)): {
						"charge": 0.00,
						"allowpayment": False,
						"paid": False
					}}

					for customer in customers:
						charges[customer["userid"]] = {
							"charge": 0.00,
							"allowpayment": False,
							"paid": False
						}

					orders = json.dumps({"groups": [], "charges": charges })
					info = json.dumps({"donedining": False, "dinersseated": False, "cut": int(info["cut"]) })

					schedule = Schedule(userid, -1, locationid, "", "", time, "requested", '', '', location.type, json.dumps(customers), note, orders, '', info)

					db.session.add(schedule)
					db.session.commit()

					return { "msg": "reservation added", "status": "new", "receivingUsers": receivingUsers, "receivingLocations": receivingLocations }
			else:
				errormsg = "Location doesn't exist"
		else:
			errormsg = "A payment method is required"
			status = "cardrequired"
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/change_location_state/<id>")
def change_location_state(id):
	location = Location.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		locationListed = locationInfo["listed"]
		numproducts = Product.query.filter_by(locationId=id).count()
		numservices = Service.query.filter_by(locationId=id).count()

		accountid = locationInfo["accountId"]

		account = stripe.Account.list_external_accounts(accountid, object="bank_account", limit=1)
		bankaccounts = len(account.data)

		if (locationListed == False and ((numproducts > 0 or numservices > 0) and bankaccounts == 1)) or (locationListed == True):
			locationInfo["listed"] = False if locationInfo["listed"] == True else True
			location.info = json.dumps(locationInfo)

			db.session.commit()

			return { "msg": "Change location state", "listed": locationInfo["listed"] }
		else:
			if locationListed == False:
				if numproducts == 0 and numservices == 0:
					errormsg = "Menu setup required"
					status = "menusetuprequired"
				else:
					errormsg = "Bank account required"
					status = "bankaccountrequired"
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/set_location_public/<id>")
def set_location_public(id):
	owner = Owner.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if owner != None:
		info = json.loads(owner.info)

		locationId = info["locationId"]
		location = Location.query.filter_by(id=locationId).first()

		if location != None:
			info = json.loads(location.info)

			info["listed"] = True

			location.info = json.dumps(info)

			db.session.commit()

			return { "msg": "Location listed publicly" }
		else:
			errormsg = "Location doesn't exist"
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_hours", methods=["POST"])
def get_hours():
	content = request.get_json()

	locationid = content['locationid']
	day = content['day']

	scheduled = Schedule.query.filter_by(locationId=locationid).all()
	location = Location.query.filter_by(id=locationid).first()
	times = []
	errormsg = ""
	status = ""

	if location != None:
		hours = json.loads(location.hours)

		openTime = hours[day]["opentime"]
		closeTime = hours[day]["closetime"]

		for data in scheduled:
			time = int(data.nextTime) if data.nextTime != "" else int(data.time)
			times.append(time)

		return { "openTime": openTime, "closeTime": closeTime, "scheduled": times }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
