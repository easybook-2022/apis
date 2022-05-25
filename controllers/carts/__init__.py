from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import pymysql.cursors, json, os
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from info import *
from models import *

cors = CORS(app)

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
	if push_notif == True:
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

@app.route("/welcome_carts", methods=["GET"])
def welcome_carts():
	datas = Cart.query.all()
	carts = []

	for data in datas:
		carts.append(data.id)

	return { "msg": "welcome to carts of easygo", "carts": carts }

@app.route("/get_num_items/<id>")
def get_num_items(id):
	datas = query("select * from cart where adder = " + str(id) + " and status = 'unlisted'", True)

	return { "numCartItems": len(datas) }

@app.route("/get_cart_items/<id>")
def get_cart_items(id):
	user = User.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if user != None:
		datas = Cart.query.filter_by(adder=user.id, status="unlisted").all()
		items = []
		active = True if len(datas) > 0 else False

		for data in datas:
			product = Product.query.filter_by(id=data.productId).first()
			quantity = int(data.quantity)
			options = json.loads(data.options)
			others = json.loads(data.others)
			sizes = json.loads(data.sizes)
			userInput = json.loads(data.userInput)

			if data.status == 'checkout':
				active = False

			for k, option in enumerate(options):
				option['key'] = "option-" + str(k)

			for k, other in enumerate(others):
				other['key'] = "other-" + str(k)

			for k, size in enumerate(sizes):
				size['key'] = "size-" + str(k)

			if product == None:
				userInput = json.loads(data.userInput)

			image = json.loads(product.image) if product != None else {"name": ""}
			items.append({
				"key": "cart-item-" + str(data.id),
				"id": str(data.id),
				"name": product.name if product != None else userInput["name"],
				"productId": product.id if product != None else None, 
				"note": data.note, 
				"image": image if image["name"] != "" else {"width": 300, "height": 300}, 
				"options": options, "others": others, "sizes": sizes, "quantity": quantity,
				"status": data.status
			})

		return { "cartItems": items, "activeCheckout": active }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_item_to_cart", methods=["POST"])
def add_item_to_cart():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	productid = content['productid']
	productinfo = content['productinfo']
	quantity = content['quantity']
	options = content['options']
	others = content['others']
	sizes = content['sizes']
	note = content['note']
	type = content['type']

	user = User.query.filter_by(id=userid).first()
	product = Product.query.filter_by(id=productid).first()

	errormsg = ""
	status = ""

	if errormsg == "":
		options = json.dumps(options)
		others = json.dumps(others)
		sizes = json.dumps(sizes)

		userInput = json.dumps({ "name": productinfo, "type": type })
		cartitem = Cart(locationid, productid, userInput, quantity, userid, options, others, sizes, note, "unlisted", "", "")

		db.session.add(cartitem)
		db.session.commit()

		return { "msg": "item added to cart" }

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/remove_item_from_cart/<id>")
def remove_item_from_cart(id):
	cartitem = Cart.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if cartitem != None:
		db.session.delete(cartitem)
		db.session.commit()

		return { "msg": "Cart item removed from cart" }
	else:
		errormsg = "Cart item doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

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
	errormsg = ""
	status = ""

	if user != None:
		username = user.username
		orderNumber = getRanStr()

		cart = Cart.query.filter_by(adder=adder).first()
		locationId = str(cart.locationId)
		owners = query("select id, info from owner where info like '%\"locationId\": \"" + locationId + "\"%'", True)
		receiver = []
		pushids = []

		for owner in owners:
			info = json.loads(owner["info"])

			if info["pushToken"] != "":
				pushids.append(info["pushToken"])

			receiver.append("owner" + str(owner["id"]))

		productName = ""
		quantity = int(cart.quantity)
		if cart.productId == -1:
			userInput = json.loads(cart.userInput)
			productName = userInput["name"]
		else:
			product = Product.query.filter_by(id=cart.productId).first()
			productName = product.name

		customer = User.query.filter_by(id=cart.adder).first()
		speak = { "name": productName, "quantity": quantity, "customer": customer.username, "orderNumber": orderNumber }

		if len(pushids) > 0:
			pushmessages = []
			for pushid in pushids:
				pushmessages.append(pushInfo(
					pushid, 
					"An order requested",
					"A customer requested an order",
					content
				))

			push(pushmessages)

		query("update cart set status = 'checkout', orderNumber = '" + orderNumber + "' where adder = " + str(adder) + " and orderNumber = ''", False)

		return { "msg": "order sent", "receiver": receiver, "speak": speak }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/order_done", methods=["POST"])
def order_done():
	content = request.get_json()

	userid = str(content['userid'])
	ordernumber = content['ordernumber']
	locationid = content['locationid']

	user = User.query.filter_by(id=userid).first()
	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if user != None and location != None:
		locationInfo = json.loads(location.info)
		username = user.username
		adder = user.id

		sql = "select * from cart where adder = " + str(adder) + " and orderNumber = '" + ordernumber + "' and "
		sql += "((status = 'inprogress' and not waitTime = '' and userInput like '%\"type\": \"restaurant\"%') or "
		sql += "(status = 'checkout' and waitTime = '' and userInput like '%\"type\": \"store\"%'))"
		
		datas = query(sql, True)

		if len(datas) > 0:
			for data in datas:
				groupId = ""

				for k in range(20):
					groupId += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 0))

				product = Product.query.filter_by(id=data['productId']).first()

				if product != None:
					location = Location.query.filter_by(id=product.locationId).first()

				sizes = json.loads(data['sizes'])
				others = json.loads(data['others'])
				quantity = int(data['quantity'])
				userInput = json.loads(data['userInput'])

				quantity = int(data['quantity'])
				options = data['options']
				others = data['others']
				sizes = json.dumps(sizes)

				userInfo = User.query.filter_by(id=userid).first()
				info = json.loads(userInfo.info)

				query("delete from cart where id = " + str(data['id']), False)
		
			return { "msg": "Order delivered and payment made" }
		else:
			errormsg = "Order doesn't exist"
			status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/set_wait_time", methods=["POST"])
def set_wait_time():
	content = request.get_json()
	errormsg = ""
	status = ""

	ordernumber = content['ordernumber']
	waitTime = str(content['waitTime'])

	cartitems = Cart.query.filter_by(orderNumber=ordernumber).count()

	if cartitems > 0:
		query("update cart set status = 'inprogress', waitTime = '" + waitTime + "' where orderNumber = '" + ordernumber + "'", False)

		data = Cart.query.filter_by(orderNumber=ordernumber).first()
		receiver = "user" + str(data.adder)

		return { "msg": "success", "receiver": receiver }
	else:
		errormsg = "Orders don't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/edit_cart_item/<id>")
def edit_cart_item(id):
	cartitem = Cart.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if cartitem != None:
		product = Product.query.filter_by(id=cartitem.productId).first()
		quantity = int(cartitem.quantity)
		userInput = json.loads(cartitem.userInput)
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

		if product != None:
			if product.price == "":
				for size in sizes:
					if size["selected"] == True:
						cost += quantity * float(size["price"])
			else:
				cost += quantity * float(product.price)

			for other in others:
				if other["selected"] == True:
					cost += float(other["price"])
		else:
			if "price" in userInput:
				cost += quantity * float(userInput["price"])

		image = json.loads(product.image) if product != None else {"name": ""}
		info = {
			"name": product.name if product != None else (userInput["name"] if "name" in userInput else ""),
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"price": float(product.price) if product != None else (userInput["price"] if "price" in userInput else 0),
			"quantity": quantity,
			"options": options,
			"others": others,
			"sizes": sizes,
			"note": cartitem.note,
			"cost": cost if cost > 0 else None
		}

		return { "cartItem": info, "msg": "cart item fetched" }
	else:
		errormsg = "Cart item doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

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
	errormsg = ""
	status = ""

	if cartitem != None:
		cartitem.quantity = quantity
		cartitem.options = json.dumps(options)
		cartitem.others = json.dumps(others)
		cartitem.sizes = json.dumps(sizes)
		cartitem.note = note

		db.session.commit()

		return { "msg": "cart item is updated" }
	else:
		errormsg = "Cart item doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/see_orders/<id>")
def see_orders(id):
	datas = Cart.query.filter_by(orderNumber=id).all()
	orders = []

	for data in datas:
		product = Product.query.filter_by(id=data.productId).first()
		quantity = int(data.quantity)
		options = json.loads(data.options)
		others = json.loads(data.others)
		sizes = json.loads(data.sizes)
		userInput = json.loads(data.userInput)

		for k, option in enumerate(options):
			option['key'] = "option-" + str(k)

		for k, other in enumerate(others):
			other['key'] = "other-" + str(k)

		for k, size in enumerate(sizes):
			size['key'] = "size-" + str(k)

		image = json.loads(product.image) if product != None else {"name": ""}
		orders.append({
			"key": "cart-item-" + str(data.id),
			"id": str(data.id),
			"name": product.name if product != None else userInput['name'],
			"note": data.note,
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"options": options,
			"others": others,
			"sizes": sizes,
			"quantity": quantity
		})

	return { "orders": orders }
