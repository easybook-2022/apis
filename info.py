import pymysql.cursors, json, os
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from haversine import haversine

test = True

local = test
test_sms = test
send_msg = True
push_notif = True

host = 'localhost'
user = 'geottuse'
password = 'G3ottu53?'
database = 'easygo'
server_url = "0.0.0.0"
local_url = "192.168.0.172"
apphost = server_url if test == False else local_url
googleAdApi = "U9nEo26pxqI1o-fQNp2c4A"

account_sid = "ACc2195555d01f8077e6dcd48adca06d14" if test_sms == True else "AC8c3cd78674e391f0834a086891304e52"
auth_token = "244371c21d9c8e735f0e08dd4c29249a" if test_sms == True else "b7f9e3b46ac445302a4a0710e95f44c1"
mss = "MG376dcb41368d7deca0bda395f36bf2a7"
client = Client(account_sid, auth_token)

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

def getRanStr():
	strid = ""

	for k in range(6):
		strid += str(randint(0, 9))

	return strid

def pushInfo(to, title, body, data):
	return PushMessage(to=to, title=title, body=body, data=data)

def push(messages):
	if push_notif == True:
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

def writeToFile(uri, name):
	binary_data = a2b_base64(uri)

	fd = open(os.path.join("static", name), 'wb')
	fd.write(binary_data)
	fd.close()
