# backend - flask
Get customers in front of restaurants' door in seconds

# dependencies
install - flask werkzeug flask-cors Flask-SQLAlchemy Flask-Migrate gunicorn mysql-connector-python pymysql mysqlclient haversine stripe twilio cryptography

# server setup
install - wheel uwsgi

pip install -r requirements.txt

# add new column to table
flask db init (create migrations folder)
flask db migrate -m "update db schema"
flask db upgrade
