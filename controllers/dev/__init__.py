from flask import request
from flask_cors import CORS
from info import *
from models import *
from PIL import Image
import os, shutil, json

cors = CORS(app)

@app.route("/welcome_dev")
def welcome_dev():
	return { "msg": "welcome to dev of EasyBook" }

@app.route("/reset")
def reset():
	delete = False
	users = query("select * from user", True).fetchall()
	
	for user in users:
		delete = True

		query("delete from user where id = " + str(user['id']))

	if delete == True:
		query("ALTER table user auto_increment = 1")

	delete = False
	owners = query("select * from owner", True).fetchall()
	for owner in owners:
		delete = True
		query("delete from owner where id = " + str(owner['id']))

	if delete == True:
		query("ALTER table owner auto_increment = 1")

	delete = False
	locations = query("select * from location", True).fetchall()
	for location in locations:
		delete = True
		logo = location['logo']

		locationInfo = json.loads(location['info'])

		if logo != "" and logo != None and os.path.exists("static/" + logo):
			os.remove("static/" + logo)

		query("delete from location where id = " + str(location['id']))

	if delete == True:
		query("ALTER table location auto_increment = 1")

	delete = False
	menus = query("select * from menu", True).fetchall()
	for menu in menus:
		delete = True
		image = menu['image']

		if image != "" and image != None and os.path.exists("static/" + image):
			os.remove("static/" + image)

		query("delete from menu where id = " + str(menu['id']))

	if delete == True:
		query("ALTER table menu auto_increment = 1")

	delete = False
	services = query("select * from service", True).fetchall()
	for service in services:
		delete = True
		image = service['image']

		if image != "" and image != None and os.path.exists("static/" + image):
			os.remove("static/" + image)

		query("delete from service where id = " + str(service['id']))

	if delete == True:
		query("ALTER table service auto_increment = 1")

	delete = False
	schedules = query("select * from schedule", True).fetchall()
	for schedule in schedules:
		delete = True

		query("delete from schedule where id = " + str(schedule['id']))

	if delete == True:
		query("ALTER table schedule auto_increment = 1")

	delete = False
	products = query("select * from product", True).fetchall()
	for product in products:
		delete = True
		image = product['image']

		if image != "" and image != None and os.path.exists("static/" + image):
			os.remove("static/" + image)

		query("delete from product where id = " + str(product['id']))

	if delete == True:
		query("ALTER table product auto_increment = 1")

	delete = False
	carts = query("select * from cart", True).fetchall()
	for cart in carts:
		delete = True

		query("delete from cart where id = " + str(cart['id']))

	if delete == True:
		query("ALTER table cart auto_increment = 1")

	delete = False
	tables = query("select * from dining_table", True).fetchall()
	for table in tables:
		delete = True

		query("delete from dining_table where id = " + str(table['id']))

	if delete == True:
		query("ALTER table dining_table auto_increment = 1")

	files = os.listdir("static")

	for file in files:
		if "." in file:
			if file != "" and file != None and os.path.exists("static/" + file):
				os.remove("static/" + file)

	return { "reset": True }

@app.route("/push", methods=["POST"])
def push():
	content = request.get_json()

	type = content['type']

	if type == 'user':
		userid = content['userid']
		user = query("select * from user where id = " + str(userid), True).fetchone()[0]
	else:
		ownerid = content['ownerid']
		user = query("select * from owner where id = " + str(ownerid), True).fetchone()[0]

	message = content['message']
	data = content['data']

	errormsg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		pushtoken = info["pushToken"]

		response = PushClient().publish(
			PushMessage(
				to=pushtoken,
				title="this is the title",
				body=message,
				data=data
			)
		)

		if response.status == "ok":
			return { "msg": "push sent successfully" }

		errormsg = "push failed to sent"
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/dev_delete_owner/<id>")
def dev_delete_owner(id):
	owner = query("select * from owner where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if owner != None:
		profile = owner.profile

		if os.path.exists("static/" + profile):
			os.remove("static/" + profile)

		query("delete from owner where id = " + str(owner["id"]))

		return { "msg": "Owner delete" }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_new_owner")
def add_new_owner():
	datas = db.session.query(Owner)
	columns = []

	for data in datas:
		columns.append(json.dumps(data))

	return { "columns": columns }

@app.route("/delete_location/<id>")
def delete_location(id):
	location = query("select * from location where id = " + str(id), True).fetchone()
	menus = query("select * from menu where locationId = " + str(id), True).fetchone()
	products = query("select * from product where locationId = " + str(id), True).fetchone()

	errormsg = ""
	status = ""

	if location != None:
		logo = location.logo

		if os.path.exists("static/" + logo):
			os.remove("static/" + logo)

		info = json.loads(location.info)
		menuPhotos = info["menuPhotos"]

		for photo in menuPhotos:
			if os.path.exists("static/" + photo):
				os.remove("static/" + photo)

		for menu in menus:
			if os.path.exists("static/" + menu.image):
				os.remove("static/" + menu.image)

		for product in products:
			if os.path.exists("static/" + product.image):
				os.remove("static/" + product.image)

			query("delete from product where id = " + str(product["id"]))

		query("delete from location where id = " + str(location["id"]))

		return { "msg": "Location deleted" }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/delete_user/<id>")
def delete_user(id):
	user = query("select * from user where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)

		query("delete from user where id = " + str(user["id"]))

		return { "msg": "User deleted" }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/delete_all_users")
def delete_all_users():
	users = User.query.all()
	ids = []

	for user in users:
		ids.append(user.id)

	query("delete from user where id in (" + json.dumps(ids)[1:-1] + ")")

	return { "msg": "Users deleted" }

@app.route("/twilio_test")
def twilio_test():
	'''incoming_phone_number = client.incoming_phone_numbers \
		.create(
			phone_number='+15005550006',
			voice_url='http://demo.twilio.com/docs/voice.xml'
		)'''

	message = client.messages.create(
		body='All in the game, yo',
		messaging_service_sid=mss,
		to='+16479263868'
	)

	return { "message": message.sid }

@app.route("/read_other_db")
def read_other_db():
	results = readOtherDB("select * from user where id = 1", True).fetchone()["data"]

	return results["cellnumber"]

@app.route("/open_app_in_message")
def open_app_in_message():
	message = client.messages.create(
		body='facebook://',
		messaging_service_sid=mss,
		to='+16479263868'
	)

	return { "message": message.sid }

@app.route("/add_to_incomplete_table")
def add_to_incomplete_table():
	tables = query("select * from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = 'dining_table'", True).fetchall()
	datas = []

	for info in tables:
		datas.append(info["COLUMN_NAME"])

	return { "msg": datas }

@app.route("/insert_into_table")
def insert_into_table():
	data = {
		"cellnumber": "2342342345"
	}

	insert_data = []
	columns = []
	for key in data:
		columns.append(key)
		insert_data.append("'" + str(data[key]) + "'")

	id = query("insert into user (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

	return { "id": id }

@app.route("/create_menus_with_details/<locationId>")
def create_menus_with_details(locationId):
	list = [
		{
			"menuName": "MÓN KHAI VỊ Appetizer",
			"meals": [
				{ "number": "K01", "name": "Khai vị đặc biệt.", "description": "House Special appetizers deep fried bean curd shrimp, Grilled sausage, pork, beef & chicken", "price": "12.99" },
				{ "number": "K02", "name": "Tàu hũ kỵ tôm", "description": "Deep fried bean curd shrimp", "price": "9.50" },
				{ "number": "K03", "name": "Chả giò tôm", "description": "Deep fried shrimp rolls", "price": "10.50" },
				{ "number": "K04", "name": "Chạo tôm", "description": "Shrimp on sugar cane", "price": "8.99" },
				{ "number": "K05", "name": "Nem nướng", "description": "Grilled sausage", "price": "6.00" },
				{ "number": "K06", "name": "Cánh gà chiên", "description": "Deep fried chicken wings (8 pcs)", "price": "12.00" },
				{ "number": "K07", "name": "Chả giò chay", "description": "Deep fried vegetarian spring rolls", "sizes": [{ "name": "Small", "price": "6.50" }, { "name": "Large", "price": "13.00" }] },
				{ "number": "K08", "name": "Chả giò", "description": "Deep fried pork spring rolls", "sizes": [{ "name": "Small", "price": "6.50" }, { "name": "Large", "price": "13.00" }] },
				{ "number": "K09", "name": "Gỏi cuốn", "description": "Fresh shrimp & sliced pork rolls", "sizes": [{ "name": "Small", "price": "6.50" }, { "name": "Large", "price": "13.00" }] },
				{ "number": "K10", "name": "Tôm chiến lăn bột", "description": "Fried shrimp with flour", "price": "10.50" },
				{ "number": "K11", "name": "Nem nướng cuốn", "description": "Fresh Vietnamese sausage rolls", "sizes": [{ "name": "Small", "price": "6.50" }, { "name": "Large", "price": "13.00" }] },
				{ "number": "K12", "name": "Bì cuốn", "description": "Fresh shredded pork skin rolls", "sizes": [{ "name": "Small", "price": "6.50" }, { "name": "Large", "price": "13.00" }] },
				{ "number": "K13", "name": "Thịt nướng cuốn bò/gà", "description": "Fresh grilled pork (beef/chicken) rolls", "sizes": [{ "name": "Small", "price": "6.50" }, { "name": "Large", "price": "13.00" }] },
				{ "number": "K14", "name": "Gỏi gà", "description": "Chicken salad", "price": "12.00" },
				{ "number": "K15", "name": "Gỏi xoài", "description": "Mango salad", "price": "12.00" },
				{ "number": "K16", "name": "Bộ cuốn lá lốp", "description": "Beef roll in betel leaves", "price": "12.00" },
				{ "number": "K17", "name": "Chim cút rôti", "description": "Roasted quails", "price": "16.00" }
			]
		},
		{
			"menuName": "PHO Noodle Soup",
			"meals": [
				{ "number": "PH00", "name": "Phở không", "description": "Plain rice noodle soup", "sizes": [{ "name": "Medium", "price": "9.00" }, { "name": "Large", "price": "10.00" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH01", "name": "Phở đặc biệt", "description": "House special beef rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH02", "name": "Phở tái", "description": "Rare beef with rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }] },
				{ "number": "PH03", "name": "Phở tái Bắc", "description": "Hanoi style rare beef w/ rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH04", "name": "Phở tái, nạm", "description": "Rare beef & flank w/ rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH05", "name": "Phở tái, bò viên", "description": "Rare beef & beef balls w/ rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH06", "name": "Phở tái, gân", "description": "Rare beef & tendon w/ rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH07", "name": "Phở tái, nạm, bò viên", "description": "Rare beef, flank & beef balls w/ rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH08", "name": "Phở tái, nạm, gân", "description": "Rare beef, flank & tendon w/ rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH09", "name": "Phở bò viên", "description": "Beef balls with rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH10", "name": "Phở rau cải", "description": "Vegetables with rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH11", "name": "Phở tái, gà", "description": "Rare beef & chicken with rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH12", "name": "Phở nạm gà", "description": "Beef flank and chicken with rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH13", "name": "Phở gà, bò viên", "description": "Chicken & beef balls with rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH14", "name": "Phở gà", "description": "Chicken with rice noodle soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "13.50" }], "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH15", "name": "Súp tái", "description": "Rare beef soup [w/o noodle]", "price": "10.00", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH16", "name": "Súp bò viên", "description": "Beef balls soup [w/o noodle]", "price": "10.00", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH17", "name": "Phở thịt heo nướng", "description": "Rice noodle soup with grilled pork", "price": "14.00", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH18", "name": "Phở 3 món, heo, bò, gà", "description": "Rice noodle soup with grilled pork, beef & chicken", "price": "15.50", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH19", "name": "Phở đồ biển chua cay", "description": "Seafood rice noodle soup (sweet, sour & spicy)", "price": "14.00", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH20", "name": "Phở bò kho", "description": "Beef stew with rice noodle", "price": "14.50", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH21", "name": "Phở bò tái saté", "description": "Sauté beef rice noodle soup", "price": "14.00", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH22", "name": "Phở bò tái càri", "description": "Rare beef rice noodle in curry soup", "price": "14.00", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH23", "name": "Phở càri gà", "description": "Rice noodle in curry chicken soup", "price": "14.00", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
				{ "number": "PH24", "name": "Phở càri dễ", "description": "Rice noodle in curry goat meat soup", "price": "15.50", "extras": [{ "input": "Tái", "description": "Rare beef", "price": "5.00" },{ "input": "Nạm", "description": "Flank", "price": "5.00" },{ "input": "Gân", "description": "Tendon", "price": "3.00" },{ "input": "Gà", "description": "Chicken", "price": "3.00" },{ "input": "Bò viên", "description": "Beef balls", "price": "3.00" },{ "input": "Chén soup", "description": "Extra Soup", "price": "1.00" }] },
			]
		},
		{
			"menuName": "BÁNH CUỐN Rice Flour Rolls",
			"meals": [
				{ "number": "BC01", "name": "Bánh cuốn", "description": "Ground pork flour rolls", "price": "11.00" },
				{ "number": "BC02", "name": "Bánh cuốn chả lụa", "description": "Ground pork flour rolls with meat loaf", "price": "12.00" },
				{ "number": "BC03", "name": "Bánh cuốn, bì, chả lụa", "description": "Ground pork flour rolls with shredded pork skin and meat loaf", "price": "12.50" },
				{ "number": "BC04", "name": "Bánh cuốn thịt nướng", "description": "Ground Pork flour rolls with grilled pork (beef/chicken)", "price": "12.50" },
				{ "number": "BC05", "name": "Bánh cuốn nem, bì", "description": "Ground Pork flour rolls with grilled sausage & shredded pork skin", "price": "12.50" },
				{ "number": "BC06", "name": "Bánh ướt chả lụa", "description": "Plain flour sheet with meat loaf", "price": "12.50" },
				{ "number": "BC07", "name": "Bánh ướt, bì, chả lụa", "description": "Plain flour sheet with shredded pork skin and meat loaf", "price": "12.00" },
				{ "number": "BC08", "name": "Bánh ướt, thịt nướng", "description": "Plain flour sheet with grilled pork (beef/chicken)", "price": "12.00" },
				{ "number": "BC09", "name": "Bánh ướt, nem, bì", "description": "Plain flour sheet with grilled sausage and shredded pork", "price": "12.00" }
			]
		},
		{
			"menuName": "CHÁO Congee",
			"meals": [
				{ "number": "C01", "name": "Cháo không", "description": "Plain Congee", "price": "7.00" },
				{ "number": "C02", "name": "Cháo gà", "description": "Chicken Congee", "price": "10.00" },
				{ "number": "C03", "name": "Cháo cá", "description": "Fish Congee", "price": "10.00" },
				{ "number": "C04", "name": "Cháo thập cẩm", "description": "Assorted Meat Congee", "price": "10.50" },
				{ "number": "C05", "name": "Cháo hải sản", "description": "Seafood Congee", "price": "11.00" },
				{ "number": "C06", "name": "Cháo huyết", "description": "Blood pudding congee", "price": "10.00" },
				{ "number": "C07", "name": "Dầu chao quấy", "description": "Chinese Fritter", "price": "3.00" },
			]
		},
		{
			"menuName": "HỦ TIÊU MŨ Egg Noodle Soup",
			"meals": [
				{ "number": "M01", "name": "Soup hoành thánh", "description": "Wonton soup", "price": "9.00" },
				{ "number": "M02", "name": "Mì hoành thánh", "description": "Wonton egg noodle soup", "price": "12.00" },
				{ "number": "M03", "name": "Mì đặc biệt", "description": "Meat and seafood egg noodle", "price": "14.00" },
				{ "number": "M04", "name": "Mì hải sản", "description": "Seafood egg noodle soup", "price": "5.00" },
				{ "number": "M05", "name": "Hủ tiếu mì thập cẩm", "description": "Assorted meat, seafood egg and rice noodle", "price": "14.00" },
				{ "number": "M06", "name": "Hủ tiếu mì hải sản", "description": "Seafood egg and rice noodle (with or without soup)", "price": "15.00" },
				{ "number": "M07", "name": "Hủ tiếu Mỹ Tho", "description": "South Vietnam style pork and seafood clear noodle (with or without soup)", "price": "15.00" },
				{ "number": "M08", "name": "Miến gà", "description": "Clear vermicelli chicken soup", "price": "14.00" },
				{ "number": "M09", "name": "Mì bò tái saté", "description": "Sauté beef egg noodle soup", "price": "14.00" },
				{ "number": "M10", "name": "Mì bò kho", "description": "Beef stew egg noodle", "price": "15.50" },
				{ "number": "M11", "name": "Mì tàu hũ ky tôm", "description": "Bean Curd shrimp egg noodle (with or without soup)", "price": "14.50" }
			]
		},
		{
			"menuName": "BÚN NƯỚC Vermicelli Soup",
			"meals": [
				{ "number": "BN1", "name": "Bún bò Huế", "description": "Hue' style beef, pork and blood pudding rice noodle in spicy soup", "price": "14.00" },
				{ "number": "BN2", "name": "Bún riêu cua mih ẢI RA", "description": "Vermicelli in minced pork egg blood pudding and crab paste soup", "price": "14.00" },
				{ "number": "BN3", "name": "Bún càri gà", "description": "Vermicelli in Curry chicken soup", "price": "14.00" },
				{ "number": "BN4", "name": "Bún càri dễ", "description": "Vermicelli in curry goat meat soup", "price": "15.50" },
				{ "number": "BN5", "name": "Bún hải sản chua cay", "description": "Seafood Vermicelli in soup (sweet, sour & spicy)", "price": "14.00" },
			]
		},
		{
			"menuName": "BÚN Vermicelli",
			"meals": [
				{ "number": "B01", "name": "Bún chả giò", "description": "Vermicelli with spring rolls (2 rolls)", "price": "12.50" },
				{ "number": "B02", "name": "Bún chả giò,bì,nem", "description": "Vermicelli with spring roll, shredded pork skin, grilled sausage", "price": "14.00" },
				{ "number": "B03", "name": "Bún chả giô, bì, thịt nướng", "price": "", "description": "Vermicelli with spring roll, shredded pork skin,grilled pork", "price": "14.00" },
				{ "number": "B04", "name": "Bún chả giò,thịt nướng", "price": "", "description": "Vermicelli with spring roll, and grilled pork", "price": "14.00" },
				{ "number": "B05", "name": "Bún chả giò gà nướng", "price": "", "description": "Vermicelli with spring roll, and grilled chicken", "price": "14.00" },
				{ "number": "B06", "name": "Bún bò lá lốt, bì, chả giò", "price": "", "description": "Vermicelli with beef in betel leave, shredded pork skin spring roll", "price": "14.50" },
				{ "number": "B07", "name": "Bún bò lá lốt, bì, nem", "price": "", "description": "Vermicelli with beef in betel leaves, shredded pork skin,grilled sausage", "price": "14.50" },
				{ "number": "B08", "name": "Bún bò lá lốt,bì,thịt nướng", "price": "", "description": "Vermicelli with beef in betel leave, shredded pork skin spring roll", "price": "14.50" },
				{ "number": "B09", "name": "Bún bò lá lốt,chả giò,nem", "price": "", "description": "Vermicelli with beef in betel leaves spring roll, grilled sausage", "price": "14.50" },
				{ "number": "B10", "name": "Bún bò lá lốt,nem,thịt nướng", "price": "", "description": "Vermicelli with beef in betel leaves, sausage and grilled pork", "price": "15.00" },
				{ "number": "B11", "name": "Bún chạo tôm,bì,chả giò", "price": "", "description": "Vermicelli with shrimp on sugar cane, shredded pork skin and spring roll", "price": "15.00" },
				{ "number": "B12", "name": "Bún chạo tôm, bì, nem", "price": "", "description": "Vermicelli with shrimp on sugar cane, shredded pork skin and grilled sausage", "price": "15.00" },
				{ "number": "B13", "name": "Bún chạo tôm, bì, thịt nướng", "price": "", "description": "Vermicelli with shrimp on sugar cane, shredded pork skin and grilled pork", "price": "15.00" },
				{ "number": "B14", "name": "Bún chạo tôm,nem,thịt nướng", "price": "", "description": "Vermicelli with shrimp on sugar cane, grilled sausage and grilled pork", "price": "15.00" },
				{ "number": "B15", "name": "Bún chả giò tôm (8)", "price": "", "description": "Vermicelli with shrimp rolls (8 pieces)", "price": "14.00" },
				{ "number": "B16", "name": "Bún chả giò tôm, bì, nem", "price": "", "description": "Vermicelli with shrimp roll, shredded pork skin and grilled sausage", "price": "14.50" },
				{ "number": "B17", "name": "Bún chả giò tôm,bì,thịt nướng", "price": "", "description": "Vermicelli with shrimp roll, shredded pork skin and grilled pork", "price": "15.00" },
				{ "number": "B18", "name": "Bún chả giò tôm,nem,thịt nướng", "price": "", "description": "Vermicelli with shrimp roll, grilled sausage and grilled pork", "price": "15.00" },
				{ "number": "B19", "name": "Bún Tàu hũ ky tôm (2)", "description": "Vermicelli with bean curd shrimp (2pieces)", "price": "14.50" },
				{ "number": "B20", "name": "Bún tàu hũ kỵ tôm,bì,chả giò", "description": "Vermicelli with bean curd shrimp,shredded pork skin and spring roll", "price": "14.50" },
				{ "number": "B21", "name": "Bún tàu hũ ky tôm, bì, nem", "description": "Vermicelli with bean curd shrimp, shredded pork skin and grilled sausage", "price": "14.50" },
				{ "number": "B22", "name": "Bún tàu hũ kỵ tôm,bì,thịt nướng", "description": "Vermicelli with bean curd shrimp, shredded pork skin and grilled pork", "price": "15.00" },
				{ "number": "B23", "name": "Bún tàu hũ kỵ tôm,chả giò,nem", "description": "Vermicelli with bean curd shrimp, spring roll and grilled sausage", "price": "15.00" },
				{ "number": "B24", "name": "Bún tàu hũ ky tôm,nem,thịt nướng", "description": "Vermicelli with bean curd shrimp, sausage and grilled pork", "price": "15.00" },
				{ "number": "B25", "name": "Bún heo,bò,gà nướng", "description": "Vermicelli with grilled pork, beef and chicken", "price": "15.50" },
				{ "number": "B26", "name": "Bún tàu hũ kỵ chả giò,thịt nướng", "description": "Vermicelli with bean curd shrimp, spring roll grilled pork", "price": "15.00" },
				{ "number": "B27", "name": "Bún chạo tôm chả giò,thịt nướng", "description": "Vermicelli with shrimp on sugar cane, spring roll and grilled pork", "price": "15.00" },
				{ "number": "B28", "name": "Bún bò lá lốt chả giò thịt nướng", "description": "(NEW) Vermicelli with beef in betel leaves, spring roll and grilled pork", "price": "15.50" },
				{ "number": "B29", "name": "Bún bò xào xả ớt", "description": "Vermicelli stir fried beef with lemon grass and hot pepper", "price": "15.50" }
			]
		},
		{
			"menuName": "BÁNH HỎI Thin Vermicelli",
			"meals": [
				{ "number": "BH1", "name": "Bún bò xào xả ớt", "description": "Bánh hỏi bò lá lốt", "price": "18.99" },
				{ "number": "BH2", "name": "Bún bò xào xả ớt", "description": "Bánh hỏi bò lá lốt,tàu hũ ky tôm, nem", "price": "18.99" },
				{ "number": "BH3", "name": "Bún bò xào xả ớt", "description": "Bánh hỏi,tàu hũ kỵ,chả giò,thịt nướng", "price": "18.99" },
				{ "number": "BH4", "name": "Bún bò xào xả ớt", "description": "Bánh hỏi,tàu hũ ky,nem,thịt nướng", "price": "18.99" },
				{ "number": "BH5", "name": "Bún bò xào xả ớt", "description": "Bánh hỏi chả giò tôm,nem,thịt nướng", "price": "18.99" },
				{ "number": "BH6", "name": "Bún bò xào xả ớt", "description": "Bánh hỏi heo,bò,gà nướng", "price": "18.99" }
			]
		},
		{
			"menuName": "CƠM TÂM Rice Dishes",
			"meals": [
				{ "number": "168", "name": "Cơm đặc biệt 5 món", "description": "Bean curd shrimp, steamed egg, grilled\npork, beef and shredded pork skin on rice", "price": "15.50" },
				{ "number": "169", "name": "Cơm đặc biệt 4 món", "description": "Bean curd shrimp, sausage, grilled chicken and fried egg on rice.", "price": "15.50" },
				{ "number": "170", "name": "Cơm tàu hũ ky tôm, heo gà nướng,ốpla", "description": "SPECIAL Bean curd shrimp, grilled pork chicken and fried egg on rice", "price": "15.50" },
				{ "number": "171", "name": "Cơm tàu hũ kỵ tôm sườn,bì, chả", "description": "SPECIAL Bean curd shrimp, pork chop shredded pork skin and ....\nsteamed egg on rice", "price": "15.50" },
				{ "number": "172", "name": "Cơm tàu hũ ky tôm sườn bò non,ốpla", "description": "SPECIAL Bean curd shrimp, beef short ribs, fried egg on rice", "price": "15.50" },
				{ "number": "173", "name": "Cơm tàu hũ ky tôm, gà rôti,ốpla", "description": "Bean curd shrimp roasted chicken fried egg on rice", "price": "15.50" },
				{ "number": "174", "name": "Cơm tàu hũ ky tôm gà nướng chao,ốpla", "description": "Bean curd shrimp, preserved bean curd chicken fried egg on rice.", "price": "15.50" },
				{ "number": "175", "name": "Cơm tàu hũ ky tôm (2)", "description": "Bean curd shrimp on rice (2pcs)", "price": "14.00" },
				{ "number": "176", "name": "Cơm bì, chả", "description": "Shredded pork skin and steamed egg on rice", "price": "13.00" },
				{ "number": "177", "name": "Cơm sườn nướng", "description": "Grilled pork chop on rice", "price": "14.50" },
				{ "number": "178", "name": "Cơm sườn nướng, gà nướng", "description": "Grilled pork chop, and chicken on rice", "price": "14.50" },
				{ "number": "179", "name": "Cơm sườn bì chả", "description": "Grilled pork chop shredded pork skin and steamed egg on rice", "price": "14.50" },
				{ "number": "180", "name": "Cơm sườn, bì, ốpla", "description": "Grilled pork chop, shredded pork skin and fried egg on rice", "price": "14.50" },
				{ "number": "181", "name": "Cơm sườn bò non", "description": "Grilled beef short ribs on rice", "price": "16.00" },
				{ "number": "182", "name": "Cơm sườn bò non, sườn nướng", "description": "Grilled beef short ribs and pork chop on ric", "price": "16.00" },
				{ "number": "183", "name": "Cơm sườn bò non, bì, chả", "description": "Grilled beef short ribs, shredded pork skin and steamed egg on rice", "price": "16.00" }
			]
		},
		{
			"menuName": "CƠM DĨA Rice Dishes",
			"meals": [
				{ "number": "184", "name": "Cơm sườn bò", "description": "Grilled beef short ribs shredded pork skin and fried egg on rice", "price": "16.00" },
				{ "number": "185", "name": "Cơm sườn bò non, thịt nướng", "description": "Grilled beef short ribs, grilled pork on rice", "price": "16.00" },
				{ "number": "186", "name": "Cơm thịt nướng", "description": "Grilled pork on rice", "price": "14.00" },
				{ "number": "187", "name": "Cơm thịt nướng,bì,chả", "description": "Grilled pork shredded, pork skin and steamed egg on rice", "price": "14.50" },
				{ "number": "188", "name": "Cơm tàu hũ ky tôm,chim cút rôti,ốpla", "description": "Bean curd shrimp roasted quails fried egg on rice", "price": "15.50" },
				{ "number": "189", "name": "Cơm chim cút rôti", "description": "Roasted quails on rice", "price": "15.00" },
				{ "number": "190", "name": "Cơm chim cút rôti, bì, chả", "description": "Roasted quails steamed egg shredded pork skin on rice", "price": "15.00" },
				{ "number": "191", "name": "Cơm chim cút rôti,bì,ốpla", "description": "Roasted quails fried egg and shredded pork skin on rice", "price": "15.00" },
				{ "number": "192", "name": "Cơm chim cút rôti,sườn nướng,ốpla", "description": "Roasted Quails and pork chop fried egg on rice", "price": "15.00" },
				{ "number": "193", "name": "Cơm chim cút rôti,sườn bò non,ốpla", "description": "Roasted quails grilled beef short ribs fried egg on rice", "price": "16.00" },
				{ "number": "194", "name": "Cơm chim cút rôti, gà rôti,ốpla", "description": "Roasted quails roasted chicken fried egg on rice", "price": "15.50" },
				{ "number": "195", "name": "Cơm gà rôti, bì, chả", "description": "Roasted chicken steamed egg shredded pork skin on rice", "price": "15.00" },
				{ "number": "196", "name": "Cơm gà rôti, thịt nướng, ốpla", "description": "Roasted chicken grilled pork fried egg on rice", "price": "15.00" },
				{ "number": "197", "name": "Cơm gà rôti, sườn nướng, ốpla", "description": "Roasted chicken and pork chop fried egg on rice", "price": "15.50" },
				{ "number": "198", "name": "Cơm gà nướng chao, bì chả", "description": "Preserved bean curd chicken steamed egg shredded pork skin on rice", "price": "15.00" },
				{ "number": "199", "name": "Cơm gà nướng chao, sườn nướng,ốpla", "description": "Preserved bean curd chicken pork chop fried egg on rice", "price": "15.50" }
			]
		},
		{
			"menuName": "MÓN XÀO Stir Fried",
			"meals": [
				{ "number": "203", "name": "Cơm xào xả ớt thịt bò/gà", "description": "Stir fried beef/chicken lemon grass and pepper with rice", "price": "15.50" },
				{ "number": "204", "name": "Cơm xào rau cải thịt bò/gà", "description": "Stir fried beef/chicken and mixed veggies with rice", "price": "15.50" },
				{ "number": "205", "name": "Cơm xào lăn thịt bò/gà", "description": "Stir fried curry beef/chicken and coconut milk with rice", "price": "15.50" },
				{ "number": "206", "name": "Cơm xào thơm thịt bò/gà", "description": "Stir fried beef/chicken and pineapple with rice", "price": "15.50" },
				{ "number": "207", "name": "Cơm xào saté thịt bò/gà", "description": "Stir fried beef/chicken and sauté sauce with rice", "price": "15.50" },
				{ "number": "208", "name": "Cơm xào rau cải, nấm đông cô thịt bò/gà", "description": "Stir fried beef/chicken, veggie and black mushroom with rice", "price": "15.50" },
				{ "number": "209", "name": "Cơm xào xả ớt tôm/ mực", "description": "Stir fried shrimp/squid, lemon grass and pepper with rice", "price": "16.50" },
				{ "number": "210", "name": "Cơm xào rau cải tôm/ mực", "description": "Stir fried shrimp/squid with vegetables with rice", "price": "16.50" },
				{ "number": "211", "name": "Cơm xào saté tôm/ mực", "description": "Stir fried shrimp/squid with sauté sauce with rice", "price": "16.50" },
				{ "number": "212", "name": "Cơm xào sauce Thái tôm/ mực", "description": "Stir fried shrimp/squid with Thai's sauce with rice", "price": "16.50" },
				{ "number": "213", "name": "Cơm chiên Dương Châu", "description": "Yang Chow fried rice", "price": "16.50" },
				{ "number": "214", "name": "Cơm chiên tôm", "description": "Shrimp fried rice", "price": "16.50" },
				{ "number": "215", "name": "Cơm chiên gà", "description": "Chicken fried rice", "price": "15.50" },
				{ "number": "216", "name": "Cơm chiên bò", "description": "Beef fried rice", "price": "15.50" },
				{ "number": "217", "name": "Cơm chiên, gà rôti", "description": "(SPECIAL) Roasted Chicken on fried rice", "price": "16.00" },
				{ "number": "218", "name": "Mì xào giòn thập cẩm", "description": "Stir fried assorted meat, seafood, mixed veggie with egg noodle (crispy or soft)", "price": "16.50" },
				{ "number": "219", "name": " Mì xào thập cẩm càri", "description": "Stir fried curry assorted meat, seafood, mixed veggie egg noodle (crispy or soft)", "price": "16.50" },
				{ "number": "220", "name": "Mì xào rau cải thịt bò/gà", "description": "Stir fried beef/chicken and mixed vegetables with egg noodle (crispy or soft)", "price": "16.50" },
				{ "number": "221", "name": "Mì xào hải sản", "description": "Stir fried seafood and mixed vegetables with egg noodle (crispy or soft)", "price": "16.50" },
				{ "number": "222", "name": "Hủ tiếu xào tàu xì thịt bò", "description": "Stir fried beef noodle w/black bean sauce", "price": "16.00" },
				{ "number": "223", "name": "Hủ tiếu xào saté thịt bò", "description": "Stir fried beef noodle w/sauté sauce", "price": "16.00" },
				{ "number": "224", "name": "Hủ tiếu xào thịt bò", "description": "Stir fried beef and bean sprouts with rice noodle", "price": "16.00" },
				{ "number": "225", "name": "Hủ tiếu xào rau cải bò/gà", "description": "Stir fried chicken and mixed veggie rice noodle", "price": "16.00" },
				{ "number": "226", "name": "Hủ tiếu xào hải sản", "description": "Stir fried seafood and mixed veggie with rice noodle", "price": "16.50" },
				{ "number": "227", "name": "Udon xào rau cải bò/gà", "description": "Stir fried shrimp/squid and vegetables with udon noodle", "price": "16.00" },
				{ "number": "228", "name": "Udon xào rau cải tôm/mực", "description": "Stir fried shrimp/squid, vegetables and sauté sauce with udon noodle", "price": "16.50" },
				{ "number": "229", "name": "Udon xào saté thịt bò/gà", "description": "Stir fried beef/chicken, vegetables and sauté sauce with udon noodle", "price": "16.00" },
				{ "number": "230", "name": "Udon xào saté tôm/mực", "description": "Stir fried beef/chicken and vegetables with udon noodle", "price": "16.00" },
				{ "number": "231", "name": "Udon xào thập cẩm rau cải", "description": "Stir fried assorted meat, seafood and vegetables with udon noodle", "price": "16.00" },
				{ "number": "232", "name": "Udon xào thập cẩm saté", "description": "Stir fried assorted meat, seafood, veggie and sauté sauce with udon noodle", "price": "16.00" },
				{ "number": "233", "name": "Xào lăn thịt bò/gà", "description": "Curry beef/chicken with coconut milk", "price": "17.50" },
				{ "number": "234", "name": "Xào saté thịt bò/gà", "description": "Stir fried beef/chicken with sauté sauce", "price": "17.50" },
				{ "number": "235", "name": "Xào xả ớt thịt bò/gà", "description": "Stir fried beef/chicken with lemon grass and hot pepper", "price": "17.50" },
				{ "number": "236", "name": "Xào khóm (thơm) thịt bò/gà", "description": "Stir fried beef/chicken with pineapple", "price": "17.50" },
				{ "number": "237", "name": "Xào rau cải, nấm đông cô", "description": "Stir fried beef/chicken with veggie and black mushroom", "price": "17.50" },
				{ "number": "238", "name": "Bò xào saté dĩa sắt", "description": "Stir fried beef with sauté sauce on sizzling plate", "price": "18.99" },
				{ "number": "239", "name": "Gà rôti trên dĩa sắt", "description": "Roasted chicken on sizzling plate", "price": "18.99" },
				{ "number": "240", "name": "Sườn bò non sạté dĩa sắt", "description": "Stir Fried beef short ribs with saté sauce on sizzling plate", "price": "19.99" },
				{ "number": "241", "name": "Tôm mực xào saté dĩa sắt", "description": "Stir fried shrimp and squid with saté sauce on sizzling plate", "price": "19.99" },
				{ "number": "242", "name": "Tôm mực xào tàu xì dĩa sắt", "description": "Stir fried shrimp and squid with black bean sauce on sizzling plate", "price": "19.99" },
			]
		},
		{
			"menuName": "MÓN CHAY Vegetarian",
			"meals": [
				{ "number": "V01", "name": "Chả giò chay", "description": "Deep fried veggie spring rolls", "price": "13.00" },
				{ "number": "V02", "name": "Gỏi cuốn chay", "description": "Fresh veggie rolls", "price": "13.00" },
				{ "number": "V03", "name": "Gỏi chay", "description": "Vegetarian salad", "price": "12.00" },
				{ "number": "V04", "name": "Tàu hũ chiên giòn", "description": "Deep fried tofu", "price": "10.00" },
				{ "number": "V05", "name": "Tàu hũ hấp tàu xì", "description": "Steamed tofu with black bean sauce", "price": "10.00" },
				{ "number": "V06", "name": "Pad Thái xào rau cải", "description": "Vegetable pad Thai", "price": "13.00" },
				{ "number": "V07", "name": "Cơm chiên chay", "description": "Vegetable fried rice", "price": "13.00" },
				{ "number": "V08", "name": "Rau cải xào chay", "description": "Stir fried assorted vegetable", "price": "13.00" },
				{ "number": "V09", "name": "Tàu hũ,nấm đông cô tay cầm", "description": "Tofu, vegetable and black mushroom in hot pot", "price": "14.50" },
				{ "number": "V10", "name": "Miến xào rau cải,nấm đông cô", "description": "Stir fried clear vermicelli with vegetables and black mushrooms", "price": "14.50" }
			]
		},
		{
			"menuName": "MÓN THÁI Thai Dishes",
			"meals": [
				{ "number": "T01", "name": "Pad Thái xào rau cải", "description": "Vegetable Pad Thai", "price": "13.50" },
				{ "number": "T02", "name": "Pad Thái bò", "description": "Beef Pad Thai", "price": "15.00" },
				{ "number": "T03", "name": "Pad Thái gà", "description": "Chicken Pad Thai", "price": "15.00" },
				{ "number": "T04", "name": "Pad Thái tôm", "description": "Shrimp Pad Thai", "price": "15.00" },
				{ "number": "T05", "name": "Pad Thái hải sản", "description": "Seafood Pad Thai", "price": "15.00" },
				{ "number": "T06", "name": "Cơm chiên gà Thái lan", "description": "Thai style chicken fried rice", "price": "15.00" },
				{ "number": "T07", "name": "Gà xào càri Thái", "description": "Thai style stir fried curry chicken", "price": "16.50" },
				{ "number": "T08", "name": "Bò xào càri Thái", "description": "Thai style stir fried curry beef", "price": "16.50" },
				{ "number": "T09", "name": "Gà xào chua cay Thái", "description": "Thai style stir fried curry chicken and sour spicy sauce", "price": "16.50" },
				{ "number": "T10", "name": "Hải sản xào chua cay Thái", "description": "Thai style stir fried seafood and sour spicy sauce", "price": "18.99" },
				{ "number": "T11", "name": "Tôm xào chua cay Thái", "description": "Thai style stir fried shrimp and sour spicy sauce", "price": "18.99" },
				{ "number": "T12", "name": "Mực xào chua cay Thái", "description": "Thai style stir fried squid and sour spicy sauce", "price": "18.99" },
				{ "number": "T13", "name": "Mì xào bò Thái lan", "description": "Thai style stir fried beef with egg noodle (crispy/soft)", "price": "15.00" },
				{ "number": "T14", "name": "Mì xào gà Thái lan", "description": "Thai style stir fried chicken with egg noodle (crispy/soft)", "price": "15.00" },
				{ "number": "T15", "name": "Mì xào tôm Thái lan", "description": "Thai style stir fried shrimp with egg noodle (crispy/soft)", "price": "16.50" },
				{ "number": "T16", "name": "Mì xào hải sản Thái lan", "description": "Thai style stir fried seafood with egg noodle (crispy/soft)", "price": "16.50" },
				{ "number": "CC01", "name": "Canh chua (cá bông lau hoặc tôm)", "description": "Vietnamese sweet & sour (fish or shrimp) soup\n越式鱼酸汤或虾酸汤", "price": "18.99" },
				{ "number": "CK01", "name": "Cá bông lau kho tộ hoặc thịt kho tộ", "description": "Vietnamese marinate (fish or pork) in clay pot\n卤鱼煲或卤猪肉煲", "price": "13.50" },
				{ "number": "DG01", "name": "Dưa giá", "description": "Vietnamese pickled bean sprouts\n酸芥菜", "price": "4.00" },
				{ "number": "RC01", "name": "Cơm trắng", "description": "Steam rice", "price": "2.00" },
			]
		},
		{
			"menuName": "GIẢI KHÁT Beverages",
			"meals": [
				{ "number": "D01", "name": "Chè ba màu", "description": "Combination bean pudding", "price": "6.00" },
				{ "number": "D02", "name": "Đá trái vải", "description": "Lychee with ice", "price": "5.00" },
				{ "number": "D03", "name": "Đá chanh tươi", "description": "Lime juice in sugar & ice", "price": "5.00" },
				{ "number": "D04", "name": "Cam vắt", "description": "Fresh orange juice", "price": "7.00" },
				{ "number": "D05", "name": "Soda chanh đường", "description": "Soda fesh squeezed lime juice in sugar & ice", "price": "6.00" },
				{ "number": "D06", "name": "Soda sữa hột gà", "description": "Soda whipped, condensed mil egg yolk", "price": "6.00" },
				{ "number": "D07", "name": "Soda chanh muối", "description": "Soda with salted lime juice in sugar & ice", "price": "5.00" },
				{ "number": "D08", "name": "Soda xí muội", "description": "Soda with salted plum juice in sugar & ice", "price": "5.00" },
				{ "number": "D09", "name": "Nước dừa tươi", "description": "Fresh coconut juice", "price": "5.00" },
				{ "number": "D10", "name": "Sữa đậu nành", "description": "Soya milk drink", "price": "3.00" },
				{ "number": "D11", "name": "Café sữa nóng", "description": "Vietnamese coffee with condensed milk hot drink", "price": "5.50" },
				{ "number": "D12", "name": "Café den dá", "description": "Vietnamese coffee with ice", "price": "5.50" },
				{ "number": "D13", "name": "Café sữa đá", "description": "Vietnamese coffee, condensed milk with ice", "price": "5.50" },
				{ "number": "D14", "name": "Nước ngọt", "description": "Soft drink (Coke, Sprite..)", "price": "2.00" },
				{ "number": "D15", "name": "Ice Tea", "description": "Nestea", "price": "2.00" },
				{ "number": "D16", "name": "Nước suối", "description": "Spring water", "price": "1.00" }
			],
			"menus": [
				{
					"number": "D18",
					"menuName": "Sinh tố",
					"meals": [
						{ "name": "Bơ", "description": "Avocado\n牛油果汁", "price": "6.00" },
						{ "name": "Khóm", "description": "Pineapple", "price": "6.00" },
						{ "name": "Mãng cầu", "description": "Soursop", "price": "6.00" },
						{ "name": "Sầu riêng", "description": "Durian", "price": "6.00" },
						{ "name": "Mít", "description": "Jack fruit", "price": "6.00" },
						{ "name": "Dừa tươi", "description": "Fresh coconut", "price": "6.00" },
						{ "name": "Đu đủ", "description": "Papaya", "price": "6.00" },
						{ "name": "Xoài", "description": "Mango", "price": "6.00" },
						{ "name": "Dâu tây", "description": "Strawberry", "price": "6.00" },
						{ "name": "Đậu xanh", "description": "Green bean", "price": "6.00" },
						{ "name": "Đậu đỏ", "description": "Red bean", "price": "6.00" }
					]
				}
			]
		},
		{
			"menuName": "BIA, RƯỢU Wine, Beer",
			"meals": [
				{ "number": "WBO1", "name": "Rượu KRESSMANN rượu đỏ, rượu trắng ly 8 oz", "description": "Kressmann red wine and white wine 8oz glass", "price": "10.00" },
				{ "number": "WBO2", "name": "Rượu SANTA CAROLINA rượu đỏ, rượu trắng ly 8 oz", "description": "Santa Carolina red wine and white wine 8oz glass", "price": "10.00" },
				{ "number": "WBO3", "name": "Canadian, Blue, Budweiser, Coors Light.(341ml)", "price": "5.50" },
				{ "number": "WBO4", "name": "Heineken, Tsingtao, Corona. (330ml)", "price": "6.00" }
			]
		}
	]

	products = query("select image from product where locationId = " + str(locationId), True).fetchall()
	menus = query("select image from menu where locationId = " + str(locationId), True).fetchall()

	for info in products:
		image = json.loads(info["image"])
		imageName = image["name"]

		if imageName != "":
			os.unlink("static/" + imageName)

	for info in menus:
		image = json.loads(info["image"])
		imageName = image["name"]

		if imageName != "":
			os.unlink("static/" + imageName)

	query("delete from product where locationId = " + str(locationId))
	query("delete from menu where locationId = " + str(locationId))

	def iterateList(list, pIndex, pId):
		for index, info in enumerate(list):
			description = ''

			if "description" in info:
				description = pymysql.converters.escape_string(info["description"])

			sql = "insert into menu "
			sql += "(locationId, parentMenuId, name, description, image)"
			sql += " values "
			sql += "("
			sql += str(locationId) + ", '" + str(pId) + "', "
			sql += "'" + info["menuName"] + "', "
			sql += "'" + description + "', "

			if "image" in info:
				image = info["image"]
				imageName = getId() + ".png"

				imSize = Image.open('static/' + image)

				shutil.copyfile("static/" + image, "static/" + imageName)
				os.unlink("static/" + image)

				sql += "'{\"name\":\"" + imageName + "\", \"width\": " + str(imSize.width) + ", \"height\": " + str(imSize.height) + "}'"
			else:
				sql += "'{\"name\":\"\", \"width\": 300, \"height\": 300}'"

			sql += ")"
			id = query(sql, True).lastrowid
			
			if "menus" in info:
				iterateList(info["menus"], index, id)
			
			if "meals" in info or "services" in info:
				if "meals" in info:
					infoList = "meals"
				else:
					infoList = "services"

				for eachInfo in info[infoList]:
					options = {"sizes":[],"quantities":[],"percents":[],"extras":[]}
					number = ''
					description = ''
					price = ''

					if "sizes" in eachInfo:
						options["sizes"] = eachInfo["sizes"]

					if "quantities" in eachInfo:
						options["quantities"] = eachInfo["quantities"]

					if "extras" in eachInfo:
						options["extras"] = eachInfo["extras"]

					if "number" in eachInfo:
						number = eachInfo["number"]

					if "price" in eachInfo:
						price = eachInfo["price"]

					if "description" in eachInfo:
						description = pymysql.converters.escape_string(eachInfo["description"])

					if "meals" in info:
						sql = "insert into product "
						sql += "(locationId, menuId, number, name, description, image, options, price)"
						sql += " values "
						sql += "("
						sql += str(locationId) + ", "
						sql += "'" + str(id) + "', "
						sql += "'" + number + "', "
						sql += "'" + pymysql.converters.escape_string(eachInfo["name"]) + "', "
						sql += "'" + description + "', "

						if "image" in eachInfo:
							image = eachInfo["image"]
							imageName = getId() + ".png"

							imSize = Image.open('static/' + image)

							shutil.copyfile("static/" + image, "static/" + imageName)
							os.unlink("static/" + image)

							sql += "'{\"name\":\"" + imageName + "\", \"width\": " + str(imSize.width) + ", \"height\": " + str(imSize.height) + "}', "
						else:
							sql += "'{\"name\":\"\", \"width\": 300, \"height\": 300}', "

						sql += "'" + pymysql.converters.escape_string(json.dumps(options)) + "', "
						sql += "'" + price + "'"
						sql += ")"
					else:
						sql = "insert into service "
						sql += "(locationId, menuId, name, description, image, price)"
						sql += " values "
						sql += "("
						sql += str(locationId) + ", "
						sql += "'" + str(id) + "', "
						sql += "'" + pymysql.converters.escape_string(eachInfo["name"]) + "', "
						sql += "'" + description + "', "

						if "image" in info:
							image = info["image"]
							imageName = getId() + ".png"

							imSize = Image.open('static/' + image)

							shutil.copyfile("static/" + image, "static/" + imageName)
							os.unlink("static/" + image)

							sql += "'{\"name\":\"" + imageName + "\", \"width\": " + str(imSize.width) + ", \"height\": " + str(imSize.height) + "}', "
						else:
							sql += "'{\"name\":\"\", \"width\": 300, \"height\": 300}', "

						sql += "'" + price + "'"
						sql += ")"

					query(sql)

	iterateList(list, 0, "")

	location = query("select info from location where id = " + str(locationId), True).fetchone()

	info = json.loads(location["info"])
	info["listed"] = True

	query("update location set info = '" + json.dumps(info) + "' where id = " + str(locationId))

	return { "msg": "succeed" }

@app.route("/fill_records")
def fill_records():
	products = query("select id, options from product", True).fetchall()

	for product in products:
		options = json.loads(product["options"])

		options["extras"] = []

		query("update product set options = '" + json.dumps(options) + "' where id = " + str(product["id"]))

	return { "msg": "" }

@app.route("/unfill_records")
def unfill_records():
	products = query("select id, options from product", True).fetchall()

	for product in products:
		options = json.loads(product["options"])

		if "extras" in options:
			del options["extras"]

		query("update product set options = '" + json.dumps(options) + "' where id = " + str(product["id"]))

	return { "msg": "" }

@app.route("/password")
def password():
	password = generate_password_hash('qqqqqq')

	return { "msg": "success", "password": password }
