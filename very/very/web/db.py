# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, json

from very.core.tasks import TaskRequest
from very.core.utils import kvs

app = Blueprint('db', __name__)


@app.route('/kvs/<key>')
def get_kvs(key):
    res = TaskRequest('kvs.get')(key)
    return jsonify(res or {})


@app.route('/kvs/<key>', methods=['POST'])
def create_kvs(key):
    from flask import request
    body = json.dumps(request.json, ensure_ascii=False)
    res = TaskRequest('kvs.create')(key, body)
    return jsonify(res)


@app.route('/kvs/<key>', methods=['DELETE'])
def delete_kvs(key):
    res = TaskRequest('kvs.delete')(key)
    return jsonify(res or {})
