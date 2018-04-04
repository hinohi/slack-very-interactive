from logging import getLogger

from celery import Celery

_logger = getLogger(__name__)

celery = Celery(__name__)


def task(name, **options):
    def wrapper(func):
        from functools import wraps

        _logger.info('register task: name=%s options=%s', name, options)

        @wraps(func)
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                import traceback
                _logger.error("unbounded error occur calling: %s\n%s",
                              e, traceback.format_exc())
                return traceback.extract_stack()

        return celery.task(name=name, **options)(inner)

    return wrapper


class TaskRequest:

    def __init__(self, name, **options):
        self.name = name
        self.options = options

    def __call__(self, *args, **kwargs):
        return celery.send_task(self.name,
                                args=args,
                                kwargs=kwargs,
                                **self.options).get()

    def async(self, *args, **kwargs):
        return celery.send_task(self.name,
                                args=args,
                                kwargs=kwargs,
                                **self.options)
