# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, json

from very.core.tasks import TaskRequest

app = Blueprint('db', __name__)


@app.route('/kvs/<int:kvs_id>')
def get_kvs(kvs_id):
    res = TaskRequest('kvs.get')(kvs_id)
    return jsonify(res or {})


@app.route('/kvs/<key>/')
def get_kvs_by_key(key):
    res = TaskRequest('kvs.get_by_key')(key)
    return jsonify(res or [])


@app.route('/kvs/<key>/', methods=['POST'])
def create_kvs(key):
    from flask import request
    body = json.dumps(request.json, ensure_ascii=False)
    res = TaskRequest('kvs.create')(key, body)
    return jsonify(res)


@app.route('/vls/<int:kvs_id>', methods=['DELETE'])
def delete_kvs(kvs_id):
    res = TaskRequest('kvs.delete')(kvs_id)
    return jsonify(res or {})
