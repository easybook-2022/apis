from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, json, pymysql.cursors
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

	def __init__(self, cellnumber, password):
		self.cellnumber = cellnumber
		self.password = password

	def __repr__(self):
		return '<User %r>' % self.cellnumber

class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
	addressOne = db.Column(db.String(30))
	addressTwo = db.Column(db.String(20))
	city = db.Column(db.String(20))
	province = db.Column(db.String(20))
	postalcode = db.Column(db.String(7))
	logo = db.Column(db.String(20))
	longitude = db.Column(db.String(15))
	latitude = db.Column(db.String(15))
	owners = db.Column(db.Text)

	def __init__(self, name, addressOne, addressTwo, city, province, postalcode, logo, longitude, latitude, owners):
		self.name = name
		self.addressOne = addressOne
		self.addressTwo = addressTwo
		self.city = city
		self.province = province
		self.postalcode = postalcode
		self.logo = logo
		self.longitude = longitude
		self.latitude = latitude
		self.owners = owners

	def __repr__(self):
		return '<Location %r>' % self.name

class Menu(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	categories = db.Column(db.Text)
	name = db.Column(db.String(20))
	image = db.Column(db.String(20))

	def __init__(self, locationId, categories, name, image):
		self.locationId = locationId
		self.categories = categories
		self.name = name
		self.image = image

	def __repr__(self):
		return '<Menu %r>' % self.name

class Service(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Integer)
	name = db.Column(db.String(20))
	info = db.Column(db.Text)
	image = db.Column(db.String(20))

	def __init__(self, locationId, menuId, name, info, image):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.info = info
		self.image = image

	def __repr__(self):
		return '<Service %r>' % self.name

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Integer)
	name = db.Column(db.String(20))
	image = db.Column(db.String(20))
	options = db.Column(db.Text)
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, options, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.image = image
		self.options = options
		self.price = price

	def __repr__(self):
		return '<Product %r>' % self.name

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
def welcome_menus():
	return { "msg": "welcome to menus of easygo" }

@app.route("/request_appointment", methods=["POST"])
def request_appointment():
	menuid = "29c9d9fsdkjfslkf-sdjfldsjf"

	return { "menuid": menuid, "action": "request appointment" }

@app.route("/cancel_purchase", methods=["POST"])
def cancel_purchase():
	orderid = "dsjfkldsjdsfsd9fsdjfkdsjf"

	return { "orderid": orderid, "action": "cancel purchase" }

@app.route("/confirm_purchase", methods=["POST"])
def confirm_purchase():
	orderid = "sdjfklsdsdsdfidsfsddkjf"

	return { "orderid": orderid, "action": "confirm purchase" }

@app.route("/cancel_request", methods=["POST"])
def cancel_request():
	menuid = "29c9d9fsdkjfslkf-sdjfldsjf"

	return { "menuid": menuid, "action": "cancel request" }

@app.route("/confirm_request", methods=["POST"])
def confirm_request():
	menuid = "29c9d9fsdkjfslkf-sdjfldsjf"

	return { "menuid": menuid, "action": "confirm request" }

@app.route("/request_time", methods=["POST"])
def request_time():
	menuid = "29c9d9fsdkjfslkf-sdjfldsjf"

	return { "menuid": menuid, "action": "request time" }

@app.route("/get_info", methods=["POST"])
def get_info():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	categories = content['categories']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			num_menus = Menu.query.filter_by(locationId=location.id, categories=categories).count()
			num_products = Products.query.filter_by(locationId=location.id).count()

			if num_menus > 0:
				return { "msg": "menus" }
			elif num_products > 0:
				return { "msg": "products" }
			else:
				return { "msg": "" }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/get_menus", methods=["POST"])
def get_menus():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	categories = content['categories']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			datas = query("select * from menu where locationId = " + str(locationid) + " and categories = '" + categories + "'", True)
			menus = []

			if len(datas) > 0:
				for data in datas:
					menus.append({
						"key": "menu-" + str(data['id']),
						"id": data['id'],
						"name": data['name'],
						"image": data['image'],
					})

			return { "menus": menus }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/remove_menu", methods=["POST"])
def remove_menu():
	content = request.get_json()

	id = content['id']

	menu = Menu.query.filter_by(id=id).first()

	if menu != None:
		name = menu.name

		query("delete from menu where categories like '%\"" + name + "\"%'", False)

		db.session.delete(menu)
		db.session.commit()

		return { "msg": "deleted" }

	return { "errormsg": "Menu doesn't exist" }

@app.route("/get_requests", methods=["GET"])
def get_requests():
	return { "requests": [] }

@app.route("/get_appointments", methods=["GET"])
def get_appointments():
	return { "appointments": [] }

@app.route("/accept_request", methods=["POST"])
def accept_request():
	return { "requests": [] }

@app.route("/add_menu", methods=["POST"])
def add_menu():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	categories = content['categories']
	info = content['info']
	image = content['image']

	if info != '':
		user = User.query.filter_by(id=userid).first()

		if user != None:
			location = Location.query.filter_by(id=locationid).first()

			if location != None:
				data = query("select * from menu where (categories = '" + categories + "' and name = '" + info + "')", True)

				if len(data) == 0:
					menu = Menu(locationid, categories, info, image)

					db.session.add(menu)
					db.session.commit()

					return { "id": menu.id }
				else:
					msg = "Menu already exist"
			else:
				msg = "Location doesn't exist"
		else:
			msg = "User doesn't exist"
	else:
		msg = "Name is blank"

	return { "errormsg": msg }
