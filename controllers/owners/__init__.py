from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector, pymysql.cursors, json, os
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
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

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(10), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	profile = db.Column(db.String(25))
	info = db.Column(db.String(155))

	def __init__(self, cellnumber, password, username, profile, info):
		self.cellnumber = cellnumber
		self.password = password
		self.username = username
		self.profile = profile
		self.info = info

	def __repr__(self):
		return '<User %r>' % self.cellnumber

class Owner(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cellnumber = db.Column(db.String(15), unique=True)
	password = db.Column(db.String(110), unique=True)
	username = db.Column(db.String(20))
	profile = db.Column(db.String(25))
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
	logo = db.Column(db.String(20))
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
	info = db.Column(db.String(100))
	image = db.Column(db.String(20))

	def __init__(self, locationId, parentMenuId, name, info, image):
		self.locationId = locationId
		self.parentMenuId = parentMenuId
		self.name = name
		self.info = info
		self.image = image

	def __repr__(self):
		return '<Menu %r>' % self.name

class Service(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	locationId = db.Column(db.Integer)
	menuId = db.Column(db.Text)
	name = db.Column(db.String(20))
	info = db.Column(db.Text)
	image = db.Column(db.String(20))
	price = db.Column(db.String(10))
	duration = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, info, image, price, duration):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.info = info
		self.image = image
		self.price = price
		self.duration = duration

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
	info = db.Column(db.String(100))
	image = db.Column(db.String(20))
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(150))
	price = db.Column(db.String(10))

	def __init__(self, locationId, menuId, name, info, image, options, others, sizes, price):
		self.locationId = locationId
		self.menuId = menuId
		self.name = name
		self.info = info
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
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(225))
	note = db.Column(db.String(100))
	status = db.Column(db.String(10))
	orderNumber = db.Column(db.String(10))

	def __init__(self, locationId, productId, userInput, quantity, adder, callfor, options, others, sizes, note, status, orderNumber):
		self.locationId = locationId
		self.productId = productId
		self.userInput = userInput
		self.quantity = quantity
		self.adder = adder
		self.callfor = callfor
		self.options = options
		self.others = others
		self.sizes = sizes
		self.note = note
		self.status = status
		self.orderNumber = orderNumber

	def __repr__(self):
		return '<Cart %r>' % self.productId

class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	groupId = db.Column(db.String(20))
	locationId = db.Column(db.Integer)
	productId = db.Column(db.Integer)
	serviceId = db.Column(db.Integer)
	userInput = db.Column(db.Text)
	quantity = db.Column(db.Integer)
	adder = db.Column(db.Integer)
	callfor = db.Column(db.Text)
	options = db.Column(db.Text)
	others = db.Column(db.Text)
	sizes = db.Column(db.String(200))
	time = db.Column(db.String(15))

	def __init__(self, groupId, locationId, productId, serviceId, userInput, quantity, adder, callfor, options, others, sizes, time):
		self.groupId = groupId
		self.locationId = locationId
		self.productId = productId
		self.serviceId = serviceId
		self.userInput = userInput
		self.quantity = quantity
		self.adder = adder
		self.callfor = callfor
		self.options = options
		self.others = others
		self.sizes = sizes
		self.time = time

	def __repr__(self):
		return '<Transaction %r>' % self.groupId

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

def trialInfo(): # days before over | cardrequired | trialover (id, time)
	# user = User.query.filter_by(id=id).first()
	# info = json.loads(user.info)

	# customerid = info['customerId']

	# stripeCustomer = stripe.Customer.list_sources(
	# 	customerid,
	# 	object="card",
	# 	limit=1
	# )
	# cards = len(stripeCustomer.data)
	# status = ""
	# days = 0

	# if "trialstart" in info:
	# 	if (time - info["trialstart"]) >= (86400000 * 30): # trial is over, payment required
	# 		if cards == 0:
	# 			status = "cardrequired"
	# 		else:
	# 			status = "trialover"
	# 	else:
	# 		days = 30 - int((time - info["trialstart"]) / (86400000 * 30))
	# 		status = "notover"
	# else:
	# 	if cards == 0:
	# 		status = "cardrequired"
	# 	else:
	# 		status = "trialover"

	days = 30
	status = "notover"

	return { "days": days, "status": status }

def getRanStr():
	strid = ""

	for k in range(6):
		strid += str(randint(0, 9))

	return strid

def stripeFee(amount):
	return (amount + 0.30) / (1 - 0.029)

def calcTax(amount):
	pst = 0.08 * amount
	hst = 0.05 * amount

	return pst + hst

def pushInfo(to, title, body, data):
	return PushMessage(to=to, title=title, body=body, data=data)

def customerPay(amount, userid, locationid):
	chargeamount = stripeFee(amount + calcTax(amount))
	transferamount = amount + calcTax(amount)

	user = User.query.filter_by(id=userid).first()
	info = json.loads(user.info)
	customerid = info["customerId"]

	charge = stripe.Charge.create(
		amount=int(chargeamount * 100),
		currency="cad",
		customer=customerid
	)

	if locationid != None:
		location = Location.query.filter_by(id=locationid).first()
		info = json.loads(location.info)
		accountid = info["accountId"]

		transfer = stripe.Transfer.create(
			amount=int(transferamount * 100),
			currency="cad",
			destination=accountid,
		)
	else:
		transfer = None

	return charge != None and (transfer != None or locationid == None)

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
						if locationhours == '{}':
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": "", "msg": "locationsetup" }
						else:
							return { "ownerid": ownerid, "cellnumber": cellnumber, "locationid": locationid, "locationtype": locationtype, "msg": "workinghours" }
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
	cellnumber = request.form['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	username = request.form['username']
	password = request.form['password']
	confirmPassword = request.form['confirmPassword']
	profilepath = request.files.get('profile', False)
	profileexist = False if profilepath == False else True
	permission = request.form['permission']
	errormsg = ""
	status = ""

	if username == "":
		errormsg = "Please provide a username for identification"

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

	profilename = ""
	if profileexist == True:
		profile = request.files['profile']
		profilename = profile.filename

		profile.save(os.path.join('static', profilename))
	else:
		profilename = ""
	
	if errormsg == "":
		password = generate_password_hash(password)
		info = json.dumps({"locationId": "","pushToken": ""})

		owner = Owner(cellnumber, password, username, profilename, '{}', info)
		db.session.add(owner)
		db.session.commit()

		return { "id": owner.id }

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_owner", methods=["POST"])
def add_owner():
	ownerid = request.form['ownerid']
	cellnumber = request.form['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	username = request.form['username']
	password = request.form['password']
	confirmPassword = request.form['confirmPassword']
	profilepath = request.files.get('profile', False)
	profileexist = False if profilepath == False else True
	hours = request.form['hours']
	permission = request.form['permission']

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

			profilename = ""
			if profileexist == True:
				profile = request.files['profile']
				profilename = profile.filename
				
				profile.save(os.path.join('static', profilename))
			else:
				if permission == "true":
					errormsg = "Please provide a profile for identification"

			if errormsg == "":
				ownerInfo = json.loads(owner.info)
				locationId = ownerInfo["locationId"]

				info = {"locationId": locationId, "pushToken": ""}

				password = generate_password_hash(password)
				owner = Owner(cellnumber, password, username, profilename, hours, json.dumps(info))
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
	username = request.form['username']
	cellnumber = request.form['cellnumber'].replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
	password = request.form['password']
	confirmPassword = request.form['confirmPassword']
	profilepath = request.files.get('profile', False)
	profileexist = False if profilepath == False else True
	hours = request.form['hours']
	permission = request.form['permission']

	owner = Owner.query.filter_by(id=ownerid).first()
	errormsg = ""
	status = ""

	if owner != None:
		if hours != "[]":
			owner.hours = hours

		if username != "" and owner.username != username:
			exist_username = Owner.query.filter_by(username=username).count()

			if exist_username == 0:
				owner.username = username
			else:
				errormsg = "The username is already taken"
				status = "sameusername"

		if cellnumber != "" and owner.cellnumber != cellnumber:
			exist_cellnumber = Owner.query.filter_by(cellnumber=cellnumber).count()

			if exist_cellnumber == 0:
				owner.cellnumber = cellnumber
			else:
				errormsg = "This cell number is already taken"
				status = "samecellnumber"

		if profileexist == True:
			profile = request.files['profile']
			newprofilename = profile.filename
			oldprofile = owner.profile

			if oldprofile != "" and oldprofile != None and os.path.exists("static/" + oldprofile):
				os.remove("static/" + oldprofile)

			profile.save(os.path.join('static', newprofilename))
			owner.profile = newprofilename

		if password != "" or confirmPassword != "":
			if password != "" and confirmPassword != "":
				if len(password) >= 6:
					if password == confirmPassword:
						password = generate_password_hash(password)

						owner.password = password
					else:
						errormsg = "Password is mismatch"
				else:
					errormsg = "Password needs to be atleast 6 characters long"
			else:
				if password == "":
					errormsg = "Please enter a password"
				else:
					errormsg = "Please confirm your password"

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

@app.route("/get_workers", methods=["POST"])
def get_workers():
	content = request.get_json()

	locationid = content['locationid']
	dateStr = content['dateStr']
	timeStr = content['timeStr']
	day = content['day']

	days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		datas = query("select * from owner where info like '%\"locationId\": \"" + str(locationid) + "\"%'", True)
		owners = []
		row = []
		key = 0
		numWorkers = 0

		for data in datas:
			hours = json.loads(data['hours'])

			if days[day] in hours:
				info = hours[days[day]]

				if info["working"] == True:
					opentime = info["opentime"]
					closetime = info["closetime"]

					openhour = opentime["hour"]
					openminute = opentime["minute"]

					closehour = closetime["hour"]
					closeminute = closetime["minute"]

					opentime = dateStr + openhour + ":" + openminute + ":00"
					workertime = dateStr + timeStr
					closetime = dateStr + closehour + ":" + closeminute + ":00"

					opentime = int(datetime.strptime(opentime, "%d.%m.%Y %H:%M:%S").timestamp() * 1000)
					workertime = int(datetime.strptime(workertime, "%d.%m.%Y %H:%M:%S").timestamp() * 1000)
					closetime = int(datetime.strptime(closetime, "%d.%m.%Y %H:%M:%S").timestamp() * 1000)

					if workertime >= opentime and workertime <= closetime:
						for data in datas:
							row.append({
								"key": "worker-" + str(key),
								"id": data['id'],
								"username": data['username'],
								"profile": data["profile"],
								"selected": False
							})
							key += 1
							numWorkers += 1

							if len(row) >= 3:
								owners.append({ "key": str(len(owners)), "row": row })
								row = []

						if len(row) > 0 and len(row) < 3:
							leftover = 3 - len(row)

							for k in range(leftover):
								row.append({ "key": "worker-" + str(key) })
								key += 1

							owners.append({ "key": str(len(owners)), "row": row })

		return { "msg": "get workers", "owners": owners, "numWorkers": numWorkers }
	else:
		errormsg = "Location doesn't exist"
		
	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_worker_info/<id>")
def get_worker_info(id):
	owner = Owner.query.filter_by(id=id).first()
	errormsg = ""
	status = ""
	days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

	if owner != None:
		hours = json.loads(owner.hours)
		info = {}

		for day in days:
			info[day] = {
				"start": hours[day]["opentime"]["hour"] + ":" + hours[day]["opentime"]["minute"],
				"end": hours[day]["closetime"]["hour"] + ":" + hours[day]["closetime"]["minute"],
				"working": hours[day]["working"]
			}

		return { "days": info }
	else:
		errormsg = "Owner doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

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
	content = request.get_json()

	location = Location.query.filter_by(id=id).first()
	owners = json.loads(location.owners)
	accounts = []

	for owner in owners:
		ownerInfo = Owner.query.filter_by(id=owner).first()

		hours = [
			{ "key": "0", "header": "Sunday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "working": True },
			{ "key": "1", "header": "Monday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "working": True },
			{ "key": "2", "header": "Tuesday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "working": True },
			{ "key": "3", "header": "Wednesday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "working": True },
			{ "key": "4", "header": "Thursday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "working": True },
			{ "key": "5", "header": "Friday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "working": True },
			{ "key": "6", "header": "Saturday", "opentime": { "hour": "12", "minute": "00", "period": "AM" }, "closetime": { "hour": "11", "minute": "59", "period": "PM" }, "working": True }
		]

		if "Sun" in ownerInfo.hours:
			data = json.loads(ownerInfo.hours)
			day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

			for k, info in enumerate(hours):
				openhour = int(data[day[k][:3]]["opentime"]["hour"])
				closehour = int(data[day[k][:3]]["closetime"]["hour"])
				working = data[day[k][:3]]["working"]

				openperiod = "PM" if openhour > 12 else "AM"
				openhour = int(openhour)

				if openhour == 0:
					openhour = 12
				elif openhour > 12:
					openhour -= 12

				openhour = "0" + str(openhour) if openhour < 10 else str(openhour)

				closeperiod = "PM" if closehour > 12 else "AM"
				closehour = int(closehour)

				if closehour == 0:
					closehour = 12
				elif closehour > 12:
					closehour -= 12
					
				closehour = "0" + str(closehour) if closehour < 10 else str(closehour)

				info["opentime"]["hour"] = openhour
				info["opentime"]["minute"] = data[day[k][:3]]["opentime"]["minute"]
				info["opentime"]["period"] = openperiod

				info["closetime"]["hour"] = closehour
				info["closetime"]["minute"] = data[day[k][:3]]["closetime"]["minute"]
				info["closetime"]["period"] = closeperiod
				info["working"] = working

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
			"profile": ownerInfo.profile,
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
