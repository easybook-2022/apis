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
		user = User.query.filter_by(cellnumber=cellnumber).first()

		if user != None:
			if check_password_hash(user.password, password):
				userid = user.id

				user.password = generate_password_hash(password)

				db.session.commit()

				if user.username == '':
					return { "id": userid, "msg": "setup" }
				else:
					return { "id": userid, "msg": "main" }
			else:
				errormsg = "Password is incorrect"
		else:
			errormsg = "User doesn't exist"
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
	user = User.query.filter_by(cellnumber=cellnumber).first()
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
				user = User.query.filter_by(cellnumber=cellnumber).first()

				if user == None:
					password = generate_password_hash(password)

					userInfo = json.dumps({"pushToken": ""})

					user = User(cellnumber, password, username, userInfo)
					db.session.add(user)
					db.session.commit()

					return { "id": user.id }
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

	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		if username != "":
			if user.username != username:
				exist_username = User.query.filter_by(username=username).count()

				if exist_username == 0:
					user.username = username
				else:
					errormsg = "This username is already taken"
					status = "sameusername"

		if cellnumber != "":
			if user.cellnumber != cellnumber:
				exist_cellnumber = User.query.filter_by(cellnumber=cellnumber).count()

				if exist_cellnumber == 0:
					user.cellnumber = cellnumber
				else:
					errormsg = "This cell number is already taken"
					status = "samecellnumber"

		if password != "" or confirmPassword != "":
			if password != "" and confirmPassword != "":
				if len(password) > 6:
					if password == confirmPassword:
						user.password = generate_password_hash(password)
					else:
						errormsg = "Password mismatch"
				else:
					errormsg = "Password needs to be atleast 6 characters long"
			else:
				if password == "":
					errormsg = "Password is blank"
				else:
					errormsg = "Please confirm your new password"

		info = json.loads(user.info)

		if errormsg == "":
			db.session.commit()

			return { "msg": "update successfully" }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_user_notification_token", methods=["POST"])
def update_user_notification_token():
	content = request.get_json()

	userid = content['userid']
	token = content['token']

	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		info = json.loads(user.info)
		info["pushToken"] = token

		user.info = json.dumps(info)

		db.session.commit()

		return { "msg": "Push token updated" }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_user_info/<id>")
def get_user_info(id):
	user = User.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if user != None:
		cellnumber = user.cellnumber

		f3 = str(cellnumber[0:3])
		s3 = str(cellnumber[3:6])
		l4 = str(cellnumber[6:len(cellnumber)])

		cellnumber = "(" + f3 + ") " + s3 + "-" + l4

		info = {
			"id": id,
			"username": user.username,
			"cellnumber": cellnumber
		}

		return { "userInfo": info }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_num_notifications/<userid>")
def get_num_notifications(userid):
	user = User.query.filter_by(id=userid).first()
	errormsg = ""
	status = ""

	if user != None:
		num = 0

		# cart orders called for self
		sql = "select count(*) as num from cart where adder = " + userid + " and (status = 'checkout' or status = 'ready') group by adder, orderNumber"
		numCartorderers = query(sql, True)
		num += numCartorderers[0]["num"] if len(numCartorderers) > 0 else 0

		# get schedules
		sql = "select count(*) as num from schedule where userId = " + userid + " and (status = 'cancel' or status = 'confirmed')"
		num += query(sql, True)[0]["num"]

		return { "numNotifications": num }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_notifications/<id>")
def get_notifications(id):
	user = User.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if user != None:
		userId = user.id
		notifications = []

		# cart orders called for self
		sql = "select orderNumber from cart where adder = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by orderNumber"
		datas = query(sql, True)

		for data in datas:
			cartitem = Cart.query.filter_by(orderNumber=data["orderNumber"]).first()
			numCartitems = Cart.query.filter_by(orderNumber=data["orderNumber"]).count()

			userInput = json.loads(cartitem.userInput)

			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "cart-order-self",
				"orderNumber": data['orderNumber'],
				"numOrders": numCartitems,
				"status": cartitem.status,
				"waitTime": cartitem.waitTime,
				"locationType": userInput["type"]
			})

		# get schedules
		sql = "select * from schedule where "
		sql += "(userId = " + str(id) + " and (status = 'cancel' or status = 'confirmed'))"
		datas = query(sql, True)

		for data in datas:
			location = None
			service = None

			if data['locationId'] != "":
				location = Location.query.filter_by(id=data['locationId']).first()

			if data['serviceId'] != -1:
				service = Service.query.filter_by(id=data['serviceId']).first()

			booker = User.query.filter_by(id=data['userId']).first()
			confirm = False
			info = json.loads(data['info'])
				
			if data["workerId"] > -1:
				owner = Owner.query.filter_by(id=data["workerId"]).first()

				worker = {
					"id": data["workerId"],
					"username": owner.username
				}
			else:
				worker = None

			userInput = json.loads(data['userInput'])
			serviceImage = json.loads(service.image) if service != None else {"name": ""}
			notifications.append({
				"key": "order-" + str(len(notifications)),
				"type": "service",
				"id": str(data['id']),
				"locationid": data['locationId'],
				"location": location.name,
				"worker": worker,
				"menuid": int(data['menuId']) if data['menuId'] != "" else "",
				"serviceid": int(data['serviceId']) if data['serviceId'] != -1 else "",
				"service": service.name if service != None else userInput['name'] if 'name' in userInput else "",
				"locationimage": json.loads(location.logo),
				"locationtype": location.type,
				"serviceimage": serviceImage if serviceImage["name"] != "" else {"width": 300, "height": 300},
				"serviceprice": float(service.price) if service != None else float(userInput['price']) if 'price' in userInput else "",
				"time": json.loads(data['time']),
				"action": data['status'],
				"reason": data['cancelReason'],
				"table": data['table'],
				"booker": userId == data['userId'],
				"bookerName": booker.username,
				"confirm": confirm,
				"seated": info["dinersseated"] if "dinersseated" in info else None,
				"requestPayment": True if "price" in userInput else False,
				"workerInfo": {
					"id": owner.id,
					"username": owner.username,
					"requestprice": float(userInput["price"]) if "price" in userInput else 0,
					"tip": 0
				} if data["workerId"] > -1 else {}
			})

		return { "notifications": notifications }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_reset_code/<phonenumber>")
def get_user_reset_code(phonenumber):
	user = User.query.filter_by(cellnumber=phonenumber).first()
	errormsg = ""
	status = ""

	if user != None:
		code = getRanStr()

		if test_sms == False:
			message = client.messages.create(
				body="Your EasyGO reset code is " + code,
				messaging_service_sid=mss,
				to='+1' + str(user.cellnumber)
			)

		return { "msg": "Reset code sent", "code": code }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/reset_password", methods=["POST"])
def user_reset_password():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['newPassword']
	confirmPassword = content['confirmPassword']

	user = User.query.filter_by(cellnumber=cellnumber).first()
	errormsg = ""
	status = ""

	if user != None:
		if password != '' and confirmPassword != '':
			if len(password) >= 6:
				if password == confirmPassword:
					password = generate_password_hash(password)

					user.password = password

					db.session.commit()

					if user.username == '':
						return { "id": user.id, "msg": "setup" }
					else:
						return { "id": user.id, "msg": "main" }
				else:
					errormsg = "Password is mismatch"
			else:
				errormsg = "Password needs to be atleast 6 characters long"
		else:
			if password == '':
				errormsg = "Password is blank"
			else:
				errormsg = "Please confirm your password"
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
