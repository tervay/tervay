import inspect
import os
from collections import defaultdict
from itertools import combinations

from yaml import Loader, load

from cache import cache_frame
from webpy.manager import expose, Type, Group, RenderAs

yaml_path = os.path.join(os.path.dirname(__file__), "champions.yaml")


def parse_yaml():
    data = load("\n".join(open(yaml_path).readlines()), Loader=Loader)
    return data["champions"], data["synergies"]


def get_synergies(champion_objs, synergy_objs):
    counts = defaultdict(lambda: 0)
    for champ, info in champion_objs.items():
        for origin in info["origin"].split("/"):
            counts[origin] += 1
        for class_ in info["class"].split("/"):
            counts[class_] += 1

    achieved = {}
    for synergy, cnt in counts.items():
        synergy_obj = list(filter(lambda s: s["name"] == synergy, synergy_objs))[0]
        iterable = [x for x in synergy_obj["thresholds"] if cnt >= x]
        if len(iterable) > 0:
            met = min(iterable)
            achieved[synergy] = met

    return achieved


def score_synergies(synergies):
    return sum(synergies.values())


@expose(
    name="TFT Comp Tool",
    url="tft-helper",
    group=Group.League_of_Legends,
    render_as=RenderAs.text,
)
def tft_helper(
    comma_separated_roster: Type.string,
    comma_separated_exclude: Type.string,
    level: Type.int,
):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    champs, synergies = parse_yaml()
    roster = {k: champs[k] for k in comma_separated_roster.split(",") if len(k) > 0}
    unused = {
        name: info
        for name, info in champs.items()
        if name not in roster.keys() and name not in comma_separated_exclude.split("/")
    }
    combos = combinations(list(unused.keys()), level - len(roster.keys()))

    top_score = 0
    top_roster = None
    top_synergies = None
    for combo in combos:
        new_roster = roster.copy()
        for champ in combo:
            new_roster.update({champ: champs[champ]})
        strengths = get_synergies(new_roster, synergies)
        if score_synergies(strengths) > top_score:
            top_score = score_synergies(strengths)
            top_roster = new_roster
            top_synergies = strengths

    return {"synergies": top_synergies, "roster": top_roster}
