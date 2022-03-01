from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, json, os
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
	profile = db.Column(db.String(25))
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
	logo = db.Column(db.String(20))
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
	image = db.Column(db.String(20))

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
	image = db.Column(db.String(20))
	price = db.Column(db.String(10))
	duration = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, price, duration):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.image = image
		self.price = price
		self.duration = duration

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
	note = db.Column(db.String(225))
	orders = db.Column(db.Text)
	table = db.Column(db.String(20))
	info = db.Column(db.String(100))

	def __init__(self, userId, workerId, locationId, menuId, serviceId, userInput, time, status, cancelReason, nextTime, locationType, note, orders, table, info):
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
	image = db.Column(db.String(20))
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

@app.route("/welcome_menus", methods=["GET"])
def welcome_menus():
	datas = Menu.query.all()
	menus = []

	for data in datas:
		menus.append(data.id)

	return { "msg": "welcome to menus of easygo", "menus": menus }

@app.route("/get_menus/<id>")
def get_menus(id):
	def getOtherMenu(locationId, parentMenuid):
		menuDatas = Menu.query.filter_by(locationId=locationId, parentMenuId=parentMenuid).all() # if start with menus
		items = []

		if len(menuDatas) > 0:
			for index, data in enumerate(menuDatas):
				parentMenuid = data.id
				children = Menu.query.filter_by(locationId=id, parentMenuId=parentMenuid).count()

				items.append({
					"key": "menu-" + str(index), "id": data.id, "name": data.name, 
					"image": data.image, "list": [], "listType": "list"
				})
				otherList = getOtherMenu(locationId, data.id)

				if len(otherList) > 0:
					items[len(items) - 1]["list"] = otherList
				else:
					location = Location.query.filter_by(id=locationId).first()
					type = location.type
					innerItems = []

					if type == "restaurant":
						datas = Product.query.filter_by(locationId=locationId, menuId=data.id).all()

						for data in datas:
							sizes = json.loads(data.sizes)

							innerItems.append({
								"key": "product-" + str(data.id), "id": data.id, "name": data.name, 
								"price": float(data.price) if data.price != '' else None, "sizes": sizes,
								"image": data.image, "listType": "product"
							})
					else:
						datas = Service.query.filter_by(locationId=locationId, menuId=data.id).all()

						for data in datas:
							innerItems.append({
								"key": "service-" + str(data.id), "id": data.id, 
								"name": data.name, "info": data.info, 
								"price": float(data.price), "duration": data.duration, 
								"image": data.image, "listType": "service"
							})

						items[len(items) - 1]["list"] = innerItems
		else:
			productDatas = Product.query.filter_by(locationId=locationId, menuId=parentMenuid).all() # if start with products

			if len(productDatas) > 0:
				for index, data in enumerate(productDatas):
					sizes = json.loads(data.sizes)
					
					items.append({
						"key": "product-" + str(data.id), "id": data.id, "name": data.name, 
						"price": float(data.price) if data.price != '' else None, "sizes": sizes,
						"image": data.image, "listType": "product"
					})
			else:
				serviceDatas = Service.query.filter_by(locationId=locationId, menuId=parentMenuid).all() # if start with services

				for index, data in enumerate(serviceDatas):
					items.append({
						"key": "service-" + str(data.id), "id": data.id, 
						"name": data.name, "price": float(data.price), "duration": data.duration, 
						"image": data.image, "listType": "service"
					})

		return items

	content = request.get_json()

	location = Location.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if location != None:
		menus = getOtherMenu(id, "")
		info = json.loads(location.info)
		type = ""

		if len(info["menuPhotos"]) > 0:
			photos = info["menuPhotos"]
			row = []
			rownum = 0
			menus = []
			type = "photos"

			for photo in photos:
				row.append({ "key": "row-" + str(rownum), "photo": photo })
				rownum += 1

				if len(row) == 3:
					menus.append({ "key": "menu-" + str(len(menus)), "row": row })
					row = []

			if len(row) > 0:
				leftover = 3 - len(row)

				for k in range(leftover):
					row.append({ "key": "row-" + str(rownum) })
					rownum += 1

				menus.append({ "key": "menu-" + str(len(menus)), "row": row })
		elif len(menus) > 0:
			type = "list"

		return { "type": type, "menus": menus }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/remove_menu/<id>")
def remove_menu(id):
	menu = Menu.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if menu != None:
		# delete services and products from the menu
		query("delete from service where menuId = '" + str(id) + "'", False)
		query("delete from product where menuId = '" + str(id) + "'", False)
		query("delete from menu where parentMenuId = '" + str(menu.id) + "'", False)

		image = menu.image

		if image != "" and image != None and os.path.exists("static/" + image):
			os.remove("static/" + image)

		db.session.delete(menu)
		db.session.commit()

		return { "msg": "deleted" }
	else:
		errormsg = "Menu doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_menu_info/<id>")
def get_menu_info(id):
	menu = Menu.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if menu != None:
		name = menu.name
		image = menu.image

		info = { "name": name, "image": image }

		return { "info": info, "msg": "menu info" }
	else:
		errormsg = "Menu doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/save_menu", methods=["POST"])
def save_menu():
	menuid = request.form['menuid']
	name = request.form['name']
	imagepath = request.files.get('image', False)
	imageexist = False if imagepath == False else True
	permission = request.form['permission']

	menu = Menu.query.filter_by(id=menuid).first()
	errormsg = ""
	status = ""

	if menu != None:
		menu.name = name

		if imageexist == True:
			image = request.files['image']
			newimagename = image.filename
			oldimage = menu.image

			if newimagename != oldimage:
				if oldimage != "" and oldimage != None and os.path.exists("static/" + oldimage):
					os.remove("static/" + oldimage)

				image.save(os.path.join('static', newimagename))
				menu.image = newimagename

		db.session.commit()

		return { "msg": "menu info updated" }
	else:
		errormsg = "Menu doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_menu", methods=["POST"])
def add_menu():
	locationid = request.form['locationid']
	parentMenuid = request.form['parentmenuid']
	name = request.form['name']
	info = request.form['info']
	imagepath = request.files.get('image', False)
	imageexist = False if imagepath == False else True
	permission = request.form['permission']
	errormsg = ""
	status = ""

	if name != '':
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			data = query("select * from menu where locationId = " + str(locationid) + " and (parentMenuId = '" + str(parentMenuid) + "' and name = '" + name + "')", True)

			if len(data) == 0:
				imagename = ""
				if imageexist == True:
					image = request.files['image']
					imagename = image.filename

					image.save(os.path.join("static", imagename))
				else:
					imagename = ""
				
				if errormsg == "":
					menu = Menu(locationid, parentMenuid, name, info, imagename)

					db.session.add(menu)
					db.session.commit()
					
					return { "id": menu.id }
			else:
				errormsg = "Menu already exist"
		else:
			errormsg = "Location doesn't exist"
	else:
		errormsg = "Name is blank"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/upload_menu", methods=["POST"])
def upload_menu():
	locationid = request.form['locationid']
	imagepath = request.files.get('image', False)
	imageexist = False if imagepath == False else True
	permission = request.form['permission']
	errormsg = ""
	status = ""

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		image = request.files['image']
		imagename = image.filename

		image.save(os.path.join("static", imagename))

		info = json.loads(location.info)
		menuPhotos = info["menuPhotos"]

		menuPhotos.append(str(imagename))

		info["menuPhotos"] = menuPhotos
		location.info = json.dumps(info)

		db.session.commit()

		row = []
		rownum = 0
		menus = []

		for photo in menuPhotos:
			row.append({ "key": "row-" + str(rownum), "photo": photo })
			rownum += 1

			if len(row) == 3:
				menus.append({ "key": "menu-" + str(len(menus)), "row": row })
				row = []

		if len(row) > 0:
			leftover = 3 - len(row)

			for k in range(leftover):
				row.append({ "key": "row-" + str(rownum) })
				rownum += 1

			menus.append({ "key": "menu-" + str(len(menus)), "row": row })

		return { "msg": "success", "menus": menus }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/delete_menu", methods=["POST"])
def delete_menu():
	content = request.get_json()
	status = ""
	errormsg = ""

	locationid = content['locationid']
	photo = content['photo']

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		info = json.loads(location.info)
		photos = info["menuPhotos"]

		if photo in photos:
			photos.remove(photo)

		info["menuPhotos"] = photos
		location.info = json.dumps(info)

		db.session.commit()

		row = []
		rownum = 0
		menus = []

		for photo in photos:
			row.append({ "key": "row-" + str(rownum), "photo": photo })
			rownum += 1

			if len(row) == 3:
				menus.append({ "key": "menu-" + str(len(menus)), "row": row })
				row = []

		if len(row) > 0:
			leftover = 3 - len(row)

			for k in range(leftover):
				row.append({ "key": "row-" + str(rownum) })
				rownum += 1

			menus.append({ "key": "menu-" + str(len(menus)), "row": row })

		return { "msg": "success", "menus": menus }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
