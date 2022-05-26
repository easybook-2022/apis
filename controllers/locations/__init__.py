from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_locations", methods=["GET"])
def welcome_locations():
	datas = Location.query.all()
	locations = []

	for data in datas:
		locations.append(data.id)

	return { "msg": "welcome to locations of easygo", "locations": locations }

@app.route("/setup_location", methods=["POST"])
def setup_location():
	storeName = request.form['storeName']
	phonenumber = request.form['phonenumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	addressOne = request.form['addressOne']
	addressTwo = request.form['addressTwo']
	city = request.form['city']
	province = request.form['province']
	postalcode = request.form['postalcode']
	hours = request.form['hours']
	type = request.form['type']
	longitude = request.form['longitude']
	latitude = request.form['latitude']
	ownerid = request.form['ownerid']

	owner = Owner.query.filter_by(id=ownerid).first()

	errormsg = ""
	status = ""

	if owner != None:
		location = Location.query.filter_by(phonenumber=phonenumber).first()

		if location == None:
			isWeb = request.form.get("web")

			if isWeb != None:
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
				locationInfo = json.dumps({"listed":False, "menuPhotos": [], "type": "stylist"})
				location = Location(
					storeName, addressOne, addressTwo, 
					city, province, postalcode, phonenumber, logoname,
					longitude, latitude, '["' + str(ownerid) + '"]',
					type, hours, locationInfo
				)

				db.session.add(location)
				db.session.commit()

				return { "msg": "location setup", "id": location.id }
		else:
			errormsg = "Location phone number already taken"
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_location", methods=["POST"])
def update_location():
	id = request.form['id']
	storeName = request.form['storeName']
	phonenumber = request.form['phonenumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	addressOne = request.form['addressOne']
	addressTwo = request.form['addressTwo']
	city = request.form['city']
	province = request.form['province']
	postalcode = request.form['postalcode']
			
	longitude = request.form['longitude']
	latitude = request.form['latitude']
	ownerid = request.form['ownerid']

	owner = Owner.query.filter_by(id=ownerid).first()
	errormsg = ""
	status = ""

	if owner != None:
		location = Location.query.filter_by(id=id).first()

		if location != None:
			oldlogo = json.loads(location.logo)

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

					location.logo = json.dumps({"name": imagename, "width": int(size['width']), "height": int(size['height'])})
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

					location.logo = json.dumps({"name": imagename, "width": size["width"], "height": size["height"]})

			location.name = storeName
			location.addressOne = addressOne
			location.addressTwo = addressTwo
			location.city = city
			location.province = province
			location.postalcode = postalcode
			location.phonenumber = phonenumber
			location.longitude = longitude
			location.latitude = latitude

			db.session.commit()

			return { "msg": "location updated", "id": location.id }
		else:
			errormsg = "Location doesn't exist"
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/fetch_num_appointments/<ownerid>")
def fetch_num_appointments(ownerid):
	numAppointments = query("select count(*) as num from schedule where status = 'confirmed' and workerId = " + str(ownerid), True)

	if len(numAppointments) == 1:
		num = numAppointments[0]["num"]
	else:
		num = 0

	return { "numAppointments": num }

@app.route("/fetch_num_cartorderers/<id>")
def fetch_num_cartorderers(id):
	numCartorderers = query("select count(*) as num from cart where locationId = " + str(id) + " and (status = 'checkout' or status = 'ready' or status = 'requestedOrder') group by adder, orderNumber", True)

	if len(numCartorderers) > 0:
		numCartorderers = len(numCartorderers)
	else:
		numCartorderers = 0

	return { "numCartorderers": numCartorderers }

@app.route("/set_type", methods=["POST"])
def set_type():
	content = request.get_json()

	ownerid = content['ownerid']
	locationid = content['locationid']
	type = content['type']

	owner = Owner.query.filter_by(id=ownerid).first()
	errormsg = ""
	status = ""

	if owner != None:
		location = Location.query.filter_by(id=locationid).first()

		if location != None:
			location.type = type

			db.session.commit()

			return { "msg": "" }
		else:
			errormsg = "Location doesn't exist"
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/set_location_hours", methods=["POST"])
def set_location_hours():
	content = request.get_json()
	
	locationid = content['locationid']
	hours = content['hours']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		location.hours = json.dumps(hours)

		db.session.commit()

		return { "msg": "hours updated" }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/set_receive_type", methods=["POST"])
def set_receive_type():
	content = request.get_json()

	locationid = content['locationid']
	type = content['type']

	location = Location.query.filter_by(id=locationid).first()

	if location != None:
		info = json.loads(location.info)
		info["type"] = type

		location.info = json.dumps(info)

		db.session.commit()

		return { "msg": "success" }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

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
		datas = query(sql, True)
		maxdatas = query(maxsql, True)[0]["num"]
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

			locations[0]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": json.loads(data['logo']),
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
		datas = query(sql, True)
		maxdatas = query(maxsql, True)[0]["num"]
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

			locations[1]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": json.loads(data['logo']),
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
		datas = query(sql, True)
		maxdatas = query(maxsql, True)[0]["num"]
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

			locations[2]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": json.loads(data['logo']),
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
		datas = query(sql, True)
		maxdatas = query(maxsql, True)[0]["num"]
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

			locations[3]["locations"].append({
				"key": "l-" + str(data['id']),
				"id": data['id'],
				"logo": json.loads(data['logo']),
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
	datas = query(sql, True)
	maxdatas = query(maxsql, True)[0]["num"]
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

		locations.append({
			"key": "l-" + str(data['id']),
			"id": data['id'],
			"logo": json.loads(data['logo']),
			"nav": ("restaurant" if type == "restaurant" else "salon") + "profile",
			"name": data['name'],
			"distance": distance,
			"opentime": hours[day]["opentime"],
			"closetime": hours[day]["closetime"]
		})

	return { "newlocations": locations, "index": len(datas), "max": maxdatas }
	
@app.route("/get_all_locations/<id>")
def get_all_locations(id):
	datas = Location.query.filter(Location.owners.like("%\"" + str(id) + "\"%")).all()
	locations = []

	for data in datas:
		locations.append({
			"id": data.id, "key": data.id,
			"name": data.name,
			"address": data.addressOne + ("" if data.addressTwo == "" else " " + data.addressTwo) + ", " + data.city + " " + data.province + ", " + data.postalcode,
			"type": data.type,
			"logo": json.loads(data.logo)
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

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)

		if longitude != None:
			point1 = (longitude, latitude)
			point2 = (float(location.longitude), float(location.latitude))
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

		if location.hours != '':
			data = json.loads(location.hours)
			day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

			for k, info in enumerate(hours):
				openhour = int(data[day[k][:3]]["opentime"]["hour"])
				closehour = int(data[day[k][:3]]["closetime"]["hour"])
				close = data[day[k][:3]]["close"]

				openperiod = "PM" if openhour > 12 else "AM"
				openhour = int(openhour)

				if openhour == 0:
					openhour = "12"
				elif openhour < 10:
					openhour = "0" + str(openhour)
				elif openhour > 12:
					openhour -= 12
					openhour = "0" + str(openhour) if openhour < 10 else str(openhour)

				closeperiod = "PM" if closehour > 12 else "AM"
				closehour = int(closehour)

				if closehour == 0:
					closehour = "12"
				elif closehour < 10:
					closehour = "0" + str(closehour)
				elif closehour > 12:
					closehour -= 12
					closehour = "0" + str(closehour) if closehour < 10 else str(closehour)

				info["opentime"]["hour"] = str(openhour)
				info["opentime"]["minute"] = data[day[k][:3]]["opentime"]["minute"]
				info["opentime"]["period"] = openperiod

				info["closetime"]["hour"] = str(closehour)
				info["closetime"]["minute"] = data[day[k][:3]]["closetime"]["minute"]
				info["closetime"]["period"] = closeperiod
				info["close"] = close
				info["working"] = close == False

				hours[k] = info

		phonenumber = location.phonenumber

		f3 = str(phonenumber[0:3])
		s3 = str(phonenumber[3:6])
		l4 = str(phonenumber[6:len(phonenumber)])

		phonenumber = "(" + f3 + ") " + s3 + "-" + l4

		info = {
			"id": location.id,
			"name": location.name,
			"addressOne": location.addressOne,
			"addressTwo": location.addressTwo,
			"city": location.city,
			"province": location.province,
			"postalcode": location.postalcode,
			"phonenumber": phonenumber,
			"distance": distance,
			"logo": json.loads(location.logo),
			"longitude": float(location.longitude),
			"latitude": float(location.latitude),
			"hours": hours,
			"type": location.type,
			"receiveType": locationInfo["type"],
			"fullAddress": location.addressOne + ", " + (location.addressOne if location.addressTwo != "" else "") + location.city + ", " + location.province + ", " + location.postalcode
		}

		return { "info": info }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_hours", methods=["POST"])
def get_hours():
	content = request.get_json()

	locationid = content['locationid']
	day = content['day']

	scheduled = Schedule.query.filter_by(locationId=locationid).all()
	location = Location.query.filter_by(id=locationid).first()
	times = []
	errormsg = ""
	status = ""
	daysArr = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

	if location != None:
		hours = json.loads(location.hours)
		openDays = []

		openTime = hours[day]["opentime"]
		closeTime = hours[day]["closetime"]

		for data in scheduled:
			time = json.loads(data.time)
			times.append(time)

		for day in daysArr:
			if hours[day]["close"] == False:
				openDays.append(day)

		workers = {}

		if location.type != "restaurant":
			owners = Owner.query.filter(Owner.info.like("%\"locationId\": \"" + str(locationid) + "\"%")).all()
			for owner in owners:
				hours = json.loads(owner.hours)

				for time in hours:
					if hours[time]["working"] == True or hours[time]["takeShift"] != "":
						if hours[time]["working"] == True:
							if time not in workers:
								workers[time] = [{
									"workerId": owner.id,
									"start": hours[time]["opentime"]["hour"] + ":" + hours[time]["opentime"]["minute"],
									"end": hours[time]["closetime"]["hour"] + ":" + hours[time]["closetime"]["minute"]
								}]
							else:
								workers[time].append({
									"workerId": owner.id,
									"start": hours[time]["opentime"]["hour"] + ":" + hours[time]["opentime"]["minute"],
									"end": hours[time]["closetime"]["hour"] + ":" + hours[time]["closetime"]["minute"]
								})
						else:
							if hours[time]["takeShift"] != "":
								coworker = Owner.query.filter_by(id=hours[time]["takeShift"]).first()
								coworkerHours = json.loads(coworker.hours)

								if time not in workers:
									workers[time] = [{
										"workerId": owner.id,
										"start": coworkerHours[time]["opentime"]["hour"] + ":" + coworkerHours[time]["opentime"]["minute"],
										"end": coworkerHours[time]["closetime"]["hour"] + ":" + coworkerHours[time]["closetime"]["minute"]
									}]
								else:
									workers[time].append({
										"workerId": owner.id,
										"start": coworkerHours[time]["opentime"]["hour"] + ":" + coworkerHours[time]["opentime"]["minute"],
										"end": coworkerHours[time]["closetime"]["hour"] + ":" + coworkerHours[time]["closetime"]["minute"]
									})

		return { "openTime": openTime, "closeTime": closeTime, "scheduled": times, "openDays": openDays, "workers": workers }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
