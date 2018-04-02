from flask import Flask

from . import hello
from . import simple

web = Flask(__name__)
web.register_blueprint(hello.app)
web.register_blueprint(simple.app, url_prefix='/simple')
