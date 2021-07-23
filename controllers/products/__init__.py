from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, json, pymysql.cursors, os
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
def welcome_item():
	return { "msg": "welcome to items of easygo" }

@app.route("/get_products", methods=["POST"])
def get_products():
	content = request.get_json()

	locationid = content['locationid']
	menuid = content['menuid']

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		datas = query("select * from product where menuId = '" + str(menuid) + "'", True)
		row = []
		rownum = 0
		products = []
		numproducts = 0

		if len(datas) > 0:
			for index, data in enumerate(datas):
				row.append({
					"key": "product-" + str(index),
					"id": data['id'],
					"name": data['name'],
					"image": data['image'],
					"price": data['price']
				})
				numproducts += 1

				if len(row) == 3:
					products.append({
						"key": "row-product-" + str(rownum),
						"row": row
					})

					row = []
					rownum += 1

			if len(row) > 0:
				leftover = 3 - len(row)
				last_key = int(row[-1]['key'].replace("product-", "")) + 1

				for k in range(leftover):
					row.append({ "key": "product-" + str(last_key) })
					last_key += 1

				products.append({ "key": "row-product-" + str(rownum), "row": row })

		return { "products": products, "numproducts": numproducts }
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }

@app.route("/get_product_info", methods=["POST"])
def get_product_info():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	menuid = content['menuid']
	productid = content['productid']

	user = User.query.filter_by(id=userid).first()

	if user != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			menu = Menu.query.filter_by(parentMenuId=menuid).first()

			if menu != None:
				product = Product.query.filter_by(id=productid).first()

				if product != None:
					datas = json.loads(product.options)
					options = []

					for k in range(len(datas)):
						data = datas[k]

						option = { "key": "info-" + str(k + 1), "header": data['text'], "type": data['option'] }

						if data['option'] == 'size':
							option["options"] = [
								{ "key": "info-opt-0", "header": "small" },
								{ "key": "info-opt-1", "header": "medium" },
								{ "key": "info-opt-2", "header": "large" },
								{ "key": "info-opt-3", "header": "extra large" }
							]
							option["selected"] = ""
						elif data['option'] == 'percentage':
							option["selected"] = 0
						elif data['option'] == 'quantity':
							option["selected"] = 0

						options.append(option)

					info = {
						"name": product.name,
						"info": product.info,
						"image": product.image,
						"options": options,
						"price": float(product.price)
					}

					return { "productInfo": info }
				else:
					msg = "Product doesn't exist"
			else:
				msg = "Menu doesn't exist"
		else:
			msg = "Location doesn't exist"
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/cancel_purchase/<id>")
def cancel_purchase(id):
	cartitem = Cart.query.filter_by(id=id).first()

	if cartitem != None:
		db.session.delete(cartitem)
		db.session.commit()

		return { "msg": "deleted successfully" }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg }

@app.route("/confirm_purchase", methods=["POST"])
def confirm_purchase():
	content = request.get_json()

	userid = content['userid']
	id = content['id']

	data = query("select * from cart where id = " + str(id) + " and callfor like '%\"userid\": " + str(userid) + ", \"status\": \"waiting\"%'", True)

	if len(data) > 0:
		data = data[0]

		callfor = json.loads(data['callfor'])

		for info in callfor:
			if info['userid'] == int(userid):
				info['status'] = 'confirmed'

		callfor = json.dumps(callfor)

		query("update cart set callfor = '" + callfor + "' where id = " + str(id), False)

		return { "msg": "purchase confirmed" }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg }

@app.route("/add_product", methods=["POST"])
def add_product():
	ownerid = request.form['ownerid']
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	name = request.form['name']
	info = request.form['info']
	image = request.files['image']
	options = request.form['options']
	price = request.form['price']

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			data = query("select * from product where locationId = " + str(locationid) + " and menuId = '" + str(menuid) + "' and name = '" + name + "'", True)

			if len(data) == 0:
				product = Product(locationid, menuid, name, info, image.filename, options, price)

				image.save(os.path.join('static', image.filename))

				db.session.add(product)
				db.session.commit()

				return { "id": product.id }
			else:
				msg = "Product already exist"
		else:
			msg = "Location doesn't exist"
	else:
		msg = "Owner doesn't exist"

	return { "errormsg": msg }

@app.route("/remove_product/<id>", methods=["POST"])
def remove_product(id):
	product = Product.query.filter_by(id=id).first()

	if product != None:
		image = product.image

		os.remove("static/" + image)

		db.session.delete(product)
		db.session.commit()

		return { "msg": "" }

	return { "errormsg": "Product doesn't exist" }
