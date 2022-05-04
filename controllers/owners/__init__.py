from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import pymysql.cursors, json, os, time
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from binascii import a2b_base64
from random import randint
from datetime import datetime
from info import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + user + ':' + password + '@' + host + '/' + database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MYSQL_HOST'] = host
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = database

db = SQLAlchemy(app)
migrate = Migrate(app, db)
cors = CORS(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(10), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	info = db.Column(db.String(155))

	def __init__(self, cellnumber, password, username, info):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.info = info

	def __repr__(self):
		return '<User %r>' % self.cellnumber

class Owner(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(15), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	profile = db.Column(db.String(60))
	hours = db.Column(db.Text)
	info = db.Column(db.String(120))

	def __init__(self, cellnumber, password, username, profile, hours, info):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.profile = profile
		self.hours = hours
		self.info = info

	def __repr__(self):
		return '<Owner %r>' % self.cellnumber

class Location(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	addressOne = db.Column(db.String(50))
	addressTwo = db.Column(db.String(50))
	city = db.Column(db.String(50))
	province = db.Column(db.String(50))
	postalcode = db.Column(db.String(7))
	phonenumber = db.Column(db.String(10), unique=True)
	logo = db.Column(db.String(60))
	longitude = db.Column(db.String(20))
	latitude = db.Column(db.String(20))
	owners = db.Column(db.Text)
	type = db.Column(db.String(20))
	hours = db.Column(db.Text)
	info = db.Column(db.Text)

	def __init__(
		self, 
		name, addressOne, addressTwo, city, province, postalcode, phonenumber, logo, 
		longitude, latitude, owners, type, hours, info
	):
		self.name = name
		self.addressOne = addressOne
		self.addressTwo = addressTwo
		self.city = city
		self.province = province
		self.postalcode = postalcode
		self.phonenumber = phonenumber
		self.logo = logo
		self.longitude = longitude
		self.latitude = latitude
		self.owners = owners
		self.type = type
		self.hours = hours
		self.info = info

	def __repr__(self):
		return '<Location %r>' % self.name

class Menu(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	parentMenuId = db.Column(db.Text)
	name = db.Column(db.String(20))
	image = db.Column(db.String(60))

	def __init__(self, locationId, parentMenuId, name, image):
		self.locationId = locationId
		self.parentMenuId = parentMenuId
		self.name = name
		self.image = image

	def __repr__(self):
		return '<Menu %r>' % self.name

class Service(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	name = db.Column(db.String(20))
	image = db.Column(db.String(60))
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.image = image
		self.price = price

	def __repr__(self):
		return '<Service %r>' % self.name

class Schedule(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userId = db.Column(db.Integer)
	workerId = db.Column(db.Integer)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	serviceId = db.Column(db.Integer)
	userInput = db.Column(db.Text)
	time = db.Column(db.String(15))
	status = db.Column(db.String(10))
	cancelReason = db.Column(db.String(200))
	nextTime = db.Column(db.String(15))
	locationType = db.Column(db.String(15))
	customers = db.Column(db.Text)
	note = db.Column(db.String(225))
	orders = db.Column(db.Text)
	table = db.Column(db.String(20))
	info = db.Column(db.String(100))

	def __init__(self, userId, workerId, locationId, menuId, serviceId, userInput, time, status, cancelReason, nextTime, locationType, customers, note, orders, table, info):
		self.userId = userId
		self.workerId = workerId
		self.locationId = locationId
		self.menuId = menuId
		self.serviceId = serviceId
		self.userInput = userInput
		self.time = time
		self.status = status
		self.cancelReason = cancelReason
		self.nextTime = nextTime
		self.locationType = locationType
		self.customers = customers
		self.note = note
		self.orders = orders
		self.table = table
		self.info = info

	def __repr__(self):
		return '<Appointment %r>' % self.time

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	name = db.Column(db.String(20))
	image = db.Column(db.String(60))
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(150))
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, image, options, others, sizes, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.image = image
		self.options = options
		self.others = others
		self.sizes = sizes
		self.price = price

	def __repr__(self):
		return '<Product %r>' % self.name

class Cart(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	productId = db.Column(db.Integer)
	userInput = db.Column(db.Text)
	quantity = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(225))
	note = db.Column(db.String(100))
	status = db.Column(db.String(10))
	orderNumber = db.Column(db.String(10))
	waitTime = db.Column(db.String(2))

	def __init__(self, locationId, productId, userInput, quantity, adder, options, others, sizes, note, status, orderNumber, waitTime):
		self.locationId = locationId
		self.productId = productId
		self.userInput = userInput
		self.quantity = quantity
		self.adder = adder
		self.options = options
		self.others = others
		self.sizes = sizes
		self.note = note
		self.status = status
		self.orderNumber = orderNumber
		self.waitTime = waitTime

	def __repr__(self):
		return '<Cart %r>' % self.productId

def query(sql, output):
	dbconn = pymysql.connect(
		host=host, user=user,
		password=password, db=database,
		charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor, 
		autocommit=True
	)

	cursorobj = dbconn.cursor()
	cursorobj.execute(sql)

	if output == True:
		results = cursorobj.fetchall()

		return results

def writeToFile(uri, name):
	binary_data = a2b_base64(uri)

	fd = open(os.path.join("static", name), 'wb')
	fd.write(binary_data)
	fd.close()

def getRanStr():
	strid = ""

	for k in range(6):
		strid += str(randint(0, 9))

	return strid

def pushInfo(to, title, body, data):
	return PushMessage(to=to, title=title, body=body, data=data)

def push(messages):
	if type(messages) == type([]):
		resp = PushClient().publish_multiple(messages)

		for info in resp:
			if info.status != "ok":
				return { "status": "failed" }
	else:
		resp = PushClient().publish(messages)

		if resp.status != "ok":
			return { "status": "failed" }

	return { "status": "ok" }

@app.route("/welcome_owners", methods=["GET"])
def welcome_owners():
	datas = Owner.query.all()
	owners = []

	for data in datas:
		owners.append(data.id)

	return { "msg": "welcome to owners of easygo", "owners": owners }

@app.route("/login", methods=["POST"])
def owner_login():
	content = request.get_json()

	cellnumber = content['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = content['password']
	errormsg = ""
	status = ""

	if cellnumber != "" and password != "":
		data = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True)

		if len(data) > 0:
			owner = data[0]

			if check_password_hash(owner['password'], password):
				ownerid = owner['id']
				ownerhours = owner['hours']

				data = query("select * from location where owners like '%\"" + str(ownerid) + "\"%'", True)

				if len(data) == 1:
					location = data[0]
					locationid = location['id']
					locationtype = location['type']
					locationhours = location['hours']

					if locationhours != '{}' and ownerhours != '{}':
						return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": locationtype, "msg": "main" }
					else:
						if locationhours == '{}': # location setup not done
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": "", "msg": "locationsetup" }
						else:
							if locationtype == 'hair' or locationtype == 'nail':
								return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": locationtype, "msg": "register" }
							else:
								return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": locationtype, "msg": "main" }
				else:
					return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": None, "locationtype": "", "msg": "locationsetup" }
			else:
				errormsg = "Password is incorrect"
		else:
			errormsg = "Owner doesn't exist"
	else:
		if cellnumber == "":
			errormsg = "Phone number is blank"
		else:
			errormsg = "Password is blank"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/verify/<cellnumber>")
def owner_verify(cellnumber):
	verifycode = getRanStr()

	cellnumber = cellnumber.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	owner = Owner.query.filter_by(cellnumber=cellnumber).first()
	errormsg = ""
	status = ""

	if owner == None:
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

@app.route("/register", methods=["POST"])
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
		data = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True)

		if len(data) > 0:
			errormsg = "Owner already exist"

	if password != "" and confirmPassword != "":
		if len(password) >= 6:
			if password != confirmPassword:
				errormsg = "Password is mismatch"
		else:
			errormsg = "Password needs to be atleast 6 characters long"
	else:
		if password == "":
			errormsg = "Passwod is blank"
		else:
			errormsg = "Please confirm your password"

	if errormsg == "":
		info = json.dumps({ "locationId": "", "pushToken": "" })
		owner = Owner(cellnumber, generate_password_hash(password), "", "", '{}', info)
		db.session.add(owner)
		db.session.commit()

		return { "id": owner.id }

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/save_user_info", methods=["POST"])
def save_user_info():
	id = request.form['id']
	username = request.form['username']
	errormsg = ""
	status = ""

	owner = Owner.query.filter_by(id=id).first()

	if username == "":
		errormsg = "Please provide a username for identification"

	isWeb = request.form.get("web")

	if isWeb != None:
		profile = json.loads(request.form['profile'])
		name = profile['name']

		if name != "":
			uri = profile['uri'].split(",")[1]
			size = profile['size']

			writeToFile(uri, name)

			owner.profile = json.dumps({"name": name, "width": int(size["width"]), "height": int(size["height"])})
	else:
		profilepath = request.files.get('profile', False)
		profileexist = False if profilepath == False else True

		if profileexist == True:
			profile = request.files['profile']
			imagename = profile.filename

			size = json.loads(request.form['size'])

			profile.save(os.path.join('static', imagename))
			owner.profile = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
	
	if errormsg == "":
		owner.username = username

		db.session.commit()

		return { "msg": "success" }

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_owner", methods=["POST"])
def add_owner():
	ownerid = request.form['ownerid']
	cellnumber = request.form['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	username = request.form['username']
	password = request.form['password']
	confirmPassword = request.form['confirmPassword']
	hours = request.form['hours']

	data = query("select * from owner where cellnumber = '" + str(cellnumber) + "'", True)
	errormsg = ""
	status = ""

	if len(data) == 0:
		owner = Owner.query.filter_by(id=ownerid).first()

		if owner != None:
			if username == "":
				errormsg = "Please provide a username for identification"

			if cellnumber == "":
				errormsg = "Cell number is blank"

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
			profileData = json.dumps({"name": "", "width": 0, "height": 0})

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
				else:
					errormsg = "Please provide a profile for identification"

			if errormsg == "":
				ownerInfo = json.loads(owner.info)
				locationId = ownerInfo["locationId"] 

				password = generate_password_hash(password)
				owner = Owner(cellnumber, password, username, profileData, hours, json.dumps({"locationId": locationId, "pushToken": ""}))
				db.session.add(owner)
				db.session.commit()

				location = Location.query.filter_by(id=locationId).first()
				owners = json.loads(location.owners)
				owners.append(str(owner.id))

				location.owners = json.dumps(owners)

				db.session.commit()

				return { "id": owner.id, "msg": "New owner added by an owner" }
		else:
			errormsg = "Owner doesn't exist"
	else:
		errormsg = "Owner already exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_owner", methods=["POST"])
def update_owner():
	ownerid = request.form['ownerid']
	type = request.form['type']

	owner = Owner.query.filter_by(id=ownerid).first()
	errormsg = ""
	status = ""

	if owner != None:
		if type == "cellnumber":
			cellnumber = request.form['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")

			if cellnumber != "" and owner.cellnumber != cellnumber:
				exist_cellnumber = Owner.query.filter_by(cellnumber=cellnumber).count()

				if exist_cellnumber == 0:
					owner.cellnumber = cellnumber
				else:
					errormsg = "This cell number is already taken"
					status = "samecellnumber"
		elif type == "username":
			username = request.form['username']

			if username != "" and owner.username != username:
				exist_username = Owner.query.filter_by(username=username).count()

				if exist_username == 0:
					owner.username = username
				else:
					errormsg = "The username is already taken"
					status = "sameusername"
		elif type == "profile":
			isWeb = request.form.get("web")
			oldprofile = json.loads(owner.profile)

			if isWeb != None:
				profile = json.loads(request.form['profile'])
				imagename = profile['name']

				if imagename != '' and "data" in profile['uri']:
					uri = profile['uri'].split(",")[1]
					size = profile['size']

					if oldprofile["name"] != "" and os.path.exists("static/" + oldprofile["name"]):
						os.remove("static/" + oldprofile["name"])

					writeToFile(uri, imagename)

					newprofilename = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
					owner.profile = newprofilename
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

					newprofilename = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
					owner.profile = newprofilename
		elif type == "password":
			currentPassword = request.form['currentPassword']
			newPassword = request.form['newPassword']
			confirmPassword = request.form['confirmPassword']

			if check_password_hash(owner.password, currentPassword):
				if newPassword != "" and confirmPassword != "":
					if newPassword != "" and confirmPassword != "":
						if len(newPassword) >= 6:
							if newPassword == confirmPassword:
								password = generate_password_hash(newPassword)

								owner.password = password
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

			if hours != "[]":
				owner.hours = hours

		if errormsg == "":
			db.session.commit()

			return { "id": owner.id, "msg": "Owner's info updated" }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/set_hours", methods=["POST"])
def set_hours():
	content = request.get_json()

	ownerid = content['ownerid']
	hours = content['hours']

	owner = Owner.query.filter_by(id=ownerid).first()

	if owner != None:
		owner.hours = json.dumps(hours)

		db.session.commit()

		return { "msg": "hours updated" }
	else:
		errormsg = "Owner doesn't exist"

@app.route("/update_notification_token", methods=["POST"])
def owner_update_notification_token():
	content = request.get_json()

	ownerid = content['ownerid']
	token = content['token']

	owner = Owner.query.filter_by(id=ownerid).first()
	errormsg = ""
	status = ""

	if owner != None:
		ownerInfo = json.loads(owner.info)
		ownerInfo["pushToken"] = token

		owner.info = json.dumps(ownerInfo)

		db.session.commit()

		return { "msg": "Push token updated" }
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_workers/<id>")
def get_workers(id):
	datas = Owner.query.filter(Owner.info.like("%\"locationId\": \"" + str(id) + "\"%")).all()
	owners = []
	row = []
	key = 0
	numWorkers = 0

	for data in datas:
		row.append({
			"key": "worker-" + str(key),
			"id": data.id,
			"username": data.username,
			"profile": json.loads(data.profile)
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

@app.route("/get_worker_info/<id>")
def get_worker_info(id):
	owner = Owner.query.filter_by(id=id).first()
	errormsg = ""
	status = ""
	daysArr = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

	if owner != None:
		hours = json.loads(owner.hours)
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
						coworker = Owner.query.filter_by(id=hours[time]["takeShift"]).first()
						coworkerHours = json.loads(coworker.hours)

						days[time] = {
							"start": coworkerHours[time]["opentime"]["hour"] + ":" + coworkerHours[time]["opentime"]["minute"],
							"end": coworkerHours[time]["closetime"]["hour"] + ":" + coworkerHours[time]["closetime"]["minute"]
						}

		info = {
			"username": owner.username,
			"profile": json.loads(owner.profile),
			"days": days
		}

		return info
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_all_workers_time/<id>")
def get_all_workers_time(id):
	owners = Owner.query.filter(Owner.info.like("%\"locationId\": \"" + str(id) + "\"%")).all()
	workers = {}

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

	return { "workers": workers }

@app.route("/search_workers", methods=["POST"])
def search_workers():
	content = request.get_json()

	scheduleid = content['scheduleid']
	username = content['username']

	schedule = Schedule.query.filter_by(id=scheduleid).first()
	errormsg = ""
	status = ""

	if schedule != None:
		locationId = str(schedule.locationId)
		datas = query("select * from owner where username like '%" + username + "%' and info like '%\"locationId\": \"" + str(locationId) + "\"%'", True)
		owners = []
		row = []
		key = 0

		for data in datas:
			row.append({
				"key": "worker-" + str(key),
				"id": data['id'],
				"username": data['username'],
				"profile": data["profile"],
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
	owners = Owner.query.filter(Owner.info.like("%\"locationId\": \"" + str(id) + "\"%")).all()
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

		data = json.loads(owner.hours)
		day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

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

		workerHours.append({ 
			"key": str(owner.id),
			"day": info["header"],
			"name": owner.username,
			"profile": json.loads(owner.profile),
			"hours": hours
		})

	return { "workerHours": workerHours }

@app.route("/get_other_workers", methods=["POST"])
def get_other_workers():
	content = request.get_json()
	errormsg = ""
	status = ""

	ownerid = content['ownerid']
	locationid = content['locationid']
	day = content['day']

	location = Location.query.filter_by(id=locationid).first()
	
	if location != None:
		owners = Owner.query.filter(Owner.info.like("%\"locationId\": \"" + str(locationid) + "\"%"), Owner.id!=ownerid).all()
		workers = []
		row = []
		rownum = 0

		for owner in owners:
			hours = json.loads(owner.hours)

			for time in hours:
				if time == day:
					if hours[time]["working"] == False and hours[time]["takeShift"] == "":
						row.append({ "key": str(rownum), "id": owner.id, "username": owner.username, "profile": json.loads(owner.profile) })
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
	owner = Owner.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if owner != None:
		info = json.loads(owner.info)

		location = Location.query.filter_by(id=info["locationId"]).first()
		owners = json.loads(location.owners)

		if str(id) in owners:
			owners.remove(str(id))

			location.owners = json.dumps(owners)

		db.session.delete(owner)
		db.session.commit()

		return { "msg": "Owner deleted" }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }

@app.route("/add_bankaccount", methods=["POST"])
def add_bankaccount():
	content = request.get_json()

	locationid = content['locationid']
	banktoken = content['banktoken']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		stripe.Account.create_external_account(
			accountid,
			external_account=banktoken
		)

		return { "msg": "Added a bank account" }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_bankaccount", methods=["POST"])
def update_bankaccount():
	content = request.get_json()

	locationid = content['locationid']
	oldbanktoken = content['oldbanktoken']
	banktoken = content['banktoken']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		stripe.Account.delete_external_account(
			accountid,
			oldbanktoken
		)

		stripe.Account.create_external_account(
			accountid,
			external_account=banktoken
		)

		return { "msg": "Updated a bank account" }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_accounts/<id>")
def get_accounts(id):
	location = Location.query.filter_by(id=id).first()
	owners = json.loads(location.owners)
	locationHours = json.loads(location.hours)
	accounts = []

	for owner in owners:
		ownerInfo = Owner.query.filter_by(id=owner).first()

		hours = [
			{ "key": "0", "header": "Sunday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "1", "header": "Monday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "2", "header": "Tuesday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "3", "header": "Wednesday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "4", "header": "Thursday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "5", "header": "Friday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" },
			{ "key": "6", "header": "Saturday", "opentime": { "hour": "06", "minute": "00", "period": "AM" }, "closetime": { "hour": "09", "minute": "00", "period": "PM" }, "working": True, "takeShift": "" }
		]

		if "Sun" in ownerInfo.hours:
			data = json.loads(ownerInfo.hours)
			day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

			for k, info in enumerate(hours):
				if data[day[k][:3]]["takeShift"] != "":
					worker = Owner.query.filter_by(id=data[day[k][:3]]["takeShift"]).first()

					info["takeShift"] = { "id": worker.id, "name": worker.username }

					workerHours = json.loads(worker.hours)
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

		cellnumber = ownerInfo.cellnumber

		f3 = str(cellnumber[0:3])
		s3 = str(cellnumber[3:6])
		l4 = str(cellnumber[6:len(cellnumber)])

		cellnumber = "(" + f3 + ") " + s3 + "-" + l4

		accounts.append({
			"key": "account-" + str(owner), 
			"id": owner, 
			"cellnumber": cellnumber,
			"username": ownerInfo.username,
			"profile": json.loads(ownerInfo.profile) if "name" in ownerInfo.profile else "",
			"hours": hours
		})

	return { "accounts": accounts }

@app.route("/get_bankaccounts/<id>")
def get_bankaccounts(id):
	content = request.get_json()

	location = Location.query.filter_by(id=id).first()
	locationInfo = json.loads(location.info)
	accountid = locationInfo["accountId"]
	bankaccounts = []

	accounts = stripe.Account.list_external_accounts(
		accountid,
		object="bank_account"
	)
	datas = accounts.data

	for k, data in enumerate(datas):
		bankaccounts.append({
			"key": "bankaccount-" + str(k),
			"id": str(k),
			"bankid": data.id,
			"bankname": data.bank_name,
			"number": "****" + str(data.last4),
			"default": data.default_for_currency
		})

	return { "bankaccounts": bankaccounts, "msg": "get bank accounts" }

@app.route("/set_bankaccountdefault", methods=["POST"])
def set_bankaccountdefault():
	content = request.get_json()

	locationid = content['locationid']
	bankid = content['bankid']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		stripe.Account.modify_external_account(
			accountid,
			bankid,
			default_for_currency=True
		)

		return { "msg": "Bank account set as default" }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_bankaccount_info", methods=["POST"])
def get_bankaccount_info():
	content = request.get_json()

	locationid = content['locationid']
	bankid = content['bankid']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		accounts = stripe.Account.retrieve(accountid)
		datas = accounts.external_accounts.data

		for data in datas:
			if data.id == bankid:
				routing_number = data.routing_number

				transit = routing_number[4:]
				institution = routing_number[1:4]

				info = {
					"account_holder_name": data.account_holder_name,
					"last4": data.last4,
					"transit_number": transit,
					"institution_number": institution
				}

				return { "bankaccountInfo": info }

		errormsg = "Bank doesn't exist"
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/delete_bankaccount", methods=["POST"])
def delete_bankaccount():
	content = request.get_json()

	locationid = content['locationid']
	bankid = content['bankid']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		locationInfo = json.loads(location.info)
		accountid = locationInfo["accountId"]

		stripe.Account.delete_external_account(
			accountid,
			bankid
		)

		return { "msg": "Bank account deleted" }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_reset_code/<cellnumber>")
def get_owner_reset_code(cellnumber):

	cellnumber = cellnumber.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	owner = Owner.query.filter_by(cellnumber=cellnumber).first()
	errormsg = ""
	status = ""

	if owner != None:
		code = getRanStr()

		if test_sms == False:
			message = client.messages.create(
				body="Your EasyGO reset code is " + code,
				messaging_service_sid=mss,
				to='+1' + str(owner.cellnumber)
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

	owner = Owner.query.filter_by(cellnumber=cellnumber).first()
	errormsg = ""
	status = ""

	if owner != None:
		if password != '' and confirmPassword != '':
			if len(password) >= 6:
				if password == confirmPassword:
					password = generate_password_hash(password)

					owner.password = password

					db.session.commit()

					ownerid = owner.id

					data = query("select * from location where owners like '%\"" + str(ownerid) + "\"%'", True)

					if len(data) == 0:
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
				errormsg = "Passwod is blank"
			else:
				errormsg = "Please confirm your password"
	else:
		errormsg = "User doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
