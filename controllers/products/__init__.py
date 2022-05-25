from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql.cursors, json, os
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from binascii import a2b_base64
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

@app.route("/welcome_products", methods=["GET"])
def welcome_products():
	datas = Product.query.all()
	products = []

	for data in datas:
		products.append(data.id)

	return { "msg": "welcome to products of easygo", "products": products }

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

		image = json.loads(product.image)
		info = {
			"name": product.name,
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
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
