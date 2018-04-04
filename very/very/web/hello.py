from logging import getLogger

from flask import Blueprint

_logger = getLogger(__name__)
app = Blueprint('general', __name__)


@app.route('/')
def hello():
    _logger.warning('call hello')
    return 'hello'


@app.route('/about')
def about():
    _logger.info('call about')
    return 'about'
