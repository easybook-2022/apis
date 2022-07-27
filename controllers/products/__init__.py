from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_products", methods=["GET"])
def welcome_products():
	datas = query("select * from product", True).fetchall()
	products = []

	for data in datas:
		products.append(data["id"])

	return { "msg": "welcome to products of EasyBook", "products": products }

@app.route("/get_product_info/<id>")
def get_product_info(id):
	product = query("select * from product where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if product != None:
		cost = 0.00

		options = json.loads(product["options"])

		datas = options["sizes"]
		sizes = []

		for k, data in enumerate(datas):
			price = float(data["price"])

			sizes.append({
				"key": "size-" + str(k),
				"name": data["name"],
				"price": price,
				"selected": False
			})

		datas = options["quantities"]
		quantities = []

		for k, data in enumerate(datas):
			price = float(data["price"])

			if len(str(price).split(".")[1]) < 2:
				price = str(price) + "0"

			quantities.append({
				"key": "quantity-" + str(k),
				"input": data["input"],
				"price": price,
				"selected": False
			})

		datas = options["percents"]
		percents = []

		for k, data in enumerate(datas):
			price = float(data["price"])

			if len(str(price).split(".")[1]) < 2:
				price = str(price) + "0"

			percents.append({
				"key": "percent-" + str(k),
				"input": data["input"],
				"price": price,
				"selected": False
			})

		if product["price"] != "":
			cost = float(product["price"])			

		image = json.loads(product["image"])

		if product["price"] != "":
			price = float(product["price"])

			if len(str(price).split(".")[1]) < 2:
				price = str(price) + "0"
		else:
			price = ""

		info = {
			"name": product["name"],
			"productImage": image if image["name"] != "" else {"width": 300, "height": 300},
			"sizes": sizes, "quantities": quantities, "percents": percents,
			"price": price,
			"cost": cost,
			"quantity": 1
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

	cartitem = query("select * from cart where id = " + str(cartid), True).fetchone()
	errormsg = ""
	status = ""

	if cartitem != None:
		receiver = ["user" + str(data['adder'])]

		query("delete from cart where id = " + str(cartid))

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
	price = request.form['price']
	
	location = query("select * from location where id = " + str(locationid), True).fetchone()
	info = json.loads(location["info"])
	info["listed"] = True
	
	query("update location set info = '" + json.dumps(info) + "' where id = " + str(locationid))

	errormsg = ""
	status = ""

	numProducts = query("select count(*) as num from product where locationId = " + str(locationid) + " and menuId = '" + str(menuid) + "' and name = '" + name + "'", True).fetchone()["num"]

	if numProducts == 0:
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
			data = {
				"locationId": locationid, "menuId": menuid, "name": name, "image": imageData,
				"options": options, "price": price
			}
			columns = []
			insert_data = []

			for key in data:
				columns.append(key)
				insert_data.append("'" + str(data[key]) + "'")

			id = query("insert into product (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

			return { "id": id }
	else:
		errormsg = "Product already exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_product", methods=["POST"])
def update_product():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	productid = request.form['productid']
	name = request.form['name']
	options = request.form['options']
	price = request.form['price']

	product = query("select * from product where id = " + str(productid) + " and locationId = " + str(locationid) + " and menuId = '" + str(menuid) + "'", True).fetchone()

	errormsg = ""
	status = ""
	new_data = {}

	if product != None:
		new_data["name"] = name
		new_data["price"] = price
		new_data["options"] = options

		isWeb = request.form.get("web")

		oldimage = json.loads(product["image"])

		if isWeb != None:
			image = json.loads(request.form['image'])
			imagename = image['name']

			if imagename != '' and "data" in image['uri']:
				uri = image['uri'].split(",")[1]
				size = image['size']

				if oldimage["name"] != "" and os.path.exists("static/" + oldimage["name"]):
					os.remove("static/" + oldimage["name"])

				writeToFile(uri, imagename)

				new_data["image"] = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
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
					new_data["image"] = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})

		if errormsg == "":
			update_data = []
			for key in new_data:
				update_data.append(key + " = '" + new_data[key] + "'")

			query("update product set " + ", ".join(update_data) + " where id = " + str(product["id"]))

			return { "msg": "product updated", "id": product["id"] }
	else:
		errormsg = "Product doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/remove_product/<id>", methods=["POST"])
def remove_product(id):
	product = query("select * from product where id = " + str(id), True).fetchone()
	location = query("select * from location where id = " + str(product["locationId"]), True).fetchone()

	info = json.loads(location["info"])

	numMenus = query("select count(*) as num from menu where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += query("select count(*) as num from service where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += query("select count(*) as num from product where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += len(info["menuPhotos"])

	errormsg = ""
	status = ""

	image = json.loads(product["image"])
	name = image["name"]

	if name != "" and os.path.exists("static/" + name):
		os.remove("static/" + name)

	info["listed"] = True if numMenus > 0 else False

	query("delete from product where id = " + str(id))
	query("update location set info = '" + json.dumps(info) + "' where id = " + str(location["id"]))

	return { "msg": "product deleted" }
