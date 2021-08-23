# backend - flask
Get customers in front of restaurants' door in seconds

# dependencies to install
pip install flask werkzeug flask-cors Flask-SQLAlchemy Flask-Migrate gunicorn mysql-connector-python pymysql mysqlclient haversine stripe twilio

# add new column to table
flask db init (create migrations folder)
flask db migrate -m "update db schema"
flask db upgrade
