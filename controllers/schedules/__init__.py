from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_schedules", methods=["GET"])
def welcome_schedules():
	datas = Schedule.query.all()
	schedules = []

	for data in datas:
		schedules.append(data.id)

	return { "msg": "welcome to schedules of easygo", "schedules": schedules }

@app.route("/get_requests", methods=["POST"])
def get_requests():
	content = request.get_json()

	ownerid = content['ownerid']
	locationid = content['locationid']

	errormsg = ""
	status = ""

	# get requested schedules
	datas = query("select * from schedule where locationId = " + str(locationid) + " and (status = 'requested' or status = 'change' or status = 'accepted')", True).fetchall()
	requests = []

	for data in datas:
		service = None

		if data['serviceId'] != "":
			service = query("select * from service where id = " + str(data['serviceId']), True).fetchone()

		user = query("select * from id = " + str(data['userId']), True).fetchone()

		if data['workerId'] > -1:
			owner = query("select * from owner where id = " + str(data['workerId']), True).fetchone()

			worker = { "id": data['workerId'], "username": owner["username"] }
		else:
			worker = None

		userInput = json.loads(data['userInput'])
		image = json.loads(service[0]["image"]) if service != {} else {"name": ""}
		requests.append({
			"key": "request-" + str(data['id']),
			"id": str(data['id']),
			"type": data['locationType'],
			"worker": worker,
			"userId": user["id"],
			"username": user["username"],
			"time": json.loads(data['time']),
			"name": service["name"] if service != None else userInput['name'] if 'name' in userInput else "",
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"note": data['note'],
			"status": data['status']
		})

	return { "requests": requests, "numrequests": len(requests) }

@app.route("/get_appointment_info/<id>")
def get_appointment_info(id):
	schedule = query("select * from schedule where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	locationId = schedule["locationId"]
	serviceId = schedule["serviceId"]
	userId = schedule["userId"]
	userInput = json.loads(schedule["userInput"])
	
	client = query("select * from user where id = " + str(userId), True).fetchone()

	worker = None

	if schedule["workerId"] > 0:
		workerInfo = query("select * from owner where id = " + str(schedule["workerId"]), True).fetchone()

		days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
		hours = json.loads(workerInfo["hours"])
		info = {}
		for day in days:
			if hours[day]["working"] == True:
				info[day] = {
					"start": hours[day]["opentime"]["hour"] + ":" + hours[day]["opentime"]["minute"],
					"end": hours[day]["closetime"]["hour"] + ":" + hours[day]["closetime"]["minute"],
					"working": hours[day]["working"]
				}

		worker = { "id": schedule["workerId"], "username": workerInfo["username"], "profile": workerInfo["profile"], "days": info }

	info = { 
		"client": { 
			"id": userId, 
			"name": client["username"] if client != None else userInput["name"] if "name" in userInput else "", 
			"cellnumber": userInput["cellnumber"] if "cellnumber" in userInput else None
		},
		"locationId": int(locationId), 
		"serviceId": int(serviceId) if serviceId > -1 else None, 
		"time": json.loads(schedule["time"]), 
		"worker": worker
	}

	if serviceId != -1:
		service = query("select * from service where id = " + str(serviceId), True).fetchone()

		info["name"] = service["name"]
	else:
		userInput = json.loads(schedule["userInput"])

		info["name"] = userInput["name"] if "name" in userInput else ""

	if errormsg == "":
		return info

@app.route("/make_appointment", methods=["POST"])
def make_appointment():
	content = request.get_json()
	errormsg = ""
	status = ""

	scheduleid = content['id']
	userid = content['userid']
	workerid = content['workerid']
	locationid = content['locationid']
	serviceid = content['serviceid']
	serviceinfo = content['serviceinfo']
	time = content['time']
	note = content['note']
	timeDisplay = content['timeDisplay']

	user = query("select * from user where id = " + str(userid), True).fetchone()
	location = query("select * from location where id = " + str(locationid), True).fetchone()

	if serviceid != -1:
		service = query("select * from service where id = " + str(serviceid), True).fetchone()
		schedule = query("select * from schedule where userId = " + str(userid) + " and serviceId = " + str(serviceid), True).fetchone()
		servicename = service["name"]
		menuid = service["menuId"]
	else:
		if scheduleid != None:
			schedule = query("select * from schedule where id = " + str(scheduleid), True).fetchone()
		else:
			schedule = None
		
		servicename = serviceinfo
		menuid = -1

	worker = query("select * from owner where id = " + str(workerid), True).fetchone()

	info = json.loads(location["info"])
	type = info["type"]

	sql = "select id, info from owner where "

	if type == "computer":
		sql += "info like '%\"locationId\": \"" + str(locationid) + "\"%' and info like '%\"owner\": true\"%'"
	else:
		sql += "id = " + str(workerid)

	owners = query(sql, True)
	locationInfo = json.loads(location["info"])
	receiver = []
	pushids = []

	for owner in owners:
		info = json.loads(owner["info"])

		receiver.append("owner" + str(owner["id"]))

		if info["pushToken"] != "" and info["signin"] == True:
			pushids.append({ "token": info["pushToken"], "signin": info["signin"] })

	if schedule != None: # existing schedule
		schedule["time"] = time
		schedule["status"] = 'confirmed'
		schedule["note"] = note
		schedule["workerId"] = workerid

		update_data = []
		for key in schedule:
			if key != "table":
				update_data.append(key + " = '" + str(schedule[key]) + "'")

		query("update schedule set " + ", ".join(update_data) + " where id = " + str(schedule["id"]))

		if len(pushids) > 0:
			pushmessages = []
			for info in pushids:
				pushmessages.append(pushInfo(
					info["token"], 
					"Appointment remade",
					"A client remade an appointment for service: " + servicename + " " + str(timeDisplay),
					content
				))
			
			push(pushmessages)

		speak = { "scheduleid": schedule["id"], "name": servicename, "time": json.loads(time), "worker": { "id": workerid, "username": worker["username"] }}

		return { "msg": "appointment remade", "receiver": receiver, "time": time, "speak": speak }
	else: # new schedule
		info = json.dumps({})
		userInput = json.dumps({ "name": serviceinfo, "type": "service" })

		data = {
			"userId": userid,"workerId": workerid,"locationId": locationid,"menuId": menuid,"serviceId": serviceid,
			"userInput": userInput,"time": time,"status": "confirmed","cancelReason": "","locationType": location["type"],
			"customers": 1,"note": note,"orders": "[]","info": info
		}
		columns = []
		insert_data = []
		for key in data:
			columns.append(key)
			insert_data.append("'" + str(data[key]) + "'")

		id = query("insert into schedule (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

		if len(pushids) > 0:
			pushmessages = []
			for info in pushids:
				pushmessages.append(pushInfo(
					info["token"], 
					"Appointment made",
					"A client made an appointment for service: " + servicename + " " + str(timeDisplay),
					content
				))

			push(pushmessages)

		speak = { "scheduleid": id, "name": servicename, "time": json.loads(time), "worker": { "id": workerid, "username": worker["username"] }}

		return { "msg": "appointment added", "receiver": receiver, "speak": speak }

@app.route("/book_walk_in", methods=["POST"])
def book_walk_in():
	content = request.get_json()

	workerid = content['workerid']
	locationid = content['locationid']
	time = content['time']
	note = content['note']
	type = content['type']
	client = content['client']

	data = {
		"userId": -1,"workerId": workerid,"locationId": locationid,"menuId": -1,"serviceId": -1,
		"userInput": json.dumps(client),"time": json.dumps(time),"status": "confirmed","cancelReason": "","locationType": type,
		"customers": 1,"note": note,"orders": "[]","info": "{}"
	}
	columns = []
	insert_data = []
	for key in data:
		columns.append(key)
		insert_data.append("'" + str(data[key]) + "'")

	id = query("insert into schedule (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

	return { "msg": "success", "id": id }

@app.route("/remove_booking", methods=["POST"])
def remove_booking():
	content = request.get_json()

	id = content['scheduleid']
	reason = content['reason']

	appointment = query("select * from schedule where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if appointment != None:
		user = query("select * from user where id = " + str(appointment["userId"]), True).fetchone()

		if appointment["status"] == "confirmed":
			appointment["status"] = "cancel"
			appointment["cancelReason"] = reason

			update_data = []
			for key in appointment:
				if key != "table":
					update_data.append(key + " = '" + str(appointment[key]) + "'")

			query("update schedule set " + ", ".join(update_data) + " where id = " + str(id))

			receiver = ["user" + str(appointment["userId"])]

			if user != None:
				info = json.loads(user["info"])

				if info["pushToken"] != "":
					message = "The salon cancelled your salonappointment with "
					message += "no reason" if reason == "" else "a reason"

					push(pushInfo(
						info["pushToken"],
						"Appointment cancelled",
						message,
						content
					))
			else:
				query("delete from schedule where id = " + str(id))

			return { "msg": "success", "receiver": receiver }
	else:
		errormsg = "Schedule doens't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/salon_change_appointment", methods=["POST"])
def salon_change_appointment():
	content = request.get_json()
	errormsg = ""
	status = ""

	scheduleid = content['id']
	clientid = content['clientid']
	workerid = content['workerid']
	locationid = content['locationid']
	serviceid = content['serviceid']
	serviceinfo = content['serviceinfo']
	time = content['time']
	note = content['note']
	timeDisplay = content['timeDisplay']

	client = query("select * from user where id = " + str(clientid), True).fetchone()
	location = query("select * from location where id = " + str(locationid), True).fetchone()

	if serviceid != -1:
		service = query("select * from service where id = " + str(serviceid), True).fetchone()
		schedule = query("select * from schedule where userId = " + str(clientid) + " and serviceId = " + str(serviceid), True).fetchone()
		servicename = service["name"]
		menuid = service["menuId"]
	else:
		if scheduleid != None:
			schedule = query("select * from schedule where id = " + str(scheduleid), True).fetchone()
		else:
			schedule = None
		
		servicename = serviceinfo
		menuid = -1

	pushids = []

	info = json.loads(client["info"])
	pushToken = info["pushToken"]
	receiver = "user" + str(clientid)

	schedule["time"] = time
	schedule["status"] = 'confirmed'
	schedule["note"] = note
	schedule["workerId"] = workerid

	update_data = []
	for key in schedule:
		if key != "table":
			update_data.append(key + " = '" + str(schedule[key]) + "'")

	query("update schedule set " + ", ".join(update_data) + " where id = " + str(schedule["id"]))

	if pushToken != "":
		pushmessage = pushInfo(
			pushToken, 
			"Appointment remade",
			"A salon requested a different appointment for you for service: " + servicename + " " + str(timeDisplay),
			content
		)
	
		push(pushmessage)

	return { "msg": "appointment remade", "receiver": receiver, "time": time }

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/cancel_schedule", methods=["POST"])
def cancel_schedule():
	content = request.get_json()

	id = content['scheduleid']
	reason = content['reason']

	appointment = query("select * from schedule where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if appointment != None:
		user = query("select * from user where id = " + str(appointment["userId"]), True).fetchone()

		if appointment["status"] == "confirmed":
			appointment["status"] = "cancel"
			appointment["cancelReason"] = reason

			update_data = []
			for key in appointment:
				if key != "table":
					update_data.append(key + " = '" + str(appointment[key]) + "'")

			query("update schedule set " + ", ".join(update_data) + " where id = " + str(id))

			receiver = []

			locationType = appointment["locationType"]

			if locationType == "restaurant":
				customers = json.loads(appointment["customers"])

				for customer in customers:
					receiver.append("user" + str(customer["userid"]))
			else:
				receiver.append("user" + str(appointment["userId"]))

			if user != None:
				info = json.loads(user["info"])

				if info["pushToken"] != "":
					message = "The salon cancelled your appointment with "
					message += "no reason" if reason == "" else "a reason"

					push(pushInfo(
						info["pushToken"],
						"Appointment cancelled",
						message,
						content
					))
			else:
				query("delete from schedule where id = " + str(id))
						
			return { "msg": "request cancelled", "receiver": receiver }
		else:
			errormsg = "Action is denied"
	else:
		errormsg = "Appointment doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/close_schedule/<id>")
def close_schedule(id):
	appointment = query("select * from schedule where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	locationType = appointment["locationType"]

	if appointment["status"] == "cancel":
		if locationType == "restaurant":
			customers = json.loads(appointment["customers"])
			receiver = []

			for customer in customers:
				receiver.append("user" + str(customer["userid"]))
		else:
			receiver = ["user" + str(appointment["userId"])]

		query("delete from schedule where id = " + str(id))

		return { "msg": "request deleted", "receiver": receiver }

	errormsg = "Action is denied"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/done_service/<id>")
def done_service(id):
	schedule = query("select * from schedule where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	booker = schedule["userId"]

	query("update schedule set status = 'done' where id = " + str(id))

	return { "msg": "Schedule done", "receiver": "user" + str(booker) }

@app.route("/cancel_request", methods=["POST"])
def cancel_request():
	content = request.get_json()

	userid = content['userid']
	scheduleid = content['scheduleid']
	timeDisplay = content['timeDisplay']

	schedule = query("select * from schedule where id = " + str(scheduleid), True).fetchone()
	errormsg = ""
	status = ""

	locationId = str(schedule["locationId"])
	workerId = str(schedule["workerId"])

	location = query("select * from location where id = " + str(locationId), True).fetchone()
	info = json.loads(location["info"])
	type = info["type"]

	sql = "select id from owner where "

	if type == "computer":
		sql += "info like '%\"locationId\": \"" + str(locationId) + "\"%' and info like '%\"owner\": true\"%'"
	else:
		sql += "id = " + workerId

	owners = query(sql, True)
	receivers = { "owners": [], "users": [] }

	for owner in owners:
		receivers["owners"].append("owner" + str(owner["id"]))

	if schedule["locationType"] == "restaurant" or schedule["locationType"] == "store":
		customers = json.loads(schedule["customers"])

		for customer in customers:
			if userid != customer["userid"]:
				receivers["users"].append("user" + str(customer["userid"]))

	query("delete from schedule where id = " + str(scheduleid))

	serviceName = ""
	if schedule["serviceId"] == -1:
		userInput = json.loads(schedule["userInput"])
		serviceName = userInput["name"]
	else:
		service = query("select * from service where id = " + str(schedule["serviceId"]), True).fetchone()
		serviceName = service["name"]

	worker = query("select * from owner where id = " + str(schedule["workerId"]), True).fetchone()
	workerInfo = json.loads(worker["info"])

	speak = { "scheduleid": scheduleid, "name": serviceName, "time": json.loads(schedule["time"]), "worker": { "id": workerId, "username": worker["username"] }}

	if workerInfo["pushToken"] != "" and workerInfo["signin"] == True:
		push(pushInfo(
			workerInfo["pushToken"],
			"Appointment cancelled",
			str(timeDisplay),
			content
		))

	return { "msg": "schedule cancelled", "receivers": receivers, "type": schedule["locationType"], "speak": speak }

@app.route("/get_appointments", methods=["POST"])
def get_appointments():
	content = request.get_json()
	
	ownerid = content['ownerid']
	locationid = content['locationid']

	location = query("select * from location where id = " + str(locationid), True).fetchone()
	locationInfo = json.loads(location["info"])
	receiveType = locationInfo["type"]

	sql = "select * from schedule where locationId = " + str(locationid) + " and status = 'confirmed'"

	if receiveType == "stylist":
		sql += " and workerId = " + str(ownerid)
		
	sql += " order by time"

	datas = query(sql, True)
	appointments = []

	for data in datas:
		user = query("select * from user where id = " + str(data['userId']), True).fetchone()
		service = query("select * from service where id = " + str(data['serviceId']), True).fetchone()
		worker = query("select * from owner where id = " + str(data['workerId']), True).fetchone()
		userInput = json.loads(data['userInput'])
			
		info = json.loads(data["info"])
		client = { 
			"id": data['userId'], 
			"username": user["username"] if user != None else userInput["name"] if "name" in userInput else ""
		}
		worker = { "id": worker["id"], "username": worker["username"] }
		userInput = json.loads(data['userInput'])
		image = json.loads(service["image"]) if service != None else {"name": ""}

		appointments.append({
			"key": "appointment-" + str(data['id']),
			"id": str(data['id']),
			"username": user["username"] if user != None else userInput["name"] if "name" in userInput else "",
			"client": client,
			"worker": worker,
			"time": json.loads(data['time']),
			"serviceid": service["id"] if service != None else "",
			"name": service["name"] if service != None else userInput['name'] if "name" in userInput else "",
			"image": image if image["name"] != "" else {"width": 300, "height": 300}
		})

	return { "appointments": appointments, "numappointments": len(appointments) }

@app.route("/get_cart_orderers/<id>")
def get_cart_orderers(id):
	datas = query("select adder, orderNumber from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by adder, orderNumber", True).fetchall()
	numCartorderers = query("select count(*) as num from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'inprogress') group by adder, orderNumber", True).fetchone()
	numCartorderers = numCartorderers["num"] if numCartorderers != None else 0
	cartOrderers = []

	for k, data in enumerate(datas):
		adder = query("select * from user where id = " + str(data['adder']), True).fetchone()
		numOrders = query("select count(*) as num from cart where adder = " + str(data['adder']) + " and locationId = " + str(id) + " and (status = 'checkout' or status = 'inprogress') and orderNumber = '" + data["orderNumber"] + "'", True).fetchone()["num"]

		cartitem = query("select * from cart where orderNumber = " + str(data['orderNumber']), True).fetchone()
		userInput = json.loads(cartitem["userInput"])

		cartOrderers.append({
			"key": "cartorderer-" + str(k),
			"id": len(cartOrderers),
			"adder": adder["id"],
			"username": adder["username"],
			"numOrders": numOrders,
			"orderNumber": data['orderNumber'],
			"type": userInput["type"]
		})

	return { "cartOrderers": cartOrderers, "numCartorderers": numCartorderers }

@app.route("/get_orders", methods=["POST"])
def get_orders():
	content = request.get_json()

	userid = content['userid']
	locationid = content['locationid']
	ordernumber = content['ordernumber']

	datas = query("select * from cart where adder = " + str(userid) + " and locationId = " + str(locationid) + " and orderNumber = '" + ordernumber + "'", True).fetchall()
	orders = []
	ready = True
	waitTime = datas[0]["waitTime"] if len(datas) > 0 else ""

	for data in datas:
		product = query("select * from product where id = " + str(data['productId']), True).fetchone()
		quantity = int(data['quantity'])
		options = json.loads(data['options'])
		others = json.loads(data['others'])
		sizes = json.loads(data['sizes'])
		userInput = json.loads(data['userInput'])
		cost = 0

		for k, option in enumerate(options):
			option['key'] = "option-" + str(k)

		for k, other in enumerate(others):
			other['key'] = "other-" + str(k)

		for k, size in enumerate(sizes):
			size['key'] = "size-" + str(k)

		if product != None:
			if product["price"] == "":
				for size in sizes:
					if size["selected"] == True:
						cost += float(size["price"])
			else:
				cost += float(product["price"])

			for other in others:
				if other["selected"] == True:
					cost += float(other["price"])

		image = json.loads(product["image"]) if product != None else {"name": ""}
		orders.append({
			"key": "cart-item-" + str(data['id']),
			"id": str(data['id']),
			"name": product["name"] if product != None else userInput['name'],
			"note": data['note'],
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"options": options, "others": others, "sizes": sizes, "quantity": quantity,
			"cost": (cost * quantity) if cost > 0 else None
		})

		if data['status'] == "checkout":
			ready = False

	return { "orders": orders, "ready": ready, "waitTime": waitTime }
