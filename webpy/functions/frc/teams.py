import inspect

from app import tba
from cache import cache_frame, call
from webpy.manager import Group, RenderAs, Type, expose


@expose(
    name="Team A vs Team B (H2H/Together)",
    url="frc-h2h",
    group=Group.FRC,
    render_as=RenderAs.text,
)
def head_to_head(team_1: Type.int, team_2: Type.int):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    origin_key = f"frc{max(team_1, team_2)}"
    target_key = f"frc{min(team_1, team_2)}"

    rookie_year = call(tba.team, team=origin_key)["rookie_year"]

    won_together = 0
    lost_together = 0
    tied_together = 0

    won_against = 0
    lost_against = 0
    tied_against = 0

    for year in range(rookie_year, 2019):
        matches = call(tba.team_matches, team=origin_key, year=year, simple=True)
        for match in matches:
            event = call(tba.event, event=match["event_key"])
            if event["event_type_string"] == "Offseason":
                continue
            blue = match["alliances"]["blue"]["team_keys"]
            red = match["alliances"]["red"]["team_keys"]

            if match["event_key"][:4] == "2015":
                if (
                    match["alliances"]["blue"]["score"]
                    > match["alliances"]["red"]["score"]
                ):
                    winner = "blue"
                elif (
                    match["alliances"]["blue"]["score"]
                    < match["alliances"]["red"]["score"]
                ):
                    winner = "red"
                else:
                    winner = ""
            else:
                winner = match["winning_alliance"]

            if origin_key in blue:
                if target_key in blue:
                    if winner == "blue":
                        won_together += 1
                    elif winner == "red":
                        lost_together += 1
                    else:
                        tied_together += 1
                elif target_key in red:
                    if winner == "blue":
                        won_against += 1
                    elif winner == "red":
                        lost_against += 1
                    else:
                        tied_against += 1
            else:
                if target_key in blue:
                    if winner == "blue":
                        lost_against += 1
                    elif winner == "red":
                        won_against += 1
                    else:
                        tied_against += 1
                elif target_key in red:
                    if winner == "blue":
                        lost_together += 1
                    elif winner == "red":
                        won_together += 1
                    else:
                        tied_together += 1

    together_pct = round(
        won_together * 100 / max(won_together + tied_together + lost_together, 1), 1
    )
    against_pct = round(
        won_against * 100 / max(won_against + tied_against + lost_against, 1), 1
    )
    s = (
        f"{origin_key} with {target_key} is "
        f"{won_together}-{lost_together}-{tied_together} ({together_pct}%)"
    )
    s += (
        "<br>" + f"{origin_key} against {target_key} is "
        f"{won_against}-{lost_against}-{tied_against} ({against_pct}%)"
    )
    return s
