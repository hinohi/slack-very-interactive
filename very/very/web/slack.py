# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify

from very.core.tasks import TaskRequest


app = Blueprint('slack', __name__)