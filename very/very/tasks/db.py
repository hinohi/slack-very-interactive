# -*- coding: utf-8 -*-
from very.core.tasks import task
from very.very.model import KVS


def session_wrapper(func):
    from functools import wraps
    from sqlalchemy.exc import OperationalError

    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        import traceback
        from very.very.model import session

        res = {}
        try:
            error = None
            for _ in range(3):
                try:
                    res = func(*args, **kwargs)
                    break
                except OperationalError as e:
                    error = e
                    time.sleep(0.1)
            else:
                if error:
                    raise error
        except Exception as e:
            session.rollback()
            res = {
                'error': str(e),
                'traceback': [
                    [l[0], l[1], l[2], l[3]]
                    for l in traceback.extract_stack()
                ]
            }
        finally:
            session.close()
        return res
    return wrapper


@task('kvs.get')
@session_wrapper
def get_kvs(kvs_id):
    from very.very.model import session
    kv = session.query(KVS).get(kvs_id)
    if kv is None:
        return None
    return kv.export_dict()


@task('kvs.get_by_key')
@session_wrapper
def get_kvs_by_key(key):
    from very.very.model import session
    kv_list = session.query(KVS).filter(KVS.key == key).all()
    return [kv.export_dict() for kv in kv_list]


@task('kvs.create')
@session_wrapper
def create_kvs(key, value):
    from very.very.model import session
    kv = KVS(key=key, value=value)
    session.add(kv)
    session.flush()
    return kv.export_dict()


@task('kvs.delete')
@session_wrapper
def delete_kvs(kvs_id):
    from very.very.model import session
    kv = session.query(KVS).get(kvs_id)
    if kv is not None:
        session.delete(kv)
