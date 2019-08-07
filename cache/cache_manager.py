import inspect
import os
import re

import tbapy.models
import redis as redis_package
import json
import zlib

redis = redis_package.from_url(os.environ.get('REDIS_URL'))

minute = 60
hour = minute * 60
day = hour * 24
week = day * 7

DEFAULT_CACHE_TIME = day * 2
DEFAULT_TBA_CACHE_TIME = day * 14


def store(key, value):
    byte_obj = json.dumps(value).encode()
    compressed = zlib.compress(byte_obj)
    redis.set(key, compressed)


def retrieve(key):
    cached_result = redis.get(key)
    if cached_result is not None:
        decompressed = zlib.decompress(cached_result)
        cached_result = json.loads(decompressed)

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


def call(fn, refresh=False, *args, **kwargs):
    fn_str = get_valid_filename(fn.__name__)
    args_str = get_valid_filename(str(args))
    kwargs_str = get_valid_filename(str(kwargs))
    key = f'{fn_str}({args_str}_{kwargs_str})'
    # cached_result = redis.get(key)
    cached_result = retrieve(key)
    if cached_result is not None and not refresh:
        # cached_result = json.loads(zlib.decompress(cached_result))
        return cached_result

    # noinspection PyArgumentList
    result = fn(*args, **kwargs)
    if isinstance(result, tbapy.models._base_model_class):
        result = dict(result)

    # redis.set(key, zlib.compress(json.dumps(result)))
    store(key, result)
    return result


def batch_call(iterable, fn, get_kwargs):
    keys = []
    for x in iterable:
        kwargs = get_kwargs(x)
        args = []
        fn_str = get_valid_filename(fn.__name__)
        args_str = get_valid_filename(str(args))
        kwargs_str = get_valid_filename(str(kwargs))
        key = f'{fn_str}({args_str}_{kwargs_str})'
        keys.append(key)
