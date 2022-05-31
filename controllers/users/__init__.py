from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_users", methods=["GET"])
def welcome_users():
	datas = User.query.all()
	users = []

	for data in datas:
		users.append(data.id)

	return { "msg": "welcome to users of easygo", "users": users }

@app.route("/user_login", methods=["POST"])
def user_login():
	content = request.get_json()

	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['password']
	errormsg = ""
	status = ""

	if cellnumber != '' and password != '':
		user = query("select * from user where cellnumber = '" + str(cellnumber) + "'", True).fetchone()

		if user != None:
			if check_password_hash(user["password"], password):
				userid = user["id"]

				user["password"] = generate_password_hash(password)

				update_data = []
				for key in user:
					if key != "table":
						update_data.append(key + " = '" + str(user[key]) + "'")

				query("update user set " + ", ".join(update_data) + " where id = " + str(userid))

				if user["username"] == '':
					return { "id": userid, "msg": "setup" }
				else:
					return { "id": userid, "msg": "main" }
			else:
				errormsg = "Password is incorrect"
		else:
			errormsg = "Account doesn't exist"
			status = "nonexist"
	else:
		if cellnumber == '':
			errormsg = "Cell number is blank"
		else:
			errormsg = "Password is blank"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/user_verify/<cellnumber>")
def user_verify(cellnumber):
	verifycode = getRanStr()

	cellnumber = cellnumber.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	user = query("select * from user where cellnumber = '" + str(cellnumber) + "'", True).fetchone()
	errormsg = ""
	status = ""

	if user == None:
		if test_sms == False:
			message = client.messages.create(
				body='Verify code: ' + str(verifycode),
				messaging_service_sid=mss,
				to='+1' + str(cellnumber)
			)

		return { "verifycode": verifycode }
	else:
		errormsg = "Cell number already used"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/user_register", methods=["POST"])
def user_register():
	content = request.get_json()

	username = content['username']
	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['password']
	confirmPassword = content['confirmPassword']
	errormsg = ""
	status = ""

	if username != "" and cellnumber != '' and password != '' and confirmPassword != '':
		if len(password) >= 6:
			if password == confirmPassword:
				user = query("select * from user where cellnumber = '" + str(cellnumber) + "'", True).fetchone()

				if user == None:
					password = generate_password_hash(password)

					userInfo = json.dumps({"pushToken": ""})

					data = {
						"cellnumber": cellnumber,
						"password": password,
						"username": username,
						"info": userInfo
					}
					insert_data = []
					columns = []
					for key in data:
						columns.append(key)
						insert_data.append("'" + str(data[key]) + "'")

					id = query("insert into user (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

					return { "id": id }
				else:
					errormsg = "User already exist"
			else:
				errormsg = "Password is mismatch"
		else:
			errormsg = "Password needs to be atleast 6 characters long"
	else:
		if username == '':
			errormsg = "Please enter your name"
		elif cellnumber == '':
			errormsg = "Cell number is blank"
		elif password == '':
			errormsg = "Password is blank"
		else:
			errormsg = "Please confirm your password"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_user", methods=["POST"])
def update_user():
	content = request.get_json()

	userid = content['userid']
	username = content['username']
	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['password']
	confirmPassword = content['confirmPassword']

	user = query("select * from user where id = " + str(userid), True).fetchone()
	existed_username = query("select count(*) as num from user where username = '" + str(username) + "'", True).fetchone()["num"]
	existed_cellnumber = query("select count(*) as num from user where cellnumber = '" + str(cellnumber) + "'", True).fetchone()["num"]

	errormsg = ""
	status = ""

	if username != "":
		if user["username"] != username:
			if existed_username == 0:
				user["username"] = username
			else:
				errormsg = "This username is already taken"
				status = "sameusername"

	if cellnumber != "":
		if user["cellnumber"] != cellnumber:
			if existed_cellnumber == 0:
				user["cellnumber"] = cellnumber
			else:
				errormsg = "This cell number is already taken"
				status = "samecellnumber"

	if password != "" or confirmPassword != "":
		if password != "" and confirmPassword != "":
			if len(password) > 6:
				if password == confirmPassword:
					user["password"] = generate_password_hash(password)
				else:
					errormsg = "Password mismatch"
			else:
				errormsg = "Password needs to be atleast 6 characters long"
		else:
			if password == "":
				errormsg = "Password is blank"
			else:
				errormsg = "Please confirm your new password"

	if errormsg == "":
		update_data = []
		for key in user:
			if key != "table":
				update_data.append(key + " = '" + str(user[key]) + "'")

		query("update user set " + ", ".join(update_data) + " where id = " + str(userid))

		return { "msg": "update successfully" }

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_user_notification_token", methods=["POST"])
def update_user_notification_token():
	content = request.get_json()

	userid = content['userid']
	token = content['token']

	user = query("select * from user where id = " + str(userid), True).fetchone()
	errormsg = ""
	status = ""

	info = json.loads(user["info"])
	info["pushToken"] = token

	query("update user set info = '" + json.dumps(info) + "' where id = " + str(info["id"]))

	return { "msg": "Push token updated" }

@app.route("/get_user_info/<id>")
def get_user_info(id):
	user = query("select * from user where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	cellnumber = user["cellnumber"]

	f3 = str(cellnumber[0:3])
	s3 = str(cellnumber[3:6])
	l4 = str(cellnumber[6:len(cellnumber)])

	cellnumber = "(" + f3 + ") " + s3 + "-" + l4

	info = {
		"id": id,
		"username": user["username"],
		"cellnumber": cellnumber
	}

	return { "userInfo": info }

@app.route("/get_num_notifications/<userid>")
def get_num_notifications(userid):
	user = query("select * from user where id = " + str(userid), True).fetchone()
	errormsg = ""
	status = ""

	num = 0

	# cart orders called for self
	sql = "select count(*) as num from cart where adder = " + userid + " and (status = 'checkout' or status = 'ready') group by adder, orderNumber"
	numCartorderers = query(sql, True).fetchone()
	numCartorderers = numCartorderers["num"] if numCartorderers != None else 0

	return { "numCartorderers": numCartorderers }

	num += numCartorderers

	# get schedules
	sql = "select count(*) as num from schedule where userId = " + userid + " and (status = 'cancel' or status = 'confirmed')"
	num += query(sql, True).fetchone()["num"]

	return { "numNotifications": num }

@app.route("/get_notifications/<id>")
def get_notifications(id):
	user = query("select * from user where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	userId = user["id"]
	notifications = []

	# cart orders called for self
	sql = "select orderNumber from cart where adder = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by orderNumber"
	datas = query(sql, True).fetchall()

	for data in datas:
		cartitem = query("select * from cart where orderNumber = '" + str(data["orderNumber"]) + "'", True).fetchone()
		numCartitems = query("select count(*) as num from cart where orderNumber = '" + str(data["orderNumber"]) + "'", True).fetchone()["num"]

		userInput = json.loads(cartitem["userInput"])

		notifications.append({
			"key": "order-" + str(len(notifications)),
			"type": "cart-order-self",
			"orderNumber": data['orderNumber'],
			"numOrders": numCartitems,
			"status": cartitem["status"],
			"waitTime": cartitem["waitTime"],
			"locationType": userInput["type"]
		})

	# get schedules
	sql = "select * from schedule where "
	sql += "(userId = " + str(id) + " and (status = 'cancel' or status = 'confirmed'))"
	datas = query(sql, True).fetchall()

	for data in datas:
		location = None
		service = None

		if data['locationId'] != "":
			location = query("select * from location where id = " + str(data["locationId"]), True).fetchone()

		if data['serviceId'] != -1:
			service = query("select * from service where id = " + str(data["serviceId"]), True).fetchone()

		booker = query("select * from user where id = " + str(data["userId"]), True).fetchone()
		confirm = False
		info = json.loads(data['info'])
			
		if data["workerId"] > -1:
			owner = query("select * from owner where id = " + str(data["workerId"]), True).fetchone()

			worker = { "id": data["workerId"], "username": owner["username"] }
		else:
			worker = None

		userInput = json.loads(data['userInput'])
		serviceImage = json.loads(service["image"]) if service != None else {"name": ""}
		notifications.append({
			"key": "order-" + str(len(notifications)),
			"type": "service",
			"id": str(data['id']),
			"locationid": data['locationId'],
			"location": location["name"],
			"worker": worker,
			"menuid": int(data['menuId']) if data['menuId'] != "" else "",
			"serviceid": int(data['serviceId']) if data['serviceId'] != -1 else "",
			"service": service["name"] if service != None else userInput['name'] if 'name' in userInput else "",
			"locationimage": json.loads(location["logo"]),
			"locationtype": location["type"],
			"serviceimage": serviceImage if serviceImage["name"] != "" else {"width": 300, "height": 300},
			"serviceprice": float(service["price"]) if service != None else float(userInput['price']) if 'price' in userInput else "",
			"time": json.loads(data['time']),
			"action": data['status'],
			"reason": data['cancelReason'],
			"booker": userId == data['userId'],
			"bookerName": booker["username"],
			"confirm": confirm,
			"workerInfo": { "id": owner["id"], "username": owner["username"] } if data["workerId"] > -1 else {}
		})

	return { "notifications": notifications }

@app.route("/get_reset_code/<phonenumber>")
def get_user_reset_code(phonenumber):
	user = query("select * from user where cellnumber = " + str(phonenumber), True).fetchone()
	errormsg = ""
	status = ""

	code = getRanStr()

	if test_sms == False:
		message = client.messages.create(
			body="Your EasyGO reset code is " + code,
			messaging_service_sid=mss,
			to='+1' + str(user["cellnumber"])
		)

	return { "msg": "Reset code sent", "code": code }

@app.route("/reset_password", methods=["POST"])
def user_reset_password():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['newPassword']
	confirmPassword = content['confirmPassword']

	user = query("select * from user where cellnumber = " + str(cellnumber), True).fetchone()
	errormsg = ""
	status = ""

	if password != '' and confirmPassword != '':
		if len(password) >= 6:
			if password == confirmPassword:
				password = generate_password_hash(password)

				query("update user set password = '" + password + "' where id = " + str(user["id"]))

				if user["username"] == '':
					return { "id": user["id"], "msg": "setup" }
				else:
					return { "id": user["id"], "msg": "main" }
			else:
				errormsg = "Password is mismatch"
		else:
			errormsg = "Password needs to be atleast 6 characters long"
	else:
		if password == '':
			errormsg = "Password is blank"
		else:
			errormsg = "Please confirm your password"
