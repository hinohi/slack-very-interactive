# -*- coding: utf-8 -*-
from functools import lru_cache

import redis


@lru_cache
def _kvs() -> redis.StrictRedis:
    from very.core import current_conf

    conf = current_conf()
    redis_url = getattr(conf, 'REDIS_URL', None)
    if not redis_url:
        raise ValueError('REDIS_URL not configured')
    return redis.StrictRedis.from_url(redis_url)


def set(key, value, as_pickle=True):
    if as_pickle:
        import pickle
        value = pickle.dumps(value, -1)
    return _kvs().set(key, value)


def get(key, as_pickle=True):
    value = _kvs().get(key)
    if value and as_pickle:
        import pickle
        value = pickle.loads(value)
    return value


def incr(key, amount=1):
    _kvs().incr(key, amount)


def decr(key, amount=1):
    _kvs().decr(key, amount)
