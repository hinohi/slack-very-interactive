# -*- coding: utf-8 -*-
from flask import Blueprint, json

from very.core.tasks import TaskRequest


app = Blueprint('slack', __name__)


@app.route('/interactive', method=['POST'])
def slack_interactive():
    from flask import request
    body = json.dumps(request.json, ensure_ascii=False)
    TaskRequest('kvs.create').async('slack', body)
    return 'OK'
