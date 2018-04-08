from flask import Flask

from very.core import init_app
from very.very import conf
from . import hello
from . import simple
from . import db
from . import slack

init_app(conf)

web = Flask(__name__)
web.register_blueprint(hello.app)
web.register_blueprint(simple.app, url_prefix='/simple')
web.register_blueprint(db.app, url_prefix='/db')
web.register_blueprint(slack.app, url_prefix='/slack')
