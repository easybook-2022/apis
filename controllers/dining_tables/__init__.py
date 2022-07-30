import datetime
from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

@app.route("/welcome_dining_tables")
def welcome_dining_tables():
	datas = query("select id from dining_table limit 5", True).fetchall()
	diningTables = []

	for data in datas:
		diningTables.append(data["id"])

	return { "msg": "welcome to dining tables of EasyBook", "diningTables": diningTables }

@app.route("/get_tables/<id>")
def get_tables(id):
	errormsg = ""
	status = ""

	location = query("select * from location where id = " + str(id), True).fetchone()

	if location != None:
		sql = "select * from dining_table where locationId = " + str(id)
		datas = query(sql, True).fetchall()
		tables = []

		for data in datas:
			tables.append({ "key": str(data["id"]), "tableid": data["tableId"], "name": data["name"] })

		return { "tables": tables }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_table_bills/<id>")
def get_table_bills(id):
	errormsg = ""
	status = ""

	location = query("select * from location where id = " + str(id), True).fetchone()

	if location != None:
		sql = "select * from dining_table where locationId = " + str(id) + " and not orders = '[]' order by "
		sql += "(length(orders) - length(replace(orders, 'productId', ''))) desc"

		datas = query(sql, True).fetchall()
		tables = []

		for data in datas:
			orders = json.loads(data["orders"])
			numOrders = 0

			for order in orders:
				if "done" not in order:
					numOrders += 1

			tables.append({ "key": str(data["id"]), "tableid": data["tableId"], "name": data["name"] })

		return { "tables": tables }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_ordering_tables/<id>")
def get_ordering_tables(id):
	errormsg = ""
	status = ""

	location = query("select * from location where id = " + str(id), True).fetchone()

	if location != None:
		sql = "select * from dining_table where locationId = " + str(id) + " and not orders = '[]' order by "
		sql += "(length(orders) - length(replace(orders, 'productId', ''))) desc"

		datas = query(sql, True).fetchall()
		tables = []

		for data in datas:
			orders = json.loads(data["orders"])

			if len(orders) > 0:
				for order in orders:
					if "done" not in order:
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

						order["name"] = product["name"]

						sizes = []
						quantities = []
						percents = []

						for index, info in enumerate(sizesInfo):
							sizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info] })

						for index, info in enumerate(quantitiesInfo):
							quantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info] })

						for index, info in enumerate(percentsInfo):
							percents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info] })

						order["sizes"] = sizes
						order["quantities"] = quantities
						order["percents"] = percents
						order["tableName"] = data["name"]

						tables.append(order)

		return { "tables": tables }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_qr_code/<id>")
def get_qr_code(id):
	errormsg = ""
	status = ""

	table = query("select locationId, name from dining_table where tableId = '" + str(id) + "'", True).fetchone()

	if table != None:
		location = query("select name from location where id = " + str(table["locationId"]), True).fetchone()

		return { "name": table["name"], "locationid": table["locationId"], "locationName": location["name"] }
	else:
		errormsg = "Table doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/add_table", methods=["POST"])
def add_table():
	content = request.get_json()
	errormsg = ""
	status = ""

	locationid = content['locationid']
	tableName = content['table']
	tableid = content['tableid']

	location = query("select * from location where id = " + str(locationid), True).fetchone()

	if location != None:
		table = query("select * from dining_table where name = '" + tableName + "'", True).fetchone()

		if table == None:
			tableIdExist = query("select count(*) as num from dining_table where tableId = '" + tableid + "'", True).fetchone()["num"]

			while tableIdExist > 0:
				tableid = getId()

				tableIdExist = query("select count(*) as num from dining_table where tableId = '" + tableid + "'", True).fetchone()["num"]
		else:
			status = "exist"
			errormsg = "Table already exist"

		if errormsg == "":
			data = { "tableId": tableid, "locationId": locationid, "name": tableName, "orders": '[]' }
			columns = []
			insert_data = []

			for key in data:
				columns.append(key)
				insert_data.append("'" + str(data[key]) + "'")

			id = query("insert into dining_table (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

			return { "msg": "succeed" }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/remove_table/<id>")
def remove_table(id):
	errormsg = ""
	status = ""

	numExisttable = query("select count(*) as num from dining_table where id = " + str(id), True).fetchone()["num"]

	if numExisttable > 0:
		query("delete from dining_table where id = " + str(id))

		return { "msg": "succeed" }
	else:
		errormsg = "Table doesn't exist"
		status = "nonexist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/order_meal", methods=["POST"])
def order_meal():
	content = request.get_json()
	errormsg = ""
	status = ""

	key = content['key']
	tableid = content['tableid']
	productid = content['id']
	sizes = content['sizes']
	quantities = content['quantities']
	percents = content['percents']
	image = content['image']
	quantity = int(content['quantity'])
	note = content['note']

	table = query("select * from dining_table where tableId = '" + str(tableid) + "'", True).fetchone()

	if table != None:
		location = query("select owners from location where id = " + str(table["locationId"]), True).fetchone()
		owners = json.loads(location["owners"])
		orders = json.loads(table["orders"])
		receiver = []

		for owner in owners:
			receiver.append("owner" + str(owner))

		orders.insert(0, {
			"key": key,
			"productId": productid,
			"sizes": sizes,
			"quantities": quantities,
			"percents": percents,
			"image": image,
			"quantity": quantity,
			"note": note
		})

		query("update dining_table set orders = '" + json.dumps(orders) + "' where id = " + str(table["id"]))

		return { "msg": "succeed", "receiver": receiver }
	else:
		errormsg = "Table doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/finish_order", methods=["POST"])
def finish_order():
	content = request.get_json()
	errormsg = ""
	status = ""

	orderid = content['orderid']
	tableid = content['id']

	table = query("select orders from dining_table where name = " + str(tableid), True).fetchone()

	if table != None:
		orders = json.loads(table["orders"])

		for order in orders:
			if order["key"] == orderid:
				order["done"] = True

		query("update dining_table set orders = '" + json.dumps(orders) + "' where id = " + str(tableid))

		return { "msg": "succeed" }
	else:
		errormsg = "Table doesn't exist"
		status = ""

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/view_payment/<id>")
def view_payment(id):
	errormsg = ""
	status = ""

	table = query("select name, orders from dining_table where id = " + str(id), True).fetchone()

	if table != None:
		datas = json.loads(table["orders"])
		subTotalCost = 0.00
		orders = []

		if len(datas) > 0:
			for data in datas:
				sizes = data["sizes"]
				quantities = data["quantities"]
				percents = data["percents"]

				product = query("select * from product where id = " + str(data["productId"]), True).fetchone()
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

				data["name"] = product["name"]
				cost = 0.00

				if product["price"] != "":
					subTotalCost += int(data["quantity"]) * float(product["price"])
					cost = round(int(data["quantity"]) * float(product["price"]), 2)
				else:
					if len(sizes) > 0:
						for size in sizes:
							subTotalCost += int(data["quantity"]) * sizesInfo[size]
							cost = round(int(data["quantity"]) * sizesInfo[size], 2)
					else:
						for quantity in quantities:
							subTotalCost += int(data["quantity"]) * float(quantitiesInfo[quantity])
							cost = round(int(data["quantity"]) * float(quantitiesInfo[quantity]), 2)

				for percent in percents:
					subTotalCost += int(data["quantity"]) * float(percentsInfo[percent["input"]])
					cost += round(int(data["quantity"]) * float(percentsInfo[percent["input"]]), 2)

				if len(str(cost).split(".")[1]) < 2:
					cost = str(cost) + "0"

				data["cost"] = cost

				sizes = []
				quantities = []
				percents = []

				for index, info in enumerate(sizesInfo):
					sizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info] })

				for index, info in enumerate(quantitiesInfo):
					quantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info] })

				for index, info in enumerate(percentsInfo):
					percents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info] })

				data["sizes"] = sizes
				data["quantities"] = quantities
				data["percents"] = percents

				orders.append(data)

				if "done" not in data:
					errormsg = "unfinishedOrders"
					status = "unfinishedOrders"

			if errormsg == "":
				totalCost = round((subTotalCost * 0.13) + subTotalCost, 2)
				subTotalCost = round(subTotalCost, 2)

				if len(str(subTotalCost).split(".")[1]) < 2:
					subTotalCost = str(subTotalCost) + "0"

				if len(str(totalCost).split(".")[1]) < 2:
					totalCost = str(totalCost) + "0"

				return { "orders": orders, "name": table["name"], "subTotalCost": subTotalCost, "totalCost": totalCost }
		else:
			status = "noOrders"
	else:
		errormsg = "Table doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/finish_dining/<id>")
def finish_dining(id):
	errormsg = ""
	status = ""

	table = query("select orders from dining_table where id = " + str(id), True).fetchone()

	if table != None:
		query("update dining_table set orders = '[]' where id = " + str(id))

		return { "msg": "succeed" }
	else:
		errormsg = "Table doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
