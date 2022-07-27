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

@app.route("/move")
def move():
	products = query("select id, options from product", True)

	for data in products:
		options = json.loads(data["options"])

		quantities = options["quantities"]

		for key in quantities:
			info = key["name"]

			del key["name"]

			key["input"] = info

		options["quantities"] = quantities

		query("update product set options = '" + json.dumps(options) + "' where id = " + str(data["id"]))

	return { "msg": "sizes removed and options added" }

@app.route("/insert_real_into_table")
def insert_real_into_table():
	query("delete from product where id > 11")
	query("delete from menu where id > 4")

	query("alter table product auto_increment = 12")
	query("alter table menu auto_increment = 5")
	list = [
		{
			"menuName": "Mon Khai Vi - Appetizers",
			"meals": [
				{ "name": "BÒ TÁI CHANH", "price": "15.95", "description": "Beef Ceviche in Lime Juice Selag" },
				{ "name": "CHẢ GIÒ TÔM THỊT (2–4 CUỐN)", "description": "Deep Fried Spring Rolls. \"Pork and Shrimp\" (2-4 rolls)", "quantities": [{ "name": "2 Rolls", "price": "7.95" }, { "name": "4 Rolls", "price": "11.95" }] },
				{ "name": "GÒI CUỐN TÔM THỊT (2-4 CUỐN)", "description": "Fresh Rolls with Shrimp and Pork (2-4 rolls)", "quantities": [{ "name": "2 Rolls", "price": "7.95" }, { "name": "4 Rolls", "price": "11.95" }] },
				{ "name": "GỒI CUỐN BỐN MÙA", "description": "Fresh Rolls with Avocado, Grilled Beef - Chicken - Shrimp (2-4 rolls)", "quantities": [{ "name": "4 Rolls", "price": "14.95" }] },
				{ "name": "GÒI CUỐN GÀ NƯỚNG (2-4 CUỐN)", "description": "Fresh Rolls with Grilled Chicken (2-4 rolls)", "quantities": [{ "name": "2 Rolls", "price": "7.95" }, { "name": "4 Rolls", "price": "11.95" }] },
				{ "name": "GÓI CUỐN NEM NƯỚNG (2-4 CUỐN)", "description": "Fresh Rolls with Pork Meatballs (2-4 rolls)", "quantities": [{ "name": "2 Rolls", "price": "7.95" }, { "name": "4 Rolls", "price": "11.95" }] },
				{ "name": "GÓI CUỐN BÒ NƯỚNG (2-4 CUỐN)", "description": "Fresh Rolls with Grilled Beef (2-4 rolls)", "quantities": [{ "name": "2 Rolls", "price": "7.95" }, { "name": "4 Rolls", "price": "11.95" }] },
				{ "name": "GỎI CUỐN THỊT NƯỚNG (24 CUỐN)", "description": "Fresh Rolls with Grilled Pork (2-4 rolls)", "quantities": [{ "name": "2 Rolls", "price": "7.95" }, { "name": "4 Rolls", "price": "11.95" }] },
				{ "name": "GỒI CUỐN ĐẬU HỦ (2-4 CUỐN)", "description": "Fresh Rolls with Tofu (2-4 rolls)", "quantities": [{ "name": "2 Rolls", "price": "7.95" }, { "name": "4 Rolls", "price": "11.95" }] },
				{ "name": "GỎI NGÓ SEN TÔM THỊT", "description": "Lotus Root with Pork and Shrimp Salad (Spicy and Peanut)", "quantities": [{ "name": "4 Rolls", "price": "12.95" }] },
				{ "name": "GỎI XOÀI TÔM THÁI LAN", "description": "Thai Shrimp Mango Salad (Spicy and Peanut)", "quantities": [{ "name": "4 Rolls", "price": "11.90" }] },
				{ "name": "CÁNH GÀ CHIẾN (BƠ NƯỚC MẮM, I LOVE PHỞ SAUSE, RANG MUỐI)", "description": "Deep Fired Chicken Wings with Butter or Fish Sause, I LOVE PHO Sause, Roasted Salt", "quantities": [{ "name": "4 Rolls", "price": "12.90" }] },
				{ "name": "GỎI GÀ", "description": "Chicken Salad (Spicy and Peanut)", "quantities": [{ "name": "4 Rolls", "price": "12.90" }] },
				{ "name": "GỞI VỊT", "description": "Duck Salad (Spicy and Peanu", "quantities": [{ "name": "4 Rolls", "price": "13.90" }] },
				{ "name": "CHẢ MỰC CHIẾN", "description": "Deep Fried Squid Cake", "quantities": [{ "name": "4 Rolls", "price": "16.90" }] },
				{ "name": "MỰC KHOANH VÀ KHOAI TÂY TÂM BỘT CHIÊN GIÒN", "description": "Calamari with Wedge Fried Pototes", "quantities": [{ "name": "4 Rolls", "price": "14.90" }] },
				{ "name": "TÔM VÀ KHOAI TÂY TÂM BỘT CHIÊN GIÒN", "description": "Shrimp Popcom with Wedges Fried Potatoes", "quantities": [{ "name": "4 Rolls", "price": "16.90" }] },
				{ "name": "ĐẬU HỦ CHIẾN", "description": "Deep Fried Tofu", "quantities": [{ "name": "4 Rolls", "price": "11.90" }] }
			]
		},
		{
			"menuName": "Banh Cuon - Rice Rolls",
			"meals": [
				{ "name": "BÁNH CUỐN CHẢ LỤA, BÁNH CÔNG", "description": "Steamed Rice Rolls with Vietnamese Ham, Shrimp Cake", "quantities": [{ "name": "4 Rolls", "price": "13.50" }] },
				{ "name": "BÁNH CUỐN CHÀ LỤA", "description": "Steamed Rice Rolls with Vietnamese Pork Ham", "quantities": [{ "name": "4 Rolls", "price": "11.90" }] },
				{ "name": "BÁNH CUỐN NÓNG", "description": "Steamed Ground Pork Rice Rolls", "quantities": [{ "name": "4 Rolls", "price": "11.90" }] },
				{ "name": "BÁNH ƯỚT CHẢ LỤA, BÁNH CÔNG", "description": "Steamed Plain Rice Roll with Vietnamese Pork Ham & Shrimp Cake", "quantities": [{ "name": "4 Rolls", "price": "13.50" }] },
				{ "name": "BÁNH ƯỚT CHẢ LỤA", "description": "Steamed Plain Rice Roll with Vietnamese Pork Ham", "quantities": [{ "name": "4 Rolls", "price": "11.90" }] },
				{ "name": "BÁNH ƯỚT NÓNG", "description": "Steamed Plain Rice Rolls", "quantities": [{ "name": "4 Rolls", "price": "11.90" }] }
			]
		},
		{
			"menuName": "Pho - Beef Rice Noodle",
			"meals": [
				{ "name": "PHÓ SƯỜN BỘ", "description": "Rib Backbone with Rice Noodle Soup", "sizes": [{ "name": "Large", "price": "16.45" }] },
				{ "name": "PHỞ ĐẶC BIỆT “I LOVE PHO“", "description": "\"I Love Pho\" Special Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "11.00" }, { "name": "Large", "price": "11.75" }] },
				{ "name": "PHỞ TÁI", "description": "Rare Beef w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỞ TÁI, NAM", "description": "Rare Beef & Lightly Fat Well-done Beef w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỜ TÁI, SÁCH", "description": "Rare Beef & Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỞ TÁI, GẦN", "description": "Rare Beef & Beef Tendon w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỞ TÁI, GÀ", "description": "Rare Beef & Chicken w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỞ TÁI, BÒ VIÊN", "description": "Rare Beef & Beef Balls w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỞ TÁI, VỀ DÒN", "description": "Rare Beef & Tendon Brisket w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỞ TÁI, GÂN, SÁCH", "description": "Rare Beef, Beef Tendon, Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ NAM", "description": "Lightly Fat Well-done Beef w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ NẠM, GÀ", "description": "Lightly Fat Well-done Beef & Chicken w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ NAM, BỎ VIÊN", "description": "Lightly Fat Well-done Beef & Beef Balls w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ NAM, SÁCH", "description": "Lightly Fat Well-done Beef & Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỞ NẠM, GẦN", "description": "Lightly Fat Well-done Beef & Beef Tendon w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỞ NẠM, VỀ DÒN", "description": "Lightly Fat Well-done Beef & Tendon Brisket w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
				{ "name": "PHỞ NẠM, GÂN, SÁCH", "description": "Lightly Fat Well-done Beef & Beef Tendon, Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ GÀ", "description": "Chicken w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ GÀ, BÒ VIÊN", "description": "Chicken & Beef Balls w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHO GÀ, GÅN", "description": "Chicken & Beef Tendon w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ GÀ, SÁCH", "description": "Chicken & Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ GÀ, VỀ DÒN", "description": "Chicken & Tendon Brisket w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ GÀ, GÂN, SÁCH", "description": "Chicken & Beef Tendon, Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ VẺ DÒN", "description": "Tendon Brisket w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ RAU CẢI, ĐẬU HŨ", "description": "Vegetables & Tofu w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ BÒ VIÊN", "description": "Beef Balls w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
				{ "name": "PHỞ KHÔNG", "description": "Plain Noodle Soup", "sizes": [{ "name": "Medium", "price": "10.75" }, { "name": "Large", "price": "12.75" }] },
			]
		},
		{
			"menuName": "Mi, Hu Tieu - Egg Noodle & Rice Noodle Soup",
			"meals": [
				{ "name": "TOM-YUM SOUP", "description": "Choice of Chicken or Beef or Shrimp (Noodle NOT Include)", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }] },
				{ "name": "MÌ ĐẶC BIỆT (KHÔ HOẶC NƯỚC)", "description": "\"House\" Special Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "MI DO BIEN", "description": "Seafood with Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "MỈ XÁ XÍU", "description": "B.B.Q. Pork with Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "HỦ TIỂU NAM VANG ĐẶC BIỆT", "description": "\"Nam Vang\" Special Rice Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "HỦ TIÊU ĐÓ BIÊN", "description": "Seafood with Rice Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "HỦ TIÊU MÌ ĐẶC BIỆT", "description": "\"House\" Special Rice Noodle & Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "HỦ TIÊU MÌ ĐỎ BIỂN", "description": "Seafood with Rice Noodle & Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "HỦ TIÊU MỸ THO ĐẶC BIỆT", "description": "\"My Tho\" House Special Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "14.545" }] },
				{ "name": "HỦ TIÊU MỸ THỌ ĐÔ BIÊN", "description": "\"My Tho Seafood w/Transparent Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "14.545" }] },
				{ "name": "MI BO KHO", "description": "Beef Stewed with Egg Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "HỦ TIỂU BỘ KHO", "description": "Beef Stewed with Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "HỦ TIÊU MÌ BÒ KHO", "description": "Beef Stewed with Rice Noodle & Egg Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "SÚP HOÀNH THÁNH", "description": "Wonton Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				{ "name": "MÌ HOÀNH THÁNH", "description": "B.B.Q. Pork & Wonton with Egg Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
			]
		},
		{
			"menuName": "Mi, Hu Tieu Xao - Stir Fried Egg/Rice Noodle (Pad Thai)",
			"meals": [
				{ "name": "MÌ XÀO THẬP CẢM (ONE SIZE)", "description": "Stir Fired Egg Noodle with Assorted Meat & Seafood", "price": "16.90" },
				{ "name": "MÌ XÀO ĐỒ BIÊN (ONE SIZE)", "description": "Stir Fried Egg Noodle with Seafood", "price": "16.90" },
				{ "name": "MÌ XÀO GIÒN THẬP CẢM (ONE SIZE)", "description": "Thick Lay of Fired Egg Noodle with Assorted Meat & Seafood & Veg", "price": "16.90" },
				{ "name": "MÌ XÀO GIÒN ĐỘ BIÊN (ONE SIZE)", "description": "Thick Lay of Fired Egg Noodle Top with Seafood & Veg", "price": "17.45" },
				{ "name": "HỦ TIÊU XÀO THỊT BÒ (ONE SI", "description": "Stir Fried Rice Noodle with Beef", "price": "15.90" },
				{ "name": "PAD THAI BO (ONE SIZE)", "description": "Beef Pad Thai (Spicy and Peanut)", "price": "15.90" },
				{ "name": "PAD THAI GÀ (ONE SIZE)", "description": "Chicken Pad Thai (Spicy and Peanut)", "price": "15.90" },
				{ "name": "PAD THAI TÔM (ONE SIZE)", "description": "Shrimp Pad Thai (Spicy and Peanut)", "price": "16.45" }
			]
		},
		{
			"menuName": "Bun - Vermicelli (Served W/House Sauce and Peanut",
			"meals": [
				{ "name": "BÚN ĐẬU HŨ CHIẾN", "description": "Deep Fried Tofu with Vermicelli", "price": "11.45" },
				{ "name": "BÚN CHẢ GIÒ", "description": "Deep Fried Spring Rolls with Vermicelli", "price": "11.90" },
				{ "name": "BÚN THỊT NƯỚNG", "description": "Grilled Pork with Vermicelli", "price": "12.45" },
				{ "name": "BÚN NEM NƯỚNG", "description": "Grilled Meatballs with Vermicelli", "price": "12.45" },
				{ "name": "BÚN GÀ NƯỚNG", "description": "Grilled Chicken with Vermicelli", "price": "12.90" },
				{ "name": "BÚN BÒ NƯỚNG", "description": "Grilled Beef with Vermicelli", "price": "12.90" },
				{ "name": "BÚN TÔM CÀNG NƯỚNG", "description": "Grilled Jumbo Shrimp with Vermicelli", "price": "16.90" },
				{ "name": "BÚN CHẢ GIÒ, THỊT NƯỚNG", "description": "Grill Pork & Spring Roll with Vermicelli", "price": "12.90" },
				{ "name": "BÚN CHẢ GIÒ, NEM NƯỚNG", "description": "Grilled Meatballs & Spring Roll with Vermicelli", "price": "12.90" },
				{ "name": "BÚN CHẢ GIÒ, GÀ NƯỚNG", "description": "Grilled Chicken & Spring Roll with Vermicelli", "price": "12.90" },
				{ "name": "BÚN CHẢ GIÒ, BÒ NƯỚNG", "description": "Grilled Beef & Spring Roll with Vermicelli", "price": "12.90" },
				{ "name": "BÚN CHẢ GIÒ, CHẠO TÔM", "description": "Minced Shrimp on Sugar Cane & Spring Roll with Vermicelli", "price": "12.90" },
				{ "name": "BÚN CHÀ GIÒ, THỊT NƯỚNG, NEM NƯỚNG", "description": "Grill Pork, Grilled Meatballs & Spring Roll with Vermicelli", "price": "13.45" },
				{ "name": "BÚN CHẢ GIÒ, NEM NƯỚNG, CHẠO TÔM", "description": "Grilled Meatballs, Minced Shrimp on\nSugar Cane & Spring Roll with Vermicelli", "price": "13.75" },
				{ "name": "BÚN THỊT NƯỚNG, NEM NƯỚNG", "description": "Grill Pork, Grilled Meatballs with Vermicelli", "price": "12.90" },
				{ "name": "BÚN THỊT NƯỚNG, BÒ LÁ LÓP", "description": "Grill Pork, Grilled Beef Wrapped in Herb Leaves with Vermicelli", "price": "13.95" },
				{ "name": "BÚN THỊT NƯỚNG, TÔM CÀNG", "description": "Grill Pork, Grilled Jumbo Shrimp with Vermicelli", "price": "15.90" },
				{ "name": "BÚN THỊT NƯỚNG, CHẠO TÔM", "description": "Grill Pork, Minced Shrimp on Sugar Cane with Vermicelli", "price": "12.90" },
				{ "name": "BÚN BÒ LÁ LỚP, NEM NƯỚNG", "description": "Grilled Beef Wrapped in Herb Leaves, Grilled Meatballs with Vermicelli", "price": "14.45" },
				{ "name": "BÚN BÒ LÁ LỚP, CHẠO TÔM", "description": "Grilled Beef Wrapped in Herb Leaves,\nMinced Shrimp on Sugar Cane with Vermicelli", "price": "14.95" },
				{ "name": "BÚN BÒ XÀO CỦ HÀNH", "description": "Stir Fried Beef & Onion with Vermicelli", "price": "13.95" },
				{ "name": "BÚN BÒ XÀO SATE", "description": "Stir Fried Beef with Satay Sauce on Vermicelli (Spicy)", "price": "13.95" },
				{ "name": "BÚN BÒ XÀO XẢ ỚT", "description": "Stir Fried Beef with Lemon Grass & Hot Pepper on Vermicelli (Spicy and Peanut)", "price": "13.95" }
			]
		},
		{
			"menuName": "Bun - Vermicelli Soup",
			"meals": [
				{ "name": "BÚN BÒ HUẾ", "description": "\"Hue\" Style Beef, Pork & Vietnamese Sausage on Vermicelli", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }]},
				{ "name": "BÚN MÁM", "description": "Fish, Shrimp, & Pork in Fish-Paste Soup with Vermicelli", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }]},
				{ "name": "BÚN RIỀU", "description": "Shrimp, Crab Meat & Pork in Paste Soup with Vermicelli", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }]},
				{ "name": "BÚN ỐC", "description": "Whelks Soup with Vermicelli (Only One Size)", "sizes": [{ "name": "Medium", "price": "15.90" }]},
				{ "name": "BÚN CHẢ CÁ I LOVE PHỞ", "description": "I Love Pho Style Fried Fish Cake Soup with Vermicelli (Only One Size)", "sizes": [{ "name": "Medium", "price": "15.90" }]},
				{ "name": "BUN MANG VIT", "description": "Duck & Bamboo Shoot with Vermicelli Soup", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }]},
				{ "name": "BÚN HOẶC CƠM CÀ RI GÀ", "description": "Curry Chicken with Vermicelli or Steamed Rice", "sizes": [{ "name": "Medium", "price": "10.50" }, { "name": "Large", "price": "11.95" }]}
			]
		},
		{
			"menuName": "Com Tam - Steamed Broken Rice Dishes",
			"meals": [
				{ "name": "CƠM TÂM SƯỜN NƯỚNG", "description": "Grilled Pork Chop with Steamed Broken Rice", "price": "12.45" },
				{ "name": "CƠM TÂM GÀ NƯỚNG", "description": "Grilled Chicken with Steamed Broken Rice", "price": "12.90" },
				{ "name": "CƠM TÂM SƯỜN BÒ NƯỚNG", "description": "Grilled Beef Ribs with Steamed Broken Rice", "price": "13.45" },
				{ "name": "CƠM TÁM TÔM NƯỚNG", "description": "Grilled Shrimp with Steamed Broken Rice", "price": "16.90" },
				{ "name": "CƠM TẤM SƯỜN NƯỚNG, ỐP-LA", "description": "Grilled Pork Chop with Fried Egg on Steamed Broken Rice", "price": "12.45" },	
				{ "name": "CƠM TÁM SƯỜN NƯỚNG, CHẢ TRỨNG", "description": "Grilled Pork Chop with Steamed Egg on Steamed Broken Rice", "price": "12.45" },
				{ "name": "CƠM TÁM SƯỜN NƯỚNG, TÔM NƯỚNG", "description": "Grilled Pork Chop with Grilled Shrimp on Steamed Broken Rice", "price": "15.45" },
				{ "name": "CƠM TÂM SƯỜN NƯỚNG, CHẢ TRỨNG, ỐP-LA", "description": "Grilled Pork Chop, Steamed Egg with Fried Egg on Steamed Broken Rice", "price": "12.45" },
				{ "name": "CƠM TÁM SƯỜN NƯỚNG, GÀ NƯỚNG", "description": "Grilled Pork Chop, Grilled Chicken with Steamed Broken Rice", "price": "12.90" },
				{ "name": "CƠM TÁM GÀ NƯỚNG, ỐP-LA", "description": "Grilled Chicken with Fried Egg on Steamed Broken Rice", "price": "12.90" },
				{ "name": "CƠM TÁM GÀ NƯỚNG, CHẢ TRỨNG", "description": "Grilled Chicken with Steamed Egg on Steamed Broken Rice", "price": "12.90" },
				{ "name": "CƠM TÁM GÀ NƯỚNG, TÔM NƯỚNG", "description": "Grilled Chicken with Grilled Shrimp on Steamed Broken Rice", "price": "15.90" },
				{ "name": "CƠM TÂM GÀ NƯỚNG, CHẢ TRỨNG, OP-LA", "description": "Grilled Chicken, Steamed Egg with Fried Egg on Steamed Broken Rice", "price": "12.90" },
				{ "name": "CƠM TÂM GÀ NƯỚNG, SƯỜN NƯỚNG, ỐP-LA", "description": "Grilled Chicken, Grilled Pork Chop with Fried Egg on Steamed Broken Rice", "price": "13.20" },
				{ "name": "CƠM TÁM GÀ NƯỚNG, SƯỜNG NƯỚNG, CHẢ TRỨNG", "description": "Grilled Chicken, Grilled Pork Chop with Steamed Egg on Steamed Broken Rice", "price": "13.20" },
				{ "name": "COM TAM 4 MAU", "description": "Grilled Chicken, Grilled Pork Chop, Steamed Egg. Fried Egg on Steamed Broken Rice", "price": "14.45" }
			]
		},
		{
			"menuName": "Com Xao - Stir Rice Dishes",
			"meals": [
				{ "name": "CƠM BÒ XÀO RAU CẢI", "description": "Stir Fired Beef with Vegetable on Steamed Rice.", "price": "15.90" },
				{ "name": "CƠM GÀ XÀO RAU CẢI", "description": "Stir Fried Chicken with Vegetable on Steamed Rice", "price": "15.90" },
				{ "name": "CƠM TÔM XÀO RAU CẢI", "description": "Stir Fried Shrimp with Vegetable on Steamed Rice", "price": "16.90" },
				{ "name": "CƠM MỰC XÀO RAU CẢI", "description": "Stir Fried Squid with Vegetable on Steamed Rice", "price": "16.45" },
				{ "name": "CƠM ĐẬU HŨ XÀO RAU CẢI", "description": "Stir Fried Tofu with Vegetable on Steamed Rice", "price": "15.90" },
				{ "name": "CƠM BÒ XÀO SẢ ỚT", "description": "Stir Fried Beef with Lemon Grass & Hot Pepper on Steamed Rice (Spicy)", "price": "15.90" },
				{ "name": "CƠM GÀ XÀO SẢ ỚT", "description": "Stir Fried Chicken with Lemon Grass & Hot Pepper on Steamed Rice (Spicy)", "price": "15.90" },
				{ "name": "CƠM TÔM XÀO SẢ ỚT", "description": "Stir Fried Shrimp with Lemon Grass & Hot Pepper on Steamed Rice (Spicy)", "price": "16.90" },
				{ "name": "CƠM MỰC XÀO SẢ ỚT", "description": "Stir Fried Squid with Lemon Grass & Hot Pepper on Steamed Rice (Spicy)", "price": "16.45" },
				{ "name": "CƠM BÒ XÀO SATÉ", "description": "Stir Fried Beef with Satay Sauce on Steamed Rice (Spicy)", "price": "15.90" },
				{ "name": "CƠM GÀ XÀO SATÉ", "description": "Sur Fried Chicken with Satay Sauce on Steamed Rice (Spicy)", "price": "15.90" },
				{ "name": "CƠM TÔM XÀO SATÉ", "description": "Stir Fried Shrimp with Satay Sauce on Steamed Rice (Spicy)", "price": "16.90" },
				{ "name": "CƠM MỰC XÀO SATÉ", "description": "Stir Fried Squid with Satay Sauce on Steamed Rice (Spicy)", "price": "16.45" },
				{ "name": "CƠM GÀ XÀO THÁI LAN", "description": "\"Thai Style\" Stir Fried Chicken with Steamed Rice (Spicy)", "price": "15.90" },
				{ "name": "CƠM BỎ XÀO THÁI LAN", "description": "\"Thai Style\" Stir Fried Beef with Steamed Rice (Spicy)", "price": "15.90" },
				{ "name": "CƠM TÔM XÀO THÁI LAN", "description": "\"Thai Style\" Stir Fried Shrimp with Steamed Rice (Spicy)", "price": "16.90" },
				{ "name": "CƠM MỰC XÀO THÁI LAN", "description": "\"Thai Style\" Stir Fried Squid with Steamed Rice (Spicy)", "price": "16.45" },
				{ "name": "CƠM BÒ LÚC LÁC", "description": "Fried Sautéed Cubes of Beef with Steamed Rice", "price": "16.90" }
			]
		},
		{
			"menuName": "Com Chien - Fried Rice Dishes",
			"meals": [
				{ "name": "CƠM CHIẾN GÀ NƯỚNG", "description": "Grilled Chicken on Fried Rice", "price": "15.90" },
				{ "name": "CƠM CHIÊN BÒ", "description": "Beef Fried Rice", "price": "15.90" },
				{ "name": "CƠM CHIẾN TÔM", "description": "Shrimp Fried Rice", "price": "15.90" },
				{ "name": "CƠM CHIÊN XÁ XÍU", "description": "B.B.Q. Pork Fried Rice", "price": "15.90" },
				{ "name": "CƠM CHIÊN DƯƠNG CHÂU", "description": "Yang Chow Fried Rice", "price": "16.45" },
				{ "name": "CƠM CHIÊN ĐỒ BIÊN", "description": "Seafood on Fried Rice", "price": "15.50" },
				{ "name": "CƠM CHIẾN RAU CẢI", "description": "Vegetable Fried Rice", "price": "15.90" }
			]
		},
		{
			"menuName": "Chao - Congee",
			"meals": [
				{ "name": "CHÁO CÁ", "description": "Fish Congee", "price": "12.90" },
				{ "name": "CHÁO BÒ", "description": "Beef Congee", "price": "12.90" },
				{ "name": "CHÁO ĐÔ BIỂN", "description": "Seafood Congee", "price": "13.45" },
				{ "name": "CHÁO GÀ", "description": "Chicken Congee", "price": "12.90" },
				{ "name": "CHẢO VỊT", "description": "Duck Congee", "price": "13.45" }
			]
		},
		{
			"menuName": "Banh Canh - Udon Noodle Soup",
			"meals": [
				{ "name": "BÁNH CẠNH CỦA", "description": "Crab with Udon Noodle Soup", "price": "12.90" },
				{ "name": "BÁNH CẠNH GIÒ HEO", "description": "Pork Hock with Udon Noodle Soup", "price": "12.90" },
				{ "name": "BÁNH CẠNH TÔM THỊT", "description": "Pork & Shrimp with Udon Noodle Soup", "price": "12.90" }
			]
		},
		{
			"menuName": "Banh Hoi - Platter",
			"meals": [
				{ "name": "CHÀ MỰC ĐẬU HÙ CHIÊN GIÒN BÚN MÁM TÔM", "description": "Deep Fried Squid Cake Tofu & Vermicelli w/Shrimp Sauce", "price": "25.50" },
				{ "name": "BÁNH XÈO", "description": "Vietnamese Pancake with Pork, Shrimp & Bean Sprouts", "price": "13.90" },
				{ "name": "NEM NƯỚNG, THỊT NƯỚNG, RAU SỐNG, BÁNH HỒI", "description": "Grilled Meat Balls, Grilled Pork Served w/Thin Vermicelli & Vegetables", "price": "23.50" },
				{ "name": "NEM NƯỚNG, CHẠO TÔM, RAU SÓNG, BÁNH HỎI", "description": "Grilled Meat Balls, Minced Shnmp on Sugar Cane\nServed with Thin Vermicelli & Vegetable", "price": "23.50" },
				{ "name": "NEM NƯỚNG, BÒ CUỐN LÁ LÓT, RAU SÓNG, BÁNH HỎI", "description": "Grilled Meat Balls, Grilled Beef Wrapped in Herb Leaves\nServed with Thin Vermicelli & Vegetables", "price": "23.50" },
				{ "name": "CHẠO TÔM, BÒ CUỐN LÁ LÓT, RAU SỐNG, BÁNH HỎI", "description": "Minced Shrimp on Sugar Cane, Grilled Beef Wrapped in Herb Leaves\nServed with Thin Vermicelli & Vegetables", "price": "23.50" },
				{ "name": "CÁ SALMON NƯỚNG, RAU SÓNG, BÁNH HỎI", "description": "Grilled Salmon with Lemon Served with Thin Vermicelli & Vegetables", "price": "23.50" },
				{ "name": "BO 7 MÓN", "description": "Combine 7 types of Beef on Dishes (For 2 Persons)", "price": "39.50" },
				{ "name": "BÒ NHÚNG DÁM", "description": "Beef Deep in Spicy Vinegar Hotpot (For 2 Persons)", "price": "36.50" }			
			]
		},
		{
			"menuName": "Lau - Hot Pot",
			"meals": [
				{ "name": "LÂU THẬP CẢM", "description": "Assorted Seafood Hotpot", "price": "62.50" },
				{ "name": "LÂU THÁI (CAY)", "description": "\"Thai\" Special Hotpot (Spicy)", "price": "62.50" }
			]
		},
		{
			"menuName": "Lunch and Dinner (for 2)",
			"meals": [
				{ "name": "2 CHẢ GIÒ HOẶC GỎI CUỐN TÔM THỊT", "description": "2 Spring Rolls or 2 Pork Fresh Rolls", "price": "42.50" },
				{ "name": "SÚP HOÀNH THÁNH HOẶC TOM-YUM TÔM", "description": "Wonton Soup or Tom-Yum Soup", "price": "42.50" },
				{ "name": "GÀ XÀO SATÉ HOẠC GÀ XÀO CÀ RI", "description": "Stir Fried Chicken with Satay or Stir-Fried Chicken Curry", "price": "42.50" },
				{ "name": "BÒ XÀO SATÉ HOẶC BỎ XÀO RAU CẢI", "description": "Stir Fried Beef with Satay Sauce or Vegetables", "price": "42.50" },
				{ "name": "2 CHÉN CƠM", "description": "2 Steamed Rice (S)", "price": "42.50" }
			]
		},
		{
			"menuName": "Lunch and Dinner",
			"menus": [
				{
					"menuName": "Combo 1",
					"meals": [
						{ "name": "CANH CHUA CÁ", "description": "Sweet & Sour Fish Soup", "price": "62.50" },
						{ "name": "TÔM RANG SẢ ỚT", "description": "Fried Salted Shrimp & Pork with Lemon Grass & Hot Pepper (Spicy)", "price": "62.50" },
						{ "name": "XÀ LÁCH XOÔNG XÀO THỊT BÒ", "description": "Stir Fried Beef w/Water Cress", "price": "62.50" },
						{ "name": "GÀ XÀO HÀNH GỪNG", "description": "Stir Fried Chicken w/Ginger & Onion", "price": "62.50" },
						{ "name": "DIA COM TRÁNG", "description": "Steamed Rice", "price": "62.50" },
						{ "name": "DIA DU'A CHUA", "description": "Sour Vegetable Plate", "price": "62.50" }
					]
				},
				{
					"menuName": "Combo 2",
					"meals": [
						{ "name": "CANH CHUA TÔM", "description": "Sweet & Sour Shrimp Soup", "price": "62.50" },
						{ "name": "CÁ KHO TỘ", "description": "Marinated Basa Fish & Pork Simmered in Earthen Wave Pot", "price": "62.50" },
						{ "name": "GÀ XÀO SẢ ỚT", "description": "Stir Fried Chicken with Lemon Grass & Hot Pepper (Spicy)", "price": "62.50" },
						{ "name": "BÒ XÀO RAU CẢI", "description": "Stir Fried Beef with Vegetable", "price": "62.50" },
						{ "name": "DIA COM TRANG", "description": "Steamed Rice", "price": "62.50" },
						{ "name": "DIA DU'A CHUA", "description": "Sour Vegetable Plate", "price": "62.50" }
					]
				}
			]
		},
		{
			"menuName": "Family Lunch and Dinner",
			"meals": [
				{ "name": "CANH CHUA CÁ", "description": "Vietnamese Sweet & Sour Fish Soup", "price": "20.90" },
				{ "name": "CANH CHUA TÔM", "description": "Vietnamese Sweet & Sour Shrimp Soup", "price": "20.90" },
				{ "name": "CÁ KHO TỘ", "description": "Marinated Basa Fish & Pork Simmered in Earthen Wave Pot", "price": "16.90" },
				{ "name": "THỊT KHO TỘ", "description": "Marinated Pork w/Black Peppers Simmered in Earthen Wave Pot", "price": "16.90" },
				{ "name": "TÔM RANG SẢ ỚT", "description": "Sauteed Shrimp & Pork with Lemon Grass & Hot Pepper (Spicy)", "price": "16.90" },
				{ "name": "CÁ CHIM CHIÊN MÁM GỪNG", "description": "Fried White Promprel Fish Served w/Ginger, Garlic & Fish Sauce", "price": "15.90" },
				{ "name": "XÀ LÁCH XOONG XÀO THỊT BÒ", "description": "Stir Fried Beef with Watercresh", "price": "13.90" },
				{ "name": "BÒ XÀO ĐẶC BIỆT (Bò xào cay, chua, ngọt trên dĩa nóng)", "description": "Stir Fried Beef with Sweet & Sour Sauce on Sizzling Plate", "price": "18.90" },
				{ "name": "TÔM XÀO ĐẶC BIỆT (Tôm xào cay, chua, ngọt trên dĩa nóng)", "description": "Stir Fried Shrimp with Sweet & Sour Sauce on Sizzling Plate", "price": "19.90" },
				{ "name": "CÁ XÀO ĐẶC BIỆT (Cá xào cay, chua, ngọt trên đĩa nóng)", "description": "Stir Fried Fish with Sweet & Sour Sauce on Sizzling Plate", "price": "19.90" }
			]
		},
		{
			"menuName": "Stir Fried on Sizzling Plate",
			"meals": [
				{ "name": "MỰC XÀO ĐẶC BIỆT (Mực xào cay, chua, ngọt trên đĩa nóng)", "description": "Stir Fried Squid with Sweet & Sour Sauce on Sizzling Plate", "price": "18.90" },
				{ "name": "BÒ XÀO SATÉ TRÊN DĨA NÓNG", "description": "Stir Fried Beef with Satay Sauce on Sizzling Plate", "price": "19.90" },
				{ "name": "TÔM XÀO SATÉ TRÊN DĨA NÓNG", "description": "Stir Fried Shrimp with Satay Sauce on Sizzling Plate", "price": "19.90" },
				{ "name": "CÁ XÀO SATÉ TRÊN DĨA NÓNG", "description": "Stir Fried Fish with Satay Sauce on Sizzling Plate", "price": "19.90" },
				{ "name": "MỰC XÀO SATÉ TRÊN DĨA NÓNG", "description": "Stir Fried Squid with Satay Sauce on Sizzling Plate", "price": "18.90" },
				{ "name": "BỎ XÀO TIÊU HÀNH TRÊN DĨA NÓNG", "description": "Stir Fried Beef with Onion & Black Pepper on Sizzling Plate", "price": "18.90" },
				{ "name": "BỎ LÚC LÁC TRÊN DĨA NÓNG", "description": "Stir Fried Cubes of Beef on Sizzling Plate", "price": "19.90" },
				{ "name": "CHÉN CƠM", "description": "Steamed Rice (Small Bowl)", "price": "3.75" },
				{ "name": "DIA COM", "description": "Steamed Rice Dish", "price": "6.75" }
			]
		},
		{
			"menuName": "Mon Chay - Vegetarian",
			"meals": [
				{ "name": "Chả Giò Chay", "description": "Vegetarian Spring Rolls with Tofu", "sizes": [{ "name": "Small", "price": "7.95" },{ "name": "Large", "price": "11.95"}] },
				{ "name": "Gỏi Cuốn Chay", "description": "Vegetarian Fresh rolls with Tofu", "sizes": [{ "name": "Small", "price": "7.95" },{ "name": "Large", "price": "11.95"}] },
				{ "name": "Phở rau cái, dầu hủ chạy", "description": "Vegetanan Rice Noodle Soup with Tofu", "sizes": [{ "name": "Medium", "price": "12.50" },{ "name": "Large", "price": "13.25"}] },
				{ "name": "Bun Đậu Hà Chiến.", "description": "Vegetarian Deep Fried Tofu with Vermicelli", "price": "11.45" },
				{ "name": "Cơm Chiến Rau Cải Chay", "description": "Vegetarian Fried Rice", "price": "15.90" },
				{ "name": "Cơm Rau Cai Xào Sa Tế Chạy", "description": "Fried Sautéed Vegetable with Satay on Rice", "price": "15.90" },
				{ "name": "Cơm Đậu Hủ Xào Rau Gái Chạy", "description": "Vegetarian Stir Fried Tofu with Vegetable on Steamed Rice", "price": "15.90" },
				{ "name": "Cơm Rau Cai Xào Sả ớt Chạy", "description": "Fred Sauteed Vegetable with Lemon Grass on Rice", "price": "15.90" },
				{ "name": "Pad Thai Chay", "description": "Vegetarian Pad Thai with Tofu", "price": "15.90" },
				{ "name": "Mi Xao Giòn thay", "description": "Vegetarian Thick Lay of Deep Fried Egg Noodle Top with Tofu", "price": "16.90" },
				{ "name": "Mì Xào Chay", "description": "Vegetarian Stir Fried Egg Noodle Top with Tofu", "price": "16.90" },
				{ "name": "Hủ Tiểu Xào Chạy", "description": "Vegetarian Stir Fried Rice Noodle Top with Tofu", "price": "15.90" }
			]
		},
		{
			"menuName": "Additional Orders",
			"meals": [
				{ "name": "CHÉN NƯỚC MẮM", "description": "Fish Sauce", "price": "1.50" },
				{ "name": "CHÉN SAUCE", "description": "Extra Sauce", "price": "2.00" },
				{ "name": "DĨA BÁNH HỎI HOẶC BÁNH TRÁNG", "description": "Thin Vermicelli or Rice Paper", "price": "2.50" },
				{ "name": "DĨA RAU THƠM", "description": "Extra Mint Herb Vegetables", "price": "3.50" },
				{ "name": "DĨA BÚN", "description": "Vermicelli", "price": "3.75" },
				{ "name": "OP LA, CHẢ TRỨNG", "description": "(Fried Egg, Steam Egg) \"each\"", "price": "2.50" },
				{ "name": "NEM NƯỚNG, BÁNH CÔNG", "description": "(Grilled Ground Pork Sausage, Shrimp Cake) \"each\"", "price": "3.00" },
				{ "name": "CHẢ GIÒ, SƯỜN NƯỚNG, THỊT NƯỚNG", "description": "(Fried Spring Roll, Grilled Pork Chop, Grilled Pork) \"each\"", "price": "5.00" },	
				{ "name": "GÀ NƯỚNG HOẶC SƯỜN BÒ NON NƯỚNG, BÒ NƯỚNG, CHẠO TÔM", "description": "(Grilled Chicken, Grilled Beef Ribs, Grilled Beef, Shrimp on Sugar Cane) \"each\"", "price": "5.50" },
				{ "name": "TÔM CÀNG", "description": "Jumbo Shrimp", "price": "7.00" },
				{ "name": "DĨA TÁI", "description": "Plate of Rare Beef", "price": "7.00" },
				{ "name": "DẦU CHÁO QUẢY", "description": "Chinese Frittiers", "price": "3.00" },
				{ "name": "THÊM SÚP (PHỜ)", "description": "Extra Noodle Soup (S)", "price": "6.00" },
				{ "name": "THÊM SÚP THÁI LAN", "description": "Extra \"Thai\" Hotpot Soup (S)", "price": "7.00" }
			]
		},
		{
			"menuName": "Giat Khat - Beverages",
			"meals": [
				{ "name": "CÀ PHÊ SỮA ĐÁ", "description": "Iced Coffee with Condensed Milk", "price": "4.50" },
				{ "name": "CÀ PHÊ ĐEN ĐÁ", "description": "Black Iced Coffee", "price": "4.50" },
				{ "name": "CHÈ 3 MÀU", "description": "Three Kinds of Mung Bean with Coconut Milk", "price": "5.00" },
				{ "name": "SINH TO BỔ", "description": "Avocado Milk Shake", "price": "5.00" },
				{ "name": "SINH TỐ DÂU", "description": "Strawberry Milk Shake", "price": "5.00" },
				{ "name": "SINH TỐ XOÀI", "description": "Mango Milk Shake", "price": "5.00" },
				{ "name": "SINH TỐ MÍT", "description": "Jack Fruit Milk Shake", "price": "5.00" },
				{ "name": "SINH TỐ SÂU RIÊNG", "description": "Durian Milk Shake", "price": "5.50" },
				{ "name": "SINH TỐ ĐẬU XANH", "description": "Green Bean Milk Shake", "price": "5.00" },
				{ "name": "SINH TÔ ĐẬU ĐEN", "description": "Red Bean Milk Shake", "price": "5.00" },
				{ "name": "SINH TỐ DỪA TƯƠI", "description": "Coconut Milk Shake", "price": "5.00" },
				{ "name": "SINH TÔ DỪA TƯƠI, ĐẬU ĐEN", "description": "Coconut Mixs with Red Bean Milk Shake", "price": "5.50" },
				{ "name": "NƯỚC DỪA TƯƠI", "description": "Fresh Coconut Juice", "price": "5.00" },
				{ "name": "NƯỚC TRÁI VẢI", "description": "Lychee with Ice", "price": "5.00" },
				{ "name": "SODA CHANH MUỐI", "description": "Salted Lime Juice with Soda", "price": "5.00" },
				{ "name": "SODA CHANH TƯƠI", "description": "Fresh Lime Juice with Soda", "price": "5.00" },
				{ "name": "SODA XÍ MUQI", "description": "Picked Plums with Soda", "price": "5.00" },
				{ "name": "SINH TÔ MÀNG CẦU", "description": "Soursop Smoothie", "price": "5.00" },
				{ "name": "POP CÁC LOẠI", "description": "Nestea, Coke, Diet Coke, 7-Up, Orange Pop. Water Bottle\nChoice of Jelly: Mixed Jelly, Lychee Coconut Jelly, Passion Fruit Jelly", "price": "2.50" },
				{ "name": "BUBBLE TEA", "description": "Taro, Honeydew, Strawberry, Mango, Lychee, Green Apple, Grapefruit with Fresh Lime\nCaramel Flan Cake with Blue", "price": "5.50" },
				{ "name": "NƯỚC CHANH DÂY", "description": "Pure Passion Fruit Juice", "price": "6.00" },
				{ "name": "NƯỚC CAM EP", "description": "Fresh Orange Juice", "price": "6.00" },
				{ "name": "SÂM BỎ LƯỢNG", "description": "\"Ching Bo Leung\" Sweet and Cold Soup", "price": "6.50" },
				{ "name": "BÁNH FLAN", "description": "Caramel Flan Cake with Blueberry, Raspberry", "price": "6.00" },
				{ "name": "SỮA ĐẬU NÀNH", "description": "Soymilk", "price": "2.00" }
			]
		},
		{
			"menuName": "Bia Ruou - Beer & Liquor",
			"menus": [
				{
					"menuName": "IMPOTED BEERS",
					"meals": [
						{ "name": "HEINEKEN", "description": "", "price": "6.00" },
						{ "name": "CORONA", "description": "", "price": "6.00" }
					]
				},
				{
					"menuName": "DOMESTIC BEERS",
					"meals": [
						{ "name": "LABATT BLUE", "description": "", "price": "5.50" },
						{ "name": "MOLSON CANADIAN", "description": "", "price": "5.50" },
						{ "name": "BUDWEISER", "description": "", "price": "5.50" },
						{ "name": "COOR LIGHT", "description": "", "price": "5.50" }
					]
				}
			],
			"meals": [
				{ "name": "RED WINE", "description": "", "price": "5.50" },
				{ "name": "WHITE WINE", "description": "", "price": "5.50" }
			]
		}
	]

	def iterateList(list, pIndex, pId):
		for index, info in enumerate(list):
			sql = "insert into menu "
			sql += "(locationId, parentMenuId, name, image) "
			sql += "values ("
			sql += "1, '" + str(pId) + "', "
			sql += "'" + info["menuName"] + "', "
			sql += "'{\"name\":\"\", \"width\": 300, \"height\": 300}'"
			sql += ")"
			id = query(sql, True).lastrowid

			if "menus" in info:
				iterateList(info["menus"], index, id)
			
			if "meals" in info:
				for meal in info["meals"]:
					options = {"sizes":[],"quantities":[],"percents":[]}
					price = ''

					if "sizes" in meal:
						options["sizes"] = meal["sizes"]

					if "quantities" in meal:
						options["quantities"] = meal["quantities"]

					if "price" in meal:
						price = str(meal["price"])

					sql = "insert into product "
					sql += "(locationId, menuId, name, description, image, options, price)"
					sql += " values "
					sql += "("
					sql += "1, "
					sql += "'" + str(id) + "', "
					sql += "'" + meal["name"].replace("'", "\\'") + "', "
					sql += "'" + meal["description"].replace("'", "\\'") + "', "
					sql += "'{\"name\":\"\", \"width\": 300, \"height\": 300}', "
					sql += "'" + json.dumps(options) + "', "
					sql += "'" + price + "'"
					sql += ")"
					query(sql)

	iterateList(list, 0, "")

	return { "msg": "succeed" }
