from flask import Flask, jsonify, request

app = Flask(__name__)
app.debug = True

@app.route("/", methods=["GET"])
def welcome():
	return jsonify({ "msg": "welcome to users of eatsygo" })

@app.route("/login", methods=["POST"])
def login():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']
	userid = "19c0sc-ckcvkckc"

	return jsonify({ "id": userid })

@app.route("/register", methods=["POST"])
def register():
	content = request.get_json()

	cellnumber = content['cellnumber']
	password = content['password']
	userid = "19c0sc-ckcvkckc"

	return jsonify({ "id": userid })
