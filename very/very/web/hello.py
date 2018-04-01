from flask import Blueprint

app = Blueprint('general', __name__)


@app.route('/')
def hello():
    return 'hello'


@app.route('/about')
def about():
    return 'about'
