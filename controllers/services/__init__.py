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
def welcome_services():
	return { "msg": "welcome to services of easygo" }

@app.route("/get_services", methods=["POST"])
def get_services():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	menuid = content['menuid']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			datas = query("select * from service where menuId = " + str(menuid), True)
			services = []

			if len(datas) > 0:
				for data in datas:
					services.append({
						"key": "service-" + str(data['id']),
						"id": data['id'],
						"name": data['name'],
						"image": data['image'],
					})

			return { "services": services }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/add_service", methods=["POST"])
def add_service():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	menuid = content['menuid']
	info = content['info']
	image = content['image']

	if info != '':
		user = User.query.filter_by(id=userid).first()

		if user != None:
			location = Location.query.filter_by(id=locationid).first()

			if location != None:
				data = query("select * from service where locationid = " + str(locationid) + " and menuid = '" + str(menuid) + "' and name = '" + info + "'", True)

				if len(data) == 0:
					service = Service(locationid, menuid, info, image)

					db.session.add(service)
					db.session.commit()

					return { "id": service.id }
				else:
					msg = "Service already exist"
			else:
				msg = "Location doesn't exist"
		else:
			msg = "User doesn't exist"
	else:
		msg = "Name is blank"

	return { "errormsg": msg }
