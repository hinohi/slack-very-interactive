# -*- coding: utf-8 -*-
from logging import getLogger


_logger = getLogger(__name__)


def current_conf():
    from celery.app import app_or_default
    app = app_or_default()
    return app.conf


def init_app(conf):
    from celery.app import app_or_default
    app = app_or_default()
    app.config_from_object(conf)
    _logger.warning('init app done: conf=%s', conf)

