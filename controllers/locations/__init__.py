import datetime
from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_locations")
def welcome_locations():
	datas = query("select id from location limit 5", True).fetchall()
	locations = []

	for data in datas:
		locations.append(data["id"])

	return { "msg": "welcome to locations of EasyBook", "locations": locations }

@app.route("/setup_location", methods=["POST"])
def setup_location():
	storeName = request.form['storeName']
	phonenumber = request.form['phonenumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	hours = request.form['hours']
	type = request.form['type']
	longitude = request.form['longitude']
	latitude = request.form['latitude']
	ownerid = request.form['ownerid']

	owner = query("select * from owner where id = " + str(ownerid), True).fetchone()
	ownerProfile = json.loads(owner["profile"])

	errormsg = ""
	status = ""

	location = query("select * from location where phonenumber = '" + str(phonenumber) + "'", True).fetchone()

	if location == None:
		isWeb = request.form.get("web")

		if isWeb != None: # website version
			logo = json.loads(request.form['logo'])

			uri = logo['uri'].split(",")[1]
			name = logo['name']
			size = logo['size']

			writeToFile(uri, name)

			logoname = json.dumps({"name": name, "width": int(size["width"]), "height": int(size["height"]) })
		else:
			logopath = request.files.get('logo', False)
			logoexist = False if logopath == False else True

			if logoexist == True:
				logo = request.files['logo']
				imagename = logo.filename

				logoname = json.dumps({"name": imagename, "width": 200, "height": 200})

				logo.save(os.path.join('static', imagename))
			else:
				logoname = json.dumps({"name": "", "width": 0, "height": 0})

		if errormsg == "":
			locationInfo = json.dumps({"listed":False, "menuPhotos": [], "type": "everyone"})

			data = {
				"name": storeName, "phonenumber": phonenumber, "logo": logoname,
				"longitude": longitude, "latitude": latitude, "owners": '["' + str(ownerid) + '"]', "type": type,
				"hours": hours, "info": locationInfo
			}
			columns = []
			insert_data = []

			for key in data:
				columns.append(key)
				insert_data.append("'" + str(data[key]) + "'")

			id = query("insert into location (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

			return { 
				"msg": "success", 
				"id": id, 
				"ownerProfile": ownerProfile # if it's owner's first salon
			}
	else:
		errormsg = "Location phone number already taken"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_information", methods=["POST"])
def update_information():
	content = request.get_json()
	errormsg = ""
	status = ""

	id = content['id']
	storeName = content['storeName']
	phonenumber = content['phonenumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")

	location = query("select * from location where id = " + str(id), True).fetchone()

	if location != None:
		location["name"] = storeName
		location["phonenumber"] = phonenumber

		update_data = []
		for key in location:
			if key != "table":
				update_data.append(key + " = '" + str(location[key]) + "'")

		query("update location set " + ", ".join(update_data) + " where id = " + str(location["id"]))

		return { "msg": "success", "id": location["id"] }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_address", methods=["POST"])
def update_address():
	content = request.get_json()
	errormsg = ""
	status = ""

	id = content['id']
	longitude = content['longitude']
	latitude = content['latitude']

	location = query("select * from location where id = " + str(id), True).fetchone()

	if location != None:
		location["longitude"] = longitude
		location["latitude"] = latitude

		update_data = []
		for key in location:
			if key != "table":
				update_data.append(key + " = '" + str(location[key]) + "'")

		query("update location set " + ", ".join(update_data) + " where id = " + str(location["id"]))

		return { "msg": "success", "id": location["id"] }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_logo", methods=["POST"])
def update_logo():
	errormsg = ""
	status = ""

	id = request.form['id']

	location = query("select * from location where id = " + str(id), True).fetchone()

	if location != None:
		oldlogo = json.loads(location["logo"])

		isWeb = request.form.get("web")

		if isWeb != None:
			logo = json.loads(request.form['logo'])
			imagename = logo['name']

			if imagename != '':
				uri = logo['uri'].split(",")[1]
				size = logo['size']

				if oldlogo["name"] != "" and os.path.exists(os.path.join("static", oldlogo["name"])) == True:
					os.remove("static/" + oldlogo["name"])

				writeToFile(uri, imagename)

				location["logo"] = json.dumps({"name": imagename, "width": int(size['width']), "height": int(size['height'])})
		else:
			logopath = request.files.get('logo', False)
			logoexist = False if logopath == False else True

			if logoexist == True:
				logo = request.files['logo']
				imagename = logo.filename

				size = json.loads(request.form['size'])
				
				if logo.filename != oldlogo["name"]:
					if oldlogo["name"] != "" and oldlogo["name"] != None and os.path.exists("static/" + oldlogo["name"]):
						os.remove("static/" + oldlogo["name"])

					logo.save(os.path.join('static', imagename))

				location["logo"] = json.dumps({"name": imagename, "width": size["width"], "height": size["height"]})

		query("update location set logo = " + json.dumps(location["logo"]) + " where id = " + str(id))

		return { "msg": "success", "id": location["id"] }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/fetch_num_appointments/<ownerid>")
def fetch_num_appointments(ownerid):
	numAppointments = query("select count(*) as num from schedule where status = 'confirmed' and workerId = " + str(ownerid), True).fetchone()
	numAppointments = numAppointments["num"] if numAppointments != None else 0

	return { "numAppointments": numAppointments }

@app.route("/fetch_num_cartorderers/<id>")
def fetch_num_cartorderers(id):
	numCartorderers = query("select count(*) as num from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'ready' or status = 'requestedOrder') group by adder, orderNumber", True).fetchone()
	numCartorderers = numCartorderers["num"] if numCartorderers != None else 0

	return { "numCartorderers": numCartorderers }

@app.route("/set_type", methods=["POST"])
def set_type():
	content = request.get_json()

	locationid = content['locationid']
	type = content['type']

	errormsg = ""
	status = ""

	query("update location set type = '" + type + "' where id = " + str(locationid))

	return { "msg": "success" }

@app.route("/update_location_hours", methods=["POST"])
def update_location_hours():
	content = request.get_json()
	
	locationid = content['locationid']
	hours = content['hours']

	errormsg = ""
	status = ""

	query("update location set hours = '" + hours + "' where id = " + str(locationid))

	return { "msg": "success" }

@app.route("/get_day_hours", methods=["POST"])
def get_day_hours():
	content = request.get_json()
	errormsg = ""
	status = ""

	days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

	locationid = content['locationid']
	jsonDate = content['jsonDate']

	location = query("select owners, hours from location where id = " + str(locationid), True).fetchone()

	if location != None:
		owners = query("select id, username, profile from owner where id in (" + str(location["owners"])[1:-1] + ")", True).fetchall()
		hours = json.loads(location["hours"])
			
		workers = []
		for index, owner in enumerate(owners):
			profile = json.loads(owner["profile"])
			workers.append({ 
				"key": "worker-" + str(index) + "-" + str(owner["id"]), 
				"id": owner["id"], "username": owner["username"], 
				"profile": profile if profile["name"] != "" else {"width": 360, "height": 360}
			})
		
		times = []

		dayHours = hours[jsonDate["day"]]

		opentime = dayHours["opentime"]
		closetime = dayHours["closetime"]

		openhour = int(opentime["hour"])
		openminute = int(opentime["minute"])
		closehour = int(closetime["hour"])
		closeminute = int(closetime["minute"])

		return { "opentime": opentime, "closetime": closetime, "workers": workers }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/set_receive_type", methods=["POST"])
def set_receive_type():
	content = request.get_json()
	errormsg = ""
	status = ""

	locationid = content['locationid']
	type = content['type']

	location = query("select * from location where id = " + str(locationid), True).fetchone()

	if location != None:
		info = json.loads(location["info"])
		info["type"] = type

		query("update location set info = '" + json.dumps(info) + "' where id = " + str(locationid))

		return { "msg": "success" }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }

@app.route("/get_locations", methods=["POST"])
def get_locations():
	content = request.get_json()

	longitude = content['longitude']
	latitude = content['latitude']
	name = content['locationName']
	day = content['day']
	errormsg = ""
	status = ""

	if longitude != None and latitude != None:
		longitude = float(longitude)
		latitude = float(latitude)

		locations = [
			{ "key": "0", "service": "restaurant", "header": "Restaurant(s)", "locations": [], "loading": True, "index": 0, "max": 0 },
			{ "key": "1", "service": "hair", "header": "Hair Salon(s)", "locations": [], "loading": True, "index": 0, "max": 0 },
			{ "key": "2", "service": "nail", "header": "Nail Salon(s)", "locations": [], "loading": True, "index": 0, "max": 0 },
			{ "key": "3", "service": "store", "header": "Store(s)", "locations": [], "loading": True, "index": 0, "max": 0 }
		]
		orderQuery = "and name like '%" + name + "%' " if name != "" else ""
		orderQuery += "order by ST_Distance_Sphere(point(" + str(longitude) + ", " + str(latitude) + "), point(longitude, latitude))"

		point1 = (longitude, latitude)

		# get restaurants
		sql = "select * from location where type = 'restaurant' and info like '%\"listed\": true%' " + orderQuery + " limit 0, 10"
		maxsql = "select count(*) as num from location where type = 'restaurant' and info like '%\"listed\": true%' " + orderQuery
		datas = query(sql, True).fetchall()
		maxdatas = query(maxsql, True).fetchone()["num"]
		for data in datas:
			lon2 = float(data['longitude'])
			lat2 = float(data['latitude'])

			point2 = (lon2, lat2)
			distance = haversine(point1, point2)

			if distance < 1:
				distance *= 1000
				distance = str(round(distance, 1)) + " m"
			else:
				distance = str(round(distance, 1)) + " km"

			hours = json.loads(data['hours'])
			logo = json.loads(data['logo'])
			locations[0]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": logo if logo["name"] != "" else { "width": 300, "height": 300 },
				"nav": "restaurantprofile",
				"name": data['name'],
				"distance": distance,
				"opentime": hours[day]["opentime"],
				"closetime": hours[day]["closetime"],
				"service": "restaurant"
			})

		locations[0]["index"] += len(datas)

		# get hair salons
		sql = "select * from location where type = 'hair' and info like '%\"listed\": true%' " + orderQuery + " limit 0, 10"
		maxsql = "select count(*) as num from location where type = 'hair' and info like '%\"listed\": true%' " + orderQuery
		datas = query(sql, True).fetchall()
		maxdatas = query(maxsql, True).fetchone()["num"]
		for data in datas:
			lon2 = float(data['longitude'])
			lat2 = float(data['latitude'])

			point2 = (lon2, lat2)
			distance = haversine(point1, point2)

			if distance < 1:
				distance *= 1000
				distance = str(round(distance, 1)) + " m"
			else:
				distance = str(round(distance, 1)) + " km"

			hours = json.loads(data['hours'])
			logo = json.loads(data['logo'])
			locations[1]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": logo if logo["name"] != "" else { "width": 300, "height": 300 },
				"nav": "salonprofile",
				"name": data['name'],
				"distance": distance,
				"opentime": hours[day]["opentime"],
				"closetime": hours[day]["closetime"],
				"service": "hair"
			})

		locations[1]["index"] += len(datas)

		# get nail salons
		sql = "select * from location where type = 'nail' and info like '%\"listed\": true%' " + orderQuery + " limit 0, 10"
		maxsql = "select count(*) as num from location where type = 'nail' and info like '%\"listed\": true%' " + orderQuery
		datas = query(sql, True).fetchall()
		maxdatas = query(maxsql, True).fetchone()["num"]
		for data in datas:
			lon2 = float(data['longitude'])
			lat2 = float(data['latitude'])

			point2 = (lon2, lat2)
			distance = haversine(point1, point2)

			if distance < 1:
				distance *= 1000
				distance = str(round(distance, 1)) + " m"
			else:
				distance = str(round(distance, 1)) + " km"

			hours = json.loads(data['hours'])
			logo = json.loads(data['logo'])
			locations[2]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": logo if logo["name"] != "" else { "width": 300, "height": 300 },
				"nav": "salonprofile",
				"name": data['name'],
				"distance": distance,
				"opentime": hours[day]["opentime"],
				"closetime": hours[day]["closetime"],
				"service": "nail"
			})

		locations[2]["index"] += len(datas)

		sql = "select * from location where type = 'store' and info like '%\"listed\": true%' " + orderQuery + " limit 0, 10"
		maxsql = "select count(*) as num from location where type = 'store' and info like '%\"listed\": true%' " + orderQuery
		datas = query(sql, True).fetchall()
		maxdatas = query(maxsql, True).fetchone()["num"]
		for data in datas:
			lon2 = float(data['longitude'])
			lat2 = float(data['latitude'])

			point2 = (lon2, lat2)
			distance = haversine(point1, point2)

			if distance < 1:
				distance *= 1000
				distance = str(round(distance, 1)) + " m"
			else:
				distance = str(round(distance, 1)) + " km"

			hours = json.loads(data['hours'])
			logo = json.loads(data['logo'])
			locations[3]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": logo if logo["name"] != "" else { "width": 300, "height": 300 },
				"nav": "storeprofile",
				"name": data['name'],
				"distance": distance,
				"opentime": hours[day]["opentime"],
				"closetime": hours[day]["closetime"],
				"service": "store"
			})

		locations[3]["index"] += len(datas)
		
		return { "locations": locations }
	else:
		errormsg = "Coordinates is unknown"
		status = "unknowncoords"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_more_locations", methods=["POST"])
def get_more_locations():
	content = request.get_json()

	longitude = float(content['longitude'])
	latitude = float(content['latitude'])
	name = content['locationName']
	type = content['type']
	index = str(content['index'])
	day = content['day']

	locations = []
	orderQuery = "and name like '%" + name + "%' " if name != "" else ""
	orderQuery += "order by st_distance_sphere(point(" + str(longitude) + ", " + str(latitude) + "), point(longitude, latitude))"
	lon1 = longitude
	lat1 = latitude

	# get locations
	sql = "select * from location where type = '" + type + "' and info like '%\"listed\": true%' " + orderQuery + " limit " + index + ", 10"
	maxsql = "select count(*) as num from location where type = '" + type + "' and info like '%\"listed\": true%' " + orderQuery
	datas = query(sql, True).fetchall()
	maxdatas = query(maxsql, True).fetchone()["num"]
	for data in datas:
		lon2 = float(data['longitude'])
		lat2 = float(data['latitude'])

		point1 = (lon1, lat1)
		point2 = (lon2, lat2)
		distance = haversine(point1, point2)

		if distance < 1:
			distance *= 1000
			distance = str(round(distance, 1)) + " m"
		else:
			distance = str(round(distance, 1)) + " km"

		hours = json.loads(data['hours'])
		logo = json.loads(data['logo'])
		nav = ((type == "restaurant" and "restaurant") or ((type == "nail" or type == "hair") and "salon") or (type == "store" and "store")) + "profile"
		locations.append({
			"key": "l-" + str(data['id']),
			"id": data['id'],
			"logo": logo if logo["name"] != "" else { "width": 300, "height": 300 },
			"nav": nav,
			"name": data['name'],
			"distance": distance,
			"opentime": hours[day]["opentime"],
			"closetime": hours[day]["closetime"],
			"service": type
		})

	return { "newlocations": locations, "index": len(datas), "max": maxdatas }
	
@app.route("/get_logins/<id>") # restaurant only
def get_logins(id):
	errormsg = ""
	status = ""

	location = query("select owners from location where id = " + str(id), True).fetchone()

	if location != None:
		owners = query("select id, cellnumber, info from owner where id in (" + location["owners"][1:-1] + ")", True).fetchall()

		for index, owner in enumerate(owners):
			info = json.loads(owner["info"])

			owner["key"] = "owner-" + str(index)
			owner["id"] = owner["id"]
			owner["userType"] = info["userType"]

			del owner["info"]

		return { "owners": owners }
	else:
		errormsg = "Location doesn't exist"
		status = "nonExist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_all_locations/<id>")
def get_all_locations(id):
	datas = query("select * from location where owners like '%\"" + str(id) + "\"%'", True).fetchall()
	locations = []

	for data in datas:
		logo = json.loads(data["logo"])

		locations.append({
			"id": data["id"], 
			"key": data["id"],
			"name": data["name"],
			"type": data["type"],
			"logo": logo if logo["name"] != "" else { "width": 300, "height": 300 }
		})

	return { "locations": locations }

@app.route("/get_location_profile", methods=["POST"])
def get_location_profile():
	content = request.get_json()

	locationid = str(content['locationid'])

	if 'longitude' in content:
		if content['longitude'] != None:
			longitude = float(content['longitude'])
			latitude = float(content['latitude'])
		else:
			longitude = content['longitude']
			latitude = content['latitude']
	else:
		longitude = None
		latitude = None

	location = query("select * from location where id = " + str(locationid), True).fetchone()
	errormsg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location["info"])

		if longitude != None:
			point1 = (longitude, latitude)
			point2 = (float(location["longitude"]), float(location["latitude"]))
			distance = haversine(point1, point2)

			if distance < 1:
				distance *= 1000
				distance = str(round(distance, 1)) + " m away"
			else:
				distance = str(round(distance, 1)) + " km away"
		else:
			distance = None

		hours = [
			{ "key": "0", "header": "Sunday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "close": False },
			{ "key": "1", "header": "Monday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "close": False },
			{ "key": "2", "header": "Tuesday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "close": False },
			{ "key": "3", "header": "Wednesday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "close": False },
			{ "key": "4", "header": "Thursday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "close": False },
			{ "key": "5", "header": "Friday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "close": False },
			{ "key": "6", "header": "Saturday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "close": False }
		]

		if location["hours"] != '':
			data = json.loads(location["hours"])
			day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

			for k, info in enumerate(hours):
				openhour = int(data[day[k][:3]]["opentime"]["hour"])
				closehour = int(data[day[k][:3]]["closetime"]["hour"])
				close = data[day[k][:3]]["close"]

				openperiod = "PM" if openhour >= 12 else "AM"
				openhour = int(openhour)

				if openhour == 0:
					openhour = 12
				elif openhour > 12:
					openhour -= 12

				closeperiod = "PM" if closehour >= 12 else "AM"
				closehour = int(closehour)

				if closehour == 0:
					closehour = 12
				elif closehour > 12:
					closehour -= 12

				info["opentime"]["hour"] = openhour
				info["opentime"]["minute"] = data[day[k][:3]]["opentime"]["minute"]
				info["opentime"]["period"] = openperiod

				info["closetime"]["hour"] = closehour
				info["closetime"]["minute"] = data[day[k][:3]]["closetime"]["minute"]
				info["closetime"]["period"] = closeperiod
				info["close"] = close

				hours[k] = info

		phonenumber = location["phonenumber"]

		f3 = str(phonenumber[0:3])
		s3 = str(phonenumber[3:6])
		l4 = str(phonenumber[6:len(phonenumber)])

		phonenumber = "(" + f3 + ") " + s3 + "-" + l4

		logo = json.loads(location["logo"])
		info = {
			"id": location["id"],
			"name": location["name"],
			"phonenumber": phonenumber,
			"distance": distance,
			"logo": logo if logo["name"] != "" else {"width": 300, "height": 300},
			"longitude": float(location["longitude"]),
			"latitude": float(location["latitude"]),
			"hours": hours,
			"type": location["type"],
			"receiveType": locationInfo["type"]
		}

		return { "info": info }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_location_hours/<id>")
def get_location_hours(id):
	location = query("select * from location where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if location != None:
		daysArr = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

		hours = json.loads(location["hours"])
		openDays = {}

		for day in hours:
			dayInfo = hours[day]
			openTime = dayInfo["opentime"]
			closeTime = dayInfo["closetime"]

			openHour = int(openTime["hour"])
			openMinute = int(openTime["minute"])
			closeHour = int(closeTime["hour"])
			closeMinute = int(closeTime["minute"])

			if dayInfo["close"] == False:
				openDays[day] = {
					"close": dayInfo["close"],
					"openHour": openHour,
					"openMinute": openMinute,
					"openPeriod": "PM" if openHour >= 12 else "AM",
					"closeHour": closeHour,
					"closeMinute": closeMinute,
					"closePeriod": "PM" if closeHour >= 12 else "AM"
				}

		return { "hours": openDays }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_income/<id>")
def get_income(id):
	location = query("select * from location where id = " + str(id), True).fetchone()
	errormsg = ""

	if location != None:
		tables = query("select tableId from dining_table where locationId = " + str(id), True).fetchall()
		tableIds = []

		for table in tables:
			tableIds.append(table["tableId"])

		monthly = "concat("
		monthly += "json_extract(time, '$.year'), "
		monthly += "json_extract(time, '$.month')"
		monthly += ") as monthly"

		daily = "concat("
		daily += "json_extract(time, '$.year'), "
		daily += "json_extract(time, '$.month'), "
		daily += "json_extract(time, '$.date')"
		daily += ") as daily"

		yearly = "json_extract(time, '$.year') as yearly"

		sql = "select orders, time, " + monthly + ", " + daily + ", " + yearly + " from dining_record where tableId in (" + json.dumps(tableIds)[1:-1] + ")"
		sql += " order by "
		sql += "concat("
		sql += "json_extract(time, '$.year'), "
		sql += "json_extract(time, '$.month'), "
		sql += "json_extract(time, '$.date'), "
		sql += "json_extract(time, '$.day'), "
		sql += "json_extract(time, '$.hour'), "
		sql += "json_extract(time, '$.minute')"
		sql += ")"
		datas = query(sql, True).fetchall()
		dayTotal = 0.00
		monthTotal = 0.00
		yearTotal = 0.00
		daily = []
		monthly = []
		yearly = []
		dayHold = ""
		monthHold = ""
		yearHold = ""

		for dataindex, data in enumerate(datas):
			orders = json.loads(data["orders"])
			time = json.loads(data["time"])
			day = daysArr[int(time["day"])]
			month = monthsArr[int(time["month"])]
			date = str(time["date"])
			year = str(time["year"])

			for order in orders:
				if "finish" in order:
					sizes = order["sizes"]
					quantities = order["quantities"]
					percents = order["percents"]

					product = query("select * from product where id = " + str(order["productId"]), True).fetchone()

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

					order["name"] = product["number"] if product["number"] != "" else product["name"]

					if product["price"] != "":
						dayTotal += int(order["quantity"]) * float(product["price"])
						monthTotal += int(order["quantity"]) * float(product["price"])
						yearTotal += int(order["quantity"]) * float(product["price"])
						cost = round(int(order["quantity"]) * float(product["price"]), 2)
					else:
						if len(sizes) > 0:
							for size in sizes:
								dayTotal += int(order["quantity"]) * sizesInfo[size]
								monthTotal += int(order["quantity"]) * sizesInfo[size]
								yearTotal += int(order["quantity"]) * sizesInfo[size]
						else:
							for quantity in quantities:
								dayTotal += int(order["quantity"]) * float(quantitiesInfo[quantity])
								monthTotal += int(order["quantity"]) * float(quantitiesInfo[quantity])
								yearTotal += int(order["quantity"]) * float(quantitiesInfo[quantity])

					for percent in percents:
						dayTotal += int(order["quantity"]) * float(percentsInfo[percent["input"]])
						monthTotal += int(order["quantity"]) * float(percentsInfo[percent["input"]])
						yearTotal += int(order["quantity"]) * float(percentsInfo[percent["input"]])

			if dataindex == 0:
				monthHold = data["monthly"]
				dayHold = data["daily"]
				yearHold = data["yearly"]
				
				monthly.append({ "key": "monthly-" + str(len(monthly)), "header": month + ", " + year })
				daily.append({ "key": "daily-" + str(len(daily)), "header": day + " " + month + ", " + date })
				yearly.append({ "key": "yearly-" + str(len(yearly)), "header": year })
			else:
				if data["monthly"] != monthHold: # restart total for next month
					monthHold = data["monthly"]

					monthly[len(monthly) - 1]["total"] = round(monthTotal, 2)
					monthTotal = 0.00

					monthly.append({
						"key": "monthly-" + str(len(monthly)),
						"header": month + ", " + year
					})

				if data["daily"] != dayHold: # restart total for next day
					dayHold = data["daily"]

					daily[len(daily) - 1]["total"] = round(dayTotal, 2)
					dayTotal = 0.00

					daily.append({
						"key": "daily-" + str(len(daily)),
						"header": day + " " + month + ", " + date + " " + year
					})

				if data["yearly"] != yearHold:
					yearHold = data["yearly"]

					yearly[len(yearly) - 1]["total"] = round(yearTotal, 2)
					yearlyTotal = 0.00

					yearly.append({
						"key": "yearly-" + str(len(yearly)),
						"header": year
					})

		if "total" not in monthly[len(monthly) - 1]:
			monthly[len(monthly) - 1]["total"] = round(monthTotal, 2)

		if "total" not in daily[len(daily) - 1]:
			daily[len(daily) - 1]["total"] = round(dayTotal, 2)

		if "total" not in yearly[len(yearly) - 1]:
			yearly[len(yearly) - 1]["total"] = round(yearTotal, 2)

		return { "daily": daily, "monthly": monthly, "yearly": yearly }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
