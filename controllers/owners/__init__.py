from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_owners", methods=["GET"])
def welcome_owners():
	return { "msg": "welcome to owners of easygo" }

@app.route("/owner_login", methods=["POST"])
def owner_login():
	content = request.get_json()

	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['password']
	errormsg = ""
	status = ""

	if cellnumber != "" and password != "":
		owner = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True).fetchone()

		if owner != None:
			if check_password_hash(owner['password'], password):
				ownerid = owner['id']
				ownerhours = owner['hours']
				ownerInfo = json.loads(owner['info'])
				ownerInfo["signin"] = True

				numBusiness = query("select count(*) as num from location where owners like '%\"" + str(ownerid) + "\"%'", True).fetchone()["num"]

				if numBusiness > 0:
					location = query("select * from location where owners like '%\"" + str(ownerid) + "\"%'", True).fetchone()
					locationid = location['id']
					locationtype = location['type']
					locationhours = location['hours']

					query("update owner set info = '" + str(json.dumps(ownerInfo)) + "' where id = " + str(owner['id']))
					
					if locationhours != '{}' and ownerhours != '{}':
						if numBusiness > 1:
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": locationtype, "msg": "list" }
						else:
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": locationtype, "msg": "main" }
					else:
						if locationhours == '{}': # location setup not done
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": "", "msg": "locationsetup" }
						else:
							if locationtype == 'hair' or locationtype == 'nail':
								return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": locationtype, "msg": "register" }
							else:
								if numBusiness > 1:
									return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": locationtype, "msg": "list" }
								else:
									return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": locationtype, "msg": "main" }
				else:
					return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": None, "locationtype": "", "msg": "locationsetup" }
			else:
				errormsg = "Password is incorrect"
		else:
			errormsg = "Account doesn't exist"
			status = "nonexist"
	else:
		if cellnumber == "":
			errormsg = "Phone number is blank"
		else:
			errormsg = "Password is blank"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/owner_logout/<id>")
def owner_logout(id):
	owner = query("select * from owner where id = " + str(id), True).fetchone()
	update_data = []

	errormsg = ""
	status = ""

	if owner != None:
		info = json.loads(owner["info"])
		info["signin"] = False

		query("update owner set info = '" + json.dumps(info) + "' where id = " + str(id))

		return { "msg": "success" }
	else:
		errormsg = "Account doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/owner_verify/<cellnumber>")
def owner_verify(cellnumber):
	verifycode = getRanStr()

	cellnumber = cellnumber.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	owner = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True).fetchone()
	errormsg = ""
	status = ""

	if owner == None:
		if test_sms == False:
			try:
				message = client.messages.create(
					body='Verify code: ' + str(verifycode),
					messaging_service_sid=mss,
					to='+1' + str(cellnumber)
				)
			except:
				print("could not verify: " + str(cellnumber))

		return { "verifycode": verifycode }
	else:
		errormsg = "Cell number already used"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/owner_register", methods=["POST"])
def owner_register():
	content = request.get_json()

	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['password']
	confirmPassword = content['confirmPassword']
	errormsg = ""
	status = ""

	if cellnumber == "":
		errormsg = "Cell number is blank"
	else:
		num_existing_cellnumber = query("select count(*) as num from owner where cellnumber = '" + str(cellnumber) + "'", True).fetchone()["num"]

		if num_existing_cellnumber > 0:
			errormsg = "Account already exist"

	if password != "" and confirmPassword != "":
		if len(password) >= 6:
			if password != confirmPassword:
				errormsg = "Password is mismatch"
		else:
			errormsg = "Password needs to be atleast 6 characters long"
	else:
		if password == "":
			errormsg = "Password is blank"
		else:
			errormsg = "Please confirm your password"

	if errormsg == "":
		data = {
			"cellnumber": cellnumber,
			"password": generate_password_hash(password),
			"username": "",
			"profile": "{}",
			"hours": "{}",
			"info": json.dumps({ "pushToken": "", "owner": True, "signin": False })
		}

		insert_data = []
		columns = []
		for key in data:
			columns.append(key)
			insert_data.append("'" + data[key] + "'")

		id = query("insert into owner (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

		return { "id": id }

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/save_user_info", methods=["POST"])
def save_user_info():
	id = request.form['id']
	username = request.form['username']
	hours = request.form['hours']
	errormsg = ""
	status = ""

	owner = query("select * from owner where id = " + str(id), True).fetchone()
	update_data = []

	if username == "":
		errormsg = "Please provide a username for identification"

	isWeb = request.form.get("web")

	new_profile = json.dumps({"name": "", "width": 360, "height": 360})

	if isWeb != None:
		profile = json.loads(request.form['profile'])
		name = profile['name']

		if name != "":
			uri = profile['uri'].split(",")[1]
			size = profile['size']

			writeToFile(uri, name)

			new_profile = json.dumps({"name": name, "width": int(size["width"]), "height": int(size["height"])})			
	else:
		profilepath = request.files.get('profile', False)
		profileexist = False if profilepath == False else True

		if profileexist == True:
			profile = request.files['profile']
			imagename = profile.filename

			size = json.loads(request.form['size'])

			profile.save(os.path.join('static', imagename))
			new_profile = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
	
	if errormsg == "":
		update_data.append("username = '" + username + "'")
		update_data.append("hours = '" + hours + "'")
		update_data.append("profile = '" + new_profile + "'")

		query("update owner set " + ", ".join(update_data) + " where id = " + str(owner["id"]))

		return { "msg": "success" }

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_owner", methods=["POST"])
def add_owner():
	id = request.form['id']
	cellnumber = request.form['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	username = request.form['username']
	password = request.form['password']
	confirmPassword = request.form['confirmPassword']
	hours = request.form['hours']

	owner = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True).fetchone()
	errormsg = ""
	status = ""

	location = query("select * from location where id = " + str(id), True).fetchone()
	cellnumber_exist = query("select count(*) as num from owner where cellnumber = '" + str(cellnumber) + "'", True).fetchone()["num"]

	if owner == None:
		if username == "":
			errormsg = "Please provide a username for identification"

		if cellnumber == "":
			errormsg = "Cell number is blank"
		else:
			if cellnumber_exist > 0:
				errormsg = "Cell number already used"

		if password != "" and confirmPassword != "":
			if len(password) >= 6:
				if password != confirmPassword:
					errormsg = "Password is mismatch"
			else:
				errormsg = "Password needs to be atleast 6 characters long"
		else:
			if password == "":
				errormsg = "Please enter a password"
			else:
				errormsg = "Please confirm your password"

		isWeb = request.form.get("web")
		profileData = json.dumps({"name": "", "width": 360, "height": 360})

		if isWeb != None:
			profile = json.loads(request.form['profile'])
			imagename = profile['name']

			if imagename != "":
				uri = profile['uri'].split(",")[1]
				size = profile['size']

				writeToFile(uri, imagename)

				profileData = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
		else:
			profilepath = request.files.get('profile', False)
			profileexist = False if profilepath == False else True

			if profileexist == True:
				profile = request.files['profile']
				imagename = profile.filename

				size = json.loads(request.form['size'])
				
				profile.save(os.path.join('static', imagename))
				profileData = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})

		if errormsg == "":
			data = {
				"cellnumber": cellnumber,
				"password": generate_password_hash(password),
				"username": username,
				"profile": profileData,
				"hours": hours,
				"info": json.dumps({"pushToken": "", "owner": False, "signin": False})
			}

			insert_data = []
			columns = []
			for key in data:
				columns.append(key)
				insert_data.append("'" + str(data[key]) + "'")

			ownerid = query("insert into owner (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

			owners = json.loads(location["owners"])
			owners.append(str(ownerid))

			query("update location set owners = '" + json.dumps(owners) + "' where id = " + str(location["id"]))

			return { "id": ownerid, "msg": "New owner added by an owner" }
	else:
		errormsg = "Owner already exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_owner", methods=["POST"])
def update_owner():
	ownerid = request.form['ownerid']
	type = request.form['type']

	owner = query("select * from owner where id = " + str(ownerid), True).fetchone()

	errormsg = ""
	status = ""
	new_data = {}

	if owner != None:
		if type == "cellnumber":
			cellnumber = request.form['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")

			if cellnumber != "" and owner["cellnumber"] != cellnumber:
				existing_cellnumber = query("select count(*) as num from owner where cellnumber = '" + str(cellnumber) + "'", True).fetchone()["num"]

				if existing_cellnumber == 0:
					new_data["cellnumber"] = cellnumber
				else:
					errormsg = "This cell number is already taken"
					status = "samecellnumber"
		elif type == "username":
			username = request.form['username']

			if username != "" and owner["username"] != username:
				existing_username = query("select count(*) as num from owner where username = '" + username + "'", True).fetchone()["num"]

				if existing_username == 0:
					new_data["username"] = username
				else:
					errormsg = "The username is already taken"
					status = "sameusername"
		elif type == "profile":
			isWeb = request.form.get("web")
			oldprofile = json.loads(owner["profile"])

			if isWeb != None:
				profile = json.loads(request.form['profile'])
				imagename = profile['name']

				if imagename != '' and "data" in profile['uri']:
					uri = profile['uri'].split(",")[1]
					size = profile['size']

					if oldprofile["name"] != "" and os.path.exists("static/" + oldprofile["name"]):
						os.remove("static/" + oldprofile["name"])

					writeToFile(uri, imagename)

					new_data["profile"] = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
			else:
				profilepath = request.files.get('profile', False)
				profileexist = False if profilepath == False else True

				if profileexist == True:
					profile = request.files['profile']
					imagename = profile.filename

					size = json.loads(request.form['size'])

					if oldprofile["name"] != "" and os.path.exists("static/" + oldprofile["name"]):
						os.remove("static/" + oldprofile["name"])

					profile.save(os.path.join('static', imagename))

					new_data["profile"] = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
		elif type == "password":
			currentPassword = request.form['currentPassword']
			newPassword = request.form['newPassword']
			confirmPassword = request.form['confirmPassword']

			if check_password_hash(owner["password"], currentPassword):
				if newPassword != "" and confirmPassword != "":
					if newPassword != "" and confirmPassword != "":
						if len(newPassword) >= 6:
							if newPassword == confirmPassword:
								password = generate_password_hash(newPassword)

								new_data["password"] = password
							else:
								errormsg = "Password is mismatch"
						else:
							errormsg = "Password needs to be atleast 6 characters long"
					else:
						if newPassword == "":
							errormsg = "Please enter a password"
						else:
							errormsg = "Please confirm your password"
				else:
					if newPassword == "":
						errormsg = "New password is blank"
					else:
						errormsg = "Please confirm your new password"
			else:
				errormsg = "Current password is incorrect"
		elif type == "hours":
			hours = request.form['hours']

			if hours != "{}":
				new_data["hours"] = hours

		if errormsg == "":
			update_data = []
			for key in new_data:
				if key != "table":
					update_data.append(key + " = '" + new_data[key] + "'")

			query("update owner set " + ", ".join(update_data) + " where id = " + str(ownerid))

			return { "id": owner["id"], "msg": "Owner's info updated" }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/set_owner_hours", methods=["POST"])
def set_owner_hours():
	content = request.get_json()

	ownerid = content['ownerid']
	hours = content['hours']

	owner = query("select * from owner where id = " + str(ownerid), True).fetchone()

	if owner != None:
		query("update owner set hours = '" + json.dumps(hours) + "' where id = " + str(ownerid))

		return { "msg": "hours updated" }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }

@app.route("/update_owner_notification_token", methods=["POST"])
def update_owner_notification_token():
	content = request.get_json()

	ownerid = content['ownerid']
	token = content['token']

	owner = query("select * from owner where id = " + str(ownerid), True).fetchone()
	errormsg = ""
	status = ""

	if owner != None:
		ownerInfo = json.loads(owner["info"])
		ownerInfo["pushToken"] = token

		query("update owner set info = '" + str(json.dumps(ownerInfo)) + "' where id = " + str(ownerid))

		return { "msg": "Push token updated" }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_all_stylists/<id>")
def get_all_stylists(id):
	location = query("select * from location where id = " + str(id), True).fetchone()

	workers = "(" + location["owners"][1:-1] + ")"
	datas = query("select * from owner where id in " + workers, True).fetchall()

	owners = []
	row = []
	key = 0
	numWorkers = 0

	for data in datas:
		profile = json.loads(data["profile"])
		row.append({
			"key": "worker-" + str(key),
			"id": data["id"],
			"username": data["username"],
			"profile": profile if profile["name"] != "" else {"width": 360, "height": 360}
		})
		key += 1
		numWorkers += 1

		if len(row) >= 3:
			owners.append({ "key": str(len(owners)), "row": row })
			row = []

	if len(row) > 0:
		leftover = 3 - len(row)

		for k in range(leftover):
			row.append({ "key": "worker-" + str(key) })
			key += 1

		owners.append({ "key": str(len(owners)), "row": row })

	return { "msg": "get workers", "owners": owners, "numWorkers": numWorkers }

@app.route("/get_workers_hour", methods=["POST"])
def get_workers_hour():
	content = request.get_json()
	errormsg = ""
	status = ""

	locationid = content['locationid']
	ownerid = content['ownerid']

	location = query("select * from location where id = " + str(locationid), True).fetchone()

	if location != None:
		if ownerid == None: # get all workers
			owners = "(" + location["owners"][1:-1] + ")"

			datas = query("select * from owner where id in " + owners, True).fetchall()
			owners = {}

			for data in datas:
				scheduledDatas = query("select id, time from schedule where workerId = " + str(data["id"]), True).fetchall()
				scheduled = {}

				for scheduledData in scheduledDatas:
					scheduled[scheduledData["time"]] = scheduledData["id"]

				hours = json.loads(data['hours'])
				profile = json.loads(data["profile"])

				hoursData = {
					"scheduled": scheduled,
					"profileInfo": {
						"username": data["username"],
						"profile": profile if profile["name"] != "" else {"width": 360, "height": 360},
					}
				}

				for day in hours:
					openTime = hours[day]["opentime"]["hour"] + ":" + hours[day]["opentime"]["minute"]
					openTime = { 
						"hour": hours[day]["opentime"]["hour"], 
						"minute": hours[day]["opentime"]["minute"]
					}
					closeTime = {
						"hour": hours[day]["closetime"]["hour"], 
						"minute": hours[day]["closetime"]["minute"]
					}

					hoursData[day] = {
						"open": openTime,
						"close": closeTime,
						"working": hours[day]["working"],
						"takeShift": hours[day]["takeShift"]
					}

				owners[data["id"]] = hoursData

			return { "workersHour": owners }
		else: # get only one worker
			data = query("select * from owner where id = " + str(ownerid), True).fetchone()

			if data != None:
				scheduledDatas = query("select id, time from schedule where workerId = " + str(ownerid), True).fetchall()
				scheduled = {}

				for scheduledData in scheduledDatas:
					scheduled[scheduledData["time"]] = scheduledData["id"]

				hours = json.loads(data['hours'])
				hoursData = {
					"scheduled": scheduled,
					"profileInfo": {
						"username": data["username"],
						"profile": profile if profile["name"] != "" else {"width": 360, "height": 360},
					}
				}

				for day in hours:
					openTime = hours[day]["opentime"]["hour"] + ":" + hours[day]["opentime"]["minute"]
					closeTime = hours[day]["closetime"]["hour"] + ":" + hours[day]["closetime"]["minute"]

					hoursData[day] = {
						"open": openTime,
						"close": closeTime,
						"working": hours[day]["working"],
						"takeShift": hours[day]["takeShift"]
					}

				return { "workerHour": hoursData }
			else:
				errormsg = "Worker doesn't exist"
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_workers/<id>")
def get_workers(id):
	location = query("select * from location where id = " + str(id), True).fetchone()

	workers = "(" + location["owners"][1:-1] + ")"
	datas = query("select * from owner where id in " + workers, True).fetchall()

	owners = []
	row = []
	key = 0
	numWorkers = 0

	for data in datas:
		profile = json.loads(data["profile"])
		row.append({
			"key": "worker-" + str(key),
			"id": data["id"],
			"username": data["username"],
			"profile": profile if profile["name"] != "" else {"width": 360, "height": 360}
		})
		key += 1
		numWorkers += 1

		if len(row) >= 3:
			owners.append({ "key": str(len(owners)), "row": row })
			row = []

	if len(row) > 0:
		leftover = 3 - len(row)

		for k in range(leftover):
			row.append({ "key": "worker-" + str(key) })
			key += 1

		owners.append({ "key": str(len(owners)), "row": row })

	return { "msg": "get workers", "owners": owners, "numWorkers": numWorkers }
	
@app.route("/get_stylist_info/<id>")
def get_stylist_info(id):
	owner = query("select * from owner where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""
	daysArr = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

	if owner != None:
		hours = json.loads(owner["hours"])
		days = {}

		for time in hours:
			if hours[time]["working"] == True or hours[time]["takeShift"] != "":
				if hours[time]["working"] == True:
					days[time] = {
						"start": hours[time]["opentime"]["hour"] + ":" + hours[time]["opentime"]["minute"],
						"end": hours[time]["closetime"]["hour"] + ":" + hours[time]["closetime"]["minute"]
					}
				else:
					if hours[time]["takeShift"] != "":
						coworker = query("select * from owner where id = " + str(hours[time]["takeShift"]), True).fetchone()
						coworkerHours = json.loads(coworker["hours"])

						days[time] = {
							"start": coworkerHours[time]["opentime"]["hour"] + ":" + coworkerHours[time]["opentime"]["minute"],
							"end": coworkerHours[time]["closetime"]["hour"] + ":" + coworkerHours[time]["closetime"]["minute"]
						}

		profile = json.loads(owner["profile"])
		info = {
			"username": owner["username"],
			"profile": profile if profile["name"] != "" else {"width": 360, "height": 360},
			"days": days
		}

		return info
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_all_workers_time/<id>")
def get_all_workers_time(id):
	location = query("select * from location where id = " + str(id), True).fetchone()

	workers = "(" + location["owners"][1:-1] + ")"
	owners = query("select * from owner where id in " + workers, True).fetchall()
	workers = {}

	for owner in owners:
		hours = json.loads(owner["hours"])

		for time in hours:
			if hours[time]["working"] == True or hours[time]["takeShift"] != "":
				if hours[time]["working"] == True:
					if time not in workers:
						workers[time] = [{
							"workerId": owner["id"],
							"start": hours[time]["opentime"]["hour"] + ":" + hours[time]["opentime"]["minute"],
							"end": hours[time]["closetime"]["hour"] + ":" + hours[time]["closetime"]["minute"]
						}]
					else:
						workers[time].append({
							"workerId": owner["id"],
							"start": hours[time]["opentime"]["hour"] + ":" + hours[time]["opentime"]["minute"],
							"end": hours[time]["closetime"]["hour"] + ":" + hours[time]["closetime"]["minute"]
						})
				else:
					if hours[time]["takeShift"] != "":
						coworker = query("select * from id = " + str(hours[time]["takeShift"]), True).fetchone()
						coworkerHours = json.loads(coworker["hours"])

						if time not in workers:
							workers[time] = [{
								"workerId": owner["id"],
								"start": coworkerHours[time]["opentime"]["hour"] + ":" + coworkerHours[time]["opentime"]["minute"],
								"end": coworkerHours[time]["closetime"]["hour"] + ":" + coworkerHours[time]["closetime"]["minute"]
							}]
						else:
							workers[time].append({
								"workerId": owner["id"],
								"start": coworkerHours[time]["opentime"]["hour"] + ":" + coworkerHours[time]["opentime"]["minute"],
								"end": coworkerHours[time]["closetime"]["hour"] + ":" + coworkerHours[time]["closetime"]["minute"]
							})

	return { "workers": workers }

@app.route("/search_workers", methods=["POST"])
def search_workers():
	content = request.get_json()

	scheduleid = content['scheduleid']
	username = content['username']

	schedule = query("select * from schedule where id = " + str(scheduleid), True).fetchone()
	location = query("select * from location where id = " + str(schedule.locationId), True).fetchone()

	errormsg = ""
	status = ""

	if schedule != None:
		workers = "(" + location["owners"][1:-1] + ")"
		datas = query("select * from owner where username like '%" + username + "%' and id in " + workers, True).fetchall()
		owners = []
		row = []
		key = 0

		for data in datas:
			profile = json.loads(data["profile"])
			row.append({
				"key": "worker-" + str(key),
				"id": data['id'],
				"username": data['username'],
				"profile": profile if profile["name"] != "" else {"width": 360, "height": 360},
				"selected": False
			})
			key += 1

			if len(row) == 3:
				owners.append({ "key": str(len(owners)), "row": row })
				row = []

		if len(row) > 0 and len(row) < 3:
			leftover = 3 - len(row)

			for k in range(leftover):
				row.append({ "key": "worker-" + str(key) })
				key += 1

			owners.append({ "key": str(len(owners)), "row": row })

		return { "msg": "get searched workers", "owners": owners }
	else:
		errormsg = "Schedule doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_workers_time/<id>") # salon profile
def get_workers_time(id):
	location = query("select * from location where id = " + str(id), True).fetchone()

	day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

	workers = "(" + location["owners"][1:-1] + ")"
	owners = query("select * from owner where id in " + workers, True).fetchall()
	workerHours = []

	for owner in owners:
		hours = [
			{ "key": "0", "header": "Sunday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "1", "header": "Monday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "2", "header": "Tuesday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "3", "header": "Wednesday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "4", "header": "Thursday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "5", "header": "Friday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "6", "header": "Saturday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" }
		]

		data = json.loads(owner["hours"])

		for k, info in enumerate(hours):
			openhour = int(data[day[k][:3]]["opentime"]["hour"])
			closehour = int(data[day[k][:3]]["closetime"]["hour"])
			working = data[day[k][:3]]["working"]

			openperiod = "PM" if openhour >= 12 else "AM"
			openhour = int(openhour)

			if openhour == 0:
				openhour = 12
			elif openhour > 12:
				openhour -= 12

			openhour = "0" + str(openhour) if openhour < 10 else str(openhour)

			closeperiod = "PM" if closehour >= 12 else "AM"
			closehour = int(closehour)

			if closehour == 0:
				closehour = 12
			elif closehour > 12:
				closehour -= 12

			closehour = "0" + str(closehour) if closehour < 10 else str(closehour)

			info["opentime"]["hour"] = int(openhour)
			info["opentime"]["minute"] = data[day[k][:3]]["opentime"]["minute"]
			info["opentime"]["period"] = openperiod

			info["closetime"]["hour"] = int(closehour)
			info["closetime"]["minute"] = data[day[k][:3]]["closetime"]["minute"]
			info["closetime"]["period"] = closeperiod
			info["working"] = working

			hours[k] = info

		profile = json.loads(owner["profile"])
		workerHours.append({ 
			"key": str(owner["id"]),
			"day": info["header"],
			"name": owner["username"],
			"profile": profile if profile["name"] != "" else {"width": 360, "height": 360},
			"hours": hours
		})

	return { "workers": workerHours }

@app.route("/get_other_workers", methods=["POST"])
def get_other_workers():
	content = request.get_json()
	errormsg = ""
	status = ""

	ownerid = content['ownerid']
	locationid = content['locationid']
	day = content['day']

	location = query("select * from location where id = " + str(locationid), True).fetchone()
	
	if location != None:
		workers = "(" + location["owners"][1:-1] + ")"
		owners = query("select * from owner where id in " + workers + " and not id = " + str(ownerid), True).fetchall()
		workers = []
		row = []
		rownum = 0

		for owner in owners:
			hours = json.loads(owner["hours"])
			hours = hours[day]

			if hours["working"] == True and hours["takeShift"] == "":
				profile = json.loads(owner["profile"])
				row.append({ "key": str(rownum), "id": owner["id"], "username": owner["username"], "profile": profile if profile["name"] != "" else {"width": 360, "height": 360 } })
				rownum += 1

				if len(row) == 3:
					workers.append({ "key": "worker-" + str(len(workers)), "row": row })
					row = []

		if len(row) > 0:
			leftover = 3 - len(row)

			for k in range(leftover):
				row.append({ "key": str(rownum) })
				rownum += 1

			workers.append({ "key": "worker-" + str(len(workers)), "row": row })

		return { "workers": workers }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/delete_owner/<id>")
def delete_owner(id):
	owner = query("select * from owner where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if owner != None:
		info = json.loads(owner["info"])

		location = query("select * from location where id = " + str(info["locationId"]), True).fetchone()
		owners = json.loads(location["owners"])

		if str(id) in owners:
			owners.remove(str(id))

			location.owners = json.dumps(owners)

		query("delete from owner where id = " + str(id))

		return { "msg": "Owner deleted" }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }

@app.route("/get_owner_info/<id>")
def get_owner_info(id):
	owner = query("select * from owner where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	if owner != None:
		ownerInfo = json.loads(owner["info"])

		info = { "id": id, "isOwner": ownerInfo["owner"] }

		return info
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }

@app.route("/get_accounts/<id>")
def get_accounts(id):
	errormsg = ""
	status = ""

	location = query("select * from location where id = " + str(id), True).fetchone()

	if location != None:
		owners = json.loads(location["owners"])
		locationHours = json.loads(location["hours"])
		accounts = []

		for owner in owners:
			ownerInfo = query("select * from owner where id = " + str(owner), True).fetchone()

			hours = [
				{ "key": "0", "header": "Sunday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
				{ "key": "1", "header": "Monday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
				{ "key": "2", "header": "Tuesday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
				{ "key": "3", "header": "Wednesday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
				{ "key": "4", "header": "Thursday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
				{ "key": "5", "header": "Friday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
				{ "key": "6", "header": "Saturday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" }
			]

			if "Sun" in ownerInfo["hours"]:
				data = json.loads(ownerInfo["hours"])
				day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

				for k, info in enumerate(hours):
					if data[day[k][:3]]["takeShift"] != "":
						worker = query("select * from owner where id = " + str(data[day[k][:3]]["takeShift"]), True).fetchone()

						info["takeShift"] = { "id": worker["id"], "name": worker["username"] }

						workerHours = json.loads(worker["hours"])
						hoursInfo = workerHours[day[k][:3]]
					else:
						info["takeShift"] = ""

						hoursInfo = data[day[k][:3]]

					openhour = int(hoursInfo["opentime"]["hour"])
					closehour = int(hoursInfo["closetime"]["hour"])

					openperiod = "PM" if openhour >= 12 else "AM"
					openhour = int(openhour)

					if openhour == 0:
						openhour = 12
					elif openhour > 12:
						openhour -= 12

					openhour = "0" + str(openhour) if openhour < 10 else str(openhour)

					closeperiod = "PM" if closehour >= 12 else "AM"
					closehour = int(closehour)

					if closehour == 0:
						closehour = 12
					elif closehour > 12:
						closehour -= 12
						
					closehour = "0" + str(closehour) if closehour < 10 else str(closehour)

					info["opentime"]["hour"] = openhour
					info["opentime"]["minute"] = hoursInfo["opentime"]["minute"]
					info["opentime"]["period"] = openperiod

					info["closetime"]["hour"] = closehour
					info["closetime"]["minute"] = hoursInfo["closetime"]["minute"]
					info["closetime"]["period"] = closeperiod
					info["working"] = hoursInfo["working"]
					info["close"] = locationHours[day[k][:3]]["close"]

					hours[k] = info
			else:
				hours = []

			cellnumber = ownerInfo["cellnumber"]

			f3 = str(cellnumber[0:3])
			s3 = str(cellnumber[3:6])
			l4 = str(cellnumber[6:len(cellnumber)])

			cellnumber = "(" + f3 + ") " + s3 + "-" + l4

			profile = json.loads(ownerInfo["profile"])
			accounts.append({
				"key": "account-" + str(owner), 
				"id": owner, 
				"cellnumber": cellnumber,
				"username": ownerInfo["username"],
				"profile": profile if profile["name"] != "" else {"width": 360, "height": 360},
				"hours": hours
			})

		return { "accounts": accounts }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }

@app.route("/get_reset_code/<cellnumber>")
def get_owner_reset_code(cellnumber):
	cellnumber = cellnumber.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	owner = query("select * from owner where cellnumber = " + str(cellnumber), True).fetchone()
	errormsg = ""
	status = ""

	if owner != None:
		code = getRanStr()

		if test_sms == False:
			message = client.messages.create(
				body="Your EasyGO reset code is " + code,
				messaging_service_sid=mss,
				to='+1' + str(owner["cellnumber"])
			)

		return { "msg": "Reset code sent", "code": code }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/reset_password", methods=["POST"])
def owner_reset_password():
	content = request.get_json()

	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['newPassword']
	confirmPassword = content['confirmPassword']

	owner = query("select * from owner where cellnumber = " + str(cellnumber), True).fetchone()
	errormsg = ""
	status = ""

	if owner != None:
		if password != '' and confirmPassword != '':
			if len(password) >= 6:
				if password == confirmPassword:
					password = generate_password_hash(password)

					query("update owner set password = " + str(password) + " where id = " + str(cellnumber))

					ownerid = owner["id"]

					numLocations = query("select count(*) as num from location where owners like '%\"" + str(ownerid) + "\"%'", True).fetchone()["num"]

					if numLocations == 0:
						return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": "", "locationtype": "", "msg": "setup" }
					else:
						data = data[0]

						if data['type'] != "":
							if data['hours'] != "":
								return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": data['id'], "locationtype": data['type'], "msg": "main" }
							else:
								return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": data['id'], "locationtype": data['type'], "msg": "setuphours" }
						else:
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": data['id'], "locationtype": "", "msg": "typesetup" }
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
