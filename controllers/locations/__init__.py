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

	def __init__(self, cellnumber, password, username, profile):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.profile = profile

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
	name = db.Column(db.String(20))
	addressOne = db.Column(db.String(30))
	addressTwo = db.Column(db.String(20))
	city = db.Column(db.String(20))
	province = db.Column(db.String(20))
	postalcode = db.Column(db.String(7))
	phonenumber = db.Column(db.String(10), unique=True)
	logo = db.Column(db.String(20))
	longitude = db.Column(db.String(15))
	latitude = db.Column(db.String(15))
	owners = db.Column(db.Text)
	type = db.Column(db.String(20))
	hours = db.Column(db.Text)

	def __init__(self, name, addressOne, addressTwo, city, province, postalcode, phonenumber, logo, longitude, latitude, owners, type, hours):
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

class Appointment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	serviceId = db.Column(db.Text)
	time = db.Column(db.String(15))
	status = db.Column(db.String(10))
	cancelReason = db.Column(db.String(200))
	nextTime = db.Column(db.String(15))

	def __init__(self, userId, locationId, menuId, serviceId, time, status, cancelReason, nextTime):
		self.userId = userId
		self.locationId = locationId
		self.menuId = menuId
		self.serviceId = serviceId
		self.time = time
		self.status = status
		self.cancelReason = cancelReason
		self.nextTime = nextTime

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

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		location = Location(
			name,
			addressOne, addressTwo, 
			city, province, postalcode, phonenumber, logo.filename,
			longitude, latitude, '["' + str(ownerid) + '"]',
			'', ''
		)
		db.session.add(location)

		logo.save(os.path.join('static', logo.filename))

		db.session.commit()

		owner.locationId = location.id

		db.session.commit()

		return { "id": location.id }
	else:
		return { "errormsg": "Owner doesn't exist" }

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

			return { "msg": "" }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg }

@app.route("/get_locations", methods=["POST"])
def get_locations():
	content = request.get_json()

	userid = content['userid']
	longitude = content['longitude']
	latitude = content['latitude']
	name = content['locationName']

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
			orderQuery += "order by st_distance_sphere(point(" + str(longitude) + ", " + str(latitude) + "), point(longitude, latitude))"
			lon1 = longitude
			lat1 = latitude
			rad = 6371

			# get restaurants
			sql = "select * from location where type = 'restaurant' " + orderQuery + " limit 0, 10"
			maxsql = "select count(*) as num from location where type = 'restaurant' " + orderQuery
			datas = query(sql, True)
			maxdatas = query(maxsql, True)[0]["num"]
			for data in datas:
				lon2 = float(data['longitude'])
				lat2 = float(data['latitude'])

				point1 = (lon1, lat1)
				point2 = (lon2, lat2)

				locations[0]["locations"].append({
					"key": "l-" + str(data['id']),
					"id": data['id'],
					"logo": data['logo'],
					"nav": "restaurantprofile",
					"name": data['name'],
					"radiusKm": haversine(point1, point2)
				})

			locations[0]["index"] += len(datas)

			# get nail salons
			sql = "select * from location where type = 'nail' " + orderQuery + " limit 0, 10"
			maxsql = "select count(*) as num from location where type = 'nail' " + orderQuery
			datas = query(sql, True)
			maxdatas = query(maxsql, True)[0]["num"]
			for data in datas:
				lon2 = float(data['longitude'])
				lat2 = float(data['latitude'])

				point1 = (lon1, lat1)
				point2 = (lon2, lat2)

				locations[1]["locations"].append({
					"key": "l-" + str(data['id']),
					"id": data['id'],
					"logo": data['logo'],
					"nav": "salonprofile",
					"name": data['name'],
					"radiusKm": haversine(point1, point2)
				})

			locations[1]["index"] += len(datas)

			# get hair salons
			sql = "select * from location where type = 'hair' " + orderQuery + " limit 0, 10"
			maxsql = "select count(*) as num from location where type = 'hair' " + orderQuery
			datas = query(sql, True)
			maxdatas = query(maxsql, True)[0]["num"]
			for data in datas:
				lon2 = float(data['longitude'])
				lat2 = float(data['latitude'])

				point1 = (lon1, lat1)
				point2 = (lon2, lat2)

				locations[2]["locations"].append({
					"key": "l-" + str(data['id']),
					"id": data['id'],
					"logo": data['logo'],
					"nav": "salonprofile",
					"name": data['name'],
					"radiusKm": haversine(point1, point2)
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

	user = User.query.filter_by(id=userid).first()

	if user != None:
		locations = []
		orderQuery = "and name like '%" + name + "%' " if name != "" else ""
		orderQuery += "order by st_distance_sphere(point(" + str(longitude) + ", " + str(latitude) + "), point(longitude, latitude))"
		lon1 = longitude
		lat1 = latitude
		rad = 6371

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

			locations.append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": data['logo'],
				"nav": ("restaurant" if type == "restaurant" else "salon") + "profile",
				"name": data['name'],
				"radiusKm": haversine(point1, point2)
			})

		return { "newlocations": locations, "index": len(datas), "max": maxdatas }

@app.route("/get_location_profile", methods=["POST"])
def get_location_profile():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']

	user = User.query.filter_by(id=userid).first()

	if user != None:
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

			info = {
				"id": location.id,
				"name": location.name,
				"addressOne": location.addressOne,
				"addressTwo": location.addressTwo,
				"city": location.city,
				"province": location.province,
				"postalcode": location.postalcode,
				"phonenumber": location.phonenumber,
				"logo": location.logo,
				"longitude": float(location.longitude),
				"latitude": float(location.latitude),
			}

			return { "locationInfo": info, "msg": msg }
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

		num_menus = Menu.query.filter_by(locationId=locationid, parentMenuId=menuid).count()
		num_services = Service.query.filter_by(locationId=locationid, menuId=menuid).count()
		num_products = Product.query.filter_by(locationId=locationid, menuId=menuid).count()

		menu = Menu.query.filter_by(id=menuid).first()
		menuname = ""

		if menu != None:
			menuname = menu.name

		if num_menus > 0:
			return { "msg": "menus", "menuName": menuname, "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo }
		elif num_services > 0:
			return { "msg": "services", "menuName": menuname, "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo }
		elif num_products > 0:
			return { "msg": "products", "menuName": menuname, "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo }
		else:
			return { "msg": "", "menuName": "", "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }

@app.route("/get_hours", methods=["POST"])
def get_hours():
	content = request.get_json()

	locationid = content['locationid']
	day = content['day']

	days = { "Sun": "Sunday", "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday" }

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		hours = json.loads(location.hours)

		openTime = hours[days[day]]["opentime"]
		closeTime = hours[days[day]]["closetime"]

		return { "openTime": openTime, "closeTime": closeTime }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }