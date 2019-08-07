import inspect
import os
import re

import bmemcached
import tbapy.models

mem_cache = bmemcached.Client(
    os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),
    os.environ.get('MEMCACHEDCLOUD_USERNAME'),
    os.environ.get('MEMCACHEDCLOUD_PASSWORD'))

minute = 60
hour = minute * 60
day = hour * 24
week = day * 7

DEFAULT_CACHE_TIME = day * 2
DEFAULT_TBA_CACHE_TIME = day * 14


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
    cached_result = mem_cache.get(key)

    # if theres a cache hit, return it
    if cached_result is not None:
        return cached_result, True

    # if not, store it in the cache
    result = orig_fn(**vals)
    mem_cache.set(key=key, value=result, time=duration)
    return result, False


def call(fn, refresh=False, *args, **kwargs):
    fn_str = get_valid_filename(fn.__name__)
    args_str = get_valid_filename(str(args))
    kwargs_str = get_valid_filename(str(kwargs))
    key = f'{fn_str}({args_str}_{kwargs_str})'
    cached_result = mem_cache.get(key)
    if cached_result is not None and not refresh:
        return cached_result

    # noinspection PyArgumentList
    result = fn(*args, **kwargs)
    if isinstance(result, tbapy.models._base_model_class):
        result = dict(result)

    mem_cache.set(key=key, value=result, time=DEFAULT_TBA_CACHE_TIME)
    return result
