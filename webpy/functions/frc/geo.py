import inspect
from collections import defaultdict

from util import helpers
from app import tba
from cache import batch_call, cache_frame, call
from webpy.manager import expose, Type, Group


@expose(
    name="Which teams have the most of a specific award in a state?",
    url="team_awards_per_state",
    group=Group.FRC,
)
def most_awards_per_state(award_id: Type.int, num_per_state: Type.int):
    # https://github.com/the-blue-alliance/the-blue-alliance/blob/master/consts/award_type.py#L6
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    events = [call(tba.events, year=y) for y in range(1992, 2019)]
    events = helpers.flatten_lists(events)
    events = helpers.filter_official_events(events)
    events = list(filter(lambda e: e["country"] in ["USA", "Canada"], events))
    key_to_state = {e["key"]: e["state_prov"] for e in events}
    event_awards = batch_call(
        events, tba.event_awards, lambda e: [], lambda e: {"event": e["key"]}
    )
    win_counts = defaultdict(lambda: defaultdict(lambda: 0))
    for awards_list in event_awards:
        for award in awards_list:
            if award["award_type"] == award_id:
                for recipient in award["recipient_list"]:
                    win_counts[key_to_state[award["event_key"]]][
                        recipient["team_key"]
                    ] += 1

    top5_per_state = {}
    for state, leaderboard in win_counts.items():
        leaderboard = sorted(leaderboard.items(), key=lambda t: -t[1])
        top5_per_state[state] = leaderboard[:num_per_state]

    return top5_per_state
