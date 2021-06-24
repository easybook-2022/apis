from flask import Flask, request, jsonify
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from controllers.users import app as users_controller
from controllers.services import app as services_controller

app = Flask(__name__)
app.debug = True

app.wsgi_app = DispatcherMiddleware(None, {
	'/users': users_controller,
	'/services': services_controller
})

if __name__ == "__main__":
	run_simple("localhost", 5000, app, use_reloader=True, use_debugger=True, use_evalex=True)
