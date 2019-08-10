import inspect
from collections import defaultdict

import helpers
from app import tba
from cache import cache_frame, call, batch_call
from webpy.manager import expose


@expose(name='Which teams have the most of a specific award in a state?',
        url='team_awards_per_state')
def most_awards_per_state(award_id: int, num_per_state: int):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit
    # https://github.com/the-blue-alliance/the-blue-alliance/blob/master/consts/award_type.py#L6

    print(f'most_awards_per_state({award_id}, {num_per_state})')
    print('Retrieving events')
    events = [call(tba.events, year=y) for y in range(1992, 2019)]
    events = helpers.flatten_lists(events)
    events = helpers.filter_official_events(events)
    events = list(filter(lambda e: e['country'] in ['USA', 'Canada'], events))
    key_to_state = {e['key']: e['state_prov'] for e in events}
    print(f'Retrieving awards for {len(events)} events')
    # event_awards = [call(tba.event_awards, event=e['key']) for e in events]
    # event_awards = [tba.event_awards(e['key']) for e in events]
    # event_awards = batch_call(events, tba.event_awards, lambda e: {'event': e['key']})
    event_awards = batch_call(
        events,
        tba.event_awards,
        lambda e: [],
        lambda e: {'event': e['key']}
    )
    win_counts = defaultdict(lambda: defaultdict(lambda: 0))
    print('done', flush=True)
    for awards_list in event_awards:
        for award in awards_list:
            if award['award_type'] == award_id:
                for recipient in award['recipient_list']:
                    win_counts[
                        key_to_state[
                            award['event_key']
                        ]
                    ][recipient['team_key']] += 1

    print('Processing leaderboard...')
    top5_per_state = {}
    for state, leaderboard in win_counts.items():
        leaderboard = sorted(leaderboard.items(), key=lambda t: -t[1])
        top5_per_state[state] = leaderboard[:num_per_state]

    return top5_per_state
