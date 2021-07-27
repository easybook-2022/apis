from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, os, json, stripe
from random import randint
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
stripe.api_key = "sk_test_lft1B76yZfF2oEtD5rI3y8dz"

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
def welcome_users():
	return { "msg": "welcome to carts of easygo" }

@app.route("/get_num_items/<id>")
def get_num_items(id):
	datas = query("select * from cart where adder = " + str(id), True)

	return { "numCartItems": len(datas) }

@app.route("/get_cart_items/<id>")
def get_cart_items(id):
	user = User.query.filter_by(id=id).first()

	if user != None:
		datas = query("select * from cart where adder = " + str(user.id), True)
		items = []
		active = True if len(datas) > 0 else False

		for data in datas:
			product = Product.query.filter_by(id=data['productId']).first()
			callfor = json.loads(data['callfor'])
			friends = []

			for info in callfor:
				friend = User.query.filter_by(id=info['userid']).first()

				friends.append({
					"key": str(data['id']) + "-" + str(friend.id),
					"username": friend.username,
					"profile": friend.profile,
					"status": info['status']
				})

				if info['status'] == 'waiting':
					active = False

			items.append({
				"key": "cart-item" + str(data['id']),
				"id": str(data['id']),
				"name": product.name,
				"image": product.image,
				"options": json.loads(data['options']),
				"quantity": data['quantity'],
				"price": float(int(data['quantity']) * float(product.price)),
				"orderers": friends
			})

		return { "cartItems": items, "activeCheckout": active }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/add_item_to_cart", methods=["POST"])
def add_item_to_cart():
	content = request.get_json()

	userid = content['userid']
	productid = content['productid']
	quantity = content['quantity']
	callfor = json.dumps(content['callfor'])
	options = content['options']

	user = User.query.filter_by(id=userid).first()
	msg = ""

	if user != None:
		product = Product.query.filter_by(id=productid).first()

		if product != None:
			for option in options:
				if option['type'] == 'size' and option['selected'] == '':
					msg = "Please choose a size"

			if msg == "":
				options = json.dumps(options)
				cartitem = Cart(productid, quantity, userid, callfor, options)

				db.session.add(cartitem)
				db.session.commit()

				return { "msg": "item added to cart" }
		else:
			msg = "Product doesn't exist"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/remove_item_from_cart/<id>")
def remove_item_from_cart(id):
	cartitem = Cart.query.filter_by(id=id).first()

	if cartitem != None:
		db.session.delete(cartitem)
		db.session.commit()

		return { "msg": "" }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg }

@app.route("/checkout", methods=["POST"])
def checkout():
	content = request.get_json()

	adder = content['userid']
	time = content['time']

	user = User.query.filter_by(id=adder).first()
	username = user.username

	if user != None:
		datas = query("select * from cart where adder = " + str(adder), True)

		for data in datas:
			groupId = ""

			for k in range(20):
				groupId += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 0))

			product = Product.query.filter_by(id=data['productId']).first()
			price = float(product.price)
			quantity = int(data['quantity'])
			callfor = json.loads(data['callfor'])
			options = data['options']
			friends = []

			if len(callfor) > 0:
				for info in callfor:
					friends.append(str(info['userid']))
					friend = User.query.filter_by(id=info['userid']).first()
					customerid = friend.customerid

					stripe.Charge.create(
						amount=int(price * 100),
						currency="cad",
						customer=customerid,
						description=username + " called " + product.name + " for " + friend.username
					)
			else:
				stripe.Charge.create(
					amount=int(price * 100),
					currency="cad",
					customer=user.customerid,
					description=username + " purchased " + product.name
				)

			for k in range(quantity):
				transaction = Transaction(groupId, product.id, adder, json.dumps(friends), options, time)

				db.session.add(transaction)
				db.session.commit()

			query("delete from cart where id = " + str(data['id']), False)

		return { "msg": "checkout completed" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }
