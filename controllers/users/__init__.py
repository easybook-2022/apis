from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors
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

	def __init__(self, locationId, menuId, name, image, options):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.image = image
		self.options = options

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
def welcome_users():
	return { "msg": "welcome to users of easygo" }

@app.route("/login", methods=["POST"])
def login():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']

	if cellnumber != '' and password != '':
		user = User.query.filter_by(cellnumber=cellnumber).first()

		if user != None:
			if check_password_hash(user.password, password):
				userid = user.id

				data = query("select * from location where owners like '%\"" + str(userid) + "\"%'", True)

				if len(data) == 0:
					return { "userid": userid, "locationid": "", "msg": "setup" }
				else:
					data = data[0]

					return { "userid": userid, "locationid": data['id'], "msg": "main" }
			else:
				msg = "Password is incorrect"
		else:
			msg = "User doesn't exist"
	else:
		if cellnumber == '':
			msg = "Phone number is blank"
		else:
			msg = "Password is blank"

	return { "errormsg": msg }

@app.route("/register", methods=["POST"])
def register():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']
	confirmPassword = content['confirmPassword']

	if cellnumber != '' and password != '' and confirmPassword != '':
		if len(password) >= 6:
			if password == confirmPassword:
				user = User.query.filter_by(cellnumber=cellnumber).first()

				if user == None:
					password = generate_password_hash(password)

					user = User(cellnumber, password)
					db.session.add(user)
					db.session.commit()

					return { "id": user.id }
				else:
					msg = "User already exist"
			else:
				msg = "Password is mismatch"
		else:
			msg = "Password needs to be atleast 6 characters long"
	else:
		if cellnumber == '':
			msg = "Phone number is blank"
		elif password == '':
			msg = "Passwod is blank"
		else:
			msg = "Please confirm your password"

	return { "msg": msg }, 400

@app.route("/add_bankaccount", methods=["POST"])
def add_bankaccount():
	bankaccountid = "d9d0f0d0d0-sidfidsif"

	return { "bankaccountid": bankaccountid, "action": "add bank account" }

@app.route("/get_account/<accountid>", methods=["GET"])
def get_account(accountid):
	return { "accountid": accountid, "action": "get account" }

@app.route("/get_bankaccount/<bankaccountid>", methods=["GET"])
def get_bankaccount(bankaccountid):
	return { "bankaccountid": bankaccountid, "action": "get bank account" }
