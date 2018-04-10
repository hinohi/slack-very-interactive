# -*- coding: utf-8 -*-
from flask import Blueprint

from very.core.utils import kvs


app = Blueprint('slack', __name__)


@app.route('/interactive', method=['POST'])
def slack_interactive():
    from flask import request
    key = kvs.incr('slack-key')
    kvs.set(key, request.json)
    return 'OK'


@app.route('/debug/<int:key>')
def slack_interactive(key):
    return kvs.get(key)
