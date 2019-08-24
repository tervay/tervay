import inspect

from cache import cache_frame, call
from webpy.manager import expose, Type, Group

from app import tba


@expose(name="Add two numbers", url="add", group=Group.etc)
def add(a: Type.int, b: Type.int):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    return a + b


@expose("Get Team Info", url="team_info", group=Group.FRC)
def team_info(team_number: Type.int):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    return call(tba.team, team=team_number)
