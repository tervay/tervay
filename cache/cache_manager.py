import os, inspect

import bmemcached
import re

mem_cache = bmemcached.Client(
    os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),
    os.environ.get('MEMCACHEDCLOUD_USERNAME'),
    os.environ.get('MEMCACHEDCLOUD_PASSWORD'))

minute = 60
hour = minute * 60
day = hour * 24
week = day * 7

DEFAULT_CACHE_TIME = day * 2


# https://github.com/django/django/blob/master/django/utils/text.py#L219
def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def cache_fn(duration=DEFAULT_CACHE_TIME):
    def decorator(fn):
        def interceptor(*args, **kwargs):
            fn_module = inspect.getmodule(fn)
            fn_str = get_valid_filename(fn.__name__)
            module_str = get_valid_filename(fn_module.__name__)
            args_str = get_valid_filename(str(args))
            kwargs_str = get_valid_filename(str(kwargs))
            key = f'{fn_str}_{module_str}_{args_str}_{kwargs_str}'
            cached_result = mem_cache.get(key=key)
            if cached_result:
                return cached_result

            # noinspection PyArgumentList
            result = fn(*args, **kwargs)
            mem_cache.set(
                key=key,
                value=result,
                time=duration
            )
            return result

        return interceptor

    return decorator
