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
run_stripe = True

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(10), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	profile = db.Column(db.String(25))
	info = db.Column(db.String(60))

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
	accountId = db.Column(db.String(25))

	def __init__(
		self, 
		name, addressOne, addressTwo, city, province, postalcode, phonenumber, logo, 
		longitude, latitude, owners, type, hours, accountId
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
		self.accountId = accountId

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
	info = db.Column(db.String(80))

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
	sizes = db.Column(db.String(150))
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

@app.route("/", methods=["GET"])
def welcome_users():
	return { "msg": "welcome to carts of easygo" }

@app.route("/get_num_items/<id>")
def get_num_items(id):
	datas = query("select * from cart where adder = " + str(id) + " and status = 'listed'", True)

	return { "numCartItems": len(datas) }

@app.route("/get_cart_items/<id>")
def get_cart_items(id):
	user = User.query.filter_by(id=id).first()

	if user != None:
		datas = Cart.query.filter_by(adder=user.id, status="listed").all()
		items = []
		active = True if len(datas) > 0 else False

		for data in datas:
			product = Product.query.filter_by(id=data.productId).first()
			quantity = int(data.quantity)
			callfor = json.loads(data.callfor)
			options = json.loads(data.options)
			others = json.loads(data.others)
			sizes = json.loads(data.sizes)
			friends = []
			row = []
			cost = 0

			for k, info in enumerate(callfor):
				friend = User.query.filter_by(id=info['userid']).first()

				row.append({
					"id": friend.id,
					"key": str(data.id) + "-" + str(friend.id),
					"username": friend.username,
					"profile": friend.profile,
					"status": info['status']
				})

				if len(row) == 4 or (len(callfor) - 1 == k and len(row) > 0):
					if len(callfor) - 1 == k and len(row) > 0:
						leftover = 4 - len(row)
						id = data.id + 1
						key = friend.id + 1

						for m in range(leftover):
							row.append({ "key": str(id) + "-" + str(key) })
							id += 1
							key += 1
					
					friends.append({ "key": len(friends), "row": row })
					row = []

				if info['status'] == 'waiting' or info['status'] == 'payment':
					active = False

			for k, option in enumerate(options):
				option['key'] = "option-" + str(k)

			for k, other in enumerate(others):
				other['key'] = "other-" + str(k)

			for k, size in enumerate(sizes):
				size['key'] = "size-" + str(k)

			if product.price == "":
				for size in sizes:
					if size['selected'] == True:
						cost += quantity * float(size['price'])
			else:
				cost += quantity * float(product.price)

			for other in others:
				if other['selected'] == True:
					cost += float(other['price'])

			items.append({
				"key": "cart-item-" + str(data.id),
				"id": str(data.id),
				"name": product.name,
				"productId": product.id,
				"note": data.note,
				"image": product.image,
				"options": options,
				"others": others,
				"sizes": sizes,
				"quantity": quantity,
				"cost": cost,
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
	callfor = content['callfor']
	options = content['options']
	others = content['others']
	sizes = content['sizes']
	note = content['note']

	user = User.query.filter_by(id=userid).first()
	product = Product.query.filter_by(id=productid).first()
	msg = ""
	status = ""

	if user != None and product != None:
		info = json.loads(user.info)
		customerid = info["customerId"]

		if run_stripe == True:
			customer = stripe.Customer.list_sources(
				customerid,
				object="card",
				limit=1
			)
			cards = len(customer.data)
		else:
			cards = 1

		if cards > 0 or len(callfor) > 0:
			if product.price == '':
				if "true" not in json.dumps(sizes):
					msg = "Please choose a size"
		else:
			msg = "A payment method is required"
			status = "cardrequired"
	else:
		if user != None:
			msg = "User doesn't exist"
		else:
			msg = "Product doesn't exist"

	if msg == "":
		callfor = json.dumps(callfor)
		options = json.dumps(options)
		others = json.dumps(others)
		sizes = json.dumps(sizes)

		cartitem = Cart(product.locationId, productid, quantity, userid, callfor, options, others, sizes, note, "listed", "")

		db.session.add(cartitem)
		db.session.commit()

		return { "msg": "item added to cart" }

	return { "errormsg": msg, "status": status }, 400

@app.route("/remove_item_from_cart/<id>")
def remove_item_from_cart(id):
	cartitem = Cart.query.filter_by(id=id).first()

	if cartitem != None:
		db.session.delete(cartitem)
		db.session.commit()

		return { "msg": "Cart item removed from cart" }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg }

@app.route("/checkout", methods=["POST"])
def checkout():
	def getRanStr():
		while True:
			strid = ""

			for k in range(4):
				strid += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 9))

			numsame = query("select count(*) as num from cart where orderNumber = '" + strid + "'", True)[0]["num"]

			if numsame == 0:
				return strid

	content = request.get_json()

	adder = content['userid']
	time = content['time']

	user = User.query.filter_by(id=adder).first()

	if user != None:
		username = user.username
		orderNumber = getRanStr()

		query("update cart set status = 'checkout', orderNumber = '" + orderNumber + "' where adder = " + str(adder) + " and status = 'listed'", False)

		return { "msg": "order sent" }
	else:
		msg = "User doesn't exist"

	return { "errormsg": msg }

@app.route("/order_ready", methods=["POST"])
def order_ready():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	ordernumber = content['ordernumber']

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		orders = Cart.query.filter_by(orderNumber=ordernumber).count()

		if orders > 0:
			datas = Cart.query.filter_by(adder=userid, locationId=locationid, orderNumber=ordernumber, status='checkout').all()

			for data in datas:
				data.status = "ready"

			db.session.commit()

			return { "msg": "Order ready" }
		else:
			msg = "Order doesn't exist"
	else:
		msg = "Location doesn't exist"

	return { "errormsg": msg }, 400

@app.route("/receive_payment", methods=["POST"])
def receive_payment():
	content = request.get_json()

	userid = str(content['userid'])
	ordernumber = content['ordernumber']
	locationid = content['locationid']
	time = content['time']

	user = User.query.filter_by(id=userid).first()
	location = Location.query.filter_by(id=locationid).first()
	msg = ""
	status = ""

	if user != None and location != None:
		accountid = location.accountId

		if run_stripe == True:
			account = stripe.Account.list_external_accounts(accountid, object="bank_account", limit=1)
			bankaccounts = len(account.data)
		else:
			bankaccounts = 1

		if bankaccounts == 1:
			username = user.username
			adder = user.id
			
			datas = query("select * from cart where adder = " + str(adder) + " and orderNumber = '" + ordernumber + "' and status = 'ready'", True)
			charges = {}

			for data in datas:
				groupId = ""

				for k in range(20):
					groupId += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 0))

				product = Product.query.filter_by(id=data['productId']).first()
				location = Location.query.filter_by(id=product.locationId).first()
				sizes = json.loads(data['sizes'])
				others = json.loads(data['others'])
				quantity = int(data['quantity'])
				cost = 0

				if product.price == "":
					for size in sizes:
						if size["selected"] == True:
							cost += quantity * float(size["price"])
				else:
					cost += quantity * float(product.price)

				for other in others:
					if other['selected'] == True:
						cost += float(other['price'])

				quantity = int(data['quantity'])
				callfor = json.loads(data['callfor'])
				options = data['options']
				others = data['others']
				sizes = json.dumps(sizes)
				friends = []

				if len(callfor) > 0:
					for info in callfor:
						friends.append(str(info['userid']))
						friend = User.query.filter_by(id=info['userid']).first()
						friendid = str(info['userid'])

						if friendid in charges:
							charges[friendid] += float(cost)
						else:
							charges[friendid] = float(cost)
				else:
					if userid in charges:
						charges[userid] += float(cost)
					else:
						charges[userid] = float(cost)

				for k in range(quantity):
					transaction = Transaction(groupId, 0, product.id, 0, adder, json.dumps(friends), options, others, sizes, time)

					db.session.add(transaction)
					db.session.commit()

				query("delete from cart where id = " + str(data['id']), False)

			for info in charges:
				userInfo = User.query.filter_by(id=info).first()
				customerid = json.loads(userInfo.info)["customerId"]

				if run_stripe == True:
					stripe.Charge.create(
						amount=int(charges[info] * 100),
						currency="cad",
						customer=customerid,
						transfer_data={
							"destination": location.accountId
						}
					)

			return { "msg": "Order delivered and payment made" }
		else:
			msg = "Bank account required"
			status = "bankaccountrequired"

	return { "errormsg": msg, "status": status }, 400

@app.route("/edit_cart_item/<id>")
def edit_cart_item(id):
	cartitem = Cart.query.filter_by(id=id).first()

	if cartitem != None:
		product = Product.query.filter_by(id=cartitem.productId).first()
		quantity = int(cartitem.quantity)
		cost = 0

		options = json.loads(cartitem.options)
		for k, option in enumerate(options):
			option["key"] = "option-" + str(k)

		others = json.loads(cartitem.others)
		for k, other in enumerate(others):
			other["key"] = "other-" + str(k)

		sizes = json.loads(cartitem.sizes)
		for k, size in enumerate(sizes):
			size["key"] = "size-" + str(k)

		if product.price == "":
			for size in sizes:
				if size["selected"] == True:
					cost += quantity * float(size["price"])
		else:
			cost += quantity * float(product.price)

		for other in others:
			if other["selected"] == True:
				cost += float(other["price"])

		info = {
			"name": product.name,
			"info": product.info,
			"image": product.image,
			"price": float(product.price) if product.price != "" else 0,
			"quantity": quantity,
			"options": options,
			"others": others,
			"sizes": sizes,
			"note": cartitem.note,
			"cost": cost
		}

		return { "cartItem": info, "msg": "cart item fetched" }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg }

@app.route("/update_cart_item", methods=["POST"])
def update_cart_item():
	content = request.get_json()

	cartid = content['cartid']
	quantity = content['quantity']
	options = content['options']
	others = content['others']
	sizes = content['sizes']
	note = content['note']

	cartitem = Cart.query.filter_by(id=cartid).first()

	if cartitem != None:
		cartitem.quantity = quantity
		cartitem.options = json.dumps(options)
		cartitem.others = json.dumps(others)
		cartitem.sizes = json.dumps(sizes)
		cartitem.note = note

		db.session.commit()

		return { "msg": "cart item is updated" }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg }

@app.route("/edit_call_for/<id>")
def edit_call_for(id):
	cartitem = Cart.query.filter_by(id=id).first()

	if cartitem != None:
		callfor = json.loads(cartitem.callfor)
		product = Product.query.filter_by(id=cartitem.productId).first()
		searchedfriends = []
		row = []
		key = 0
		numsearchedfriends = 0
		cost = 0

		for k, info in enumerate(callfor):
			user = User.query.filter_by(id=info['userid']).first()

			row.append({
				"key": "selected-friend-" + str(key),
				"id": user.id,
				"profile": user.profile,
				"username": user.username
			})
			key += 1
			numsearchedfriends += 1

			if len(row) == 4 or (len(callfor) - 1 == k and len(row) > 0):
				if len(callfor) - 1 == k and len(row) > 0:
					leftover = 4 - len(row)

					for k in range(leftover):
						row.append({ "key": "selected-friend-" + str(key) })
						key += 1
				
				searchedfriends.append({ "key": "selected-friend-row-" + str(len(searchedfriends)), "row": row })
				row = []

		options = json.loads(cartitem.options)
		for k, option in enumerate(options):
			option["key"] = "option-" + str(k)

		others = json.loads(cartitem.others)
		for k, other in enumerate(others):
			other["key"] = "other-" + str(k)

		sizes = json.loads(cartitem.sizes)
		for k, size in enumerate(sizes):
			size["key"] = "size-" + str(k)

		if product.price == "":
			for size in sizes:
				if size["selected"] == True:
					cost += cartitem.quantity * float(size["price"])
		else:
			cost += cartitem.quantity * float(product.price)

		for other in others:
			if other["selected"] == True:
				cost += float(other["price"])

		orderingItem = {
			"name": product.name,
			"image": product.image,
			"options": options,
			"others": others,
			"sizes": sizes,
			"quantity": cartitem.quantity,
			"cost": cost
		}

		return { "searchedFriends": searchedfriends, "numSearchedFriends": numsearchedfriends, "orderingItem": orderingItem }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg }

@app.route("/update_call_for", methods=["POST"])
def update_call_for():
	content = request.get_json()

	cartid = content['cartid']
	callfor = json.dumps(content['callfor'])

	cartitem = Cart.query.filter_by(id=cartid).first()

	if cartitem != None:
		cartitem.callfor = callfor

		db.session.commit()

		return { "msg": "Call for updated" }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg }

@app.route("/remove_call_for", methods=["POST"])
def remove_call_for():
	content = request.get_json()

	cartid = content['cartid']
	callforid = content['callforid']

	cartitem = Cart.query.filter_by(id=cartid).first()

	if cartitem != None:
		callfor = json.loads(cartitem.callfor)
		deleteindex = 0

		for k, data in enumerate(callfor):
			if data['userid'] == callforid:
				del callfor[k]

		cartitem.callfor = json.dumps(callfor)

		db.session.commit()

		return { "msg": "callfor is removed" }
	else:
		msg = "Cart item doesn't exist"

	return { "errormsg": msg }
