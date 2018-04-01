from celery import Celery

NAME = 'very'

celery = Celery(
    NAME,
    broker='sqla+sqlite:///celery_broker.sqlite',
    backend='db+sqlite:///celery_backend.sqlite',
)


def task(name, **kwargs):
    def wrapper(func):
        return celery.task(name=f'{NAME}.{name}', **kwargs)(func)
    return wrapper


class TaskRequest:

    def __init__(self, name, **options):
        self._task = celery.tasks[f'{NAME}.{name}']
        self._options = options

    def __call__(self, *args, **kwargs):
        return self._task.apply_async(args, kwargs, **self._options).get()

    def async(self, *args, **kwargs):
        return self._task.apply_async(args, kwargs, **self._options)
