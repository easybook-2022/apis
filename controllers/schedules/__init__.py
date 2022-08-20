from flask import request
from flask_cors import CORS
from info import *
from models import *
import datetime, time

cors = CORS(app)

def removeBlockedSchedules(time, workerId):
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

		sql = "select id, status, time from schedule where "
		sql += "json_extract(time, '$.day') = " + str(day) + " and "
		sql += "json_extract(time, '$.month') = " + str(month) + " and "
		sql += "json_extract(time, '$.date') = " + str(date) + " and "
		sql += "json_extract(time, '$.year') = " + str(year) + " and "
		sql += "json_extract(time, '$.hour') = " + str(hour) + " and "
		sql += "json_extract(time, '$.minute') = " + str(minute) + " and "
		sql += "workerId = " + str(workerId)

		scheduled = query(sql, True).fetchone()

		if scheduled != None:
			time = json.loads(scheduled["time"])
			time = { 
				"day": indexToDay[time["day"]], "month": indexToMonth[time["month"]], 
				"date": time["date"], "year": time["year"], 
				"hour": time["hour"], "minute": time["minute"] 
			}

			scheduled["time"] = time

			if scheduled["status"] == "confirmed" or scheduled["status"] == "w_confirmed":
				blockedEnd = True
			else:
				if scheduled["status"] == "cancel_blocked" or scheduled["status"] == "blocked":
					delete.append(scheduled["id"])

	if len(delete) > 0:
		query("delete from schedule where id in (" + json.dumps(delete)[1:-1] + ")", False)

def getBlockedSchedules(time, workerId):
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

		sql = "select id, status, time from schedule where "
		sql += "json_extract(time, '$.day') = " + str(day) + " and "
		sql += "json_extract(time, '$.month') = " + str(month) + " and "
		sql += "json_extract(time, '$.date') = " + str(date) + " and "
		sql += "json_extract(time, '$.year') = " + str(year) + " and "
		sql += "json_extract(time, '$.hour') = " + str(hour) + " and "
		sql += "json_extract(time, '$.minute') = " + str(minute) + " and "
		sql += "workerId = " + str(workerId)

		scheduled = query(sql, True).fetchone()

		if scheduled != None:
			time = json.loads(scheduled["time"])
			time = { 
				"day": indexToDay[time["day"]], "month": indexToMonth[time["month"]], 
				"date": time["date"], "year": time["year"], 
				"hour": time["hour"], "minute": time["minute"] 
			}

			scheduled["time"] = time

			if scheduled["status"] == "confirmed":
				blockedEnd = True
			else:
				if scheduled["status"] == "cancel_blocked" or scheduled["status"] == "blocked":
					delete.append(scheduled)

	return delete

def isOverLapped(schedules):
	overLap = False

	for info in schedules:
		sql = "select count(*) as num from schedule where "
		sql += "json_extract(time, '$.day') = " + str(info["day"]) + " and "
		sql += "json_extract(time, '$.month') = " + str(info["month"]) + " and "
		sql += "json_extract(time, '$.date') = " + str(info["date"]) + " and "
		sql += "json_extract(time, '$.year') = " + str(info["year"]) + " and "
		sql += "json_extract(time, '$.hour') = " + str(info["hour"]) + " and "
		sql += "json_extract(time, '$.minute') = " + str(info["minute"])

		schedule = query(sql, True).fetchone()

		if schedule["num"] > 0:
			overLap = True

	return overLap

@app.route("/welcome_schedules", methods=["GET"])
def welcome_schedules():
	datas = Schedule.query.all()
	schedules = []

	for data in datas:
		schedules.append(data.id)

	return { "msg": "welcome to schedules of EasyBook", "schedules": schedules }

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
			"name": service["name"],
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
		time = json.loads(schedule["time"])

		time = str(time["day"]) + " " + str(time["month"]) + " " + str(time["date"]) + " " + str(time["year"]) + " " + str(time["hour"]) + " " + str(time["minute"])
		blockedSchedules = getBlockedSchedules(time, schedule["workerId"])
		locationId = schedule["locationId"]
		serviceId = schedule["serviceId"]
		userId = schedule["userId"]
		
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

		time = json.loads(schedule["time"])
		day = indexToDay[time["day"]]
		month = indexToMonth[time["month"]]
		date = time["date"]
		year = time["year"]
		hour = time["hour"]
		minute = time["minute"]

		info = { 
			"client": { 
				"id": userId, 
				"name": client["username"], 
				"cellnumber": client["cellnumber"]
			},
			"locationId": int(locationId), 
			"serviceId": int(serviceId) if serviceId > -1 else None, 
			"time": { "day": day, "month": month, "date": date, "year": year, "hour": hour, "minute": minute }, 
			"note": schedule["note"],
			"worker": worker,
			"blocked": blockedSchedules
		}

		service = query("select * from service where id = " + str(serviceId), True).fetchone()

		info["name"] = service["name"]

		if errormsg == "":
			return info
	else:
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_exist_booking", methods=["POST"])
def get_exist_booking():
	content = request.get_json()

	userid = content['userid']
	serviceid = content['serviceid']

	scheduled = query("select id from schedule where userId = " + str(userid) + " and serviceId = " + str(serviceid), True).fetchone()

	return { "scheduleid": int(scheduled["id"]) if scheduled != None else -1 }

@app.route("/get_rescheduling_appointments", methods=["POST"])
def get_rescheduling_appointments():
	content = request.get_json()

	calDate = content['date']
	selectedIds = content['selectedIds']

	select_query = "select id, time, workerId from schedule"

	if len(selectedIds) > 0:
		schedules = query(select_query + " where id in (" + json.dumps(selectedIds)[1:-1] + ")", True).fetchall()
	else:
		day = str(dayToIndex[calDate['day']])
		month = str(monthToIndex[calDate['month']])
		date = str(calDate['date'])
		year = str(calDate['year'])

		schedules = query(select_query + " where json_extract(time, '$.day') = " + day + " and json_extract(time, '$.month') = " + month + " and json_extract(time, '$.date') = " + date + " and json_extract(time, '$.year') = " + year, True).fetchall()

	for schedule in schedules:
		time = json.loads(schedule["time"])

		day = str(time["day"])
		month = str(time["month"])
		date = str(time["date"])
		year = str(time["year"])
		hour = str(time["hour"])
		minute = str(time["minute"])

		time = day + " " + month + " " + date + " " + year + " " + hour + " " + minute

		blockedSchedules = getBlockedSchedules(time, schedule["workerId"])

		schedule["blockedSchedules"] = blockedSchedules

		time = json.loads(schedule["time"])
		schedule["day"] = indexToDay[time["day"]]
		schedule["month"] = indexToMonth[time["month"]]
		schedule["date"] = time["date"]
		schedule["year"] = time["year"]
		schedule["hour"] = time["hour"]
		schedule["minute"] = time["minute"]

		del schedule["time"]

	return { "msg": "success", "schedules": schedules }

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

	user = query("select * from user where id = " + str(userid), True).fetchone()
	location = query("select * from location where id = " + str(locationid), True).fetchone()

	if serviceid != -1:
		service = query("select * from service where id = " + str(serviceid), True).fetchone()
		servicename = service["name"]
		menuid = service["menuId"]
	else:
		servicename = serviceinfo
		menuid = -1

	if scheduleid != None:
		schedule = query("select * from schedule where id = " + str(scheduleid), True).fetchone()
	else:
		schedule = None

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

	sql = "select * from schedule where "
	sql += "json_extract(time, '$.day') = " + str(dayToIndex[clientTime["day"]]) + " and "
	sql += "json_extract(time, '$.month') = " + str(monthToIndex[clientTime["month"]]) + " and "
	sql += "json_extract(time, '$.date') = " + str(clientTime["date"]) + " and "
	sql += "json_extract(time, '$.year') = " + str(clientTime["year"]) + " and "
	sql += "json_extract(time, '$.hour') = " + str(clientTime["hour"]) + " and "
	sql += "json_extract(time, '$.minute') = " + str(clientTime["minute"]) + " and "
	sql += "workerId = " + str(workerid)
	scheduled = query(sql, True).fetchone()

	partOfBlocked = False

	for blockInfo in blocked:
		time = blockInfo["time"]

		day = time["day"]
		month = time["month"]
		date = time["date"]
		year = time["year"]
		hour = time["hour"]
		minute = time["minute"]

		if day == clientTime["day"] and month == clientTime["month"] and date == clientTime["date"] and year == clientTime["year"] and hour == clientTime["hour"] and minute == clientTime["minute"]:
			partOfBlocked = True

	if scheduled == None or partOfBlocked == True:
		if schedule != None: # existing schedule
			schedule["time"] = json.dumps({
				"day": dayToIndex[clientTime["day"]], "month": monthToIndex[clientTime["month"]], "date": int(clientTime["date"]), "year": int(clientTime["year"]), 
				"hour": int(clientTime["hour"]), "minute": int(clientTime["minute"])
			})
			schedule["status"] = 'confirmed'
			schedule["note"] = note
			schedule["workerId"] = workerid

			# recreate blocked times
			for info in blocked:
				time = info["newTime"]
				day = time["day"]
				month = time["month"]
				date = time["date"]
				year = time["year"]
				hour = time["hour"]
				minute = time["minute"]

				sql = "select id, time from schedule where "
				sql += "json_extract(time, '$.day') = " + str(dayToIndex[day]) + " and "
				sql += "json_extract(time, '$.month') = " + str(monthToIndex[month]) + " and "
				sql += "json_extract(time, '$.date') = " + str(date) + " and "
				sql += "json_extract(time, '$.year') = " + str(year) + " and "
				sql += "json_extract(time, '$.hour') = " + str(hour) + " and "
				sql += "json_extract(time, '$.minute') = " + str(minute) + " and "
				sql += "workerId = " + str(workerid) + " and "
				sql += "(status = 'w_confirmed' or status = 'confirmed')"
				data = query(sql, True).fetchone()

				if data != None: # new block hit confirmed schedule
					if str(data["id"]) != str(scheduleid):
						status = "scheduleConflict"

			if status == "":
				update_data = []
				for key in schedule:
					if key != "table":
						update_data.append(key + " = '" + str(schedule[key]) + "'")

				query("update schedule set " + ", ".join(update_data) + " where id = " + str(schedule["id"]))

				for info in blocked:
					newTime = info["newTime"]
					day = dayToIndex[newTime["day"]]
					month = monthToIndex[newTime["month"]]
					date = newTime["date"]
					year = newTime["year"]
					hour = newTime["hour"]
					minute = newTime["minute"]

					time = json.dumps({"day": day, "month": month, "date": date, "year": year, "hour": hour, "minute": minute})

					sql = "update schedule set status = 'blocked', "
					sql += "time = '" + time + "', workerId = " + str(workerid) + " "
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

				info = { "scheduleid": schedule["id"], "name": servicename, "time": clientTime, "worker": { "id": workerid, "username": worker["username"] }}

				return { "msg": "appointment remade", "receiver": receiver, "time": json.dumps(clientTime), "info": info }
		else: # new schedule
			time = json.dumps({
				"day": dayToIndex[clientTime["day"]], "month": monthToIndex[clientTime["month"]], "date": clientTime["date"], 
				"year": clientTime["year"], "hour": clientTime["hour"], "minute": clientTime["minute"]
			})

			data = {
				"userId": userid,"workerId": workerid,"locationId": locationid,"menuId": menuid,"serviceId": serviceid,
				"time": time, "status": "confirmed","cancelReason": "","locationType": location["type"],
				"customers": 1,"note": note,"orders": "[]","info": "{}"
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

			info = { "scheduleid": id, "name": servicename, "time": clientTime, "worker": { "id": workerid, "username": worker["username"] }}

			return { "msg": "appointment added", "receiver": receiver, "info": info }
	else:
		status = scheduled["status"]

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/book_walk_in", methods=["POST"])
def book_walk_in():
	content = request.get_json()

	workerid = content['workerid']
	locationid = content['locationid']
	clientTime = content["time"]
	bTime = content['bTime']
	eTime = content['eTime']
	note = content['note']
	type = content['type']
	client = content['client']
	serviceid = content['serviceid'] if 'serviceid' in content else -1

	# get now or the next available time for client
	# check if current time is valid
	day = int(dayToIndex[clientTime["day"]])
	month = int(monthToIndex[clientTime["month"]])
	date = clientTime["date"]
	year = clientTime["year"]
	hour = int(clientTime["hour"])
	minute = int(clientTime["minute"])
	timeDisplay = ""
	valid = False

	sql = "select count(*) as num from schedule where "
	sql += "json_extract(time, '$.day') = " + str(dayToIndex[clientTime["day"]]) + " and "
	sql += "json_extract(time, '$.month') = " + str(monthToIndex[clientTime["month"]]) + " and "
	sql += "json_extract(time, '$.date') = " + str(clientTime["date"]) + " and "
	sql += "json_extract(time, '$.year') = " + str(clientTime["year"]) + " and "
	sql += "json_extract(time, '$.hour') = " + str(clientTime["hour"]) + " and "
	sql += "json_extract(time, '$.minute') = " + str(clientTime["minute"]) + " and "
	sql += "workerId = " + str(workerid)
	scheduled = query(sql, True).fetchone()["num"]

	if scheduled == 0:
		valid = True
		timeDisplay = "right now"

	date_time = datetime.datetime(year, month, day, hour, minute)
	k = 0

	while valid == False and k < 10:
		k += 1
		bTimeInfo = bTime.split(":")
		eTimeInfo = eTime.split(":")

		bTimeInfo[0] = int(bTimeInfo[0])
		bTimeInfo[1] = int(bTimeInfo[1])

		eTimeInfo[0] = int(eTimeInfo[0])
		eTimeInfo[1] = int(eTimeInfo[1])

		bTimeInfo[1] += 15
		eTimeInfo[1] += 15

		if bTimeInfo[1] == 60:
			bTimeInfo[0] = bTimeInfo[0] + 1 if bTimeInfo[0] < 23 else 0
			bTimeInfo[1] = 0

		if eTimeInfo[1] == 60:
			eTimeInfo[0] = eTimeInfo[0] + 1 if eTimeInfo[0] < 23 else 0
			eTimeInfo[1] = 0

		bTime = str(bTimeInfo[0]) + ":" + ("0" + str(bTimeInfo[1]) if bTimeInfo[1] < 10 else str(bTimeInfo[1]))
		eTime = str(eTimeInfo[0]) + ":" + ("0" + str(eTimeInfo[1]) if eTimeInfo[1] < 10 else str(eTimeInfo[1]))

		if eTime == "0:00":
			date_time = date_time + datetime.timedelta(days=1)
			date_time_info = str(date_time).split(" ")
			date_date = date_time_info[0].split("-")
			clientTime["year"] = str(date_date[0])
			clientTime["month"] = indexToMonth[int(date_date[1]) - 1]
			clientTime["date"] = str(int(date_date[2]))
			clientTime["day"] = indexToDay[date_time.weekday()]

		timeInfo = bTime.split(":")
		clientTime["hour"] = int(timeInfo[0])
		clientTime["minute"] = int(timeInfo[1])

		sql = "select count(*) as num from schedule where "
		sql += "json_extract(time, '$.day') = " + str(dayToIndex[clientTime["day"]]) + " and "
		sql += "json_extract(time, '$.month') = " + str(monthToIndex[clientTime["month"]]) + " and "
		sql += "json_extract(time, '$.date') = " + str(clientTime["date"]) + " and "
		sql += "json_extract(time, '$.year') = " + str(clientTime["year"]) + " and "
		sql += "json_extract(time, '$.hour') = " + str(clientTime["hour"]) + " and "
		sql += "json_extract(time, '$.minute') = " + str(clientTime["minute"]) + " and "
		sql += "workerId = " + str(workerid)

		scheduled = query(sql, True).fetchone()["num"]

		if scheduled == 0:
			# check if worker is available at computing time
			worker = query("select hours from owner where id = " + str(workerid), True).fetchone()
			hours = json.loads(worker["hours"])

			day = clientTime["day"]
			hour = clientTime["hour"]
			minute = clientTime["minute"]
			calcTime = int(
				("0" + str(hour) if str(hour) == "0" else str(hour))
				+ "" + 
				("0" + str(minute) if str(minute) == "0" else str(minute))
			)

			if day[:3] in hours and hours[day[:3]]["working"] == True:
				opentime = hours[day[:3]]["opentime"]
				closetime = hours[day[:3]]["closetime"]

				openHour = "0" + opentime["hour"] if opentime["hour"] == "0" else opentime["hour"]
				openMinute = "0" + opentime["minute"] if opentime["minute"] == "0" else opentime["minute"]

				closeHour = "0" + closetime["hour"] if closetime["hour"] == "0" else closetime["hour"]
				closeMinute = "0" + closetime["minute"] if closetime["minute"] == "0" else closetime["minute"]

				opentime = int(openHour + "" + openMinute)
				closetime = int(closeHour + "" + closeMinute)

				if calcTime >= opentime and calcTime <= closetime:
					valid = True

					hour = int(clientTime["hour"])
					minute = int(clientTime["minute"])
					timeDisplay = str(hour - 12 if hour > 12 else hour) + ":" + str("0" + str(minute) if minute < 10 else minute)
					timeDisplay += "pm" if hour >= 12 else "am"

	time = json.dumps({"day": clientTime["day"], "month": clientTime["month"], "date": clientTime["date"], "year": clientTime["year"], "hour": clientTime["hour"], "minute": clientTime["minute"]})
	data = {
		"userId": -1,"workerId": workerid,"locationId": locationid,"menuId": -1,"serviceId": serviceid if serviceid != None else -1,
		"time": time, "status": "w_confirmed","cancelReason": "","locationType": type,
		"customers": 1,"note": note,"orders": "[]","info": "{}"
	}

	columns = []
	insert_data = []
	for key in data:
		columns.append(key)
		insert_data.append("'" + str(data[key]) + "'")

	query("insert into schedule (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")")

	location = query("select owners from location where id = " + str(locationid), True).fetchone()
	owners = "(" + location["owners"][1:-1] + ")"

	sql = "select id, info from owner where id in " + owners

	owners = query(sql, True)
	receiver = []

	for owner in owners:
		info = json.loads(owner["info"])

		receiver.append("owner" + str(owner["id"]))

	return { "msg": "success", "timeDisplay": timeDisplay, "receiver": receiver }

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

	sql = "select count(*) as num from schedule where workerId = " + str(workerid) + " and status = 'blocked' and "
	sql += "json_extract(time, '$.day') = " + str(dayToIndex[jsonDate["day"]]) + " and "
	sql += "json_extract(time, '$.month') = " + str(monthToIndex[jsonDate["month"]]) + " and "
	sql += "json_extract(time, '$.date') = " + str(jsonDate["date"]) + " and "
	sql += "json_extract(time, '$.year') = " + str(jsonDate["year"]) + " and "
	sql += "json_extract(time, '$.hour') = " + str(jsonDate["hour"]) + " and "
	sql += "json_extract(time, '$.minute') = " + str(jsonDate["minute"])
	blocked = query(sql, True).fetchone()["num"]

	if blocked == 0:
		location = query("select id, type from location where owners like '%\"" + str(workerid) + "\"%'", True).fetchone()

		if location != None:
			time = json.dumps({
				"day": dayToIndex[jsonDate["day"]], "month": monthToIndex[jsonDate["month"]], "date": jsonDate["date"], "year": jsonDate["year"], 
				"hour": jsonDate["hour"], "minute": jsonDate["minute"]
			})
			data = {
				"userId": -1,"workerId": workerid, "locationId": location["id"], "menuId": -1, "serviceId": -1,
				"time": time, "status": "blocked", "cancelReason": "", "locationType": location["type"],
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
		sql = "delete from schedule where workerId = " + str(workerid) + " and status = 'blocked' and "
		sql += "json_extract(time, '$.day') = " + str(dayToIndex[jsonDate["day"]]) + " and "
		sql += "json_extract(time, '$.month') = " + str(monthToIndex[jsonDate["month"]]) + " and "
		sql += "json_extract(time, '$.date') = " + str(jsonDate["date"]) + " and "
		sql += "json_extract(time, '$.year') = " + str(jsonDate["year"]) + " and "
		sql += "json_extract(time, '$.hour') = " + str(jsonDate["hour"]) + " and "
		sql += "json_extract(time, '$.minute') = " + str(jsonDate["minute"])

		query(sql)

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

	client = query("select * from user where id = " + str(clientid), True).fetchone()
	worker = query("select username, hours from owner where id = " + str(workerid), True).fetchone()
	location = query("select * from location where id = " + str(locationid), True).fetchone()

	if location != None:
		if serviceid != -1:
			service = query("select * from service where id = " + str(serviceid), True).fetchone()
			servicename = service["name"]
			menuid = service["menuId"]
		else:
			servicename = serviceinfo
			menuid = -1

		if scheduleid != None:
			schedule = query("select * from schedule where id = " + str(scheduleid), True).fetchone()
		else:
			schedule = None

		pushids = []

		sql = "select * from schedule where "
		sql += "json_extract(time, '$.day') = " + str(dayToIndex[clientTime["day"]]) + " and "
		sql += "json_extract(time, '$.month') = " + str(monthToIndex[clientTime["month"]]) + " and "
		sql += "json_extract(time, '$.date') = " + str(clientTime["date"]) + " and "
		sql += "json_extract(time, '$.year') = " + str(clientTime["year"]) + " and "
		sql += "json_extract(time, '$.hour') = " + str(clientTime["hour"]) + " and "
		sql += "json_extract(time, '$.minute') = " + str(clientTime["minute"]) + " and "
		sql += "workerId = " + str(workerid)
		scheduled = query(sql, True).fetchone()

		if (scheduled == None or (scheduled["status"] == "cancel" or scheduled["status"] == "cancel_booked")) or (scheduled != None and "\"id\": " + str(scheduled["id"])) in json.dumps(blocked):
			info = { "msg": "appointment remade", "time": clientTime, "worker": { "id": workerid, "username": worker["username"] }}

			if client != None:
				locationInfo = json.loads(location["info"])
				clientInfo = json.loads(client["info"])
				pushToken = clientInfo["pushToken"]

				info["receiveType"] = locationInfo["type"]
				
				if locationInfo["type"] == "everyone":
					receiver = {"user": "user" + str(clientid), "owners":[]}

					owners = "(" + location["owners"][1:-1] + ")"

					owners = query("select id from owner where id in " + owners, True).fetchall()

					for owner in owners:
						receiver["owners"].append("owner" + str(owner["id"]))
				else:
					receiver = "user" + str(clientid)

				info["receiver"] = receiver

			schedule["time"] = json.dumps({
				"day": dayToIndex[clientTime["day"]], "month": monthToIndex[clientTime["month"]], "date": clientTime["date"], "year": clientTime["year"],
				"hour": clientTime["hour"], "minute": clientTime["minute"]
			})

			schedule["status"] = 'confirmed'
			schedule["note"] = note
			schedule["workerId"] = workerid

			# recreate blocked times
			workingHours = json.loads(worker["hours"])

			for blockedInfo in blocked:
				newTime = blockedInfo["newTime"]
				day = newTime["day"]
				month = monthToIndex[newTime["month"]]
				date = str(newTime["date"])
				year = str(newTime["year"])
				hour = str(newTime["hour"])
				minute = str(newTime["minute"])

				dayInfo = workingHours[day[:3]]
				endtime = dayInfo["closetime"]
				endhour = str(endtime["hour"])
				endminute = str(endtime["minute"])

				timeOne = int(hour + minute)
				timeTwo = int(endhour + endminute)

				if timeOne <= timeTwo:
					sql = "select id from schedule where "
					sql += "json_extract(time, '$.day') = " + str(dayToIndex[day]) + " and "
					sql += "json_extract(time, '$.month') = " + str(month) + " and "
					sql += "json_extract(time, '$.date') = " + date + " and "
					sql += "json_extract(time, '$.year') = " + year + " and "
					sql += "json_extract(time, '$.hour') = " + str(hour) + " and "
					sql += "json_extract(time, '$.minute') = " + str(minute) + " and workerId = " + str(workerid)
					data = query(sql, True).fetchone()

					if data != None:
						if ("\"id\":" + str(data["id"])) not in json.dumps(blocked).replace(" ", "") and str(data["id"]) != str(schedule["id"]):
							status = "scheduleConflict"
				else:
					status = "scheduleConflict"

			if status == "":
				update_data = []
				for key in schedule:
					if key != "table":
						update_data.append(key + " = '" + str(schedule[key]) + "'")

				query("update schedule set " + ", ".join(update_data) + " where id = " + str(schedule["id"]))

				for blockedInfo in blocked:
					newTime = blockedInfo["newTime"]
					day = dayToIndex[newTime["day"]]
					month = monthToIndex[newTime["month"]]
					date = newTime["date"]
					year = newTime["year"]
					hour = newTime["hour"]
					minute = newTime["minute"]

					time = json.dumps({"day": day, "month": month, "date": date, "year": year, "hour": hour, "minute": minute})

					sql = "update schedule set "
					sql += "time = '" + time + "', "
					sql += "workerId = " + str(workerid) + " "
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

@app.route("/push_appointments", methods=["POST"])
def push_appointments():
	content = request.get_json()
	errormsg = ""
	status = ""

	infos = content['schedules']
	ids = []

	for info in infos:
		ids.append(info)

	sql = "select * from schedule where id in (" + json.dumps(ids)[1:-1] + ")"

	schedules = query(sql, True).fetchall()
	receiver = []
	rebooks = {}

	for info in schedules:
		newInfo = infos[str(info["id"])]

		info["time"] = json.dumps({"day": dayToIndex[newInfo["day"]], "month": monthToIndex[newInfo["month"]], "date": newInfo["date"], "year": int(newInfo["year"]), "hour": int(newInfo["hour"]), "minute": int(newInfo["minute"]) })

		if info["userId"] > -1:
			receiver.append("user" + str(info["userId"]))

		if info["status"] == "confirmed":
			rebooks[str(info["id"])] = { "day": newInfo["day"], "month": newInfo["month"], "date": newInfo["date"], "year": int(newInfo["year"]), "hour": int(newInfo["hour"]), "minute": int(newInfo["minute"]) }

		update_data = []
		for key in info:
			if key != "table":
				update_data.append(key + " = '" + str(info[key]) + "'")

		query("update schedule set " + ", ".join(update_data) + " where id = " + str(info["id"]))

	return { "msg": "succeed", "receiver": receiver, "rebooks": rebooks }

@app.route("/cancel_schedule", methods=["POST"])
def cancel_schedule():
	content = request.get_json()

	id = content['scheduleid']
	reason = content['reason']

	appointment = query("select * from schedule where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if appointment != None:
		time = json.loads(appointment["time"])
		time = str(time["day"]) + " " + str(time["month"]) + " " + str(time["date"]) + " " + str(time["year"]) + " " + str(time["hour"]) + " " + str(time["minute"])
		blockedSchedules = getBlockedSchedules(time, appointment["workerId"])
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

		time = json.loads(appointment["time"])
		time = str(time["day"]) + " " + str(time["month"]) + " " + str(time["date"]) + " " + str(time["year"]) + " " + str(time["hour"]) + " " + str(time["minute"])
		removeBlockedSchedules(time, appointment["workerId"])

		return { "msg": "request deleted", "receiver": receiver }

	errormsg = "Action is denied"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/done_service/<id>")
def done_service(id):
	schedule = query("select * from schedule where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	booker = schedule["userId"]
	locationId = schedule["locationId"]

	query("delete from schedule where id = " + str(id))

	data = {
		"tableId": "", "orders": "[]", "time": schedule["time"], 
		"service": str(json.dumps({"userId": schedule["userId"], "workerId": schedule["workerId"], "serviceId": schedule["serviceId"]})), 
		"locationId": str(locationId)
	}
	columns = []
	insert_data = []

	for key in data:
		columns.append(key)
		insert_data.append("'" + data[key] + "'")

	query("insert into income_record (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")")

	time = json.loads(schedule["time"])
	time = str(time["day"]) + " " + str(time["month"]) + " " + str(time["date"]) + " " + str(time["year"]) + " " + str(time["hour"]) + " " + str(time["minute"])
	removeBlockedSchedules(time, schedule["workerId"])
	
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

	time = json.loads(schedule["time"])
	time = str(time["day"]) + " " + str(time["month"]) + " " + str(time["date"]) + " " + str(time["year"]) + " " + str(time["hour"]) + " " + str(time["minute"])
	removeBlockedSchedules(time, schedule["workerId"])

	service = query("select * from service where id = " + str(schedule["serviceId"]), True).fetchone()
	serviceName = service["name"]

	worker = query("select * from owner where id = " + str(schedule["workerId"]), True).fetchone()
	workerInfo = json.loads(worker["info"])

	time = json.loads(schedule["time"])
	time = { "day": indexToDay[time["day"]], "month": time["month"], "date": time["date"], "year": time["year"], "hour": time["hour"], "minute": time["minute"] }
	info = { "scheduleid": scheduleid, "name": serviceName, "time": time, "worker": { "id": workerId, "username": worker["username"] }}

	if workerInfo["pushToken"] != "" and workerInfo["signin"] == True:
		push(pushInfo(
			workerInfo["pushToken"],
			"Appointment cancelled",
			str(timeDisplay),
			content
		))

	return { "msg": "schedule cancelled", "receivers": receivers, "type": schedule["locationType"], "info": info }

@app.route("/get_appointments", methods=["POST"])
def get_appointments():
	content = request.get_json()
	
	ownerid = content['ownerid']
	locationid = content['locationid']

	owner = query("select info from owner where id = " + str(ownerid), True).fetchone()
	location = query("select * from location where id = " + str(locationid), True).fetchone()

	ownerInfo = json.loads(owner["info"])
	isOwner = ownerInfo["userType"] == "owner"

	locationInfo = json.loads(location["info"])
	receiveType = locationInfo["type"]

	sql = "select * from schedule where locationId = " + str(locationid) + " and (status = 'confirmed' or status = 'w_confirmed')"
	selfView = False

	if isOwner == False:
		if receiveType == "owner":
			sql += " and workerId = " + str(ownerid)
			selfView = True
		
	sql += " order by concat("
	sql += "json_extract(time, '$.year'), "
	sql += "(if(json_extract(time, '$.month') < 10, concat('0', json_extract(time, '$.month')), json_extract(time, '$.month'))), "
	sql += "(if(json_extract(time, '$.date') < 10, concat('0', json_extract(time, '$.date')), json_extract(time, '$.date'))), "
	sql += "(if(json_extract(time, '$.hour') < 10, concat('0', json_extract(time, '$.hour')), json_extract(time, '$.hour'))), "
	sql += "(if(json_extract(time, '$.minute') < 10, concat('0', json_extract(time, '$.minute')), json_extract(time, '$.minute')))"
	sql += ") limit 10"

	datas = query(sql, True)
	appointments = []

	for data in datas:
		user = query("select * from user where id = " + str(data['userId']), True).fetchone()
		service = query("select * from service where id = " + str(data['serviceId']), True).fetchone()
		worker = query("select * from owner where id = " + str(data['workerId']), True).fetchone()
			
		info = json.loads(data["info"])
		client = { 
			"id": user["id"], 
			"username": user["username"]
		}
		worker = { "id": worker["id"], "username": worker["username"] }
		image = json.loads(service["image"]) if service != None else {"name": ""}
		time = json.loads(data["time"])

		time = { "day": indexToDay[int(time["day"])], "month": indexToMonth[int(time["month"])], "date": time["date"], "year": time["year"], "hour": time["hour"], "minute": time["minute"] }
		appointments.append({
			"key": "appointment-" + str(data['id']),
			"id": str(data['id']),
			"username": user["username"],
			"client": client,
			"worker": worker if selfView == False else None,
			"time": time,
			"serviceid": service["id"] if service != None else "",
			"name": service["name"],
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"type": data["status"]
		})

	return { "appointments": appointments, "numappointments": len(appointments) }

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
		options = json.loads(data["options"])
		sizes = options["sizes"]
		quantities = options["quantities"]
		percents = options["percents"]

		product = query("select * from product where id = " + str(data['productId']), True).fetchone()
		productOptions = json.loads(product["options"])
		productSizes = productOptions["sizes"]
		productQuantities = productOptions["quantities"]
		productPercents = productOptions["percents"]

		sizesInfo = {}
		for info in productSizes:
			if info["name"] in sizes:
				sizesInfo[info["name"]] = float(info["price"])

		quantitiesInfo = {}
		for info in productQuantities:
			if info["input"] in quantities:
				quantitiesInfo[info["input"]] = float(info["price"])

		percentsInfo = {}
		for info in productPercents:
			if info["input"] in percents:
				percentsInfo[info["input"]] = float(info["price"])

		quantity = int(data['quantity'])
		cost = 0

		if product != None:
			if product["price"] == "":
				for info in sizes:
					cost += quantity * float(sizesInfo[info])

				for info in quantities:
					cost += quantity * float(quantitiesInfo[info])
			else:
				cost = float(product["price"]) * quantity

		cartItemSizes = []
		cartItemQuantities = []
		cartItemPercents = []

		for index, info in enumerate(sizesInfo):
			cartItemSizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info], "selected": info in sizes })

		for index, info in enumerate(quantitiesInfo):
			cartItemQuantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info], "selected": info in quantities })

		for index, info in enumerate(percentsInfo):
			cartItemPercents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info], "selected": info in percents })

		image = json.loads(product["image"]) if product != None else {"name": ""}
		orders.append({
			"key": "cart-item-" + str(data['id']),
			"id": str(data['id']),
			"name": product["name"],
			"note": data['note'],
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"sizes": cartItemSizes, "quantities": cartItemQuantities, "percents": cartItemPercents, "quantity": quantity,
			"cost": cost
		})

		if data['status'] == "checkout":
			ready = False

	return { "orders": orders, "ready": ready, "waitTime": waitTime }
