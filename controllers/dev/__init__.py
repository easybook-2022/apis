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

	delete = False
	records = query("select * from income_record", True).fetchall()
	for info in records:
		delete = True

		query("delete from income_record where id = " + str(info["id"]))

	if delete == True:
		query("ALTER table income_record auto_increment = 1")

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
	list = {
		"logo": "ilovepho.png",
		"menus": [
			{
				"menuName": "Mon Khai Vi - Appetizers",
				"meals": [
					{ "number": "100", "name": "BÒ TÁI CHANH", "price": "15.95", "description": "Beef Ceviche in Lime Juice Selag" },
					{ "number": "101", "name": "CHẢ GIÒ TÔM THỊT (2–4 CUỐN)", "description": "Deep Fried Spring Rolls. \"Pork and Shrimp\" (2-4 rolls)", "quantities": [{ "input": "2 Rolls", "price": "7.95" }, { "input": "4 Rolls", "price": "11.95" }] },
					{ "number": "102", "name": "GÒI CUỐN TÔM THỊT (2-4 CUỐN)", "description": "Fresh Rolls with Shrimp and Pork (2-4 rolls)", "quantities": [{ "input": "2 Rolls", "price": "7.95" }, { "input": "4 Rolls", "price": "11.95" }] },
					{ "number": "102A", "name": "GỒI CUỐN BỐN MÙA", "description": "Fresh Rolls with Avocado, Grilled Beef - Chicken - Shrimp (2-4 rolls)", "quantities": [{ "input": "4 Rolls", "price": "14.95" }] },
					{ "number": "103", "name": "GÒI CUỐN GÀ NƯỚNG (2-4 CUỐN)", "description": "Fresh Rolls with Grilled Chicken (2-4 rolls)", "quantities": [{ "input": "2 Rolls", "price": "7.95" }, { "input": "4 Rolls", "price": "11.95" }] },
					{ "number": "104", "name": "GÓI CUỐN NEM NƯỚNG (2-4 CUỐN)", "description": "Fresh Rolls with Pork Meatballs (2-4 rolls)", "quantities": [{ "input": "2 Rolls", "price": "7.95" }, { "input": "4 Rolls", "price": "11.95" }] },
					{ "number": "105", "name": "GÓI CUỐN BÒ NƯỚNG (2-4 CUỐN)", "description": "Fresh Rolls with Grilled Beef (2-4 rolls)", "quantities": [{ "input": "2 Rolls", "price": "7.95" }, { "input": "4 Rolls", "price": "11.95" }] },
					{ "number": "106", "name": "GỎI CUỐN THỊT NƯỚNG (24 CUỐN)", "description": "Fresh Rolls with Grilled Pork (2-4 rolls)", "quantities": [{ "input": "2 Rolls", "price": "7.95" }, { "input": "4 Rolls", "price": "11.95" }] },
					{ "number": "107", "name": "GỒI CUỐN ĐẬU HỦ (2-4 CUỐN)", "description": "Fresh Rolls with Tofu (2-4 rolls)", "quantities": [{ "input": "2 Rolls", "price": "7.95" }, { "input": "4 Rolls", "price": "11.95" }] },
					{ "number": "108", "name": "GỎI NGÓ SEN TÔM THỊT", "description": "Lotus Root with Pork and Shrimp Salad (Spicy and Peanut)", "quantities": [{ "input": "4 Rolls", "price": "12.95" }] },
					{ "number": "109", "name": "GỎI XOÀI TÔM THÁI LAN", "description": "Thai Shrimp Mango Salad (Spicy and Peanut)", "quantities": [{ "input": "4 Rolls", "price": "11.90" }] },
					{ "number": "110", "name": "CÁNH GÀ CHIÊN (BƠ NƯỚC MẮM, I LOVE PHỞ SAUSE, RANG MUỐI)", "description": "Deep Fired Chicken Wings with Butter or Fish Sause, I LOVE PHO Sause, Roasted Salt", "quantities": [{ "input": "4 Rolls", "price": "12.90" }] },
					{ "number": "111", "name": "GỎI GÀ", "description": "Chicken Salad (Spicy and Peanut)", "quantities": [{ "input": "4 Rolls", "price": "12.90" }] },
					{ "number": "112", "name": "GỞI VỊT", "description": "Duck Salad (Spicy and Peanu", "quantities": [{ "input": "4 Rolls", "price": "13.90" }] },
					{ "number": "113", "name": "CHẢ MỰC CHIÊN", "description": "Deep Fried Squid Cake", "quantities": [{ "input": "4 Rolls", "price": "16.90" }], "image": "113.png"},
					{ "number": "114", "name": "MỰC KHOANH VÀ KHOAI TÂY TÂM BỘT CHIÊN GIÒN", "description": "Calamari with Wedge Fried Pototes", "quantities": [{ "input": "4 Rolls", "price": "14.90" }], "image": "114.png"},
					{ "number": "114A", "name": "TÔM VÀ KHOAI TÂY TÂM BỘT CHIÊN GIÒN", "description": "Shrimp Popcom with Wedges Fried Potatoes", "quantities": [{ "input": "4 Rolls", "price": "16.90" }], "image": "114A.png"},
					{ "number": "115", "name": "ĐẬU HỦ CHIÊN", "description": "Deep Fried Tofu", "quantities": [{ "input": "4 Rolls", "price": "11.90" }] }
				]
			},
			{
				"menuName": "Banh Cuon - Rice Rolls",
				"meals": [
					{ "number": "116", "name": "BÁNH CUỐN CHẢ LỤA, BÁNH CÔNG", "description": "Steamed Rice Rolls with Vietnamese Ham, Shrimp Cake", "quantities": [{ "input": "4 Rolls", "price": "13.50" }] },
					{ "number": "117", "name": "BÁNH CUỐN CHÀ LỤA", "description": "Steamed Rice Rolls with Vietnamese Pork Ham", "quantities": [{ "input": "4 Rolls", "price": "11.90" }] },
					{ "number": "118", "name": "BÁNH CUỐN NÓNG", "description": "Steamed Ground Pork Rice Rolls", "quantities": [{ "input": "4 Rolls", "price": "11.90" }] },
					{ "number": "120", "name": "BÁNH ƯỚT CHẢ LỤA, BÁNH CÔNG", "description": "Steamed Plain Rice Roll with Vietnamese Pork Ham & Shrimp Cake", "quantities": [{ "input": "4 Rolls", "price": "13.50" }] },
					{ "number": "121", "name": "BÁNH ƯỚT CHẢ LỤA", "description": "Steamed Plain Rice Roll with Vietnamese Pork Ham", "quantities": [{ "input": "4 Rolls", "price": "11.90" }] },
					{ "number": "122", "name": "BÁNH ƯỚT NÓNG", "description": "Steamed Plain Rice Rolls", "quantities": [{ "input": "4 Rolls", "price": "11.90" }] }
				]
			},
			{
				"menuName": "Pho - Beef Rice Noodle",
				"meals": [
					{ "number": "200", "name": "PHỞ SƯỜN BÒ", "description": "Rib Backbone with Rice Noodle Soup", "sizes": [{ "name": "Large", "price": "16.45" }] },
					{ "number": "201", "name": "PHỞ ĐẶC BIỆT “I LOVE PHO“", "description": "\"I Love Pho\" Special Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "11.00" }, { "name": "Large", "price": "11.75" }] },
					{ "number": "202", "name": "PHỞ TÁI", "description": "Rare Beef w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "203", "name": "PHỞ TÁI, NAM", "description": "Rare Beef & Lightly Fat Well-done Beef w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "204", "name": "PHỜ TÁI, SÁCH", "description": "Rare Beef & Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "205", "name": "PHỞ TÁI, GẦN", "description": "Rare Beef & Beef Tendon w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "206", "name": "PHỞ TÁI, GÀ", "description": "Rare Beef & Chicken w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "207", "name": "PHỞ TÁI, BÒ VIÊN", "description": "Rare Beef & Beef Balls w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "208", "name": "PHỞ TÁI, VỀ DÒN", "description": "Rare Beef & Tendon Brisket w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "209", "name": "PHỞ TÁI, GÂN, SÁCH", "description": "Rare Beef, Beef Tendon, Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "210", "name": "PHỞ NAM", "description": "Lightly Fat Well-done Beef w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "211", "name": "PHỞ NẠM, GÀ", "description": "Lightly Fat Well-done Beef & Chicken w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "212", "name": "PHỞ NAM, BỎ VIÊN", "description": "Lightly Fat Well-done Beef & Beef Balls w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "213", "name": "PHỞ NAM, SÁCH", "description": "Lightly Fat Well-done Beef & Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "214", "name": "PHỞ NẠM, GẦN", "description": "Lightly Fat Well-done Beef & Beef Tendon w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "215", "name": "PHỞ NẠM, VỀ DÒN", "description": "Lightly Fat Well-done Beef & Tendon Brisket w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.50" }, { "name": "Large", "price": "14.50" }] },
					{ "number": "216", "name": "PHỞ NẠM, GÂN, SÁCH", "description": "Lightly Fat Well-done Beef & Beef Tendon, Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "217", "name": "PHỞ GÀ", "description": "Chicken w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "218", "name": "PHỞ GÀ, BÒ VIÊN", "description": "Chicken & Beef Balls w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "219", "name": "PHO GÀ, GÅN", "description": "Chicken & Beef Tendon w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "220", "name": "PHỞ GÀ, SÁCH", "description": "Chicken & Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "221", "name": "PHỞ GÀ, VỀ DÒN", "description": "Chicken & Tendon Brisket w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "222", "name": "PHỞ GÀ, GÂN, SÁCH", "description": "Chicken & Beef Tendon, Beef Tripe w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "223", "name": "PHỞ VẺ DÒN", "description": "Tendon Brisket w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "224", "name": "PHỞ RAU CẢI, ĐẬU HŨ", "description": "Vegetables & Tofu w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "225", "name": "PHỞ BÒ VIÊN", "description": "Beef Balls w/Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "13.00" }, { "name": "Large", "price": "15.00" }] },
					{ "number": "226", "name": "PHỞ KHÔNG", "description": "Plain Noodle Soup", "sizes": [{ "name": "Medium", "price": "10.75" }, { "name": "Large", "price": "12.75" }] },
				]
			},
			{
				"menuName": "Mi, Hu Tieu - Egg Noodle & Rice Noodle Soup",
				"meals": [
					{ "number": "300", "name": "TOM-YUM SOUP", "description": "Choice of Chicken or Beef or Shrimp (Noodle NOT Include)", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }] },
					{ "number": "301", "name": "MÌ ĐẶC BIỆT (KHÔ HOẬC NƯỚC)", "description": "\"House\" Special Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "302", "name": "MÌ ĐÔ BIỀN", "description": "Seafood with Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "303", "name": "MỈ XÁ XÍU", "description": "B.B.Q. Pork with Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "304", "name": "HỦ TIỂU NAM VANG ĐẶC BIỆT", "description": "\"Nam Vang\" Special Rice Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "305", "name": "HỦ TIÊU ĐÓ BIỀN", "description": "Seafood with Rice Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "306", "name": "HỦ TIÊU MÌ ĐẶC BIỆT", "description": "\"House\" Special Rice Noodle & Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "307", "name": "HỦ TIÊU MÌ ĐỎ BIỂN", "description": "Seafood with Rice Noodle & Egg Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "308", "name": "HỦ TIÊU MỸ THO ĐẶC BIỆT", "description": "\"My Tho\" House Special Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "14.545" }] },
					{ "number": "309", "name": "HỦ TIÊU MỸ THỌ ĐÔ BIỀN", "description": "\"My Tho Seafood w/Transparent Noodle Soup (with soup or dry)", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "14.545" }] },
					{ "number": "310", "name": "MI BO KHO", "description": "Beef Stewed with Egg Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }], "image": "310.png"},
					{ "number": "311", "name": "HỦ TIỂU BÒ KHO", "description": "Beef Stewed with Rice Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "312", "name": "HỦ TIÊU MÌ BÒ KHO", "description": "Beef Stewed with Rice Noodle & Egg Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "313", "name": "SÚP HOÀNH THÁNH", "description": "Wonton Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
					{ "number": "314", "name": "MÌ HOÀNH THÁNH", "description": "B.B.Q. Pork & Wonton with Egg Noodle Soup", "sizes": [{ "name": "Medium", "price": "12.90" }, { "name": "Large", "price": "13.90" }] },
				]
			},
			{
				"menuName": "Mi, Hu Tieu Xao - Stir Fried Egg/Rice Noodle (Pad Thai)",
				"meals": [
					{ "number": "315", "name": "MÌ XÀO THẬP CẢM (ONE SIZE)", "description": "Stir Fired Egg Noodle with Assorted Meat & Seafood", "price": "16.90" },
					{ "number": "316", "name": "MÌ XÀO ĐỒ BIỀN (ONE SIZE)", "description": "Stir Fried Egg Noodle with Seafood", "price": "16.90" },
					{ "number": "317", "name": "MÌ XÀO GIÒN THẬP CẢM (ONE SIZE)", "description": "Thick Lay of Fired Egg Noodle with Assorted Meat & Seafood & Veg", "price": "16.90" },
					{ "number": "318", "name": "MÌ XÀO GIÒN ĐÔ BIỀN (ONE SIZE)", "description": "Thick Lay of Fired Egg Noodle Top with Seafood & Veg", "price": "17.45", "image": "318.png"},
					{ "number": "319", "name": "HỦ TIÊU XÀO THỊT BÒ (ONE SIZE)", "description": "Stir Fried Rice Noodle with Beef", "price": "15.90" },
					{ "number": "320", "name": "PAD THAI BÒ (ONE SIZE)", "description": "Beef Pad Thai (Spicy and Peanut)", "price": "15.90", "image": "320.png"},
					{ "number": "321", "name": "PAD THAI GÀ (ONE SIZE)", "description": "Chicken Pad Thai (Spicy and Peanut)", "price": "15.90" },
					{ "number": "322", "name": "PAD THAI TÔM (ONE SIZE)", "description": "Shrimp Pad Thai (Spicy and Peanut)", "price": "16.45" }
				]
			},
			{
				"menuName": "Bun - Vermicelli (Served W/House Sauce and Peanut",
				"meals": [
					{ "number": "401", "name": "BÚN ĐẬU HŨ CHIÊN", "description": "Deep Fried Tofu with Vermicelli", "price": "11.45" },
					{ "number": "402", "name": "BÚN CHẢ GIÒ", "description": "Deep Fried Spring Rolls with Vermicelli", "price": "11.90" },
					{ "number": "403", "name": "BÚN THỊT NƯỚNG", "description": "Grilled Pork with Vermicelli", "price": "12.45" },
					{ "number": "404", "name": "BÚN NEM NƯỚNG", "description": "Grilled Meatballs with Vermicelli", "price": "12.45" },
					{ "number": "405", "name": "BÚN GÀ NƯỚNG", "description": "Grilled Chicken with Vermicelli", "price": "12.90" },
					{ "number": "406", "name": "BÚN BÒ NƯỚNG", "description": "Grilled Beef with Vermicelli", "price": "12.90" },
					{ "number": "407", "name": "BÚN TÔM CÀNG NƯỚNG", "description": "Grilled Jumbo Shrimp with Vermicelli", "price": "16.90" },
					{ "number": "408", "name": "BÚN CHẢ GIÒ, THỊT NƯỚNG", "description": "Grill Pork & Spring Roll with Vermicelli", "price": "12.90" },
					{ "number": "409", "name": "BÚN CHẢ GIÒ, NEM NƯỚNG", "description": "Grilled Meatballs & Spring Roll with Vermicelli", "price": "12.90" },
					{ "number": "410", "name": "BÚN CHẢ GIÒ, GÀ NƯỚNG", "description": "Grilled Chicken & Spring Roll with Vermicelli", "price": "12.90" },
					{ "number": "411", "name": "BÚN CHẢ GIÒ, BÒ NƯỚNG", "description": "Grilled Beef & Spring Roll with Vermicelli", "price": "12.90" },
					{ "number": "412", "name": "BÚN CHẢ GIÒ, CHẠO TÔM", "description": "Minced Shrimp on Sugar Cane & Spring Roll with Vermicelli", "price": "12.90" },
					{ "number": "414", "name": "BÚN CHÀ GIÒ, THỊT NƯỚNG, NEM NƯỚNG", "description": "Grill Pork, Grilled Meatballs & Spring Roll with Vermicelli", "price": "13.45" },
					{ "number": "415", "name": "BÚN CHẢ GIÒ, NEM NƯỚNG, CHẠO TÔM", "description": "Grilled Meatballs, Minced Shrimp on\nSugar Cane & Spring Roll with Vermicelli", "price": "13.75" },
					{ "number": "416", "name": "BÚN THỊT NƯỚNG, NEM NƯỚNG", "description": "Grill Pork, Grilled Meatballs with Vermicelli", "price": "12.90" },
					{ "number": "417", "name": "BÚN THỊT NƯỚNG, BÒ LÁ LÓP", "description": "Grill Pork, Grilled Beef Wrapped in Herb Leaves with Vermicelli", "price": "13.95" },
					{ "number": "418", "name": "BÚN THỊT NƯỚNG, TÔM CÀNG", "description": "Grill Pork, Grilled Jumbo Shrimp with Vermicelli", "price": "15.90" },
					{ "number": "419", "name": "BÚN THỊT NƯỚNG, CHẠO TÔM", "description": "Grill Pork, Minced Shrimp on Sugar Cane with Vermicelli", "price": "12.90" },
					{ "number": "421", "name": "BÚN BÒ LÁ LỚP, NEM NƯỚNG", "description": "Grilled Beef Wrapped in Herb Leaves, Grilled Meatballs with Vermicelli", "price": "14.45" },
					{ "number": "422", "name": "BÚN BÒ LÁ LỚP, CHẠO TÔM", "description": "Grilled Beef Wrapped in Herb Leaves,\nMinced Shrimp on Sugar Cane with Vermicelli", "price": "14.95" },
					{ "number": "423", "name": "BÚN BÒ XÀO CỦ HÀNH", "description": "Stir Fried Beef & Onion with Vermicelli", "price": "13.95" },
					{ "number": "424", "name": "BÚN BÒ XÀO SATE", "description": "Stir Fried Beef with Satay Sauce on Vermicelli (Spicy)", "price": "13.95" },
					{ "number": "425", "name": "BÚN BÒ XÀO XẢ ỚT", "description": "Stir Fried Beef with Lemon Grass & Hot Pepper on Vermicelli (Spicy and Peanut)", "price": "13.95" }
				]
			},
			{
				"menuName": "Bun - Vermicelli Soup",
				"meals": [
					{ "number": "426", "name": "BÚN BÒ HUẾ", "description": "\"Hue\" Style Beef, Pork & Vietnamese Sausage on Vermicelli", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }]},
					{ "number": "427", "name": "BÚN MẮM", "description": "Fish, Shrimp, & Pork in Fish-Paste Soup with Vermicelli", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }]},
					{ "number": "428", "name": "BÚN RIỀU", "description": "Shrimp, Crab Meat & Pork in Paste Soup with Vermicelli", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }]},
					{ "number": "429", "name": "BÚN ỐC", "description": "Whelks Soup with Vermicelli (Only One Size)", "sizes": [{ "name": "Medium", "price": "15.90" }]},
					{ "number": "429A", "name": "BÚN CHẢ CÁ I LOVE PHỞ", "description": "I Love Pho Style Fried Fish Cake Soup with Vermicelli (Only One Size)", "sizes": [{ "name": "Medium", "price": "15.90" }]},
					{ "number": "430", "name": "BUN MANG VIT", "description": "Duck & Bamboo Shoot with Vermicelli Soup", "sizes": [{ "name": "Medium", "price": "13.45" }, { "name": "Large", "price": "15.45" }]},
					{ "number": "431", "name": "BÚN HOẬC CƠM CÀ RI GÀ", "description": "Curry Chicken with Vermicelli or Steamed Rice", "sizes": [{ "name": "Medium", "price": "10.50" }, { "name": "Large", "price": "11.95" }]}
				]
			},
			{
				"menuName": "Com Tam - Steamed Broken Rice Dishes",
				"meals": [
					{ "number": "501", "name": "CƠM TẤM SƯỜN NƯỚNG", "description": "Grilled Pork Chop with Steamed Broken Rice", "price": "12.45" },
					{ "number": "502", "name": "CƠM TẤM GÀ NƯỚNG", "description": "Grilled Chicken with Steamed Broken Rice", "price": "12.90" },
					{ "number": "503", "name": "CƠM TẤM SƯỜN BÒ NƯỚNG", "description": "Grilled Beef Ribs with Steamed Broken Rice", "price": "13.45" },
					{ "number": "504", "name": "CƠM TẤM TÔM NƯỚNG", "description": "Grilled Shrimp with Steamed Broken Rice", "price": "16.90" },
					{ "number": "505", "name": "CƠM TẤM SƯỜN NƯỚNG, ỐP-LA", "description": "Grilled Pork Chop with Fried Egg on Steamed Broken Rice", "price": "12.45" },	
					{ "number": "507", "name": "CƠM TẤM SƯỜN NƯỚNG, CHẢ TRỨNG", "description": "Grilled Pork Chop with Steamed Egg on Steamed Broken Rice", "price": "12.45" },
					{ "number": "508", "name": "CƠM TẤM SƯỜN NƯỚNG, TÔM NƯỚNG", "description": "Grilled Pork Chop with Grilled Shrimp on Steamed Broken Rice", "price": "15.45" },
					{ "number": "511", "name": "CƠM TẤM SƯỜN NƯỚNG, CHẢ TRỨNG, ỐP-LA", "description": "Grilled Pork Chop, Steamed Egg with Fried Egg on Steamed Broken Rice", "price": "12.45" },
					{ "number": "512", "name": "CƠM TẤM SƯỜN NƯỚNG, GÀ NƯỚNG", "description": "Grilled Pork Chop, Grilled Chicken with Steamed Broken Rice", "price": "12.90" },
					{ "number": "513", "name": "CƠM TẤM GÀ NƯỚNG, ỐP-LA", "description": "Grilled Chicken with Fried Egg on Steamed Broken Rice", "price": "12.90" },
					{ "number": "514", "name": "CƠM TẤM GÀ NƯỚNG, CHẢ TRỨNG", "description": "Grilled Chicken with Steamed Egg on Steamed Broken Rice", "price": "12.90" },
					{ "number": "516", "name": "CƠM TẤM GÀ NƯỚNG, TÔM NƯỚNG", "description": "Grilled Chicken with Grilled Shrimp on Steamed Broken Rice", "price": "15.90" },
					{ "number": "519", "name": "CƠM TẤM GÀ NƯỚNG, CHẢ TRỨNG, OP-LA", "description": "Grilled Chicken, Steamed Egg with Fried Egg on Steamed Broken Rice", "price": "12.90" },
					{ "number": "520", "name": "CƠM TẤM GÀ NƯỚNG, SƯỜN NƯỚNG, ỐP-LA", "description": "Grilled Chicken, Grilled Pork Chop with Fried Egg on Steamed Broken Rice", "price": "13.20" },
					{ "number": "522", "name": "CƠM TẤM GÀ NƯỚNG, SƯỜNG NƯỚNG, CHẢ TRỨNG", "description": "Grilled Chicken, Grilled Pork Chop with Steamed Egg on Steamed Broken Rice", "price": "13.20" },
					{ "number": "523", "name": "CƠM TAM 4 MAU", "description": "Grilled Chicken, Grilled Pork Chop, Steamed Egg. Fried Egg on Steamed Broken Rice", "price": "14.45", "image": "523.png"}
				]
			},
			{
				"menuName": "Com Xao - Stir Rice Dishes",
				"meals": [
					{ "number": "524", "name": "CƠM BÒ XÀO RAU CẢI", "description": "Stir Fired Beef with Vegetable on Steamed Rice.", "price": "15.90" },
					{ "number": "525", "name": "CƠM GÀ XÀO RAU CẢI", "description": "Stir Fried Chicken with Vegetable on Steamed Rice", "price": "15.90" },
					{ "number": "526", "name": "CƠM TÔM XÀO RAU CẢI", "description": "Stir Fried Shrimp with Vegetable on Steamed Rice", "price": "16.90" },
					{ "number": "527", "name": "CƠM MỰC XÀO RAU CẢI", "description": "Stir Fried Squid with Vegetable on Steamed Rice", "price": "16.45" },
					{ "number": "528", "name": "CƠM ĐẬU HŨ XÀO RAU CẢI", "description": "Stir Fried Tofu with Vegetable on Steamed Rice", "price": "15.90" },
					{ "number": "529", "name": "CƠM BÒ XÀO SẢ ỚT", "description": "Stir Fried Beef with Lemon Grass & Hot Pepper on Steamed Rice (Spicy)", "price": "15.90" },
					{ "number": "530", "name": "CƠM GÀ XÀO SẢ ỚT", "description": "Stir Fried Chicken with Lemon Grass & Hot Pepper on Steamed Rice (Spicy)", "price": "15.90" },
					{ "number": "53", "name": "CƠM TÔM XÀO SẢ ỚT", "description": "Stir Fried Shrimp with Lemon Grass & Hot Pepper on Steamed Rice (Spicy)", "price": "16.90" },
					{ "number": "531", "name": "CƠM MỰC XÀO SẢ ỚT", "description": "Stir Fried Squid with Lemon Grass & Hot Pepper on Steamed Rice (Spicy)", "price": "16.45" },
					{ "number": "532", "name": "CƠM BÒ XÀO SATÉ", "description": "Stir Fried Beef with Satay Sauce on Steamed Rice (Spicy)", "price": "15.90" },
					{ "number": "533", "name": "CƠM GÀ XÀO SATÉ", "description": "Sur Fried Chicken with Satay Sauce on Steamed Rice (Spicy)", "price": "15.90" },
					{ "number": "534", "name": "CƠM TÔM XÀO SATÉ", "description": "Stir Fried Shrimp with Satay Sauce on Steamed Rice (Spicy)", "price": "16.90" },
					{ "number": "535", "name": "CƠM MỰC XÀO SATÉ", "description": "Stir Fried Squid with Satay Sauce on Steamed Rice (Spicy)", "price": "16.45" },
					{ "number": "536", "name": "CƠM GÀ XÀO THÁI LAN", "description": "\"Thai Style\" Stir Fried Chicken with Steamed Rice (Spicy)", "price": "15.90" },
					{ "number": "537", "name": "CƠM BỎ XÀO THÁI LAN", "description": "\"Thai Style\" Stir Fried Beef with Steamed Rice (Spicy)", "price": "15.90" },
					{ "number": "538", "name": "CƠM TÔM XÀO THÁI LAN", "description": "\"Thai Style\" Stir Fried Shrimp with Steamed Rice (Spicy)", "price": "16.90" },
					{ "number": "539", "name": "CƠM MỰC XÀO THÁI LAN", "description": "\"Thai Style\" Stir Fried Squid with Steamed Rice (Spicy)", "price": "16.45" },
					{ "number": "540", "name": "CƠM BÒ LÚC LÁC", "description": "Fried Sautéed Cubes of Beef with Steamed Rice", "price": "16.90" }
				]
			},
			{
				"menuName": "Com Chien - Fried Rice Dishes",
				"meals": [
					{ "number": "542", "name": "CƠM CHIÊN GÀ NƯỚNG", "description": "Grilled Chicken on Fried Rice", "price": "15.90", "image": "542.png"},
					{ "number": "543", "name": "CƠM CHIÊN BÒ", "description": "Beef Fried Rice", "price": "15.90" },
					{ "number": "544", "name": "CƠM CHIÊN TÔM", "description": "Shrimp Fried Rice", "price": "15.90" },
					{ "number": "545", "name": "CƠM CHIÊN XÁ XÍU", "description": "B.B.Q. Pork Fried Rice", "price": "15.90" },
					{ "number": "546", "name": "CƠM CHIÊN DƯƠNG CHÂU", "description": "Yang Chow Fried Rice", "price": "16.45" },
					{ "number": "547", "name": "CƠM CHIÊN ĐỒ BIỀN", "description": "Seafood on Fried Rice", "price": "15.50" },
					{ "number": "548", "name": "CƠM CHIÊN RAU CẢI", "description": "Vegetable Fried Rice", "price": "15.90" }
				]
			},
			{
				"menuName": "Chao - Congee",
				"meals": [
					{ "number": "601", "name": "CHÁO CÁ", "description": "Fish Congee", "price": "12.90" },
					{ "number": "602", "name": "CHÁO BÒ", "description": "Beef Congee", "price": "12.90" },
					{ "number": "603", "name": "CHÁO ĐÔ BIỂN", "description": "Seafood Congee", "price": "13.45" },
					{ "number": "604", "name": "CHÁO GÀ", "description": "Chicken Congee", "price": "12.90" },
					{ "number": "606", "name": "CHẢO VỊT", "description": "Duck Congee", "price": "13.45" }
				]
			},
			{
				"menuName": "Banh Canh - Udon Noodle Soup",
				"meals": [
					{ "number": "607", "name": "BÁNH CANH CUA", "description": "Crab with Udon Noodle Soup", "price": "12.90" },
					{ "number": "608", "name": "BÁNH CANH GIÒ HEO", "description": "Pork Hock with Udon Noodle Soup", "price": "12.90" },
					{ "number": "609", "name": "BÁNH CANH TÔM THỊT", "description": "Pork & Shrimp with Udon Noodle Soup", "price": "12.90" }
				]
			},
			{
				"menuName": "Banh Hoi - Platter",
				"meals": [
					{ "number": "700", "name": "CHÀ MỰC ĐẬU HÙ CHIÊN GIÒN BÚN MÁM TÔM", "description": "Deep Fried Squid Cake Tofu & Vermicelli w/Shrimp Sauce", "price": "25.50" },
					{ "number": "701", "name": "BÁNH XÈO", "description": "Vietnamese Pancake with Pork, Shrimp & Bean Sprouts", "price": "13.90" },
					{ "number": "702", "name": "NEM NƯỚNG, THỊT NƯỚNG, RAU SỐNG, BÁNH HỒI", "description": "Grilled Meat Balls, Grilled Pork Served w/Thin Vermicelli & Vegetables", "price": "23.50" },
					{ "number": "703", "name": "NEM NƯỚNG, CHẠO TÔM, RAU SÓNG, BÁNH HỎI", "description": "Grilled Meat Balls, Minced Shnmp on Sugar Cane\nServed with Thin Vermicelli & Vegetable", "price": "23.50" },
					{ "number": "704", "name": "NEM NƯỚNG, BÒ CUỐN LÁ LÓT, RAU SÓNG, BÁNH HỎI", "description": "Grilled Meat Balls, Grilled Beef Wrapped in Herb Leaves\nServed with Thin Vermicelli & Vegetables", "price": "23.50" },
					{ "number": "705", "name": "CHẠO TÔM, BÒ CUỐN LÁ LÓT, RAU SỐNG, BÁNH HỎI", "description": "Minced Shrimp on Sugar Cane, Grilled Beef Wrapped in Herb Leaves\nServed with Thin Vermicelli & Vegetables", "price": "23.50" },
					{ "number": "707", "name": "CÁ SALMON NƯỚNG, RAU SÓNG, BÁNH HỎI", "description": "Grilled Salmon with Lemon Served with Thin Vermicelli & Vegetables", "price": "23.50" },
					{ "number": "708", "name": "BO 7 MÓN", "description": "Combine 7 types of Beef on Dishes (For 2 Persons)", "price": "39.50" },
					{ "number": "709", "name": "BÒ NHÚNG DÁM", "description": "Beef Deep in Spicy Vinegar Hotpot (For 2 Persons)", "price": "36.50" }			
				]
			},
			{
				"menuName": "Lau - Hot Pot",
				"meals": [
					{ "number": "710", "name": "LÂU THẬP CẢM", "description": "Assorted Seafood Hotpot", "price": "62.50" },
					{ "number": "711", "name": "LÂU THÁI (CAY)", "description": "\"Thai\" Special Hotpot (Spicy)", "price": "62.50" }
				]
			},
			{
				"menuName": "Lunch and Dinner (for 2)",
				"meals": [
					{ "name": "2 CHẢ GIÒ HOẬC GỎI CUỐN TÔM THỊT", "description": "2 Spring Rolls or 2 Pork Fresh Rolls", "price": "42.50" },
					{ "name": "SÚP HOÀNH THÁNH HOẬC TOM-YUM TÔM", "description": "Wonton Soup or Tom-Yum Soup", "price": "42.50" },
					{ "name": "GÀ XÀO SATÉ HOẠC GÀ XÀO CÀ RI", "description": "Stir Fried Chicken with Satay or Stir-Fried Chicken Curry", "price": "42.50" },
					{ "name": "BÒ XÀO SATÉ HOẬC BỎ XÀO RAU CẢI", "description": "Stir Fried Beef with Satay Sauce or Vegetables", "price": "42.50" },
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
					{ "number": "801", "name": "CANH CHUA CÁ", "description": "Vietnamese Sweet & Sour Fish Soup", "price": "20.90" },
					{ "number": "802", "name": "CANH CHUA TÔM", "description": "Vietnamese Sweet & Sour Shrimp Soup", "price": "20.90" },
					{ "number": "803", "name": "CÁ KHO TỘ", "description": "Marinated Basa Fish & Pork Simmered in Earthen Wave Pot", "price": "16.90" },
					{ "number": "804", "name": "THỊT KHO TỘ", "description": "Marinated Pork w/Black Peppers Simmered in Earthen Wave Pot", "price": "16.90" },
					{ "number": "805", "name": "TÔM RANG SẢ ỚT", "description": "Sauteed Shrimp & Pork with Lemon Grass & Hot Pepper (Spicy)", "price": "16.90" },
					{ "number": "806", "name": "CÁ CHIM CHIÊN MÁM GỪNG", "description": "Fried White Promprel Fish Served w/Ginger, Garlic & Fish Sauce", "price": "15.90" },
					{ "number": "809", "name": "XÀ LÁCH XOONG XÀO THỊT BÒ", "description": "Stir Fried Beef with Watercresh", "price": "13.90" },
					{ "number": "810", "name": "BÒ XÀO ĐẶC BIỆT (Bò xào cay, chua, ngọt trên dĩa nóng)", "description": "Stir Fried Beef with Sweet & Sour Sauce on Sizzling Plate", "price": "18.90" },
					{ "number": "811", "name": "TÔM XÀO ĐẶC BIỆT (Tôm xào cay, chua, ngọt trên dĩa nóng)", "description": "Stir Fried Shrimp with Sweet & Sour Sauce on Sizzling Plate", "price": "19.90" },
					{ "number": "812", "name": "CÁ XÀO ĐẶC BIỆT (Cá xào cay, chua, ngọt trên đĩa nóng)", "description": "Stir Fried Fish with Sweet & Sour Sauce on Sizzling Plate", "price": "19.90" }
				]
			},
			{
				"menuName": "Stir Fried on Sizzling Plate",
				"meals": [
					{ "number": "813", "name": "MỰC XÀO ĐẶC BIỆT (Mực xào cay, chua, ngọt trên đĩa nóng)", "description": "Stir Fried Squid with Sweet & Sour Sauce on Sizzling Plate", "price": "18.90" },
					{ "number": "814", "name": "BÒ XÀO SATÉ TRÊN DĨA NÓNG", "description": "Stir Fried Beef with Satay Sauce on Sizzling Plate", "price": "19.90" },
					{ "number": "815", "name": "TÔM XÀO SATÉ TRÊN DĨA NÓNG", "description": "Stir Fried Shrimp with Satay Sauce on Sizzling Plate", "price": "19.90" },
					{ "number": "816", "name": "CÁ XÀO SATÉ TRÊN DĨA NÓNG", "description": "Stir Fried Fish with Satay Sauce on Sizzling Plate", "price": "19.90" },
					{ "number": "817", "name": "MỰC XÀO SATÉ TRÊN DĨA NÓNG", "description": "Stir Fried Squid with Satay Sauce on Sizzling Plate", "price": "18.90" },
					{ "number": "818", "name": "BỎ XÀO TIÊU HÀNH TRÊN DĨA NÓNG", "description": "Stir Fried Beef with Onion & Black Pepper on Sizzling Plate", "price": "18.90" },
					{ "number": "819", "name": "BỎ LÚC LÁC TRÊN DĨA NÓNG", "description": "Stir Fried Cubes of Beef on Sizzling Plate", "price": "19.90" },
					{ "number": "820", "name": "CHÉN CƠM", "description": "Steamed Rice (Small Bowl)", "price": "3.75" },
					{ "number": "821", "name": "DIA COM", "description": "Steamed Rice Dish", "price": "6.75" }
				]
			},
			{
				"menuName": "Mon Chay - Vegetarian",
				"meals": [
					{ "number": "V01", "name": "Chả Giò Chay", "description": "Vegetarian Spring Rolls with Tofu", "sizes": [{ "name": "Small", "price": "7.95" },{ "name": "Large", "price": "11.95"}] },
					{ "number": "V02", "name": "Gỏi Cuốn Chay", "description": "Vegetarian Fresh rolls with Tofu", "sizes": [{ "name": "Small", "price": "7.95" },{ "name": "Large", "price": "11.95"}] },
					{ "number": "V03", "name": "Phở rau cái, dầu hủ chạy", "description": "Vegetanan Rice Noodle Soup with Tofu", "sizes": [{ "name": "Medium", "price": "12.50" },{ "name": "Large", "price": "13.25"}] },
					

					{ "number": "V04", "name": "Bún Đậu Hủ CHIÊN.", "description": "Vegetarian Deep Fried Tofu with Vermicelli", "price": "11.45" },
					{ "number": "V05", "name": "Cơm CHIÊN Rau Cải Chay", "description": "Vegetarian Fried Rice", "price": "15.90" },
					{ "number": "V06", "name": "Cơm Rau Cai Xào Sa Tế Chạy", "description": "Fried Sautéed Vegetable with Satay on Rice", "price": "15.90" },
					{ "number": "V07", "name": "Cơm Đậu Hủ Xào Rau Gái Chạy", "description": "Vegetarian Stir Fried Tofu with Vegetable on Steamed Rice", "price": "15.90" },
					{ "number": "V08", "name": "Cơm Rau Cai Xào Sả ớt Chạy", "description": "Fred Sauteed Vegetable with Lemon Grass on Rice", "price": "15.90" },
					{ "number": "V09", "name": "Pad Thai Chay", "description": "Vegetarian Pad Thai with Tofu", "price": "15.90" },
					{ "number": "V10", "name": "Mì Xào Giòn Chay", "description": "Vegetarian Thick Lay of Deep Fried Egg Noodle Top with Tofu", "price": "16.90" },
					{ "number": "V11", "name": "Mì Xào Chay", "description": "Vegetarian Stir Fried Egg Noodle Top with Tofu", "price": "16.90" },
					{ "number": "V12", "name": "Hủ Tiểu Xào Chạy", "description": "Vegetarian Stir Fried Rice Noodle Top with Tofu", "price": "15.90" }
				]
			},
			{
				"menuName": "Additional Orders",
				"meals": [
					{ "number": "AD", "name": "CHÉN NƯỚC MẮM", "description": "Fish Sauce", "price": "1.50" },
					{ "number": "AD1", "name": "CHÉN SAUCE", "description": "Extra Sauce", "price": "2.00" },
					{ "number": "AD2", "name": "DĨA BÁNH HỎI HOẬC BÁNH TRÁNG", "description": "Thin Vermicelli or Rice Paper", "price": "2.50" },
					{ "number": "AD3", "name": "DĨA RAU THƠM", "description": "Extra Mint Herb Vegetables", "price": "3.50" },
					{ "number": "AD4", "name": "DĨA BÚN", "description": "Vermicelli", "price": "3.75" },
					{ "number": "AD5", "name": "OP LA, CHẢ TRỨNG", "description": "(Fried Egg, Steam Egg) \"each\"", "price": "2.50" },
					{ "number": "AD6", "name": "NEM NƯỚNG, BÁNH CÔNG", "description": "(Grilled Ground Pork Sausage, Shrimp Cake) \"each\"", "price": "3.00" },
					{ "number": "AD7", "name": "CHẢ GIÒ, SƯỜN NƯỚNG, THỊT NƯỚNG", "description": "(Fried Spring Roll, Grilled Pork Chop, Grilled Pork) \"each\"", "price": "5.00" },	
					{ "number": "AD8", "name": "GÀ NƯỚNG HOẬC SƯỜN BÒ NON NƯỚNG, BÒ NƯỚNG, CHẠO TÔM", "description": "(Grilled Chicken, Grilled Beef Ribs, Grilled Beef, Shrimp on Sugar Cane) \"each\"", "price": "5.50" },
					{ "number": "AD9", "name": "TÔM CÀNG", "description": "Jumbo Shrimp", "price": "7.00" },
					{ "number": "AD10", "name": "DĨA TÁI", "description": "Plate of Rare Beef", "price": "7.00" },
					{ "number": "AD12", "name": "DẦU CHÁO QUẢY", "description": "Chinese Frittiers", "price": "3.00" },
					{ "number": "AD13", "name": "THÊM SÚP (PHỜ)", "description": "Extra Noodle Soup (S)", "price": "6.00" },
					{ "number": "AD14", "name": "THÊM SÚP THÁI LAN", "description": "Extra \"Thai\" Hotpot Soup (S)", "price": "7.00" }
				]
			},
			{
				"menuName": "Giat Khat - Beverages",
				"meals": [
					{ "number": "N01", "name": "CÀ PHÊ SỮA ĐÁ", "description": "Iced Coffee with Condensed Milk", "price": "4.50" },
					{ "number": "N02", "name": "CÀ PHÊ ĐEN ĐÁ", "description": "Black Iced Coffee", "price": "4.50" },
					{ "number": "N03", "name": "CHÈ 3 MÀU", "description": "Three Kinds of Mung Bean with Coconut Milk", "price": "5.00" },
					{ "number": "N04", "name": "SINH TỐ BỔ", "description": "Avocado Milk Shake", "price": "5.00" },
					{ "number": "N05", "name": "SINH TỐ DÂU", "description": "Strawberry Milk Shake", "price": "5.00" },
					{ "number": "N06", "name": "SINH TỐ XOÀI", "description": "Mango Milk Shake", "price": "5.00" },
					{ "number": "N07", "name": "SINH TỐ MÍT", "description": "Jack Fruit Milk Shake", "price": "5.00" },
					{ "number": "N08", "name": "SINH TỐ SÂU RIÊNG", "description": "Durian Milk Shake", "price": "5.50" },
					{ "number": "N09", "name": "SINH TỐ ĐẬU XANH", "description": "Green Bean Milk Shake", "price": "5.00" },
					{ "number": "N10", "name": "SINH TÔ ĐẬU ĐEN", "description": "Red Bean Milk Shake", "price": "5.00" },
					{ "number": "N11", "name": "SINH TỐ DỪA TƯƠI", "description": "Coconut Milk Shake", "price": "5.00" },
					{ "number": "N12", "name": "SINH TÔ DỪA TƯƠI, ĐẬU ĐEN", "description": "Coconut Mixs with Red Bean Milk Shake", "price": "5.50" },
					{ "number": "N13", "name": "NƯỚC DỪA TƯƠI", "description": "Fresh Coconut Juice", "price": "5.00" },
					{ "number": "N14", "name": "NƯỚC TRÁI VẢI", "description": "Lychee with Ice", "price": "5.00" },
					{ "number": "N15", "name": "SODA CHANH MUỐI", "description": "Salted Lime Juice with Soda", "price": "5.00" },
					{ "number": "N16", "name": "SODA CHANH TƯƠI", "description": "Fresh Lime Juice with Soda", "price": "5.00" },
					{ "number": "N17", "name": "SODA XÍ MUQI", "description": "Picked Plums with Soda", "price": "5.00" },
					{ "number": "N18", "name": "SINH TÔ MÀNG CẦU", "description": "Soursop Smoothie", "price": "5.00" },
					{ "number": "N19", "name": "POP CÁC LOẠI", "description": "Nestea, Coke, Diet Coke, 7-Up, Orange Pop. Water Bottle\nChoice of Jelly: Mixed Jelly, Lychee Coconut Jelly, Passion Fruit Jelly", "price": "2.50" },
					{ "number": "N20", "name": "BUBBLE TEA", "description": "Taro, Honeydew, Strawberry, Mango, Lychee, Green Apple, Grapefruit with Fresh Lime\nCaramel Flan Cake with Blue", "price": "5.50" },
					{ "number": "N32", "name": "NƯỚC CHANH DÂY", "description": "Pure Passion Fruit Juice", "price": "6.00" },
					{ "number": "N33", "name": "NƯỚC CAM EP", "description": "Fresh Orange Juice", "price": "6.00" },
					{ "number": "N34", "name": "SÂM BỎ LƯỢNG", "description": "\"Ching Bo Leung\" Sweet and Cold Soup", "price": "6.50" },
					{ "number": "N35", "name": "BÁNH FLAN", "description": "Caramel Flan Cake with Blueberry, Raspberry", "price": "6.00" },
					{ "number": "N36", "name": "SỮA ĐẬU NÀNH", "description": "Soymilk", "price": "2.00" }
				]
			},
			{
				"menuName": "Bia Ruou - Beer & Liquor",
				"image": "drinks.png",
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
	}




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

	location = query("select info from location where id = " + str(locationId), True).fetchone()
	imSize = Image.open('static/' + list["logo"])

	info = json.loads(location["info"])
	info["listed"] = True

	logoName = getId() + ".png"
	logo = json.dumps({"name": logoName, "width": str(imSize.width), "height": str(imSize.height)})

	query("update location set logo = '" + logo + "', info = '" + json.dumps(info) + "' where id = " + str(locationId))

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
