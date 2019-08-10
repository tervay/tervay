import inspect
import os
import re

import tbapy.models
import redis as redis_package
from redis.client import Pipeline

import json
import zlib

redis = redis_package.from_url(os.environ.get('REDIS_URL'))

minute = 60
hour = minute * 60
day = hour * 24
week = day * 7

DEFAULT_CACHE_TIME = day * 2
DEFAULT_TBA_CACHE_TIME = day * 14


def preprocess(x):
    return zlib.compress(json.dumps(x).encode())


def postprocess(x):
    return json.loads(zlib.decompress(x))


def store(key, value, pipe=None):
    compressed = preprocess(value)
    if pipe is None:
        redis.set(key, compressed)
    else:
        pipe.set(key, compressed)


def retrieve(key, pipe=None):
    if pipe is None:
        cached_result = redis.get(key)
        if cached_result is not None:
            cached_result = postprocess(cached_result)

        return cached_result
    else:
        cached_result = pipe.get(key)
        return cached_result


# https://github.com/django/django/blob/master/django/utils/text.py#L219
def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    s = str(s).lstrip('/').replace('/', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def cache_frame(frame, duration=DEFAULT_CACHE_TIME):
    # Check that we aren't doing this recursively...
    parent_parent_frame = inspect.getouterframes(frame)[1][0]
    _, _, parent_parent_fn_name, _, _ = inspect.getframeinfo(
        parent_parent_frame)
    if parent_parent_fn_name == cache_frame.__name__:
        return None, None

    # Get the original function and what was passed to it in order to call it
    _, _, _, vals = inspect.getargvalues(frame)
    filename, _, fn_name, _, _ = inspect.getframeinfo(frame)
    orig_frame = inspect.getouterframes(frame)[0][0]
    orig_fn = orig_frame.f_globals[fn_name]

    filename_str = get_valid_filename(filename)
    fn_name_str = get_valid_filename(fn_name)
    vals_str = get_valid_filename(str(vals))
    key = f'{filename_str}::{fn_name_str}({vals_str})'
    # cached_result = redis.get(key)
    cached_result = retrieve(key)

    # if theres a cache hit, return it
    if cached_result is not None:
        # cached_result = json.loads(zlib.decompress(cached_result))
        return cached_result, True

    # if not, store it in the cache
    result = orig_fn(**vals)
    # redis.set(key, zlib.compress(json.dumps(result)))
    store(key, result)
    return result, False


def call(fn, refresh=False, pipe=None, *args, **kwargs):
    fn_str = get_valid_filename(fn.__name__)
    args_str = get_valid_filename(str(args))
    kwargs_str = get_valid_filename(str(kwargs))
    key = f'{fn_str}({args_str}_{kwargs_str})'
    # cached_result = redis.get(key)
    cached_result = retrieve(key, pipe=pipe)
    if cached_result is not None and not refresh:
        # cached_result = json.loads(zlib.decompress(cached_result))
        return cached_result

    # noinspection PyArgumentList
    result = fn(*args, **kwargs)
    if isinstance(result, tbapy.models._base_model_class):
        result = dict(result)

    # redis.set(key, zlib.compress(json.dumps(result)))
    store(key, result, pipe=pipe)
    return result


def batch_call(iterable, fn, get_args, get_kwargs):
    with redis.pipeline() as pipe:
        print('Building first pipe call')
        keys = []
        for x in iterable:
            args = get_args(x)
            kwargs = get_kwargs(x)
            fn_str = get_valid_filename(fn.__name__)
            args_str = get_valid_filename(str(args))
            kwargs_str = get_valid_filename(str(kwargs))
            key = f'{fn_str}({args_str}_{kwargs_str})'
            keys.append(key)

        print('Retrieving based on first calls')
        for key in keys:
            retrieve(key, pipe=pipe)

        print('Executing first pipe call')
        res1 = pipe.execute()
        results = {}
        for key, res in zip(keys, res1):
            if res is not None:
                res = postprocess(res)
            results[key] = res

        print('Building second pipe call')
        for x in iterable:
            args = get_args(x)
            kwargs = get_kwargs(x)
            fn_str = get_valid_filename(fn.__name__)
            args_str = get_valid_filename(str(args))
            kwargs_str = get_valid_filename(str(kwargs))
            key = f'{fn_str}({args_str}_{kwargs_str})'
            if results[key] is None:
                results[key] = call(fn, *args, **kwargs, pipe=pipe)

        print('Executing second pipe call')
        pipe.execute()

        return list(results.values())
