import pymysql.cursors, json, os, paramiko, pandas
from twilio.rest import Client
from exponent_server_sdk import PushClient, PushMessage
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint
from haversine import haversine
from sshtunnel import SSHTunnelForwarder
from os.path import expanduser
from binascii import a2b_base64

test = True

local = test
send_text = test == False
push_notif = test == False

host = 'localhost'
user = 'geottuse'
password = 'G3ottu53?'
database = 'easybook'
server_url = "0.0.0.0"
local_url = "10.0.0.60"
apphost = server_url if test == False else local_url
googleAdApi = "U9nEo26pxqI1o-fQNp2c4A"
photoUrl = "http://" + local_url + ":5001/flask/static/"

account_sid = "AC8c3cd78674e391f0834a086891304e52" if send_text == True else "ACc2195555d01f8077e6dcd48adca06d14"
auth_token = "b7f9e3b46ac445302a4a0710e95f44c1" if send_text == True else "244371c21d9c8e735f0e08dd4c29249a"
mss = "MG376dcb41368d7deca0bda395f36bf2a7"
client = Client(account_sid, auth_token)

monthToIndex = {'January': 0, 'February': 1, 'March': 2, 'April': 3, 'May': 4, 'June': 5, 'July': 6, 'August': 7, 'September': 8, 'October': 9, 'November': 10, 'December': 11}
dayToIndex = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}
indexToMonth = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
indexToDay = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

#monthsObj
#daysObj
#monthsArr
#daysArr



# ssh_host = '159.203.13.53'
# ssh_username = 'root'
# ssh_password = 'qwerty'

# sql_username = 'geottuse'
# sql_password = 'G3ottu53?'
# sql_database = 'easybook'

# key = paramiko.RSAKey.from_private_key_file("./id_rsa.pem")

# tunnel = SSHTunnelForwarder(
# 	(ssh_host, 22),
#   ssh_username="root",
#   ssh_pkey=key,
#   ssh_private_key_password="qwerty",
#   remote_bind_address=('127.0.0.1', 3306)
# )

# tunnel.start()

# print("connected")

# sdbconn = pymysql.connect(
# 	host=host, user=user,
# 	password=password, db=database,
# 	charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor, 
# 	port=tunnel.local_bind_port
# )
# scursorobj = sdbconn.cursor()

# print("database established")

def query(sql, output = False):
	dbconn = pymysql.connect(
		host=host, user=user,
		password=password, db=database,
		charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor, 
		autocommit=True
	)
	cursorobj = dbconn.cursor()
	cursorobj.execute(sql)

	dbconn.close()

	if output == True:
		return cursorobj

def getId():
	letters = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
	]
	char = ""

	for k in range(randint(10, 20)):
		if randint(0, 9) % 2 == 0:
			char += str(randint(0, 9))
		else:
			char += (letters[randint(0, 25)]).upper()
	        
	return char

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
