from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_carts", methods=["GET"])
def welcome_carts():
	datas = Cart.query.all()
	carts = []

	for data in datas:
		carts.append(data.id)

	return { "msg": "welcome to carts of EasyBook", "carts": carts }

@app.route("/get_num_items/<id>")
def get_num_items(id):
	numCartItems = query("select count(*) as num from cart where adder = " + str(id) + " and status = 'unlisted'", True).fetchone()["num"]

	return { "numCartItems": numCartItems }

@app.route("/get_cart_items/<id>")
def get_cart_items(id):
	user = query("select * from user where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	datas = query("select * from cart where adder = " + str(user["id"]) + " and status = 'unlisted'", True).fetchall()
	items = []
	active = True if len(datas) > 0 else False

	for data in datas:
		product = query("select * from product where id = " + str(data["productId"]), True).fetchone()
		quantity = int(data["quantity"])
		sizes = json.loads(data["sizes"])
		userInput = json.loads(data["userInput"])

		if data["status"] == 'checkout':
			active = False

		for k, size in enumerate(sizes):
			size['key'] = "size-" + str(k)

		if product == None:
			userInput = json.loads(data["userInput"])

		image = json.loads(product["image"]) if product != None else {"name": ""}

		if len(sizes) > 0:
			for size in sizes:
				if size["selected"] == True:
					cost = float(size["price"]) * quantity
		else:
			cost = float(product["price"]) * quantity

		items.append({
			"key": "cart-item-" + str(data["id"]),
			"id": str(data["id"]),
			"name": product["name"] if product != None else userInput["name"],
			"productId": product["id"] if product != None else None, 
			"note": data["note"], 
			"image": image if image["name"] != "" else {"width": 300, "height": 300}, 
			"sizes": sizes, "quantity": quantity,
			"status": data["status"],
			"cost": cost
		})

	return { "cartItems": items, "activeCheckout": active }

@app.route("/add_item_to_cart", methods=["POST"])
def add_item_to_cart():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	productid = content['productid']
	productinfo = content['productinfo']
	quantity = content['quantity']
	sizes = content['sizes']
	note = content['note']
	type = content['type']

	sizes = json.dumps(sizes)

	userInput = json.dumps({ "name": productinfo, "type": type })

	data = {
		"locationId": locationid, "productId": productid,
		"userInput": userInput, "quantity": quantity, "adder": userid,
		"sizes": sizes, "note": note,
		"status": "unlisted", "orderNumber": "", "waitTime": ""
	}
	columns = []
	insert_data = []

	for key in data:
		columns.append(key)
		insert_data.append("'" + str(data[key]) + "'")

	query("insert into cart (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")")

	return { "msg": "item added to cart" }

@app.route("/remove_item_from_cart/<id>")
def remove_item_from_cart(id):
	cartitem = query("select * from cart where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if cartitem != None:
		query("delete from cart where id = " + str(id))

		return { "msg": "Cart item removed from cart" }
	else:
		errormsg = "Cart item doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/checkout", methods=["POST"])
def checkout():
	content = request.get_json()

	adder = content['userid']
	time = content['time']

	user = query("select * from user where id = " + str(adder), True).fetchone()
	cart = query("select * from cart where adder = " + str(adder), True).fetchone()
	product = query("select * from product where id = " + str(cart["productId"]), True).fetchone()
	customer = query("select * from user where id = " + str(cart["adder"]), True).fetchone()

	errormsg = ""
	status = ""

	username = user["username"]
	orderNumber = getRanStr()
	
	locationId = str(cart["locationId"])
	owners = query("select id, info from owner where info like '%\"locationId\": \"" + locationId + "\"%'", True).fetchall()
	receiver = []
	pushids = []

	for owner in owners:
		info = json.loads(owner["info"])

		if info["pushToken"] != "" and info["signin"] == True:
			pushids.append({ "token": info["pushToken"], "signin": info["signin"] })

		receiver.append("owner" + str(owner["id"]))

	productName = ""
	quantity = int(cart["quantity"])
	if cart["productId"] == -1:
		userInput = json.loads(cart["userInput"])
		productName = userInput["name"]
	else:
		productName = product["name"]

	speak = { "name": productName, "quantity": quantity, "customer": customer["username"], "orderNumber": orderNumber }

	if len(pushids) > 0:
		pushmessages = []
		for info in pushids:
			pushmessages.append(pushInfo(
				info["token"], 
				"An order requested",
				"A customer requested an order",
				content
			))

		push(pushmessages)

	query("update cart set status = 'checkout', orderNumber = '" + orderNumber + "' where adder = " + str(adder) + " and orderNumber = ''")

	return { "msg": "order sent", "receiver": receiver, "speak": speak }

@app.route("/order_done", methods=["POST"])
def order_done():
	content = request.get_json()
	errormsg = ""
	status = ""

	userid = str(content['userid'])
	ordernumber = content['ordernumber']
	locationid = content['locationid']

	user = query("select * from user where id = " + str(userid), True).fetchone()
	location = query("select * from location where id = " + str(locationid), True).fetchone()

	if user != None and location != None:
		locationInfo = json.loads(location["info"])
		username = user["username"]
		adder = user["id"]

		sql = "select * from cart where adder = " + str(adder) + " and orderNumber = '" + ordernumber + "'"
		sql += " and ((status = 'inprogress' or status = 'checkout') and (userInput like '%\"type\": \"store\"%' or userInput like '%\"type\": \"restaurant\"%'))"
		
		datas = query(sql, True).fetchall()

		if len(datas) > 0:
			if (location['type'] == 'restaurant' and datas[0]['waitTime'] != "") or location['type'] == 'store':
				for data in datas:
					groupId = ""

					for k in range(20):
						groupId += chr(randint(65, 90)) if randint(0, 9) % 2 == 0 else str(randint(0, 0))

					product = query("select * from product where id = " + str(data['productId']), True).fetchone()

					sizes = json.loads(data['sizes'])
					quantity = int(data['quantity'])
					userInput = json.loads(data['userInput'])

					quantity = int(data['quantity'])
					sizes = json.dumps(sizes)
					info = json.loads(user["info"])

					query("delete from cart where id = " + str(data['id']))
			
				return { "msg": "Order delivered and payment made" }
			else:
				errormsg = "No wait time"
				status = "nowaittime"
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

	cartitem = query("select * from cart where orderNumber = '" + ordernumber + "'", True).fetchone()

	cartitem["status"] = 'inprogress'
	cartitem["waitTime"] = waitTime

	update_data = []
	for key in cartitem:
		if key != "table":
			update_data.append(key + " = '" + str(cartitem[key]) + "'")

	query("update cart set " + ", ".join(update_data) + " where id = " + str(cartitem["id"]), False)

	receiver = "user" + str(cartitem["adder"])

	return { "msg": "success", "receiver": receiver }

@app.route("/edit_cart_item/<id>")
def edit_cart_item(id):
	cartitem = query("select * from cart where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	product = query("select * from product where id = " + str(cartitem["productId"]), True).fetchone()
	quantity = int(cartitem["quantity"])
	userInput = json.loads(cartitem["userInput"])
	cost = 0

	sizes = json.loads(cartitem["sizes"])
	for k, size in enumerate(sizes):
		size["key"] = "size-" + str(k)

	if product != None:
		if product["price"] == "":
			for size in sizes:
				if size["selected"] == True:
					cost += quantity * float(size["price"])
		else:
			cost += quantity * float(product["price"])
	else:
		if "price" in userInput:
			cost += quantity * float(userInput["price"])

	image = json.loads(product["image"]) if product != None else {"name": ""}
	info = {
		"name": product["name"] if product != None else (userInput["name"] if "name" in userInput else ""),
		"image": image if image["name"] != "" else {"width": 300, "height": 300},
		"price": float(product["price"]) if product != None and product["price"] else (userInput["price"] if "price" in userInput else 0),
		"quantity": quantity,
		"sizes": sizes,
		"note": cartitem["note"],
		"cost": cost if cost > 0 else None
	}

	return { "cartItem": info, "msg": "cart item fetched" }

@app.route("/update_cart_item", methods=["POST"])
def update_cart_item():
	content = request.get_json()

	cartid = content['cartid']
	quantity = content['quantity']
	sizes = content['sizes']
	note = content['note']

	cartitem = query("select * from cart where id = " + str(cartid), True).fetchone()
	errormsg = ""
	status = ""

	new_data = {
		"quantity": quantity,
		"sizes": json.dumps(sizes),
		"note": note
	}
	update_data = []

	for key in new_data:
		update_data.append(key + " = '" + str(new_data[key]) + "'")

	query("update cart set " + ", ".join(update_data) + " where id = " + str(cartid))

	return { "msg": "cart item is updated" }

@app.route("/see_orders/<id>")
def see_orders(id):
	datas = query("select * from cart where orderNumber = " + str(id), True).fetchall()
	orders = []

	for data in datas:
		product = query("select * from product where id = " + str(data["productId"]), True).fetchone()
		quantity = int(data["quantity"])
		sizes = json.loads(data["sizes"])
		userInput = json.loads(data["userInput"])

		for k, size in enumerate(sizes):
			size['key'] = "size-" + str(k)

		if len(sizes) > 0:
			for size in sizes:
				if size["selected"] == True:
					cost = float(size["price"]) * quantity
		else:
			cost = float(product["price"]) * quantity

		image = json.loads(product["image"]) if product != None else {"name": ""}
		orders.append({
			"key": "cart-item-" + str(data["id"]),
			"id": str(data["id"]),
			"name": product["name"] if product != None else userInput['name'],
			"note": data["note"],
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"sizes": sizes,
			"quantity": quantity,
			"cost": cost,
		})

	return { "orders": orders }
