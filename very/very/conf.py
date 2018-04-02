import os
from very.core.conf import *


_redis_url = os.environ.get('REDIS_URL')
if _redis_url:
    BROKER_URL = _redis_url
    CELERY_RESULT_BACKEND = _redis_url

CELERY_IMPORTS = (
    'very.very.tasks.simple',
)
