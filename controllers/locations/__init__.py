from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, os, math, json, stripe, socket
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
	customers = db.Column(db.Text)
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
def welcome_locations():
	return { "msg": "welcome to locations of easygo" }

@app.route("/setup_location", methods=["POST"])
def setup_location():
	name = request.form['storeName']
	phonenumber = request.form['phonenumber']
	addressOne = request.form['addressOne']
	addressTwo = request.form['addressTwo']
	city = request.form['city']
	province = request.form['province']
	postalcode = request.form['postalcode']
	logo = request.files['logo']
	longitude = request.form['longitude']
	latitude = request.form['latitude']
	ownerid = request.form['ownerid']
	time = request.form['time']
	ipAddress = request.form['ipAddress']

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		location = Location.query.filter_by(phonenumber=phonenumber).first()

		if location == None:
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

			location = Location(
				name, addressOne, addressTwo, 
				city, province, postalcode, phonenumber, logo.filename,
				longitude, latitude, '["' + str(ownerid) + '"]',
				'', '', connectedaccount.id
			)
			db.session.add(location)
			db.session.commit()

			owner.locationId = location.id

			db.session.commit()

			logo.save(os.path.join('static', logo.filename))

		if os.path.isfile('static/' + logo.filename):
			return { "msg": "location setup", "id": location.id }
		else:
			logo.save(os.path.join('static', logo.filename))

			msg = "Logo cannot be saved"
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg }

@app.route("/update_location", methods=["POST"])
def update_location():
	name = request.form['storeName']
	phonenumber = request.form['phonenumber']
	addressOne = request.form['addressOne']
	addressTwo = request.form['addressTwo']
	city = request.form['city']
	province = request.form['province']
	postalcode = request.form['postalcode']
	longitude = request.form['longitude']
	latitude = request.form['latitude']
	ownerid = request.form['ownerid']
	time = request.form['time']
	ipAddress = request.form['ipAddress']

	filepath = request.files.get('logo', False)
	fileexist = False if filepath == False else True

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		locationid = owner.locationId

		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			accountid = location.accountId

			if fileexist == True:
				logo = request.files['logo']

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

			if fileexist == True:
				logo = request.files['logo']
				oldlogo = location.logo

				if logo.filename != oldlogo:
					location.logo = logo.filename

					if os.path.exists("static/" + oldlogo):
						os.remove("static/" + oldlogo)

					logo.save(os.path.join('static', logo.filename))

			db.session.commit()

			return { "msg": "location updated", "id": location.id }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg }

@app.route("/fetch_num_requests/<id>")
def fetch_num_requests(id):
	numRequests = query("select count(*) as num from schedule where locationId = " + str(id) + " and status = 'requested'", True)[0]["num"]

	return { "numRequests": numRequests }

@app.route("/fetch_num_appointments/<id>")
def fetch_num_appointments(id):
	numAppointments = query("select count(*) as num from schedule where locationId = " + str(id) + " and status = 'accepted'", True)[0]["num"]

	return { "numAppointments": numAppointments }

@app.route("/fetch_num_reservations/<id>")
def fetch_num_reservations(id):
	numReservations = query("select count(*) as num from schedule where locationId = " + str(id) + " and status = 'accepted' and not customers = '[]'", True)[0]["num"]

	return { "numReservations": numReservations }

@app.route("/set_type", methods=["POST"])
def set_type():
	content = request.get_json()

	ownerid = content['ownerid']
	locationid = content['locationid']
	type = content['type']

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			location.type = type

			db.session.commit()

			return { "msg": "" }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg }

@app.route("/set_hours", methods=["POST"])
def set_hours():
	content = request.get_json()

	ownerid = content['ownerid']
	locationid = content['locationid']
	hours = content['hours']

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			location.hours = json.dumps(hours)

			db.session.commit()

			return { "msg": "hours updated" }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg }

@app.route("/get_locations", methods=["POST"])
def get_locations():
	content = request.get_json()

	userid = content['userid']
	longitude = float(content['longitude'])
	latitude = float(content['latitude'])
	name = content['locationName']
	day = content['day']

	if longitude != None and latitude != None:
		longitude = float(longitude)
		latitude = float(latitude)

		user = User.query.filter_by(id=userid).first()

		if user != None:
			locations = [
				{ "key": "0", "service": "restaurant", "header": "Restaurant(s)", "locations": [], "loading": True, "index": 0, "max": 0 },
				{ "key": "1", "service": "hair", "header": "Hair Salon(s)", "locations": [], "loading": True, "index": 0, "max": 0 },
				{ "key": "2", "service": "nail", "header": "Nail Salon(s)", "locations": [], "loading": True, "index": 0, "max": 0 }
			]
			orderQuery = "and name like '%" + name + "%' " if name != "" else ""
			orderQuery += "order by ST_Distance_Sphere(point(" + str(longitude) + ", " + str(latitude) + "), point(longitude, latitude))"

			point1 = (longitude, latitude)

			# get restaurants
			sql = "select * from location where type = 'restaurant' " + orderQuery + " limit 0, 10"
			maxsql = "select count(*) as num from location where type = 'restaurant' " + orderQuery
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
			sql = "select * from location where type = 'hair' " + orderQuery + " limit 0, 10"
			maxsql = "select count(*) as num from location where type = 'hair' " + orderQuery
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
			sql = "select * from location where type = 'nail' " + orderQuery + " limit 0, 10"
			maxsql = "select count(*) as num from location where type = 'nail' " + orderQuery
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
			msg = "User doesn't exist"
	else:
		msg = "Coordinates is unknown"

	return { "errormsg": msg }

@app.route("/get_more_locations", methods=["POST"])
def get_more_locations():
	content = request.get_json()

	userid = content['userid']
	longitude = float(content['longitude'])
	latitude = float(content['latitude'])
	name = content['locationName']
	type = content['type']
	index = str(content['index'])
	day = content['day']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		locations = []
		orderQuery = "and name like '%" + name + "%' " if name != "" else ""
		orderQuery += "order by st_distance_sphere(point(" + str(longitude) + ", " + str(latitude) + "), point(longitude, latitude))"
		lon1 = longitude
		lat1 = latitude

		# get locations
		sql = "select * from location where type = '" + type + "' " + orderQuery + " limit " + index + ", 10"
		maxsql = "select count(*) as num from location where type = '" + type + "' " + orderQuery
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

	locationid = content['locationid']

	if content['longitude'] != None:
		longitude = float(content['longitude'])
		latitude = float(content['latitude'])
	else:
		longitude = content['longitude']
		latitude = content['latitude']

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		num_menus = Menu.query.filter_by(locationId=locationid, parentMenuId="").count()
		num_services = Service.query.filter_by(locationId=locationid, menuId="").count()
		num_products = Product.query.filter_by(locationId=locationid, menuId="").count()

		msg = ""
		if num_menus > 0:
			msg = "menus"
		elif num_services > 0:
			msg = "services"
		elif num_products > 0:
			msg = "products"

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
			{ "key": "0", "header": "Sunday", "opentime": { "hour": "00", "minute": "00", "period": "AM" }, "closetime": { "hour": "00", "minute": "00", "period": "AM" }},
			{ "key": "1", "header": "Monday", "opentime": { "hour": "00", "minute": "00", "period": "AM" }, "closetime": { "hour": "00", "minute": "00", "period": "AM" }},
			{ "key": "2", "header": "Tuesday", "opentime": { "hour": "00", "minute": "00", "period": "AM" }, "closetime": { "hour": "00", "minute": "00", "period": "AM" }},
			{ "key": "3", "header": "Wednesday", "opentime": { "hour": "00", "minute": "00", "period": "AM" }, "closetime": { "hour": "00", "minute": "00", "period": "AM" }},
			{ "key": "4", "header": "Thursday", "opentime": { "hour": "00", "minute": "00", "period": "AM" }, "closetime": { "hour": "00", "minute": "00", "period": "AM" }},
			{ "key": "5", "header": "Friday", "opentime": { "hour": "00", "minute": "00", "period": "AM" }, "closetime": { "hour": "00", "minute": "00", "period": "AM" }},
			{ "key": "6", "header": "Saturday", "opentime": { "hour": "00", "minute": "00", "period": "AM" }, "closetime": { "hour": "00", "minute": "00", "period": "AM" }}
		]

		if location.hours != '':
			data = json.loads(location.hours)
			day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

			for k, info in enumerate(hours):
				info["opentime"]["hour"] = data[day[k][:3]]["opentime"]["hour"]
				info["opentime"]["minute"] = data[day[k][:3]]["opentime"]["minute"]
				info["opentime"]["period"] = data[day[k][:3]]["opentime"]["period"]

				info["closetime"]["hour"] = data[day[k][:3]]["closetime"]["hour"]
				info["closetime"]["minute"] = data[day[k][:3]]["closetime"]["minute"]
				info["closetime"]["period"] = data[day[k][:3]]["closetime"]["period"]

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
			"hours": hours
		}

		return { "locationInfo": info, "msg": msg }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }

@app.route("/make_reservation", methods=["POST"])
def make_reservation():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	time = content['time']
	customers = json.dumps(content['diners'])
	note = content['note']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			requested_reservation = Schedule.query.filter_by(
				locationId=locationid,
				menuId="",
				serviceId="",
				userId=userid,
				status='requested'
			).first()
			rebooked_reservation = Schedule.query.filter_by(
				locationId=locationid,
				menuId="",
				serviceId="",
				userId=userid,
				status='rebook'
			).first()

			if requested_reservation == None and rebooked_reservation == None: # nothing created yet
				schedule = Schedule(userid, locationid, "", "", time, "requested", '', '', location.type, customers, note, '{"groups":[],"donedining":false}', '')

				db.session.add(schedule)
				db.session.commit()

				msg = "reservation added"

				return { "msg": msg }
			else:
				if rebooked_reservation != None:
					rebooked_reservation.status = 'requested'
					rebooked_reservation.time = time
					rebooked_reservation.customers = customers

					db.session.commit()

					msg = "reservation re-requested"

					return { "msg": msg }
				else:
					msg = "reservation already requested"
		else:
			msg = "Location doesn't exist"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_info", methods=["POST"])
def get_info():
	content = request.get_json()

	locationid = content['locationid']
	menuid = content['menuid']

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		addressOne = location.addressOne
		addressTwo = location.addressTwo
		city = location.city
		province = location.province
		postalcode = location.postalcode

		storeName = location.name
		storeAddress = addressOne + " " + addressTwo + ", " + city + ", " + province + " " + postalcode
		storeLogo = location.logo
		locationType = 'salon' if location.type == 'nail' or location.type == 'hair' else 'restaurant'

		num_menus = Menu.query.filter_by(locationId=locationid, parentMenuId=menuid).count()
		num_services = Service.query.filter_by(locationId=locationid, menuId=menuid).count()
		num_products = Product.query.filter_by(locationId=locationid, menuId=menuid).count()

		menu = Menu.query.filter_by(id=menuid).first()
		menuName = ""
		menuInfo = ""

		if menu != None:
			menuName = menu.name
			menuInfo = menu.info

		if num_menus > 0:
			return { "msg": "menus", "menuName": menuName, "menuInfo": menuInfo, "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo, "locationType": locationType }
		elif num_services > 0:
			return { "msg": "services", "menuName": menuName, "menuInfo": menuInfo, "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo, "locationType": locationType }
		elif num_products > 0:
			return { "msg": "products", "menuName": menuName, "menuInfo": menuInfo, "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo, "locationType": locationType }
		else:
			return { "msg": "", "menuName": menuName, "menuInfo": menuInfo, "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo, "locationType": locationType }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }

@app.route("/get_hours", methods=["POST"])
def get_hours():
	content = request.get_json()

	locationid = content['locationid']
	day = content['day']

	scheduled = Schedule.query.filter_by(locationId=locationid).all()
	location = Location.query.filter_by(id=locationid).first()
	times = []

	if location != None:
		hours = json.loads(location.hours)

		openTime = hours[day]["opentime"]
		closeTime = hours[day]["closetime"]

		for data in scheduled:
			times.append(int(data.time))

		return { "openTime": openTime, "closeTime": closeTime, "scheduled": times }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }
