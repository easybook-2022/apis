from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_services", methods=["GET"])
def welcome_services():
	datas = Location.query.all()
	services = []

	for data in datas:
		services.append(data.id)

	return { "msg": "welcome to services of EasyBook", "services": services }

@app.route("/get_service_info/<id>")
def get_service_info(id):
	service = query("select * from service where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	image = json.loads(service["image"])
	info = {
		"name": service["name"],
		"serviceImage": image if image["name"] != "" else {"width": 300, "height": 300},
		"price": float(service["price"])
	}

	return { "serviceInfo": info }

@app.route("/add_service", methods=["POST"])
def add_service():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	name = request.form['name']
	price = request.form['price']

	location = query("select * from location where id = " + str(locationid), True).fetchone()
	info = json.loads(location["info"])
	info["listed"] = True

	errormsg = ""
	status = ""

	numServices = query("select count(*) as num from service where locationId = " + str(locationid) + " and menuId = '" + str(menuid) + "' and name = '" + name + "'", True).fetchone()["num"]

	if numServices == 0:
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
			data = {
				"locationId": locationid, "menuId": menuid, "name": name, "image": imageData,
				"price": price
			}
			columns = []
			insert_data = []

			for key in data:
				columns.append(key)
				insert_data.append("'" + str(data[key]) + "'")

			id = query("insert into service (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid
			query("update location set info = '" + json.dumps(info) + "' where id = " + str(locationid))

			return { "id": id }
	else:
		errormsg = "Service already exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/update_service", methods=["POST"])
def update_service():
	locationid = request.form['locationid']
	menuid = request.form['menuid']
	serviceid = request.form['serviceid']
	name = request.form['name']
	price = request.form['price']

	location = query("select * from location where id = " + str(locationid), True).fetchone()
	errormsg = ""
	status = ""

	service = query("select * from service where id = " + str(serviceid) + " and locationId = " + str(locationid) + " and menuId = " + str(menuid), True).fetchone()

	service["name"] = name
	service["price"] = price

	isWeb = request.form.get("web")
	oldimage = json.loads(service["image"])

	if isWeb != None:
		image = json.loads(request.form['image'])
		imagename = image['name']

		if imagename != '' and "data" in image['uri']:
			uri = image['uri'].split(",")[1]
			size = image['size']

			if oldimage["name"] != "" and os.path.exists(os.path.join("static", oldimage["name"])) == True:
				os.remove("static/" + oldimage["name"])

			writeToFile(uri, imagename)

			service["image"] = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
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

				service["image"] = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})

	if errormsg == "":
		update_data = []
		for key in service:
			update_data.append(key + " = '" + str(service[key]) + "'")

		query("update service set " + ", ".join(update_data) + " where id = " + str(service["id"]))

		return { "msg": "service updated" }

@app.route("/remove_service/<id>")
def remove_service(id):
	service = query("select * from service where id = " + str(id), True).fetchone()

	image = json.loads(service["image"])

	if image["name"] != "" and os.path.exists("static/" + image["name"]):
		os.remove("static/" + image["name"])

	query("delete from service where id = " + str(id))

	location = query("select * from location where id = " + str(service["locationId"]), True).fetchone()
	info = json.loads(location["info"])

	numMenus = query("select count(*) as num from menu where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += query("select count(*) as num from service where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += query("select count(*) as num from product where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += len(info["menuPhotos"])

	info["listed"] = True if numMenus > 0 else False

	query("update location set info = '" + str(json.dumps(info)) + "' where id = " + str(location["id"]))

	return { "msg": "success" }
