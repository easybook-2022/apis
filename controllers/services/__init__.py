from flask import Flask, jsonify, request

app = Flask(__name__)
app.debug = True

@app.route("/", methods=["GET"])
def welcome():
	return jsonify({ "msg": "welcome to services of eatsygo" })

@app.route("/request_appointment", methods=["POST"])
def request_appointment():
	serviceid = "29c9d9fsdkjfslkf-sdjfldsjf"

	return jsonify({ "serviceid": serviceid })
