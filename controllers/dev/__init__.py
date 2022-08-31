from flask import request
from flask_cors import CORS
from info import *
from models import *
from PIL import Image
import os, shutil, json

cors = CORS(app)

@app.route("/reset/<type>")
def reset(type):
	if type == "user" or type == "all":
		delete = False
		users = query("select * from user", True).fetchall()
		
		for user in users:
			delete = True

			query("delete from user where id = " + str(user['id']))

		if delete == True:
			query("ALTER table user auto_increment = 1")

	if type == "owner" or type == "all":
		delete = False
		owners = query("select * from owner", True).fetchall()
		for owner in owners:
			delete = True

			profile = json.loads(owner["profile"])

			if "name" in profile and profile["name"] != "" and os.path.exists("static/" + profile["name"]):
				os.remove("static/" + profile["name"])

			query("delete from owner where id = " + str(owner['id']))

		if delete == True:
			query("ALTER table owner auto_increment = 1")

	if type == "location" or type == "all":
		delete = False
		locations = query("select * from location", True).fetchall()
		for location in locations:
			delete = True
			logo = json.loads(location['logo'])

			if "name" in logo and logo["name"] != "" and os.path.exists("static/" + logo["name"]):
				os.remove("static/" + logo["name"])

			query("delete from location where id = " + str(location['id']))

		if delete == True:
			query("ALTER table location auto_increment = 1")

	if type == "menu" or type == "all":
		delete = False
		menus = query("select * from menu", True).fetchall()
		for menu in menus:
			delete = True
			image = json.loads(menu['image'])

			if image["name"] != "" and image["name"] != "" and os.path.exists("static/" + image["name"]):
				os.remove("static/" + image["name"])

			query("delete from menu where id = " + str(menu['id']))

		if delete == True:
			query("ALTER table menu auto_increment = 1")

	if type == "service" or type == "all":
		delete = False
		services = query("select * from service", True).fetchall()
		for service in services:
			delete = True
			image = json.loads(service['image'])

			if "name" in image and image["name"] != "" and os.path.exists("static/" + image["name"]):
				os.remove("static/" + image["name"])

			query("delete from service where id = " + str(service['id']))

		if delete == True:
			query("ALTER table service auto_increment = 1")

	if type == "schedule" or type == "all":
		delete = False
		schedules = query("select * from schedule", True).fetchall()
		for schedule in schedules:
			delete = True

			query("delete from schedule where id = " + str(schedule['id']))

		if delete == True:
			query("ALTER table schedule auto_increment = 1")

	if type == "product" or type == "all":
		delete = False
		products = query("select * from product", True).fetchall()
		for product in products:
			delete = True
			image = json.loads(product['image'])

			if "name" in image and image["name"] != "" and os.path.exists("static/" + image["name"]):
				os.remove("static/" + image["name"])

			query("delete from product where id = " + str(product['id']))

		if delete == True:
			query("ALTER table product auto_increment = 1")

	if type == "cart" or type == "all":
		delete = False
		carts = query("select * from cart", True).fetchall()
		for cart in carts:
			delete = True

			query("delete from cart where id = " + str(cart['id']))

		if delete == True:
			query("ALTER table cart auto_increment = 1")

	if type == "table" or type == "all":
		delete = False
		tables = query("select * from dining_table", True).fetchall()
		for table in tables:
			delete = True

			query("delete from dining_table where id = " + str(table['id']))

		if delete == True:
			query("ALTER table dining_table auto_increment = 1")

	if type == "record" or type == "all":
		delete = False
		records = query("select * from income_record", True).fetchall()
		for info in records:
			delete = True

			query("delete from income_record where id = " + str(info["id"]))

		if delete == True:
			query("ALTER table income_record auto_increment = 1")

	if type == "all":
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

@app.route("/create_test_info", methods=["POST"])
def create_test_info():
	content = request.get_json()

	locationid = content["locationid"]
	type = content["type"]
	list = { "logo": "logo.jpeg" }

	if type == "salon":
		list["menus"] = [
			{
				"menuName": "Foot Care",
				"image": "footcare.jpeg",
				"services": [
					{ "name": "Add On Shellac", "price": "15" },
					{ "name": "Shellac Removal", "price": "15" },
					{ "name": "Shellac Color Only", "price": "25.00" },
					{ "name": "Express Pedicure (30 Mins)", "price": "30.00", "description": "Includes warm whirlpool soak, color removal,\ntrimming and shaping nails, cuticles care and regular polish." },
					{ "name": "Spa Pedicure (35 Mins)", "price": "45.00", "description": "Includes warm whirlpool soak with Rock Sea Salt, nails, cuticles & callous care, a mini massage with oil, hot\ntowel wrap, and application of regular polish. And Paraffin." },
					{ "name": "Deluxe Pedicure (45 Mins)", "price": "59.00", "description": "Includes warm whirlpool soak with Foaming Flower Soap; nails, cuticles & callous care, relaxing lotion\nmassage, paraffin, and mint mask, finishing with hot towel wrap and regular polish." },
					{ "name": "The One Lavender Pedicure (55 Mins)", "price": "69.00", "description": "Enjoy the relaxing and anti-stress benefits of Lavender. This treatment starts with a gentle exfoliation\nconsisting of Lavender Salt and scrubs to remove dry skin and improve skin's texture. The feet are wrapped\nin Lavender paraffin & a mask. Regular polish is included." },
					{ "name": "Organic Pedicure (60 Mins)", "price": "75.00", "description": "Designed to brighten & lighten skin tone for a flawless, porcelain finish without the use of dangerous\nchemicals in purely natural & organic treatment.\n\nYour choice of fresh lemon & ginger/orange & ginger" }
				]
			},
			{
				"menuName": "Nail Enhancement",
				"image": "nailenhancement.jpeg",
				"services": [
					{ "name": "Dip Overlay (Short Nail)", "price": "50.00" },
					{ "name": "Dip Overlay Full Set (Short Nail)", "price": "55.00" },
					{ "name": "Dip Overlay Fill in (Short Nail)", "price": "50.00" },
					{ "name": "Acrylic Full Set (with Shellac)", "price": "50.00" },
					{ "name": "Acrylic Fill in (with Shellac)", "price": "45.00" },
					{ "name": "Solar Gel Full Set (with Shellac)", "price": "65.00" },
					{ "name": "Solar Gel Fill in (with Shellac)", "price": "55.00" },
					{ "name": "Bio Gel Overlay", "price": "55.00"},
					{ "name": "Bio Gel Full Set (with Shellac)", "price": "60.00" },
					{ "name": "Bio Gel Fill in (with Shellac)", "price": "55.00" },
					{ "name": "Nail Removed Only", "price": "15.00" },
					{ "name": "UV Gel Full Set (with Shellac)", "price": "55.00" },
					{ "name": "UV Gel Fill in (with Shellac)", "price": "50.00" },
					{ "name": "Manicure with Nails Extra", "price": "10.00" },
					{ "name": "Long Nails Extra", "price": "10.00" }
				]
			},
			{
				"menuName": "Hand Care",
				"image": "handcare.jpeg",
				"services": [
					{ "name": "Shellac Removal only", "price": "10.00" },
					{ "name": "Shellac Color Only", "price": "20.00" },
					{ "name": "Shellac Removal", "price": "10.00" },
					{ "name": "Express Manicure", "price": "30.00" }
				]
			},
			{
				"menuName": "Kids Services",
				"description": "Under 8 Years Old",
				"image": "kidsservices.jpeg",
				"services": [
					{ "name": "Princess Manicure", "price": "15.00" },
					{ "name": "Princess Pedicure", "price": "25.00" },
					{ "name": "Princess Manicure & Pedicure", "price": "35.00" },
					{ "name": "Fingers & Toe Polish", "price": "15.00" },
					{ "name": "Toe Polish", "price": "8.00" },
					{ "name": "Fingers Polish", "price": "7.00" }
				]
			},
			{
				"menuName": "Facial",
				"image": "facial.jpeg",
				"services": [
					{ "name": "Basic Facial", "price": "50.00" },
					{ "name": "Deep Cleaning", "price": "65.00" },
					{ "name": "Teen Facial", "price": "40.00" },
					{ "name": "Acne Facial Treatment", "price": "75.00" },
					{ "name": "Aqua Peeling Head", "price": "20.00" },
					{ "name": "RF Eyes Pen", "price": "10.00" },
					{ "name": "Oxygen Spayer", "price": "15.00" }
				]
			},
			{
				"menuName": "Eyelash Extensions",
				"image": "eyelashextensions.png",
				"services": [
					{ "name": "Classic Eyelash Extension Full Set", "price": "11.45" },
					{ "name": "Classic Fill 2 Weeks (30 Mins)", "price": "11.90" },
					{ "name": "Volume Lash Set Extensions Full Set", "price": "12.45" },
					{ "name": "Volume Lash Fill 2 Weeks (30 Mins)", "description": "Grilled Meatballs with Vermicelli", "price": "12.45" }
				]
			},
			{
				"menuName": "Waxing",
				"image": "waxing.jpeg",
				"menus": [
					{
						"menuName": "For Her Waxing",
						"services": [
							{ "name": "Bikini Line", "price": "25.00" },
							{ "name": "Brazilian", "price": "45.00" },
							{ "name": "Eyebrow", "price": "9.00" },
							{ "name": "Lip", "price": "6.00" },
							{ "name": "Chin", "price": "9.00" },
							{ "name": "Full Face", "price": "35.00" },
							{ "name": "Sideburns", "price": "12.00" },
							{ "name": "Half Arms", "price": "25.00" },
							{ "name": "Full Arms", "price": "35.00" },
							{ "name": "Half Leg", "price": "25.00" },
							{ "name": "Full Legs", "price": "45.00" },
							{ "name": "Under arms", "price": "20.00" },
							{ "name": "Threading Eyebrow", "price": "10.00" }
						]
					},
					{
						"menuName": "For Him Waxing",
						"description": "By Appointment Only",
						"services": [
							{ "name": "Boyzilian", "price": "75.00" },
							{ "name": "Under arms", "price": "25.00" },
							{ "name": "Full Legs", "price": "75.00" },
							{ "name": "Full Chest", "price": "45.00"},
							{ "name": "Full Back", "price": "55.00" }
						]
					}
				]
			},
			{
				"menuName": "Relaxing Massages",
				"image": "relaxingmassages.png",
				"services": [
					{ "name": "Half Body 30 Mins", "price": "45.00" },
					{ "name": "Full Body Massage 60 Mins", "price": "70.00" },
					{ "name": "Hot Stone Massage 30 Mins", "price": "50.00" },
					{ "name": "Hot Stone Massage 60 Mins", "price": "90.00" },
					{ "name": "Leg Massage 20 Mins", "price": "30.00" },
					{ "name": "Shoulders & Neck 30 Mins", "price": "45.00" },
					{ "name": "Foot Massage 20 Mins", "price": "30.00" }
				]
			}
		]
	else:
		list["menus"] = [
			{
				"menuName": "APPETIZER",
				"meals": [
					{ "number": "", "name": "HOUSE SALAD", "price": "9.00", "description": "MIXTURE OF FRESH LETTUCE AND GARDEN VEGETABLES" },
					{ "number": "", "name": "WINGS", "price": "13.00", "description": "HONEY GARLIC, BBQ, OR JERK" },
					{ "number": "", "name": "ACKEE AND SALTFISH", "price": "12.00", "description": "ACKEE SAUTEED WITH SALTFISH, SERVED WITH FRIED DUMPLING" },
					{ "number": "", "name": "JERK CHICKEN SKEWERS", "price": "12.00", "description": "JERK CHICKEN, FRIED DUMPLING AND PLANTAIN STACKED ON A SKEWER" },
					{ "number": "", "name": "JERK PORK SKEWERS", "price": "13.00", "description": "JERK PORK, FRIED DUMPLING AND PLANTAIN STACKED ON A SKEWER" },
					{ "number": "", "name": "SHRIMP", "price": "14.50", "description": "CURRY OR JERK" },
					{ "number": "", "name": "JAMAICAN PATTY", "price": "3.50", "description": "LIGHT, DELICATE PASTRY FILLED WITH A CHOICE OF\nSPICY BEEF, MILD BEEF, CHICKEN OR VEGGIE" },
					{ "number": "", "name": "JERK PORK", "price": "12.50", "description": "PORK MARINATED IN OUR SCOTTHILL JERK SEASONING" }
				]
			},
			{
				"menuName": "NOODLE SOUP",
				"meals": [
					{ "number": "", "name": "Veggie Soup", "price": "12.95", "description": "" },
					{ "number": "", "name": "Chicken Soup", "price": "14.95", "description": "" }
				]
			}
		]

	products = query("select image from product where locationId = " + str(locationid), True).fetchall()
	menus = query("select image from menu where locationId = " + str(locationid), True).fetchall()

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

	query("delete from product where locationId = " + str(locationid))
	query("delete from menu where locationId = " + str(locationid))

	def iterateList(list, pIndex, pId):
		for index, info in enumerate(list):
			description = ''

			if "description" in info:
				description = pymysql.converters.escape_string(info["description"])

			sql = "insert into menu "
			sql += "(locationId, parentMenuId, name, description, image)"
			sql += " values "
			sql += "("
			sql += str(locationid) + ", '" + str(pId) + "', "
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
						sql += str(locationid) + ", "
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
						sql += str(locationid) + ", "
						sql += "'" + str(id) + "', "
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

						sql += "'" + price + "'"
						sql += ")"

					query(sql)

	iterateList(list["menus"], 0, "")

	location = query("select owners, info from location where id = " + str(locationid), True).fetchone()

	# salons only
	if type == "salon":
		workers = "(" + location["owners"][1:-1] + ")"

		workers = query("select id, profile from owner where id in " + workers, True).fetchall()

		for index, info in enumerate(workers):
			profile = json.loads(info["profile"])
			imSize = Image.open("static/profile" + str(index + 1) + ".jpg")
			profileName = profile["name"]

			if profile["name"] != "": # profile exist
				shutil.copyfile("static/profile" + str(index + 1) + ".jpg", "static/" + profile["name"])
			else:
				profileName = getId() + ".jpeg"
				shutil.copyfile("static/profile" + str(index + 1) + ".jpg", "static/" + profileName)
				profile["name"] = profileName
				profile["width"] = str(imSize.width)
				profile["height"] = str(imSize.height)

			os.unlink("static/profile" + str(index + 1) + ".jpg")

			query("update owner set profile = '" + json.dumps(profile) + "' where id = " + str(info["id"]))

	imSize = Image.open('static/' + list["logo"])

	info = json.loads(location["info"])
	info["listed"] = True

	logoName = getId() + ".png"
	logo = json.dumps({"name": logoName, "width": str(imSize.width), "height": str(imSize.height)})

	query("update location set logo = '" + logo + "', info = '" + json.dumps(info) + "' where id = " + str(locationid))

	shutil.copyfile("static/" + list["logo"], "static/" + logoName)
	os.unlink("static/" + list["logo"])

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
