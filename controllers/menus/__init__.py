from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_menus", methods=["GET"])
def welcome_menus():
	datas = Menu.query.all()
	menus = []

	for data in datas:
		menus.append(data["id"])

	return { "msg": "welcome to menus of EasyBook", "menus": menus }

@app.route("/get_menus/<id>")
def get_menus(id):
	def getOtherMenu(locationId, parentMenuid):
		menuDatas = query("select * from menu where locationId = " + str(locationId) + " and parentMenuId = '" + str(parentMenuid) + "'", True).fetchall()
		location = query("select * from location where id = " + str(locationId), True).fetchone()
		productDatas = query("select * from product where locationId = " + str(locationId) + " and menuId = '" + str(parentMenuid) + "'", True).fetchall()
		serviceDatas = query("select * from service where locationId = " + str(locationId) + " and menuId = '" + str(parentMenuid) + "'", True).fetchall()

		items = []

		if len(menuDatas) > 0:
			if len(productDatas) > 0:
				for index, data in enumerate(productDatas):
					sizes = json.loads(data["sizes"])
					
					image = json.loads(data["image"])
					items.append({
						"key": "product-" + str(data["id"]), "id": data["id"], "name": data["name"], 
						"price": float(data["price"]) if data["price"] != '' else None, "sizes": sizes,
						"image": image if image["name"] != "" else {"width": 300, "height": 300}, "listType": "product",
						"show": True
					})
			elif len(serviceDatas) > 0:
				for index, data in enumerate(serviceDatas):
					image = json.loads(data["image"])
					items.append({
						"key": "service-" + str(data["id"]), "id": data["id"], 
						"name": data["name"], "price": float(data["price"]), 
						"image": image if image["name"] != "" else {"width": 300, "height": 300}, "listType": "service",
						"show": True
					})

			for index, data in enumerate(menuDatas):
				parentMenuid = data["id"]
				
				image = json.loads(data["image"])
				items.append({
					"key": "menu-" + str(index), "id": data["id"], "name": data["name"], 
					"image": image if image["name"] != "" else {"width": 300, "height": 300}, "list": [], "listType": "list",
					"show": True
				})
				otherList = getOtherMenu(locationId, data["id"])

				if len(otherList) > 0:
					items[len(items) - 1]["list"] = otherList
				else:
					type = location["type"]
					innerItems = []

					if type == "restaurant":
						datas = query("select * from product where locationId = " + str(locationId) + " and menuId = '" + str(data["id"]) + "'", True).fetchall()

						for data in datas:
							sizes = json.loads(data["sizes"])

							image = json.loads(data["image"])
							innerItems.append({
								"key": "product-" + str(data["id"]), "id": data["id"], "name": data["name"], 
								"price": float(data["price"]) if data["price"] != '' else None, "sizes": sizes,
								"image": image if image["name"] != "" else {"width": 300, "height": 300}, 
								"listType": "product"
							})
					else:
						datas = query("select * from service where locationId = " + str(locationId) + " and menuId = '" + str(data["id"]) + "'", True).fetchall()

						for data in datas:
							image = json.loads(data["image"])
							innerItems.append({
								"key": "service-" + str(data["id"]), "id": data["id"], 
								"name": data["name"], "info": data["info"], 
								"price": float(data["price"]), 
								"image": image if image["name"] != "" else {"width": 300, "height": 300}, 
								"listType": "service"
							})

						items[len(items) - 1]["list"] = innerItems
		else:
			if len(productDatas) > 0:
				for index, data in enumerate(productDatas):
					sizes = json.loads(data["sizes"])
					
					image = json.loads(data["image"])
					items.append({
						"key": "product-" + str(data["id"]), "id": data["id"], "name": data["name"], 
						"price": float(data["price"]) if data["price"] != '' else None, "sizes": sizes,
						"image": image if image["name"] != "" else {"width": 300, "height": 300}, "listType": "product",
						"show": True
					})
			elif len(serviceDatas) > 0:
				for index, data in enumerate(serviceDatas):
					image = json.loads(data["image"])
					items.append({
						"key": "service-" + str(data["id"]), "id": data["id"], 
						"name": data["name"], "price": float(data["price"]), 
						"image": image if image["name"] != "" else {"width": 300, "height": 300}, "listType": "service",
						"show": True
					})

		return items

	location = query("select * from location where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	list = getOtherMenu(id, "") # list
	menuPhotos = []
	info = json.loads(location["info"])

	if len(info["menuPhotos"]) > 0:
		photos = info["menuPhotos"]
		row = []
		rownum = 0
		
		for photo in photos:
			row.append({ "key": "row-" + str(rownum), "photo": { "name": photo["image"], "width": photo["width"], "height": photo["height"] } })
			rownum += 1

			if len(row) == 3:
				menuPhotos.append({ "key": "menu-" + str(len(menuPhotos)), "row": row })
				row = []

		if len(row) > 0:
			leftover = 3 - len(row)

			for k in range(leftover):
				row.append({ "key": "row-" + str(rownum) })
				rownum += 1

			menuPhotos.append({ "key": "menu-" + str(len(menuPhotos)), "row": row })

	return { "list": list, "photos": menuPhotos }

@app.route("/remove_menu/<id>")
def remove_menu(id):
	menu = query("select * from menu where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	location = query("select * from location where id = " + str(menu["locationId"]), True).fetchone()
	info = json.loads(location["info"])

	# delete services and products from the menu
	query("delete from service where menuId = '" + str(id) + "'")
	query("delete from product where menuId = '" + str(id) + "'")
	query("delete from menu where parentMenuId = '" + str(menu["id"]) + "'")

	image = json.loads(menu["image"])

	if image["name"] != "" and os.path.exists("static/" + image["name"]):
		os.remove("static/" + image["name"])

	query("delete from menu where id = " + str(id))

	numMenus = query("select count(*) as num from menu where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += query("select count(*) as num from product where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += query("select count(*) as num from service where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += len(info["menuPhotos"])

	info["listed"] = True if numMenus > 0 else False
	location["info"] = json.dumps(info)

	query("update location set info = '" + json.dumps(info) + "' where id = " + str(location["id"]))

	return { "msg": "deleted" }

@app.route("/get_menu_info/<id>")
def get_menu_info(id):
	menu = query("select * from menu where id = " + str(id), True).fetchone()
	errormsg = ""
	status = ""

	name = menu["name"]
	image = json.loads(menu["image"])

	info = { 
		"name": name, 
		"menuImage": image if image["name"] != "" else {"width": 300, "height": 300} 
	}

	return { "info": info, "msg": "menu info" }

@app.route("/save_menu", methods=["POST"])
def save_menu():
	menuid = request.form['menuid']
	name = request.form['name']
	menu = query("select * from menu where id = " + str(menuid), True).fetchone()

	errormsg = ""
	status = ""
	new_data = {}

	menu["name"] = name

	isWeb = request.form.get("web")

	if isWeb != None:
		image = json.loads(request.form['image'])
		imagename = image['name']

		if imagename != "" and "data" in image['uri']:
			uri = image['uri'].split(",")[1]
			size = image['size']

			writeToFile(uri, imagename)

			new_data["image"] = json.dumps({"name": imagename, "width": int(size["width"]), "height": int(size["height"])})
	else:
		imagepath = request.files.get('image', False)
		imageexist = False if imagepath == False else True

		if imageexist == True:
			image = request.files['image']
			size = json.loads(request.form['size'])
			imagename = image.filename
			oldimage = json.loads(menu["image"])

			if imagename != oldimage["name"]:
				if oldimage["name"] != "" and os.path.exists("static/" + oldimage["name"]):
					os.remove("static/" + oldimage["name"])

				image.save(os.path.join('static', imagename))

				new_data["image"] = json.dumps({"name": imagename, "width": size['width'], "height": size['height']})

	if "image" in new_data:
		query("update menu set image = '" + new_data["image"] + "' where id = " + str(menuid))

	return { "msg": "menu info updated" }

@app.route("/add_menu", methods=["POST"])
def add_menu():
	locationid = request.form['locationid']
	parentMenuid = request.form['parentmenuid']
	name = request.form['name']

	errormsg = ""
	status = ""

	if name != '':
		location = query("select * from location where id = " + str(locationid), True).fetchone()
		info = json.loads(location["info"])
		info["listed"] = True

		location["info"] = json.dumps(info)

		numMenu = query("select count(*) as num from menu where locationId = " + str(locationid) + " and (parentMenuId = '" + str(parentMenuid) + "' and name = '" + name + "')", True).fetchone()["num"]

		if numMenu == 0:
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
					"locationId": locationid, "parentMenuId": parentMenuid,
					"name": name, "image": imageData
				}
				columns = []
				insert_data = []

				for key in data:
					columns.append(key)
					insert_data.append("'" + str(data[key]) + "'")

				id = query("insert into menu (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid
				
				return { "id": id }
		else:
			errormsg = "Menu already exist"
	else:
		errormsg = "Name is blank"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/upload_menu", methods=["POST"])
def upload_menu():
	locationid = request.form['locationid']

	errormsg = ""
	status = ""

	location = query("select * from location where id = " + str(locationid), True).fetchone()

	isWeb = request.form.get("web")

	if isWeb != None:
		image = json.loads(request.form['image'])
		size = json.loads(request.form['size'])

		uri = image['uri'].split(",")[1]
		imagename = image['name']

		writeToFile(uri, imagename)

		photo = { "image": imagename, "width": size['width'], "height": size['height'] }
	else:
		imagepath = request.files.get('image', False)
		imageexist = False if imagepath == False else True

		image = request.files['image']
		size = json.loads(request.form['size'])
		imagename = image.filename

		image.save(os.path.join("static", imagename))
		photo = { "image": imagename, "width": size['width'], "height": size['height'] }

	info = json.loads(location["info"])
	menuPhotos = info["menuPhotos"]
	menuPhotos.append(photo)

	info["menuPhotos"] = menuPhotos
	info["listed"] = True
	
	query("update location set info = '" + json.dumps(info) + "' where id = " + str(locationid))

	return { "msg": "success" }

@app.route("/delete_menu", methods=["POST"])
def delete_menu():
	content = request.get_json()
	status = ""
	errormsg = ""

	locationid = content['locationid']
	photo = content['photo']

	location = query("select * from location where id = " + str(locationid), True).fetchone()

	info = json.loads(location["info"])
	photos = info["menuPhotos"]

	for index, photoInfo in enumerate(photos):
		if photoInfo["image"] == photo:
			photos.pop(index)

	info["menuPhotos"] = photos

	numMenus = query("select count(*) as num from menu where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += query("select count(*) as num from product where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += query("select count(*) as num from service where locationId = " + str(location["id"]), True).fetchone()["num"]
	numMenus += len(photos)

	info["listed"] = True if numMenus > 0 else False

	query("update location set info = '" + json.dumps(info) + "' where id = " + str(locationid))

	return { "msg": "success" }
