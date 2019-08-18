import inspect

from app import tba
from cache import cache_frame, call
from webpy.manager import expose

chairmans = 0
chairmans_finalist = 69
woodie_flowers = 3
engineering_inspiration = 9
deans_list = 4
rookie_all_star = 10
rookie_inspiration = 15
industrial_design = 16
quality = 17
safety = 18
creativity = 20
engineering_excellence = 21
autonomous = 71
entrepreneurship = 22
gracious_professionalism = 11
highest_rookie_seed = 14
imagery = 27
innovation_in_control = 29
judges = 13
spirit = 30

master_events = {
    "2019micmp": ["2019micmp1", "2019micmp2", "2019micmp3", "2019micmp4"],
    "2019oncmp": ["2019oncmp1", "2019oncmp2"],
}

child_events = {e: k for k, v in master_events.items() for e in v}


@expose(name="SLFF 2019 Scoring", url="score-slff")
def score_slff(team_number: int, event_key: str):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    return score_team_event(team_number, event_key, refresh=False, wk=10)


def score_team_event(team_number, event_key, refresh=False, wk=7):
    event_blob = call(tba.event, event=event_key)
    team_key = f"frc{team_number}"
    if event_blob["week"] is not None:  # not champs
        award_pt_map = {
            chairmans: 60,
            engineering_inspiration: 45,
            rookie_all_star: 25,
            rookie_inspiration: 15,
            autonomous: 20,
            creativity: 20,
            innovation_in_control: 20,
            industrial_design: 20,
            engineering_excellence: 20,
            quality: 20,
            deans_list: 5,
            woodie_flowers: 10,
            entrepreneurship: 5,
            gracious_professionalism: 5,
            imagery: 5,
            highest_rookie_seed: 5,
            judges: 5,
            safety: 5,
            spirit: 5,
        }
    else:
        award_pt_map = {
            chairmans: 110,
            chairmans_finalist: 90,
            engineering_inspiration: 60,
            rookie_all_star: 35,
            rookie_inspiration: 20,
            autonomous: 30,
            creativity: 30,
            innovation_in_control: 30,
            industrial_design: 30,
            engineering_excellence: 30,
            quality: 30,
            deans_list: 15,
            woodie_flowers: 30,
            entrepreneurship: 10,
            gracious_professionalism: 10,
            imagery: 10,
            highest_rookie_seed: 10,
            judges: 10,
            safety: 10,
            spirit: 10,
        }

    award_pts = 0
    event_awards = call(tba.event_awards, event=event_key, refresh=refresh)
    for award in event_awards:
        for recipient in award["recipient_list"]:
            if recipient["team_key"] == team_key:
                award_pts += award_pt_map.get(award["award_type"], 0)

    try:
        district_pts = call(tba.event_district_points, event=event_key, refresh=refresh)
    except TypeError:
        district_pts = {"qual_points": 0, "alliance_points": 0, "elim_points": 0}
    else:
        if district_pts is None or not district_pts["points"]:
            district_pts = {"qual_points": 0, "alliance_points": 0, "elim_points": 0}
        else:
            try:
                district_pts = district_pts["points"][team_key]
            except KeyError:
                district_pts = {
                    "qual_points": 0,
                    "alliance_points": 0,
                    "elim_points": 0,
                }

    qual_pts = district_pts["qual_points"]
    picking_pts = district_pts["alliance_points"]

    if event_blob["event_type_string"] in [
        "District Championship",
        "District Championship Division",
    ]:
        qual_pts /= 3
        picking_pts /= 3

    # elim_pts = district_pts['elim_points']

    # force elims points
    elim_pts = 0
    matches = call(tba.event_matches, event=event_key, refresh=refresh)
    for match in matches:
        if match["comp_level"] == "qm":
            continue
        for color in ["blue", "red"]:
            if team_key in match["alliances"][color]["team_keys"]:
                if (
                    match["winning_alliance"] is not None
                    and match["winning_alliance"] == color
                ):
                    elim_pts += 5

    to_return = [
        qual_pts,
        picking_pts,
        elim_pts,
        award_pts,
        qual_pts + picking_pts + elim_pts + award_pts,
    ]

    if event_key in child_events.keys():
        parent = child_events[event_key]
        parent_scores = score_team_event(team_number, parent, refresh=refresh, wk=wk)
        for i, score in enumerate(parent_scores, start=0):
            to_return[i] += score

    return {
        "qual": to_return[0],
        "alliance": to_return[1],
        "elim": to_return[2],
        "award": to_return[3],
        "total": to_return[4],
    }
