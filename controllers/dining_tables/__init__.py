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
		datas = query("select * from dining_table where locationId = " + str(id), True).fetchall()
		tables = []

		for data in datas:
			orders = json.loads(data["orders"])
			numOrders = 0

			for order in orders:
				if "done" not in order:
					numOrders += 1

			tables.append({ "key": str(data["id"]), "tableid": data["tableId"], "name": data["name"], "numOrders": numOrders })

		return { "tables": tables }
	else:
		errormsg = ""
		status = ""

	return { "errormsg": errormsg, "status": status }, 400

@app.route("/get_table/<id>")
def get_table(id):
	errormsg = ""
	status = ""

	table = query("select locationId, name from dining_table where tableId = '" + str(id) + "'", True).fetchone()

	if table != None:
		return { "name": table["name"], "locationid": table["locationId"] }
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
		numExisttable = query("select count(*) as num from dining_table where lower(replace(name, ' ', '')) = '" + tableName + "'", True).fetchone()["num"]

		while numExisttable > 0:
			tableName = getId()

			numExisttable = query("select count(*) as num from dining_table where lower(replace(name, ' ', '')) = '" + tableName + "'", True).fetchone()["num"]

		if errormsg == "":
			data = { "tableId": tableid, "locationId": locationid, "name": tableName, "orders": '[]', "status": "active" }
			columns = []
			insert_data = []

			for key in data:
				columns.append(key)
				insert_data.append("'" + str(data[key]) + "'")

			id = query("insert into dining_table (" + ", ".join(columns) + ") values (" + ", ".join(insert_data) + ")", True).lastrowid

			return { "msg": "succeed" }
	else:
		errormsg = "Location doesn't exist"

	return { "errormsg": errormsg, "status": status }

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
	image = content['image']
	quantity = int(content['quantity'])

	table = query("select * from dining_table where tableId = '" + str(tableid) + "' and status = 'active'", True).fetchone()

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
			"image": image,
			"quantity": quantity
		})

		query("update dining_table set orders = '" + json.dumps(orders) + "', status = 'active' where id = " + str(table["id"]))

		return { "msg": "succeed", "receiver": receiver }
	else:
		errormsg = "Table doesn't exist"

	return { "errormsg": errormsg, "status": status }

@app.route("/get_table_orders/<id>")
def get_table_orders(id):
	errormsg = ""
	status = ""

	table = query("select orders from dining_table where id = " + str(id), True).fetchone()

	if table != None:
		datas = json.loads(table["orders"])
		orders = []

		if len(datas) > 0:
			for data in datas:
				if "done" not in data:
					product = query("select * from product where id = " + str(data["productId"]), True).fetchone()
					data["name"] = product["name"]

					if product["price"] != '':
						data["cost"] = int(data["quantity"]) * float(product["price"])
					else:
						sizes = data["sizes"]

						for size in sizes:
							if size["selected"] == True:
								data["cost"] = int(data["quantity"]) * float(size["price"])

					orders.append(data)

			return { "orders": orders }
		else:
			status = "noOrders"
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

	table = query("select orders from dining_table where id = " + str(tableid), True).fetchone()

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

	table = query("select orders from dining_table where id = " + str(id), True).fetchone()

	if table != None:
		datas = json.loads(table["orders"])
		subTotalCost = 0.00
		orders = []

		if len(datas) > 0:
			for data in datas:
				product = query("select * from product where id = " + str(data["productId"]), True).fetchone()
				data["name"] = product["name"]
				sizes = data["sizes"]

				if len(sizes) > 0:
					for size in sizes:
						if size["selected"] == True:
							subTotalCost += int(data["quantity"]) * float(size["price"])
							data["cost"] = int(data["quantity"]) * float(size["price"])
				else:
					subTotalCost += int(data["quantity"]) * float(product["price"])
					data["cost"] = int(data["quantity"]) * float(product["price"])

				orders.append(data)

				if "done" not in data:
					errormsg = "unfinishedOrders"
					status = "unfinishedOrders"

			if errormsg == "":
				totalCost = (subTotalCost * 0.13) + subTotalCost

				return { "orders": orders, "subTotalCost": round(subTotalCost, 2), "totalCost": round(totalCost, 2) }
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
		query("update dining_table set orders = '[]', status = 'inactive' where id = " + str(id))

		return { "msg": "succeed" }
	else:
		errormsg = "Table doesn't exist"

	return { "errormsg": errormsg, "status": status }, 400
