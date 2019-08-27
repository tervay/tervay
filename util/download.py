from app import tba
from cache import batch_call
from util import helpers


def download_event_teams():
    events = batch_call(
        [2017, 2018, 2019], tba.events, lambda y: [], lambda y: {"year": y}
    )
    events = helpers.flatten_lists(events)

    batch_call(events, tba.event_matches, lambda e: [], lambda e: {"event": e["key"]})
    # batch_call(events, tba.event_teams, lambda e: [], lambda e: {"event": e["key"]})
