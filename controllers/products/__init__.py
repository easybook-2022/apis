from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, stripe, json, os
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
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
	info = db.Column(db.String(120))

	def __init__(self, cellnumber, password, username, profile, info):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.profile = profile
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
	longitude = db.Column(db.String(15))
	latitude = db.Column(db.String(15))
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

	def __init__(self, userId, locationId, menuId, serviceId, time, status, cancelReason, nextTime, locationType, customers, note, orders, table, info):
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

def trialInfo(id, time): # days before over | cardrequired | trialover
	user = User.query.filter_by(id=id).first()
	info = json.loads(user.info)

	customerid = info['customerId']

	stripeCustomer = stripe.Customer.list_sources(
		customerid,
		object="card",
		limit=1
	)
	cards = len(stripeCustomer.data)
	status = ""
	days = 0

	if "trialstart" in info:
		if (time - info["trialstart"]) >= (86400000 * 30): # trial is over, payment required
			if cards == 0:
				status = "cardrequired"
			else:
				status = "trialover"
		else:
			days = 30 - int((time - info["trialstart"]) / (86400000 * 30))
			status = "notover"
	else:
		if cards == 0:
			status = "cardrequired"
		else:
			status = "trialover"

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

@app.route("/welcome_products", methods=["GET"])
def welcome_products():
	datas = Product.query.all()
	products = []

	for data in datas:
		products.append(data.id)

	return { "msg": "welcome to products of easygo", "products": products }

@app.route("/get_products", methods=["POST"])
def get_products():
	content = request.get_json()

	locationid = content['locationid']
	menuid = content['menuid']

	location = Location.query.filter_by(id=locationid).first()
	msg = ""
	status = ""

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
					"price": data['price'],
					"sizes": len(json.loads(data['sizes'])),
					"options": json.loads(data['options'])
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

	return { "errormsg": msg, "status": status }, 400

@app.route("/get_product_info/<id>")
def get_product_info(id):
	content = request.get_json()

	product = Product.query.filter_by(id=id).first()
	msg = ""
	status = ""

	if product != None:
		datas = json.loads(product.options)
		options = []

		for k, data in enumerate(datas):
			option = { "key": "option-" + str(k), "header": data['text'], "type": data['option'] }

			if data['option'] == 'percentage':
				option["selected"] = 0
			elif data['option'] == 'amount':
				option["selected"] = 0

			options.append(option)

		datas = json.loads(product.others)
		others = []

		for k, data in enumerate(datas):
			others.append({
				"key": "other-" + str(k), 
				"name": data['name'], 
				"input": data['input'], 
				"price": float(data['price']),
				"selected": False
			})

		datas = json.loads(product.sizes)
		sizes = []

		for k, data in enumerate(datas):
			sizes.append({
				"key": "size-" + str(k),
				"name": data["name"],
				"price": float(data["price"]),
				"selected": False
			})

		info = {
			"name": product.name,
			"info": product.info,
			"image": product.image,
			"options": options,
			"others": others,
			"sizes": sizes,
			"price": float(product.price) if product.price != "" else 0,
			"cost": float(product.price) if product.price != "" else 0
		}

		return { "productInfo": info }
	else:
		msg = "Product doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/cancel_cart_order", methods=["POST"])
def cancel_cart_order():
	content = request.get_json()

	userid = content['userid']
	cartid = content['cartid']

	sql = "select * from cart where id = " + str(cartid) + " and "
	sql += "("
	sql += "callfor like '%\"userid\": \"" + str(userid) + "\", \"status\": \"waiting\"%'"
	sql += " or "
	sql += "callfor like '%\"status\": \"waiting\", \"userid\": \"" + str(userid) + "\"%'"
	sql += ")"

	data = query(sql, True)
	msg = ""
	status = ""

	if len(data) > 0:
		data = data[0]

		receiver = ["user" + str(data['adder'])]
		callfor = json.loads(data['callfor'])

		for k, info in enumerate(callfor):
			if info['userid'] == userid:
				del callfor[k]

		if len(callfor) > 0:
			query("update cart set callfor = '" + json.dumps(callfor) + "' where id = " + str(cartid), False)
		else:
			query("delete from cart where id = " + str(cartid), False)

		return { "msg": "Orderer deleted", "receiver": receiver }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/confirm_cart_order", methods=["POST"])
def confirm_cart_order():
	content = request.get_json()

	userid = content['userid']
	id = content['id']

	sql = "select * from cart where id = " + str(id) + " and "
	sql += "("
	sql += "callfor like '%\"userid\": \"" + str(userid) + "\", \"status\": \"waiting\"%'"
	sql += " or "
	sql += "callfor like '%\"status\": \"waiting\", \"userid\": \"" + str(userid) + "\"%'"
	sql += ")"

	data = query(sql, True)
	msg = ""
	status = ""

	if len(data) > 0:
		data = data[0]

		receiver = ["user" + str(data['adder'])]
		callfor = json.loads(data['callfor'])

		for info in callfor:
			if info['userid'] == userid:
				info['status'] = 'confirmed'

		query("update cart set callfor = '" + json.dumps(callfor) + "' where id = " + str(id), False)

		return { "msg": "Order confirmed", "receiver": receiver }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/add_product", methods=["POST"])
def add_product():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	name = request.form['name']
	info = request.form['info']
	imagepath = request.files.get('image', False)
	imageexist = False if imagepath == False else True
	options = request.form['options']
	others = request.form['others']
	sizes = request.form['sizes']
	price = request.form['price']
	permission = request.form['permission']

	location = Location.query.filter_by(id=locationid).first()
	msg = ""
	status = ""

	if location != None:
		data = query("select * from product where locationId = " + str(locationid) + " and menuId = '" + str(menuid) + "' and name = '" + name + "'", True)

		if len(data) == 0:
			price = price if len(sizes) > 0 else ""

			imagename = ""
			if imageexist == True:
				image = request.files['image']
				imagename = image.filename

				image.save(os.path.join('static', imagename))
			else:
				if permission == "true":
					msg = "Please take a good photo"

			if msg == "":
				product = Product(locationid, menuid, name, info, imagename, options, others, sizes, price)

				db.session.add(product)
				db.session.commit()

				return { "id": product.id }
		else:
			msg = "Product already exist"
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/update_product", methods=["POST"])
def update_product():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	productid = request.form['productid']
	name = request.form['name']
	info = request.form['info']
	imagepath = request.files.get('image', False)
	imageexist = False if imagepath == False else True
	options = request.form['options']
	others = request.form['others']
	sizes = request.form['sizes']
	price = request.form['price']
	permission = request.form['permission']

	location = Location.query.filter_by(id=locationid).first()
	msg = ""
	status = ""

	if location != None:
		product = Product.query.filter_by(id=productid, locationId=locationid, menuId=menuid).first()

		if product != None:
			product.name = name
			product.info = info
			product.price = price
			product.options = options
			product.others = others
			product.sizes = sizes

			if imageexist == True:
				image = request.files['image']
				newimagename = image.filename
				oldimage = product.image

				if oldimage != newimagename:
					if oldimage != "" and os.path.exists("static/" + oldimage):
						os.remove("static/" + oldimage)

					image.save(os.path.join('static', newimagename))
					product.image = newimagename
			else:
				if permission == "true":
					msg = "Please take a good photo"

			if msg == "":
				db.session.commit()

				return { "msg": "product updated", "id": product.id }
		else:
			msg = "Product doesn't exist"
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg, "status": status }, 400

@app.route("/remove_product/<id>", methods=["POST"])
def remove_product(id):
	product = Product.query.filter_by(id=id).first()
	msg = ""
	status = ""

	if product != None:
		image = product.image

		if os.path.exists("static/" + image):
			os.remove("static/" + image)

		db.session.delete(product)
		db.session.commit()

		return { "msg": "product deleted" }
	else:
		msg = "Product doesn't exist"

	return { "errormsg": msg, "status": status }, 400
