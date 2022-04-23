from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import pymysql.cursors, json, os
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from binascii import a2b_base64
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
cors = CORS(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(10), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	info = db.Column(db.String(155))

	def __init__(self, cellnumber, password, username, info):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.info = info

	def __repr__(self):
		return '<User %r>' % self.cellnumber

class Owner(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(15), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	profile = db.Column(db.String(60))
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
	logo = db.Column(db.String(60))
	longitude = db.Column(db.String(20))
	latitude = db.Column(db.String(20))
	owners = db.Column(db.Text)
	type = db.Column(db.String(20))
	hours = db.Column(db.Text)
	info = db.Column(db.Text)

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
	image = db.Column(db.String(60))

	def __init__(self, locationId, parentMenuId, name, image):
		self.locationId = locationId
		self.parentMenuId = parentMenuId
		self.name = name
		self.image = image

	def __repr__(self):
		return '<Menu %r>' % self.name

class Service(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	name = db.Column(db.String(20))
	image = db.Column(db.String(60))
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.image = image
		self.price = price

	def __repr__(self):
		return '<Service %r>' % self.name

class Schedule(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer)
	workerId = db.Column(db.Integer)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	serviceId = db.Column(db.Integer)
	userInput = db.Column(db.Text)
	time = db.Column(db.String(15))
	status = db.Column(db.String(10))
	cancelReason = db.Column(db.String(200))
	nextTime = db.Column(db.String(15))
	locationType = db.Column(db.String(15))
	customers = db.Column(db.Text)
	note = db.Column(db.String(225))
	orders = db.Column(db.Text)
	table = db.Column(db.String(20))
	info = db.Column(db.String(100))

	def __init__(self, userId, workerId, locationId, menuId, serviceId, userInput, time, status, cancelReason, nextTime, locationType, customers, note, orders, table, info):
		self.userId = userId
		self.workerId = workerId
		self.locationId = locationId
		self.menuId = menuId
		self.serviceId = serviceId
		self.userInput = userInput
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
	image = db.Column(db.String(60))
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(150))
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, options, others, sizes, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
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
	userInput = db.Column(db.Text)
	quantity = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(225))
	note = db.Column(db.String(100))
	status = db.Column(db.String(10))
	orderNumber = db.Column(db.String(10))
	waitTime = db.Column(db.String(2))

	def __init__(self, locationId, productId, userInput, quantity, adder, options, others, sizes, note, status, orderNumber, waitTime):
		self.locationId = locationId
		self.productId = productId
		self.userInput = userInput
		self.quantity = quantity
		self.adder = adder
		self.options = options
		self.others = others
		self.sizes = sizes
		self.note = note
		self.status = status
		self.orderNumber = orderNumber
		self.waitTime = waitTime

	def __repr__(self):
		return '<Cart %r>' % self.productId

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

def writeToFile(uri, name):
	binary_data = a2b_base64(uri)

	fd = open(os.path.join("static", name), 'wb')
	fd.write(binary_data)
	fd.close()

def getRanStr():
	strid = ""

	for k in range(6):
		strid += str(randint(0, 9))

	return strid

def pushInfo(to, title, body, data):
	return PushMessage(to=to, title=title, body=body, data=data)

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
	errormsg = ""
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

				if len(row) == 2:
					products.append({ "key": "row-product-" + str(rownum), "row": row })
					row = []
					rownum += 1

			if len(row) > 0:
				last_key = int(row[-1]['key'].replace("product-", "")) + 1

				if len(row) < 2:
					row.append({ "key": "product-" + str(last_key) })
					last_key += 1

				products.append({ "key": "row-product-" + str(rownum), "row": row })

		return { "products": products, "numproducts": numproducts }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_product_info/<id>")
def get_product_info(id):
	product = Product.query.filter_by(id=id).first()
	errormsg = ""
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
			"image": json.loads(product.image),
			"options": options,
			"others": others,
			"sizes": sizes,
			"price": float(product.price) if product.price != "" else 0,
			"cost": float(product.price) if product.price != "" else 0
		}

		return { "productInfo": info }
	else:
		errormsg = "Product doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/cancel_cart_order", methods=["POST"])
def cancel_cart_order():
	content = request.get_json()

	userid = content['userid']
	cartid = content['cartid']

	sql = "select * from cart where id = " + str(cartid)
	data = query(sql, True)
	errormsg = ""
	status = ""

	if len(data) > 0:
		data = data[0]

		receiver = ["user" + str(data['adder'])]

		query("delete from cart where id = " + str(cartid), False)

		return { "msg": "Orderer deleted", "receiver": receiver }
	else:
		errormsg = "Cart item doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_product", methods=["POST"])
def add_product():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	name = request.form['name']
		
	options = request.form['options']
	others = request.form['others']
	sizes = request.form['sizes']
	price = request.form['price']

	location = Location.query.filter_by(id=locationid).first()
	info = json.loads(location.info)
	info["listed"] = True
	location.info = json.dumps(info)
	errormsg = ""
	status = ""

	if location != None:
		data = query("select * from product where locationId = " + str(locationid) + " and menuId = '" + str(menuid) + "' and name = '" + name + "'", True)

		if len(data) == 0:
			price = price if len(sizes) > 0 else ""

			isWeb = request.form.get("web")
			imageData = json.dumps({"name": "", "width": 0, "height": 0})

			if isWeb != None:
				image = json.loads(request.form['image'])
				imagename = image['name']

				if imagename != "":
					uri = image['uri'].split(",")[1]
					size = image['size']

					imageData = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})

					writeToFile(uri, imagename)
			else:
				imagepath = request.files.get('image', False)
				imageexist = False if imagepath == False else True

				if imageexist == True:
					image = request.files['image']
					imagename = image.filename

					size = json.loads(request.form['size'])

					image.save(os.path.join('static', imagename))
					imageData = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})

			if errormsg == "":
				product = Product(locationid, menuid, name, imageData, options, others, sizes, price)

				db.session.add(product)
				db.session.commit()

				return { "id": product.id }
		else:
			errormsg = "Product already exist"
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_product", methods=["POST"])
def update_product():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	productid = request.form['productid']
	name = request.form['name']
	options = request.form['options']
	others = request.form['others']
	sizes = request.form['sizes']
	price = request.form['price']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		product = Product.query.filter_by(id=productid, locationId=locationid, menuId=menuid).first()

		if product != None:
			product.name = name
			product.price = price
			product.options = options
			product.others = others
			product.sizes = sizes

			isWeb = request.form.get("web")

			oldimage = json.loads(product.image)

			if isWeb != None:
				image = json.loads(request.form['image'])
				imagename = image['name']

				if imagename != '' and "data" in image['uri']:
					uri = image['uri'].split(",")[1]
					size = image['size']

					if oldimage["name"] != "" and os.path.exists("static/" + oldimage["name"]):
						os.remove("static/" + oldimage["name"])

					writeToFile(uri, imagename)

					product.image = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
			else:
				imagepath = request.files.get('image', False)
				imageexist = False if imagepath == False else True

				if imageexist == True:
					image = request.files['image']
					imagename = image.filename

					size = json.loads(request.form['size'])

					if oldimage["name"] != imagename:
						if oldimage["name"] != "" and os.path.exists("static/" + oldimage["name"]):
							os.remove("static/" + oldimage["name"])

						image.save(os.path.join('static', imagename))
						product.image = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})

			if errormsg == "":
				db.session.commit()

				return { "msg": "product updated", "id": product.id }
		else:
			errormsg = "Product doesn't exist"
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/remove_product/<id>", methods=["POST"])
def remove_product(id):
	product = Product.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if product != None:
		image = json.loads(product.image)
		name = image["name"]

		if name != "" and os.path.exists("static/" + name):
			os.remove("static/" + name)

		db.session.delete(product)

		location = Location.query.filter_by(id=product.locationId).first()
		info = json.loads(location.info)

		numMenus = Menu.query.filter_by(locationId=location.id).count() + Service.query.filter_by(locationId=location.id).count() + Product.query.filter_by(locationId=location.id).count() + len(info["menuPhotos"])

		info["listed"] = True if numMenus > 0 else False
		location.info = json.dumps(info)

		db.session.commit()

		return { "msg": "product deleted" }
	else:
		errormsg = "Product doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
