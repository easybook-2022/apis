from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pymysql.cursors, json, os
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from binascii import a2b_base64
from random import randint
from info import *
from models import *

cors = CORS(app)

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

@app.route("/welcome_services", methods=["GET"])
def welcome_services():
	datas = Location.query.all()
	services = []

	for data in datas:
		services.append(data.id)

	return { "msg": "welcome to services of easygo", "services": services }

@app.route("/get_service_info/<id>")
def get_service_info(id):
	service = Service.query.filter_by(id=id).first()
	errormsg = ""
	status = ""

	if service != None:
		image = json.loads(service.image)
		info = {
			"name": service.name,
			"image": image if image["name"] != "" else {"width": 300, "height": 300},
			"price": float(service.price)
		}

		return { "serviceInfo": info }
	else:
		errormsg = "Service doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_service", methods=["POST"])
def add_service():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	name = request.form['name']
	price = request.form['price']

	location = Location.query.filter_by(id=locationid).first()
	info = json.loads(location.info)
	info["listed"] = True
	location.info = json.dumps(info)

	errormsg = ""
	status = ""

	if location != None:
		data = query("select * from service where locationId = " + str(locationid) + " and menuId = '" + str(menuid) + "' and name = '" + name + "'", True)

		if len(data) == 0:
			isWeb = request.form.get("web")
			imageData = json.dumps({"name": "", "width": 0, "height": 0})

			if isWeb != None:
				image = json.loads(request.form['image'])
				imagename = image["name"]

				if imagename != "":
					uri = image['uri'].split(",")[1]
					size = image['size']

					writeToFile(uri, imagename)

					imageData = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
			else:
				imagepath = request.files.get('image', False)
				imageexist = False if imagepath == False else True

				if imageexist == True:
					image = request.files['image']
					imagename = image.filename

					size = json.loads(request.form['size'])

					image.save(os.path.join("static", imagename))
					imageData = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})

			if errormsg == "":
				service = Service(locationid, menuid, name, imageData, price)

				db.session.add(service)
				db.session.commit()

				return { "id": service.id }
		else:
			errormsg = "Service already exist"
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_service", methods=["POST"])
def update_service():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	serviceid = request.form['serviceid']
	name = request.form['name']
	price = request.form['price']

	location = Location.query.filter_by(id=locationid).first()
	errormsg = ""
	status = ""

	if location != None:
		service = Service.query.filter_by(id=serviceid, locationId=locationid, menuId=menuid).first()

		if service != None:
			service.name = name
			service.price = price

			isWeb = request.form.get("web")
			oldimage = json.loads(service.image)

			if isWeb != None:
				image = json.loads(request.form['image'])
				imagename = image['name']

				if imagename != '' and "data" in image['uri']:
					uri = image['uri'].split(",")[1]
					size = image['size']

					if oldimage["name"] != "" and os.path.exists(os.path.join("static", oldimage["name"])) == True:
						os.remove("static/" + oldimage["name"])

					writeToFile(uri, imagename)

					newimagename = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
					service.image = newimagename
			else:
				imagepath = request.files.get('image', False)
				imageexist = False if imagepath == False else True

				if imageexist == True:
					image = request.files['image']
					size = json.loads(request.form['size'])
					imagename = image.filename

					if oldimage["name"] != imagename:
						if oldimage["name"] != "" and os.path.exists("static/" + oldimage["name"]):
							os.remove("static/" + oldimage["name"])

						image.save(os.path.join('static', imagename))

						newimagename = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
						service.image = newimagename

			if errormsg == "":
				db.session.commit()

				return { "msg": "service updated", "id": service.id }
		else:
			errormsg = "Service already exist"
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/remove_service/<id>")
def remove_service(id):
	service = Service.query.filter_by(id=id).first()

	if service != None:
		image = json.loads(service.image)

		if image["name"] != "" and os.path.exists("static/" + image["name"]):
			os.remove("static/" + image["name"])

		db.session.delete(service)

		location = Location.query.filter_by(id=service.locationId).first()
		info = json.loads(location.info)

		numMenus = Menu.query.filter_by(locationId=location.id).count() + Service.query.filter_by(locationId=location.id).count() + Product.query.filter_by(locationId=location.id).count() + len(info["menuPhotos"])

		info["listed"] = True if numMenus > 0 else False
		location.info = json.dumps(info)

		db.session.commit()

		return { "msg": "" }

	return { "errormsg": "Service doesn't exist" }
