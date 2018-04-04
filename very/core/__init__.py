from logging import getLogger


_logger = getLogger(__name__)


def current_conf():
    from celery import current_app

    app = current_app()
    return app.current_conf()


def init_app(conf):
    from celery.app import app_or_default
    app = app_or_default()
    app.config_from_object(conf)
    _logger.warning('init app done: conf=%s', conf)
    _logger.warning('BROKER_URL=%s', getattr(conf, 'BROKER_URL', None))
    _logger.warning('CELERY_RESULT_BACKEND=%s', getattr(conf, 'CELERY_RESULT_BACKEND', None))
