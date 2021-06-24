from flask import Flask, jsonify, request

app = Flask(__name__)
app.debug = True

@app.route("/", methods=["GET"])
def welcome():
	return jsonify({ "msg": "welcome to services of eatsygo" })

@app.route("/request_appointment", methods=["POST"])
def request_appointment():
	serviceid = "29c9d9fsdkjfslkf-sdjfldsjf"

	return jsonify({ "serviceid": serviceid, "action": "request appointment" })

@app.route("/cancel_purchase", methods=["POST"])
def cancel_purchase():
	orderid = "dsjfkldsjdsfsd9fsdjfkdsjf"

	return jsonify({ "orderid": orderid, "action": "cancel purchase" })

@app.route("/confirm_purchase", methods=["POST"])
def confirm_purchase():
	orderid = "sdjfklsdsdsdfidsfsddkjf"

	return jsonify({ "orderid": orderid, "action": "confirm purchase" })

@app.route("/cancel_request", methods=["POST"])
def cancel_request():
	serviceid = "29c9d9fsdkjfslkf-sdjfldsjf"

	return jsonify({ "serviceid": serviceid, "action": "cancel request" })

@app.route("/confirm_request", methods=["POST"])
def confirm_request():
	serviceid = "29c9d9fsdkjfslkf-sdjfldsjf"

	return jsonify({ "serviceid": serviceid, "action": "confirm request" })
