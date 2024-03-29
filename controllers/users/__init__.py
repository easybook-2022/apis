from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

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

				if user["username"] == '':
					return { "id": userid, "msg": "setup" }
				else:
					return { "id": userid, "msg": "main" }
			else:
				errormsg = "Password is incorrect"
		else:
			status = "nonexist"
	else:
		if cellnumber == '':
			errormsg = "Cell number is blank"
		else:
			errormsg = "Password is blank"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/user_verify/<cellnumber>")
def user_verify(cellnumber):
	verifycode = getId()

	cellnumber = cellnumber.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	user = query("select * from user where cellnumber = '" + str(cellnumber) + "'", True).fetchone()
	errormsg = ""
	status = ""

	if user == None:
		if send_text == True:
			message = client.messages.create(
				body='EasyBook User Verify code: ' + str(verifycode),
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

	if cellnumber != '' and password != '' and confirmPassword != '':
		if len(password) >= 6:
			if password == confirmPassword:
				user = query("select * from user where cellnumber = '" + str(cellnumber) + "'", True).fetchone()

				if user == None:
					password = generate_password_hash(password)

					data = {
						"username": username,
						"cellnumber": cellnumber,
						"password": password,
						"info": json.dumps({"pushToken": ""})
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
		if cellnumber == '':
			errormsg = "Cell number is blank"
		elif password == '':
			errormsg = "Password is blank"
		else:
			errormsg = "Please confirm your password"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_user", methods=["POST"])
def update_user():
	content = request.get_json()
	errormsg = ""
	status = ""

	userid = content['userid']
	username = content['username']
	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['password']
	confirmPassword = content['confirmPassword']

	user = query("select * from user where id = " + str(userid), True).fetchone()

	if user != None:
		existed_username = query("select count(*) as num from user where username = '" + str(username) + "'", True).fetchone()["num"]
		existed_cellnumber = query("select count(*) as num from user where cellnumber = '" + str(cellnumber) + "'", True).fetchone()["num"]

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
				if len(password) >= 6:
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
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_user_notification_token", methods=["POST"])
def update_user_notification_token():
	content = request.get_json()
	errormsg = ""
	status = ""

	userid = content['userid']
	token = content['token']

	user = query("select * from user where id = " + str(userid), True).fetchone()

	if user != None:
		errormsg = ""
		status = ""

		info = json.loads(user["info"])
		info["pushToken"] = token

		query("update user set info = '" + json.dumps(info) + "' where id = " + str(userid))

		return { "msg": "Push token updated" }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_user_info/<id>")
def get_user_info(id):
	errormsg = ""
	status = ""

	user = query("select * from user where id = " + str(id), True).fetchone()

	if user != None:
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
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_num_notifications/<userid>")
def get_num_notifications(userid):
	errormsg = ""
	status = ""

	user = query("select * from user where id = " + str(userid), True).fetchone()

	if user != None:
		num = 0

		# cart orders called for self
		sql = "select count(*) as num from cart where adder = " + userid + " and (status = 'checkout' or status = 'ready') group by adder, orderNumber"
		numCartorderers = query(sql, True).fetchone()
		numCartorderers = numCartorderers["num"] if numCartorderers != None else 0

		num += numCartorderers

		# get schedules
		sql = "select count(*) as num from schedule where userId = " + userid + " and (status = 'cancel' or status = 'confirmed')"
		num += query(sql, True).fetchone()["num"]

		return { "numNotifications": num }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_notifications/<id>")
def get_notifications(id):
	errormsg = ""
	status = ""

	user = query("select * from user where id = " + str(id), True).fetchone()

	if user != None:
		userId = user["id"]
		notifications = []

		# cart orders called for self
		sql = "select orderNumber from cart where adder = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by orderNumber"
		datas = query(sql, True).fetchall()

		for data in datas:
			cartitem = query("select * from cart where orderNumber = '" + str(data["orderNumber"]) + "'", True).fetchone()
			numCartitems = query("select count(*) as num from cart where orderNumber = '" + str(data["orderNumber"]) + "'", True).fetchone()["num"]
			location = query("select * from location where id = " + str(cartitem["locationId"]), True).fetchone()

			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "cart-order-self",
				"orderNumber": data['orderNumber'],
				"numOrders": numCartitems,
				"status": cartitem["status"],
				"waitTime": cartitem["waitTime"],
				"locationType": location["type"]
			})

		# get schedules
		sql = "select * from schedule where "
		sql += "(userId = " + str(id) + " and (status = 'cancel' or status = 'confirmed')) order by concat("
		sql += "json_extract(time, '$.year'), "
		sql += "json_extract(time, '$.month'), "
		sql += "json_extract(time, '$.date'), "
		sql += "json_extract(time, '$.hour'), "
		sql += "json_extract(time, '$.minute')"
		sql += ")"
		datas = query(sql, True).fetchall()

		for data in datas:
			time = json.loads(data["time"])
			location = query("select * from location where id = " + str(data["locationId"]), True).fetchone()
			service = query("select * from service where id = " + str(data["serviceId"]), True).fetchone()
			booker = query("select * from user where id = " + str(data["userId"]), True).fetchone()
			confirm = False
			info = json.loads(data['info'])
				
			owner = query("select * from owner where id = " + str(data["workerId"]), True).fetchone()
			worker = { "id": data["workerId"], "username": owner["username"] }
			
			time = {"day": indexToDay[time["day"]], "month": indexToMonth[time["month"]], "date": time["date"], "year": time["year"], "hour": time["hour"], "minute": time["minute"]}

			locationLogo = json.loads(location["logo"])
			serviceImage = json.loads(service["image"])

			# get points and reward information

			numVisited = query("select count(*) as num from income_record where json_extract(service, '$.userId') = " + str(id) + " and locationId = " + str(data["locationId"]), True).fetchone()["num"]

			if numVisited % 7 == 0:
				leftoverPoints = 0
			else:
				leftoverPoints = 7 - (numVisited % 7)

			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "service",
				"id": str(data['id']),
				"locationid": data['locationId'],
				"location": location["name"],
				"worker": worker,
				"menuid": int(data['menuId']) if data['menuId'] != "" else "",
				"serviceid": int(data['serviceId']) if data['serviceId'] != -1 else "",
				"service": service["name"],
				"locationimage": locationLogo if locationLogo["name"] != "" else { "width": 300, "height": 300 },
				"locationtype": location["type"],
				"serviceimage": serviceImage if serviceImage["name"] != "" else {"width": 300, "height": 300},
				"serviceprice": float(service["price"]),
				"time": time,
				"action": data['status'],
				"reason": data['cancelReason'],
				"booker": userId == data['userId'],
				"bookerName": booker["username"],
				"confirm": confirm,
				"workerInfo": { "id": owner["id"], "username": owner["username"] } if data["workerId"] > -1 else {},
				"leftoverVisits": leftoverPoints
			})

		return { "notifications": notifications }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_reset_code/<phonenumber>")
def get_user_reset_code(phonenumber):
	user = query("select * from user where cellnumber = " + str(phonenumber), True).fetchone()
	errormsg = ""
	status = ""

	code = getId()

	if send_text == True:
		message = client.messages.create(
			body="Your EasyBook reset code is " + code,
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
