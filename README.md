# backend - flask
Get customers in front of restaurants' door in seconds

# dependencies to install
pip install flask werkzeug flask-cors flask_mysqldb Flask-SQLAlchemy Flask-Migrate gunicorn

# add new column to table
flask db init flask db migrate -m "Initial migration." flask db upgrade
