from flask import Blueprint, jsonify

from very.core.tasks import TaskRequest

app = Blueprint('simple', __name__)


@app.route('/add/<int:x>/<int:y>')
def add(x, y):
    resp = TaskRequest('add')(x, y)
    return jsonify(result=resp)


@app.route('/sub/<int:x>/<int:y>')
def sub(x, y):
    resp = TaskRequest('sub')(x, y)
    return jsonify(result=resp)


@app.route('/mul/<int:x>/<int:y>')
def mul(x, y):
    resp = TaskRequest('mul')(x, y)
    return jsonify(result=resp)


@app.route('/div/<int:x>/<int:y>')
def div(x, y):
    resp = TaskRequest('div')(x, y)
    return jsonify(result=resp)
