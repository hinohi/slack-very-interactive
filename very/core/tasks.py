from logging import getLogger

from celery import Celery

_logger = getLogger(__name__)

celery = Celery(__name__)


def task(name, **kwargs):
    def wrapper(func):
        _logger.info('register task: name=%s option=%s', name, kwargs)
        return celery.task(name=name, **kwargs)(func)
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
