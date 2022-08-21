from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_carts", methods=["GET"])
def welcome_carts():
	datas = query("select * from cart", True).fetchall()
	carts = []

	for data in datas:
		carts.append(data["id"])

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
		quantity = int(data["quantity"])
		options = json.loads(data["options"])
		sizes = options["sizes"]
		quantities = options["quantities"]
		percents = options["percents"]
		extras = options["extras"]

		product = query("select * from product where id = " + str(data["productId"]), True).fetchone()
		productOptions = json.loads(product["options"])
		productSizes = productOptions["sizes"]
		productQuantities = productOptions["quantities"]
		productPercents = productOptions["percents"]
		productExtras = productOptions["extras"]

		sizesInfo = {}
		for info in productSizes:
			if info["name"] in sizes:
				sizesInfo[info["name"]] = float(info["price"])

		quantitiesInfo = {}
		for info in productQuantities:
			if info["input"] in quantities:
				quantitiesInfo[info["input"]] = float(info["price"])

		percentsInfo = {}
		for info in productPercents:
			if info["input"] in percents:
				percentsInfo[info["input"]] = float(info["price"])

		extrasInfo = {}
		for info in productExtras:
			if info["input"] in extras:
				extrasInfo[info["input"]] = float(info["price"])

		cost = 0.00

		if data["status"] == 'checkout':
			active = False

		image = json.loads(product["image"]) if product != None else {"name": ""}

		if len(sizes) > 0 or len(quantities) > 0:
			for info in sizes:
				cost += float(sizesInfo[info]) * quantity

			for info in quantities:
				cost += float(quantitiesInfo[info]) * quantity
		else:
			cost = float(product["price"]) * quantity

		if len(percents) > 0 or len(extras) > 0:
			for info in percents:
				cost += float(percentsInfo[info]) * quantity

			for info in extras:
				cost += float(extrasInfo[info]) * quantity

		sizes = []
		quantities = []
		percents = []
		extras = []

		for index, info in enumerate(sizesInfo):
			sizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info] })

		for index, info in enumerate(quantitiesInfo):
			quantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info] })

		for index, info in enumerate(percentsInfo):
			percents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info] })

		for index, info in enumerate(extrasInfo):
			extras.append({ "key": "extra-" + str(index), "input": info, "price": extrasInfo[info] })

		items.append({
			"key": "cart-item-" + str(data["id"]),
			"id": str(data["id"]),
			"name": product["name"],
			"productId": product["id"] if product != None else None, 
			"note": data["note"], 
			"image": image if image["name"] != "" else {"width": 300, "height": 300}, 
			"sizes": sizes, "quantities": quantities, "percents": percents, "extras": extras, 
			"quantity": quantity, "status": data["status"],
			"cost": cost
		})

	return { "cartItems": items, "activeCheckout": active }

@app.route("/add_item_to_cart", methods=["POST"])
def add_item_to_cart():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	productid = content['productid']
	quantity = content['quantity']
	sizes = content['sizes']
	quantities = content['quantities']
	percents = content['percents']
	extras = content['extras']
	note = content['note']
	type = content['type']

	options = json.dumps({"sizes": sizes, "quantities": quantities, "percents": percents, "extras": extras})

	data = {
		"locationId": locationid, "productId": productid,
		"quantity": quantity, "adder": userid,
		"options": options, "note": note,
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

	user = query("select * from user where id = " + str(adder), True).fetchone()
	cart = query("select * from cart where adder = " + str(adder), True).fetchone()
	product = query("select * from product where id = " + str(cart["productId"]), True).fetchone()
	customer = query("select * from user where id = " + str(cart["adder"]), True).fetchone()

	errormsg = ""
	status = ""

	username = user["username"]
	orderNumber = getId()
	
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
	productName = product["name"]

	newInfo = { "name": productName, "quantity": quantity, "customer": customer["username"], "orderNumber": orderNumber }

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

	return { "msg": "order sent", "receiver": receiver, "info": newInfo }

@app.route("/get_cart_orderers/<id>")
def get_cart_orderers(id):
	datas = query("select adder, orderNumber from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by adder, orderNumber", True).fetchall()
	numCartorderers = query("select count(*) as num from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by adder, orderNumber", True).fetchone()
	numCartorderers = numCartorderers["num"] if numCartorderers != None else 0
	cartOrderers = []

	for k, data in enumerate(datas):
		adder = query("select * from user where id = " + str(data['adder']), True).fetchone()
		numOrders = query("select count(*) as num from cart where adder = " + str(data['adder']) + " and locationId = " + str(id) + " and (status = 'checkout' or status = 'inprogress') and orderNumber = '" + data["orderNumber"] + "'", True).fetchone()["num"]

		cartitem = query("select * from cart where orderNumber = '" + str(data['orderNumber']) + "'", True).fetchone()
		location = query("select type from location where id = " + str(cartitem["locationId"]), True).fetchone()

		cartOrderers.append({
			"key": "cartorderer-" + str(k),
			"id": len(cartOrderers),
			"adder": adder["id"],
			"username": adder["username"],
			"numOrders": numOrders,
			"orderNumber": data['orderNumber'],
			"type": location["type"]
		})

	return { "cartOrderers": cartOrderers, "numCartorderers": numCartorderers }

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
		sql += " and (status = 'inprogress' or status = 'checkout')"
		
		datas = query(sql, True).fetchall()

		if len(datas) > 0:
			if (location['type'] == 'restaurant' and datas[0]['waitTime'] != "") or location['type'] == 'store':
				for data in datas:
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

	if cartitem != None:
		product = query("select * from product where id = " + str(cartitem["productId"]), True).fetchone()
		productOptions = json.loads(product["options"])
		productSizes = productOptions["sizes"]
		productQuantities = productOptions["quantities"]
		productPercents = productOptions["percents"]
		productExtras = productOptions["extras"]

		options = json.loads(cartitem["options"])
		sizes = options["sizes"]
		quantities = options["quantities"]
		percents = options["percents"]
		extras = options["extras"]

		sizesInfo = {}
		for info in productSizes:
			sizesInfo[info["name"]] = float(info["price"])

		quantitiesInfo = {}
		for info in productQuantities:
			quantitiesInfo[info["input"]] = float(info["price"])

		percentsInfo = {}
		for info in productPercents:
			percentsInfo[info["input"]] = float(info["price"])

		extrasInfo = {}
		for info in productExtras:
			extrasInfo[info["input"]] = float(info["price"])

		quantity = int(cartitem["quantity"])
		cost = 0

		if product["price"] == "":
			for info in sizes:
				cost += quantity * float(sizesInfo[info])

			for info in quantities:
				cost += quantity * float(quantitiesInfo[info])
		else:
			cost += quantity * float(product["price"])

		for info in percents:
			cost += quantity * float(percentsInfo[info])

		for info in extras:
			cost += quantity * float(extrasInfo[info])

		cartItemSizes = []
		cartItemQuantities = []
		cartItemPercents = []
		cartItemExtras = []

		for index, info in enumerate(sizesInfo):
			cartItemSizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info], "selected": info in sizes })

		for index, info in enumerate(quantitiesInfo):
			cartItemQuantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info], "selected": info in quantities })

		for index, info in enumerate(percentsInfo):
			cartItemPercents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info], "selected": info in percents })

		for index, info in enumerate(extrasInfo):
			cartItemExtras.append({ "key": "extra-" + str(index), "input": info, "price": extrasInfo[info], "selected": info in extras })

		image = json.loads(product["image"]) if product != None else {"name": ""}
		info = {
			"name": product["name"],
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"price": float(product["price"]) if product["price"] != "" else "",
			"quantity": quantity,
			"sizes": cartItemSizes, "quantities": cartItemQuantities, "percents": cartItemPercents, "extras": cartItemExtras,
			"note": cartitem["note"],
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
	sizes = content['sizes']
	quantities = content['quantities']
	percents = content['percents']
	extras = content['extras']
	note = content['note']

	cartitem = query("select * from cart where id = " + str(cartid), True).fetchone()

	if cartitem != None:
		errormsg = ""
		status = ""

		new_data = {
			"quantity": quantity,
			"options": json.dumps({"sizes": sizes, "quantities": quantities, "percents": percents, "extras": extras}),
			"note": note
		}
		update_data = []

		for key in new_data:
			update_data.append(key + " = '" + str(new_data[key]) + "'")

		query("update cart set " + ", ".join(update_data) + " where id = " + str(cartid))

		return { "msg": "cart item is updated" }
	else:
		errormsg = "Cart item doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/see_orders/<id>")
def see_orders(id):
	datas = query("select * from cart where orderNumber = '" + str(id) + "'", True).fetchall()
	orders = []

	for data in datas:
		product = query("select * from product where id = " + str(data["productId"]), True).fetchone()
		productOptions = json.loads(product["options"])
		productSizes = productOptions["sizes"]
		productQuantities = productOptions["quantities"]
		productPercents = productOptions["percents"]
		productExtras = productOptions["extras"]

		options = json.loads(data["options"])
		sizes = options["sizes"]
		quantities = options["quantities"]
		percents = options["percents"]
		extras = options["extras"]

		sizesInfo = {}
		for info in productSizes:
			sizesInfo[info["name"]] = float(info["price"])

		quantitiesInfo = {}
		for info in productQuantities:
			quantitiesInfo[info["input"]] = float(info["price"])

		percentsInfo = {}
		for info in productPercents:
			percentsInfo[info["input"]] = float(info["price"])

		extrasInfo = {}
		for info in productExtras:
			extrasInfo[info["input"]] = float(info["price"])

		quantity = int(data["quantity"])
		cost = 0.00

		if product["price"] == "":
			for info in sizes:
				cost += quantity * float(sizesInfo[info])

			for info in quantities:
				cost += quantity * float(quantitiesInfo[info])
		else:
			cost = quantity * float(product["price"])

		for info in percents:
			cost += quantity * float(percentsInfo[info])

		for info in extras:
			cost += quantity * float(extrasInfo[info])

		cartItemSizes = []
		cartItemQuantities = []
		cartItemPercents = []
		cartItemExtras = []

		for index, info in enumerate(sizesInfo):
			cartItemSizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info], "selected": info in sizes })

		for index, info in enumerate(quantitiesInfo):
			cartItemQuantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info], "selected": info in quantities })

		for index, info in enumerate(percentsInfo):
			cartItemPercents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info], "selected": info in percents })

		for index, info in enumerate(extrasInfo):
			cartItemExtras.append({ "key": "extra-" + str(index), "input": info, "price": extrasInfo[info], "selected": info in extras })

		image = json.loads(product["image"]) if product != None else {"name": ""}
		orders.append({
			"key": "cart-item-" + str(data["id"]),
			"id": str(data["id"]),
			"name": product["name"],
			"note": data["note"],
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"sizes": cartItemSizes, "quantities": cartItemQuantities, "percents": cartItemPercents, "extras": cartItemExtras, 
			"quantity": quantity,
			"cost": cost,
		})

	return { "orders": orders }

@app.route("/get_orders", methods=["POST"])
def get_orders():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	ordernumber = content['ordernumber']

	datas = query("select * from cart where adder = " + str(userid) + " and locationId = " + str(locationid) + " and orderNumber = '" + ordernumber + "'", True).fetchall()
	orders = []
	ready = True
	waitTime = datas[0]["waitTime"] if len(datas) > 0 else ""

	for data in datas:
		options = json.loads(data["options"])
		sizes = options["sizes"]
		quantities = options["quantities"]
		percents = options["percents"]
		extras = options["extras"]

		product = query("select * from product where id = " + str(data['productId']), True).fetchone()
		productOptions = json.loads(product["options"])
		productSizes = productOptions["sizes"]
		productQuantities = productOptions["quantities"]
		productPercents = productOptions["percents"]
		productExtras = productOptions["extras"]

		sizesInfo = {}
		for info in productSizes:
			if info["name"] in sizes:
				sizesInfo[info["name"]] = float(info["price"])

		quantitiesInfo = {}
		for info in productQuantities:
			if info["input"] in quantities:
				quantitiesInfo[info["input"]] = float(info["price"])

		percentsInfo = {}
		for info in productPercents:
			if info["input"] in percents:
				percentsInfo[info["input"]] = float(info["price"])

		extrasInfo = {}
		for info in productExtras:
			if info["input"] in extras:
				extrasInfo[info["input"]] = float(info["price"])

		quantity = int(data['quantity'])
		cost = 0

		if product["price"] == "":
			for info in sizes:
				cost += quantity * float(sizesInfo[info])

			for info in quantities:
				cost += quantity * float(quantitiesInfo[info])
		else:
			cost = float(product["price"]) * quantity

		cartItemSizes = []
		cartItemQuantities = []
		cartItemPercents = []
		cartItemExtras = []

		for index, info in enumerate(sizesInfo):
			cartItemSizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info], "selected": info in sizes })

		for index, info in enumerate(quantitiesInfo):
			cartItemQuantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info], "selected": info in quantities })

		for index, info in enumerate(percentsInfo):
			cartItemPercents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info], "selected": info in percents })

		for index, info in enumerate(extrasInfo):
			cartItemExtras.append({ "key": "extra-" + str(index), "input": info, "price": extrasInfo[info], "selected": info in extras })

		image = json.loads(product["image"]) if product != None else {"name": ""}
		orders.append({
			"key": "cart-item-" + str(data['id']),
			"id": str(data['id']),
			"name": product["number"] if "number" in product else product["name"],
			"note": data['note'],
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"sizes": cartItemSizes, "quantities": cartItemQuantities, 
			"percents": cartItemPercents, "extras": cartItemExtras,
			"quantity": quantity,
			"cost": cost
		})

		if data['status'] == "checkout":
			ready = False

	return { "orders": orders, "ready": ready, "waitTime": waitTime }
