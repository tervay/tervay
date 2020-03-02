import inspect

from app import tba
from cache import cache_frame, call
from webpy.manager import Group, RenderAs, Type, expose


@expose(name="Add two numbers", url="add", group=Group.etc, render_as=RenderAs.text)
def add(a: Type.int, b: Type.int):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    return a + b


@expose("Get Team Info", url="team_info", group=Group.FRC, render_as=RenderAs.text)
def team_info(team_number: Type.int):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    return call(tba.team, team=team_number)
