CELERY_TIMEZONE = 'Asia/Tokyo'
BROKER_URL = 'sqla+sqlite:///celery_broker.sqlite'
CELERY_RESULT_BACKEND = 'db+sqlite:///celery_backend.sqlite'
