from flask import Flask

from very.core import init_app
from very.very import conf
from . import hello
from . import simple

init_app(conf)

web = Flask(__name__)
web.register_blueprint(hello.app)
web.register_blueprint(simple.app, url_prefix='/simple')
