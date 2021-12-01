from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from twilio.rest import Client
import stripe, mysql.connector, pymysql.cursors

local = True
test_stripe = True

host = 'localhost'
user = 'geottuse'
password = 'G3ottu53?'
database = 'easygo'
server_url = "0.0.0.0"
local_url = "192.168.0.172"
apphost = server_url if local == False else local_url
stripe.api_key = "sk_test_lft1B76yZfF2oEtD5rI3y8dz" if test_stripe == True else "sk_live_AeoXx4kxjfETP2fTR7IkdTYC"
test_sms = False
fee = 0.98

account_sid = "ACc2195555d01f8077e6dcd48adca06d14" if test_sms == True else "AC8c3cd78674e391f0834a086891304e52"
auth_token = "244371c21d9c8e735f0e08dd4c29249a" if test_sms == True else "b7f9e3b46ac445302a4a0710e95f44c1"
mss = "MG376dcb41368d7deca0bda395f36bf2a7"
client = Client(account_sid, auth_token)
