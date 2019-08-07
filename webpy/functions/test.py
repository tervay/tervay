import inspect

from cache import cache_frame
from webpy.manager import expose


@expose(name='Add two numbers', url='add')
def add(a: int, b: int) -> int:
    r = cache_frame(inspect.currentframe())
    if r is not None:
        return r

    return a + b
