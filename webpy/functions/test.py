import inspect

from cache import cache_frame
from webpy.manager import expose


@expose(name='Add two numbers', url='add')
def add(a: int, b: int):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    return a + b


@expose(name='Idiot Calculator', url='_idiot')
def idiot(This_Person_Is_An_Idiot: str):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    return 'Jack is an idiot'
