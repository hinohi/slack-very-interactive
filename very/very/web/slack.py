# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify

from very.core.utils import kvs


app = Blueprint('slack', __name__)


@app.route('/interactive', methods=['POST'])
def slack_interactive():
    from flask import request
    key = kvs.incr('slack-key')
    kvs.set(key, request.data)
    print(key, request.data)
    return 'OK'


@app.route('/debug/<int:key>')
def slack_debug(key):
    return jsonify(kvs.get(key) or {})
