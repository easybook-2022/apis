import datetime
from flask import request
from flask_cors import CORS
from info import *
from models import *

cors = CORS(app)

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
			tableOrders = []

			if len(orders) > 0:
				numDone = 0

				for order in orders:
					if "finish" not in order:
						numDone = numDone + 1 if "done" in order else numDone

						sizes = order["sizes"]
						quantities = order["quantities"]
						percents = order["percents"]
						extras = order["extras"]

						product = query("select * from product where id = " + str(order["productId"]), True).fetchone()
						productOptions = json.loads(product["options"])
						productSizes = productOptions["sizes"]
						productQuantities = productOptions["quantities"]
						productPercents = productOptions["percents"]
						productExtras = productOptions["extras"]

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

						extrasInfo = {}
						for info in productExtras:
							if info["input"] in extras:
								extrasInfo[info["input"]] = float(info["price"]) if "price" in info else 0

						order["name"] = product["number"] if product["number"] != "" else product["name"]

						sizes = []
						quantities = []
						percents = []
						extras = []

						for index, info in enumerate(sizesInfo):
							sizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info] })

						for index, info in enumerate(quantitiesInfo):
							quantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info] })

						for index, info in enumerate(percentsInfo):
							percents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info] })

						for index, info in enumerate(extrasInfo):
							extras.append({ "key": "extra-" + str(index), "input": info, "price": extrasInfo[info] })

						order["sizes"] = sizes
						order["quantities"] = quantities
						order["percents"] = percents
						order["extras"] = extras
						order["tableName"] = data["name"]
						order["tableId"] = data["tableId"]
						order["finish"] = True if "done" in order else False

						tableOrders.append(order)

				if numDone < len(orders) and len(tableOrders) > 0:
					tables.append({ "id": data["name"], "key": "table-" + str(len(tables)), "orders": tableOrders }) 

		return { "tables": tables }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_qr_code/<id>")
def get_qr_code(id):
	errormsg = ""
	status = ""

	table = query("select locationId, name, orders, status from dining_table where tableId = '" + id + "'", True).fetchone()

	if table != None:
		location = query("select name from location where id = " + str(table["locationId"]), True).fetchone()

		if table["status"] == "finish":
			query("update dining_table set status = 'active' where tableId = '" + id + "'")

		orders = json.loads(table["orders"])
		numOrders = 0

		for order in orders:
			numOrders += 1
				
		return { "name": table["name"], "locationid": table["locationId"], "locationName": location["name"], "status": table["status"], "numOrders": numOrders }
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
		table = query("select * from dining_table where name = '" + tableName + "' and locationId = " + str(locationid), True).fetchone()

		if table == None:
			tableIdExist = query("select count(*) as num from dining_table where tableId = '" + tableid + "' and locationId = " + str(locationid), True).fetchone()["num"]

			while tableIdExist > 0:
				tableid = getId()

				tableIdExist = query("select count(*) as num from dining_table where tableId = '" + tableid + "' and locationId = " + str(locationid), True).fetchone()["num"]
		else:
			status = "exist"
			errormsg = "Table already exist"

		if errormsg == "":
			data = { "tableId": tableid, "locationId": locationid, "name": tableName, "orders": '[]', "status": "finish" }
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

	newOrders = json.loads(content['orders'])
	tableid = content['tableid']

	table = query("select * from dining_table where tableId = '" + tableid + "'", True).fetchone()

	if table != None:
		location = query("select owners from location where id = " + str(table["locationId"]), True).fetchone()
		owners = json.loads(location["owners"])
		orders = json.loads(table["orders"])
		receiver = []

		for owner in owners:
			receiver.append("owner" + str(owner))

		for newOrder in newOrders:
			key = newOrder["key"]
			existingKey = query("select count(*) as num from dining_table where orders like '%\"key\": \"" + key + "\"%'", True).fetchone()["num"]

			while existingKey == True:
				key = getId()

			orders.append({
				"key": key,
				"productId": newOrder["productId"],
				"sizes": newOrder["sizes"],
				"quantities": newOrder["quantities"],
				"percents": newOrder["percents"],
				"extras": newOrder["extras"],
				"image": newOrder["image"],
				"quantity": newOrder["quantity"],
				"note": newOrder["note"]
			})

		query("update dining_table set orders = '" + pymysql.converters.escape_string(json.dumps(orders)) + "' where tableId = '" + tableid + "'")

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
	tableid = content['tableid']

	table = query("select orders from dining_table where tableId = '" + str(tableid) + "'", True).fetchone()

	if table != None:
		orders = json.loads(table["orders"])
		numDone = 0

		for order in orders:
			if order["key"] == orderid:
				order["done"] = True

			numDone = numDone + 1 if "done" in order else numDone

		if numDone == len(orders):
			for order in orders:
				order["finish"] = True

		query("update dining_table set orders = '" + pymysql.converters.escape_string(json.dumps(orders)) + "' where tableId = '" + str(tableid) + "'")

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
				extras = data["extras"]

				product = query("select * from product where id = " + str(data["productId"]), True).fetchone()
				productOptions = json.loads(product["options"])
				productSizes = productOptions["sizes"]
				productQuantities = productOptions["quantities"]
				productPercents = productOptions["percents"]
				productExtras = productOptions["extras"]

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

				extrasInfo = {}
				for info in productExtras:
					if info["input"] in extras:
						extrasInfo[info["input"]] = float(info["price"]) if "price" in info else 0

				data["name"] = product["number"] if product["number"] != "" else product["name"]
				cost = 0.00

				if product["price"] != "":
					subTotalCost += int(data["quantity"]) * float(product["price"])
					cost = round(int(data["quantity"]) * float(product["price"]), 2)
				else:
					for size in sizes:
						subTotalCost += int(data["quantity"]) * sizesInfo[size]
						cost = round(int(data["quantity"]) * sizesInfo[size], 2)

					for quantity in quantities:
						subTotalCost += int(data["quantity"]) * float(quantitiesInfo[quantity])
						cost = round(int(data["quantity"]) * float(quantitiesInfo[quantity]), 2)

				for percent in percents:
					subTotalCost += int(data["quantity"]) * float(percentsInfo[percent])
					cost += round(int(data["quantity"]) * float(percentsInfo[percent]), 2)

				for extra in extras:
					subTotalCost += int(data["quantity"]) * float(extrasInfo[extra])
					cost += round(int(data["quantity"]) * float(extrasInfo[extra]), 2)

				if len(str(cost).split(".")[1]) < 2:
					cost = str(cost) + "0"

				sizes = []
				quantities = []
				percents = []
				extras = []

				for index, info in enumerate(sizesInfo):
					sizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info] })

				for index, info in enumerate(quantitiesInfo):
					quantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info] })

				for index, info in enumerate(percentsInfo):
					percents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info] })

				for index, info in enumerate(extrasInfo):
					extras.append({ "key": "extra-" + str(index), "input": info, "price": extrasInfo[info] })

				data["cost"] = cost
				data["sizes"] = sizes
				data["quantities"] = quantities
				data["percents"] = percents
				data["extras"] = extras

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

@app.route("/view_table_orders/<tableId>")
def view_table_orders(tableId):
	errormsg = ""
	status = ""

	table = query("select name, orders from dining_table where tableId = '" + tableId + "'", True).fetchone()

	if table != None:
		datas = json.loads(table["orders"])
		orders = []

		for data in datas:
			sizes = data["sizes"]
			quantities = data["quantities"]
			percents = data["percents"]
			extras = data["extras"]

			product = query("select * from product where id = " + str(data["productId"]), True).fetchone()
			productOptions = json.loads(product["options"])
			productSizes = productOptions["sizes"]
			productQuantities = productOptions["quantities"]
			productPercents = productOptions["percents"]
			productExtras = productOptions["extras"]

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

			extrasInfo = {}
			for info in productExtras:
				if info["input"] in extras:
					extrasInfo[info["input"]] = float(info["price"]) if "price" in info else 0

			data["name"] = product["name"]
			cost = 0.00

			if product["price"] != "":
				cost = round(int(data["quantity"]) * float(product["price"]), 2)
			else:
				for size in sizes:
					cost += round(int(data["quantity"]) * sizesInfo[size], 2)

				for quantity in quantities:
					cost += round(int(data["quantity"]) * float(quantitiesInfo[quantity]), 2)

			for percent in percents:
				cost += round(int(data["quantity"]) * float(percentsInfo[percent]), 2)

			for extra in extras:
				cost += round(int(data["quantity"]) * float(extrasInfo[extra]), 2)

			if len(str(cost).split(".")[1]) < 2:
				cost = str(cost) + "0"

			data["cost"] = cost

			sizes = []
			quantities = []
			percents = []
			extras = []

			for index, info in enumerate(sizesInfo):
				sizes.append({ "key": "size-" + str(index), "name": info, "price": sizesInfo[info] })

			for index, info in enumerate(quantitiesInfo):
				quantities.append({ "key": "quantity-" + str(index), "input": info, "price": quantitiesInfo[info] })

			for index, info in enumerate(percentsInfo):
				percents.append({ "key": "percent-" + str(index), "input": info, "price": percentsInfo[info] })

			for index, info in enumerate(extrasInfo):
				extras.append({ "key": "extra-" + str(index), "input": info, "price": extrasInfo[info] })

			data["sizes"] = sizes
			data["quantities"] = quantities
			data["percents"] = percents
			data["extras"] = extras
			data["price"] = product["price"]

			orders.append(data)

		return { "orders": orders, "name": table["name"] }
	else:
		errormsg = "Table doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/finish_dining", methods=["POST"])
def finish_dining():
	content = request.get_json()
	errormsg = ""
	status = ""

	tableid = content['tableid']
	time = json.dumps(content['time'])

	table = query("select locationId, tableId, orders from dining_table where id = " + str(tableid), True).fetchone()

	if table != None:
		data = {
			"tableId": table["tableId"], "orders": pymysql.converters.escape_string(table["orders"]), 
			"time": time, "service": "{}", "locationId": table["locationId"]
		}
		columns = []
		insert_data = []

		for key in data:
			columns.append(key)
			insert_data.append("'" + str(data[key]) + "'")

		query("insert into income_record (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")")
		query("update dining_table set orders = '[]', status = 'finish' where id = " + str(tableid))

		return { "msg": "succeed" }
	else:
		errormsg = "Table doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
