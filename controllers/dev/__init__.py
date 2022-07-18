from flask import request
from flask_cors import CORS
from info import *
from models import *

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

@app.route("/get_id_after_insert")
def get_id_after_insert():
	data = {
		"cellnumber": "2323423",
		"password": "fdfd",
		"username": "dfd",
		"profile": "",
		"hours": "",
		"info": ""
	}

	insert_data = []
	columns = []
	for key in data:
		columns.append(key)
		insert_data.append("'" + str(data[key]) + "'")

	id = query("insert into owner (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

	return { "id": id }

@app.route("/get_num")
def get_num():
	num = query("select count(*) as num from owner group by id", True).fetchone()["num"]

	return { "num": num }

@app.route("/open_app_in_message")
def open_app_in_message():
	message = client.messages.create(
		body='facebook://',
		messaging_service_sid=mss,
		to='+16479263868'
	)

	return { "message": message.sid }

@app.route("/add_individ_time")
def add_individ_time():
	schedules = query("select * from schedule", True).fetchall()
	times = []

	for info in schedules:
		id = info["id"]

		time = json.loads(info["time"])

		day = time["day"]
		month = time["month"]
		date = time["date"]
		year = time["year"]
		hour = time["hour"]
		minute = time["minute"]

		times.append(time)

		query("update schedule set day = '" + day + "', month = '" + month + "', date = " + str(date) + ", year = " + str(year) + ", hour = " + str(hour) + ", minute = " + str(minute) + " where id = " + str(id), False)

	return { "msg": "all schedules updated", "times": times }

@app.route("/password")
def password():
	password = generate_password_hash("888888")

	return {"msg": password}

