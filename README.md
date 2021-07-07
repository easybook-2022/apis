# backend - flask
Get customers in front of restaurants' door in seconds

# dependencies to install
pip install flask werkzeug flask-cors Flask-SQLAlchemy Flask-Migrate gunicorn mysql-connector-python pymysql

# add new column to table
flask db init
flask db migrate -m "message"
flask db upgrade
