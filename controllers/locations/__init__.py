from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, os
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
def welcome_locations():
	return { "msg": "welcome to locations of easygo" }

@app.route("/setup_location", methods=["POST"])
def setup_location():
	name = request.form['storeName']
	addressOne = request.form['addressOne']
	addressTwo = request.form['addressTwo']
	city = request.form['city']
	province = request.form['province']
	postalcode = request.form['postalcode']
	logo = request.files['logo']
	longitude = request.form['longitude']
	latitude = request.form['latitude']
	owner = request.form['userid']

	user = User.query.filter_by(id=owner).first()

	if user != None:
		location = Location(
			name,
			addressOne, addressTwo, 
			city, province, postalcode, logo.filename,
			longitude, latitude, '["' + str(owner) + '"]'
		)
		db.session.add(location)
		db.session.commit()

		logo.save(os.path.join('static', logo.filename))

		return { "id": location.id }
	else:
		return { "errormsg": "User doesn't exist" }

@app.route("/get_info", methods=["POST"])
def get_info():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	menuid = content['menuid']
	categories = content['categories']

	user = User.query.filter_by(id=userid).first()

	if user != None:
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

			num_menus = Menu.query.filter_by(locationId=locationid, categories=categories).count()
			num_products = Product.query.filter_by(locationId=locationid, menuId=menuid).count()

			if num_menus > 0:
				return { "msg": "menus", "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo }
			elif num_products > 0:
				return { "msg": "products", "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo }
			else:
				return { "msg": "", "storeName": storeName, "storeAddress": storeAddress, "storeLogo": storeLogo }
		else:
			msg = "Location doesn't exist"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }
