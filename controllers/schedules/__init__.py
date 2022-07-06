from flask import request
from flask_cors import CORS
from info import *
from models import *
import datetime, time

cors = CORS(app)

def removeBlockedSchedules(time):
	time = time.split(" ")

	day = time[0]
	month = time[1]
	date = time[2]
	year = time[3]

	hour = int(time[4])
	minute = int(time[5])
	delete = []
	blockedEnd = False

	while hour > 0 and blockedEnd == False:
		minute += 15

		if minute > 59:
			hour += 1
			minute = 0

			if hour == 24:
				hour = 0

		sql = "select id, status, day, month, date, year from schedule where "
		sql += "day = '" + day + "' and "
		sql += "month = '" + month + "' and "
		sql += "date = " + str(date) + " and "
		sql += "year = " + str(year) + " and "
		sql += "hour = " + str(hour) + " and "
		sql += "minute = " + str(minute)

		scheduled = query(sql, True).fetchone()

		if scheduled != None:
			if scheduled["status"] == "confirmed":
				blockedEnd = True
			else:
				delete.append(scheduled["id"])

	if len(delete) > 0:
		query("delete from schedule where id in (" + json.dumps(delete)[1:-1] + ")", False)

def getBlockedSchedules(time):
	time = time.split(" ")

	day = time[0]
	month = time[1]
	date = time[2]
	year = time[3]

	hour = int(time[4])
	minute = int(time[5])
	delete = []
	blockedEnd = False

	while hour > 0 and blockedEnd == False:
		minute += 15

		if minute > 59:
			hour += 1
			minute = 0

			if hour == 24:
				hour = 0

		sql = "select id, status, day, month, date, year, hour, minute from schedule where "
		sql += "day = '" + day + "' and "
		sql += "month = '" + month + "' and "
		sql += "date = " + str(date) + " and "
		sql += "year = " + str(year) + " and "
		sql += "hour = " + str(hour) + " and "
		sql += "minute = " + str(minute)

		scheduled = query(sql, True).fetchone()

		if scheduled != None:
			time = json.dumps({ 
				"day": scheduled["day"], "month": scheduled["month"], 
				"date": scheduled["date"], "year": scheduled["year"], 
				"hour": scheduled["hour"], "minute": scheduled["minute"] 
			})
			scheduled["time"] = time

			if scheduled["status"] == "confirmed":
				blockedEnd = True
			else:
				del scheduled["day"]
				del scheduled["month"]
				del scheduled["date"]
				del scheduled["year"]
				del scheduled["hour"]
				del scheduled["minute"]

				delete.append(scheduled)

	return delete

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
		time = {"day": data["day"], "month": data["month"], "date": data["date"], "year": data["year"], "hour": data["hour"], "minute": data["minute"]}
		requests.append({
			"key": "request-" + str(data['id']),
			"id": str(data['id']),
			"type": data['locationType'],
			"worker": worker,
			"userId": user["id"],
			"username": user["username"],
			"time": time,
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

	if schedule != None:
		time = schedule["day"] + " " + schedule["month"] + " " + str(schedule["date"]) + " " + str(schedule["year"]) + " " + str(schedule["hour"]) + " " + str(schedule["minute"])
		blockedSchedules = getBlockedSchedules(time)
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

		day = schedule["day"]
		month = schedule["month"]
		date = schedule["date"]
		year = schedule["year"]
		hour = schedule["hour"]
		minute = schedule["minute"]

		info = { 
			"client": { 
				"id": userId, 
				"name": client["username"] if client != None else userInput["name"] if "name" in userInput else "", 
				"cellnumber": userInput["cellnumber"] if "cellnumber" in userInput else None
			},
			"locationId": int(locationId), 
			"serviceId": int(serviceId) if serviceId > -1 else None, 
			"time": { "day": day, "month": month, "date": date, "year": year, "hour": hour, "minute": minute }, 
			"note": schedule["note"],
			"worker": worker,
			"blocked": blockedSchedules
		}

		if serviceId != -1:
			service = query("select * from service where id = " + str(serviceId), True).fetchone()

			info["name"] = service["name"]
		else:
			userInput = json.loads(schedule["userInput"])

			info["name"] = userInput["name"] if "name" in userInput else ""

		if errormsg == "":
			return info
	else:
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

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
	clientTime = content['time']
	note = content['note']
	timeDisplay = content['timeDisplay']
	blocked = content['blocked']
	unix = str(content['unix'])

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
	owners = "(" + location["owners"][1:-1] + ")"
	type = info["type"]

	sql = "select id, info from owner where id in " + owners

	owners = query(sql, True)
	locationInfo = json.loads(location["info"])
	receiver = []
	pushids = []

	for owner in owners:
		info = json.loads(owner["info"])

		receiver.append("owner" + str(owner["id"]))

		if info["pushToken"] != "" and info["signin"] == True:
			pushids.append({ "token": info["pushToken"], "signin": info["signin"] })

	scheduled = query("select * from schedule where time = " + unix, True).fetchone()

	if scheduled == None or "\"unix\":" + unix in json.dumps(blocked).replace(" ", ""):
		if schedule != None: # existing schedule
			schedule["day"] = clientTime["day"]
			schedule["month"] = clientTime["month"]
			schedule["date"] = clientTime["date"]
			schedule["year"] = clientTime["year"]
			schedule["hour"] = clientTime["hour"]
			schedule["minute"] = clientTime["minute"]
			schedule["status"] = 'confirmed'
			schedule["note"] = note
			schedule["workerId"] = workerid

			# recreate blocked times
			for info in blocked:
				data = query("select id, time from schedule where time = " + info["newUnix"], True).fetchone()

				if data != None:
					if ("\"id\": " + str(data["id"])) not in json.dumps(blocked):
						status = "scheduleConflict"

			if status == "":
				update_data = []
				for key in schedule:
					if key != "table":
						update_data.append(key + " = '" + str(schedule[key]) + "'")

				query("update schedule set " + ", ".join(update_data) + " where id = " + str(schedule["id"]))

				for info in blocked:
					newTime = info["newTime"]
					day = newTime["day"]
					month = newTime["month"]
					date = str(newTime["date"])
					year = str(newTime["year"])
					hour = str(newTime["hour"])
					minute = str(newTime["minute"])

					sql = "update schedule set status = 'blocked', "
					sql += "time = " + info["newUnix"] + ", "
					sql += "day = '" + day + "', month = '" + month + "', date = " + date + ", year = " + year + ", "
					sql += "hour = " + hour + ", minute = " + minute + " "
					sql += "where id = " + str(info["id"])

					query(sql)
			# end code

			if status == "":
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

				speak = { "scheduleid": schedule["id"], "name": servicename, "time": clientTime, "worker": { "id": workerid, "username": worker["username"] }}

				return { "msg": "appointment remade", "receiver": receiver, "time": json.dumps(clientTime), "speak": speak }
		else: # new schedule
			info = json.dumps({})
			userInput = json.dumps({ "name": serviceinfo, "type": "service" })

			data = {
				"userId": userid,"workerId": workerid,"locationId": locationid,"menuId": menuid,"serviceId": serviceid,
				"userInput": userInput, "day": clientTime["day"], "month": clientTime["month"], "date": clientTime["date"], 
				"year": clientTime["year"], "hour": clientTime["hour"], "minute": clientTime["minute"], "time": unix,"status": 
				"confirmed","cancelReason": "","locationType": location["type"],
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

			speak = { "scheduleid": id, "name": servicename, "time": clientTime, "worker": { "id": workerid, "username": worker["username"] }}

			return { "msg": "appointment added", "receiver": receiver, "speak": speak }
	else:
		status = scheduled["status"]

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/book_walk_in", methods=["POST"])
def book_walk_in():
	content = request.get_json()

	workerid = content['workerid']
	locationid = content['locationid']
	clientTime = content["time"]
	note = content['note']
	type = content['type']
	client = content['client']
	serviceid = content['serviceid'] if 'serviceid' in content else -1
	unix = int(content["unix"])

	# get now or the next available time for client
	# check if current time is valid
	monthsArr = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	daysArr = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
	months = {'January': '1', 'February': '2', 'March': '3', 'April': '4', 'May': '5', 'June': '6', 'July': '7', 'August': '8', 'September': '9', 'October': '10', 'November': '11', 'December': '12'}
	days = {'Sunday': '1', 'Monday': '2', 'Tuesday': '3', 'Wednesday': '4', 'Thursday': '5', 'Friday': '6', 'Saturday': '7'}

	day = int(days[clientTime["day"]])
	month = int(months[clientTime["month"]])
	date = clientTime["date"]
	year = clientTime["year"]
	hour = clientTime["hour"]
	minute = clientTime["minute"]

	date_time = datetime.datetime(year, month, date, 0, 0)
	date_time_info = str(date_time).split(" ")
	date_date = date_time_info[0].split("-")

	date_year = str(date_date[0])
	date_month = monthsArr[int(date_date[1]) - 1]
	date_day = str(int(date_date[2]))
	date_weekday = daysArr[date_time.weekday()]

	bM = "0"
	eM = "10"
	bH = hour
	eH = hour

	if minute >= 10:
		bM = str(minute)[:1]
		eM = int(str(minute)[1:])

	if minute >= 0 and minute < 15: # 0 to 14
		eMone = 0
		eMtwo = 15
	elif minute < 30: # 15 to 29
		eMone = 15
		eMtwo = 30
	elif minute < 45: # 30 to 45
		eMone = 30
		eMtwo = 45
	else: # 45 to above
		eMone = 45
		eMtwo = 0

		eH = eH + 1 if eH < 23 else 0

	bTime = str(bH) + ":" + str(eMone)
	eTime = str(eH) + ":" + str(eMtwo)
	timeDisplay = ""
	valid = False

	clientTime = json.dumps({"day": date_weekday, "month": date_month, "date": date_day, "year": date_year, "hour": bH, "minute": eMone })
	sql = "select count(*) as num from schedule where "
	sql += "day = '" + date_weekday + "' and month = '" + date_month + "' and date = " + str(date_day) + " and year = " + str(date_year) + " "
	sql += "hour = " + str(bH) + " and minute = " + str(eMone) + " "
	sql += "workerId = " + str(workerid)
	scheduled = query(sql, True).fetchone()["num"]

	if scheduled == 0:
		valid = True
		timeDisplay = "right now"

	while valid == False:
		bTimeInfo = bTime.split(":")
		eTimeInfo = eTime.split(":")

		bTimeInfo[0] = int(bTimeInfo[0])
		bTimeInfo[1] = int(bTimeInfo[1])

		eTimeInfo[0] = int(eTimeInfo[0])
		eTimeInfo[1] = int(eTimeInfo[1])

		bTimeInfo[1] += 15
		eTimeInfo[1] += 15

		unix += 900000

		if bTimeInfo[1] == 60:
			bTimeInfo[0] = bTimeInfo[0] + 1 if bTimeInfo[0] < 23 else 0
			bTimeInfo[1] = 0

		if eTimeInfo[1] == 60:
			eTimeInfo[0] = eTimeInfo[0] + 1 if eTimeInfo[0] < 23 else 0
			eTimeInfo[1] = 0

		bTime = str(bTimeInfo[0]) + ":" + ("0" + str(bTimeInfo[1]) if bTimeInfo[1] < 10 else str(bTimeInfo[1]))
		eTime = str(eTimeInfo[0]) + ":" + ("0" + str(eTimeInfo[1]) if eTimeInfo[1] < 10 else str(eTimeInfo[1]))

		if eTime == "0:00":
			new_date = date_time + datetime.timedelta(days=1)
			date_time = new_date
			date_time_info = str(date_time).split(" ")
			date_date = date_time_info[0].split("-")
			date_year = str(date_date[0])
			date_month = monthsArr[int(date_date[1]) - 1]
			date_day = str(int(date_date[2]))
			date_weekday = daysArr[date_time.weekday()]

		timeInfo = bTime.split(":")
		hour = int(timeInfo[0])
		minute = int(timeInfo[1])

		sql = "select count(*) as num from schedule where time = " + str(unix) + " and workerId = " + str(workerid)
		scheduled = query(sql, True).fetchone()["num"]

		if scheduled == 0:
			valid = True

			timeInfo = json.loads(clientTime)
			hour = int(timeInfo["hour"])
			minute = int(timeInfo["minute"])
			timeDisplay = str(hour - 12 if hour > 12 else hour) + ":" + str("0" + str(minute) if minute < 10 else minute)
			timeDisplay += "pm" if hour >= 12 else "am"

	time = json.loads(clientTime)
	data = {
		"userId": -1,"workerId": workerid,"locationId": locationid,"menuId": -1,"serviceId": serviceid if serviceid != None else -1,
		"userInput": json.dumps(client),"day": time["day"], "month": time["month"], "date": time["date"], "year": time["year"], 
		"hour": time["hour"], "minute": time["minute"], "time": str(unix), "status": "confirmed","cancelReason": "","locationType": type,
		"customers": 1,"note": note,"orders": "[]","info": "{}"
	}

	columns = []
	insert_data = []
	for key in data:
		columns.append(key)
		insert_data.append("'" + str(data[key]) + "'")

	query("insert into schedule (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")")

	return { "msg": "success", "timeDisplay": timeDisplay }

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

@app.route("/block_time", methods=["POST"])
def block_time():
	content = request.get_json()
	errormsg = ""
	status = ""

	workerid = content['workerid']
	jsonDate = content['jsonDate']
	time = str(content['time'])

	blocked = query("select count(*) as num from schedule where workerId = " + str(workerid) + " and status = 'blocked' and time = " + time, True).fetchone()["num"]

	if blocked == 0:
		location = query("select id, type from location where owners like '%\"" + str(workerid) + "\"%'", True).fetchone()

		if location != None:
			data = {
				"userId": -1,"workerId": workerid, "locationId": location["id"], "menuId": -1, "serviceId": -1,
				"userInput": json.dumps({}), "day": jsonDate["day"], "month": jsonDate["month"], "date": jsonDate["date"], "year": jsonDate["year"], 
				"hour": jsonDate["hour"], "minute": jsonDate["minute"], "time": time, "status": "blocked", "cancelReason": "", "locationType": location["type"],
				"customers": 0, "note": "", "orders": "[]", "info": "{}"
			}
			columns = []
			insert_data = []
			for key in data:
				columns.append(key)
				insert_data.append("'" + str(data[key]) + "'")

			query("insert into schedule (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")")

			return { "msg": "success", "action": "add" }
		else:
			errormsg = "Location doesn't exist"
	else:
		query("delete from schedule where workerId = " + str(workerid) + " and status = 'blocked' and time = " + time)

		return { "msg": "success", "action": "remove" }

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
	clientTime = content['time']
	note = content['note']
	timeDisplay = content['timeDisplay']
	blocked = content['blocked']
	unix = str(content['unix'])

	client = query("select * from user where id = " + str(clientid), True).fetchone()
	worker = query("select username from owner where id = " + str(workerid), True).fetchone()
	location = query("select * from location where id = " + str(locationid), True).fetchone()

	if location != None:
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

		scheduled = query("select * from schedule where time = " + unix, True).fetchone()

		if scheduled == None or (scheduled != None and "\"id\": " + str(scheduled["id"])) in json.dumps(blocked):
			info = { "msg": "appointment remade", "time": clientTime, "worker": { "id": workerid, "username": worker["username"] }}

			if client != None:
				clientInfo = json.loads(client["info"])
				pushToken = clientInfo["pushToken"]
				receiver = "user" + str(clientid)

				info["receiver"] = receiver

			schedule["time"] = unix
			schedule["day"] = clientTime["day"]
			schedule["month"] = clientTime["month"]
			schedule["date"] = clientTime["date"]
			schedule["year"] = clientTime["year"]
			schedule["hour"] = clientTime["hour"]
			schedule["minute"] = clientTime["minute"]
			schedule["status"] = 'confirmed'
			schedule["note"] = note
			schedule["workerId"] = workerid

			# recreate blocked times
			for blockedInfo in blocked:
				newTime = blockedInfo["newTime"]
				day = newTime["day"]
				month = newTime["month"]
				date = str(newTime["date"])
				year = str(newTime["year"])
				hour = str(newTime["hour"])
				minute = str(newTime["minute"])

				sql = "select id from schedule where "
				sql += "day = '" + day + "' and month = '" + month + "' and date = " + date + " and year = " + year + " and "
				sql += "hour = " + hour + " and minute = " + minute
				data = query(sql, True).fetchone()

				if data != None:
					print(data)
					if ("\"id\": " + str(data["id"])) not in json.dumps(blocked) and str(data["id"]) != str(schedule["id"]):
						status = "scheduleConflict"

			if status == "":
				update_data = []
				for key in schedule:
					if key != "table":
						update_data.append(key + " = '" + str(schedule[key]) + "'")

				query("update schedule set " + ", ".join(update_data) + " where id = " + str(schedule["id"]))

				for blockedInfo in blocked:
					newTime = blockedInfo["newTime"]
					day = newTime["day"]
					month = newTime["month"]
					date = str(newTime["date"])
					year = str(newTime["year"])
					hour = str(newTime["hour"])
					minute = str(newTime["minute"])

					sql = "update schedule set time = " + blockedInfo["newUnix"] + ", "
					sql += "day = '" + newTime["day"] + "', month = '" + newTime["month"] + "', date = " + str(newTime["date"]) + ", year = " + str(newTime["year"]) + ", "
					sql += "hour = " + str(newTime["hour"]) + ", minute = " + str(newTime["minute"]) + " "
					sql += "where id = " + str(blockedInfo["id"])

					query(sql)

				if client != None:
					if pushToken != "":
						pushmessage = pushInfo(
							pushToken, 
							"Appointment remade",
							"A salon requested a different appointment for you for service: " + servicename + " " + str(timeDisplay),
							content
						)
					
						push(pushmessage)

				return info
		else:
			status = scheduled["status"]
	else:
		errormsg = "Location doesn't exist"

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
		time = appointment["day"] + " " + appointment["month"] + " " + str(appointment["date"]) + " " + str(appointment["year"]) + " " + str(appointment["hour"]) + " " + str(appointment["minute"])
		blockedSchedules = getBlockedSchedules(time)
		user = query("select * from user where id = " + str(appointment["userId"]), True).fetchone()

		if appointment["status"] == "confirmed":
			appointment["status"] = "cancel"
			appointment["cancelReason"] = reason

			update_data = []
			for key in appointment:
				if key != "table":
					update_data.append(key + " = '" + str(appointment[key]) + "'")

			query("update schedule set " + ", ".join(update_data) + " where id = " + str(id))

			for info in blockedSchedules:
				query("update schedule set status = 'cancel_blocked' where id = " + str(info["id"]))

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

		time = appointment["day"] + " " + appointment["month"] + " " + str(appointment["date"]) + " " + str(appointment["year"]) + " " + str(appointment["hour"]) + " " + str(appointment["minute"])
		removeBlockedSchedules(time)

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

	time = schedule["day"] + " " + schedule["month"] + " " + str(schedule["date"]) + " " + str(schedule["year"]) + " " + str(schedule["hour"]) + " " + str(schedule["minute"])
	removeBlockedSchedules(time)
	
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
	owners = "(" + location["owners"][1:-1] + ")"
	type = info["type"]

	sql = "select id from owner where id in " + owners + " and info like '%\"owner\": true\"%'"

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

	time = schedule["day"] + " " + schedule["month"] + " " + str(schedule["date"]) + " " + str(schedule["year"]) + " " + str(schedule["hour"]) + " " + str(schedule["minute"])
	removeBlockedSchedules(time)

	serviceName = ""
	if schedule["serviceId"] == -1:
		userInput = json.loads(schedule["userInput"])
		serviceName = userInput["name"]
	else:
		service = query("select * from service where id = " + str(schedule["serviceId"]), True).fetchone()
		serviceName = service["name"]

	worker = query("select * from owner where id = " + str(schedule["workerId"]), True).fetchone()
	workerInfo = json.loads(worker["info"])

	time = { "day": schedule["day"], "month": schedule["month"], "date": schedule["date"], "year": schedule["year"], "hour": schedule["hour"], "minute": schedule["minute"] }
	speak = { "scheduleid": scheduleid, "name": serviceName, "time": time, "worker": { "id": workerId, "username": worker["username"] }}

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
		
	sql += " order by time limit 10"

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

		time = { "day": data["day"], "month": data["month"], "date": data["date"], "year": data["year"], "hour": data["hour"], "minute": data["minute"] }
		appointments.append({
			"key": "appointment-" + str(data['id']),
			"id": str(data['id']),
			"username": user["username"] if user != None else userInput["name"] if "name" in userInput else "",
			"client": client,
			"worker": worker,
			"time": time,
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
