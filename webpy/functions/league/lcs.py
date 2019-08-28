import inspect
import itertools
from collections import defaultdict

from cache import cache_frame
from webpy.manager import expose, Type, Group, RenderAs

all_data = {
    "LCK": {
        "points": {"GRF": 70, "SKT": 90, "DWG": 30, "SBG": 10, " KZ": 50, " AF": 0},
        "standings": [
            "GRF",
            "DWG",
            "SBG",
            "SKT",
            " AF",
            "GEN",
            " KZ",
            " KT",
            "HLE",
            "JAG",
        ],
        "rewards": [1000, 90, 70, 40, 20, 0, 0, 0, 0, 0],
        "gauntlet_teams": 4,
        "locks": {" AF": 5, "SBG": 4},
    },
    "LCS": {
        "points": {
            " TL": 90,
            " C9": 40,
            "TSM": 70,
            "CLG": 0,
            " CG": 0,
            "FLY": 40,
            "OPT": 0,
            "FOX": 10,
            "GGS": 10,
        },
        "standings": [
            " TL",
            " C9",
            "CLG",
            "TSM",
            " CG",
            "OPT",
            "GGS",
            "100",
            "FLY",
            "FOX",
        ],
        "gauntlet_teams": 4,
        "rewards": [1000, 100, 70, 40, 20, 20, 0, 0, 0, 0],
        "locks": {"TSM": 5, "OPT": 6, "CLG": 4, " CG": 3},
    },
    "LEC": {
        "points": {
            " G2": 90,
            "FNC": 50,
            " OG": 70,
            "SPY": 30,
            "VIT": 10,
            "S04": 0,
            "RGE": 0,
            " SK": 10,
        },
        "standings": [
            " G2",
            "FNC",
            "SPY",
            "S04",
            "RGE",
            "VIT",
            " SK",
            " OG",
            "MSF",
            " XL",
        ],
        "gauntlet_teams": 4,
        "rewards": [1000, 90, 70, 40, 20, 20, 0, 0, 0, 0],
        "locks": {"SPY": 6, "VIT": 5},
    },
    "LPL": {
        "points": {
            "FPX": 50,
            " IG": 90,
            "TES": 30,
            "JDG": 70,
            "RNG": 10,
            "BLG": 0,
            "DMO": 10,
            "SNG": 0,
            "EDG": 0,
            "LNG": 0,
        },
        "standings": [
            "FPX",
            "TES",
            "RNG",
            "BLG",
            "EDG",
            " IG",
            "LNG",
            "SNG",
            " WE",
            "JDG",
            "DMO",
            " V5",
            " RW",
            "LGD",
            " VG",
            "OMG",
        ],
        "gauntlet_teams": 3,
        "rewards": [1000, 90, 70, 40, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0],
        "locks": {"SNG": 8, " IG": 7},
    },
    "LMS": {
        "points": {" JT": 30, "AHQ": 50, "MAD": 70, " FW": 90, "HKA": 10, "GRX": 10},
        "standings": [" JT", "AHQ", "HKA", "MAD", "GRX", " FW", "ALF"],
        "gauntlet_teams": 4,
        "rewards": [1000, 90, 70, 40, 20, 20, 0, 0],
        "locks": {"MAD": 4},
    },
}


@expose(
    name="Foldy Sheet Generator",
    url="worlds-foldy-sheet",
    group=Group.League_of_Legends,
    render_as=RenderAs.table,
)
def worlds_foldy_sheet(region: Type.string):
    r, cache_hit = cache_frame(inspect.currentframe())
    if r is not None:
        return r, cache_hit

    perms = None
    if region.upper() == "LCK":
        perms = generate_lck_perms()
    if region.upper() == "LCS":
        perms = generate_lcs_perms()
    if region.upper() == "LEC":
        perms = generate_lec_perms()
    if region.upper() == "LPL":
        perms = generate_lpl_perms()
    if region.upper() == "LMS":
        perms = generate_lms_perms()

    return perms_to_foldy(region, perms)


def perms_to_foldy(region, perms):
    headers = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
    counts = defaultdict(lambda: 0)
    lines = [
        ",".join(
            headers[: len(perms[0])]
            + ["WIN", "PTS"]
            + headers[: all_data[region]["gauntlet_teams"]]
        )
    ]
    for perm in perms:
        newline = ",".join(perm) + ","
        split_winner = perm[0]
        newline += f"{split_winner},"

        pts = defaultdict(lambda: 0)
        for k, v in all_data[region]["points"].items():
            pts[k] = v

        for i, team in enumerate(perm):
            pts[team] = (
                pts[team] + all_data[region]["rewards"][i],
                all_data[region]["rewards"][i],
            )

        for team, pt_val in pts.items():
            if type(pt_val) is int:
                pts[team] = (pt_val, 0)

        sorted_pts = sorted(pts.items(), key=lambda t: t[1], reverse=True)
        pts_winner = sorted_pts[0][0]
        if split_winner == pts_winner:
            pts_winner = sorted_pts[1][0]
        newline += f"{pts_winner},"

        counts[split_winner] += 1
        counts[pts_winner] += 1

        c = 0
        for team, _ in sorted_pts:
            if c == all_data[region]["gauntlet_teams"]:
                break
            if team not in [split_winner, pts_winner]:
                newline += f"{team},"
                c += 1
        lines.append(newline)

    table = []
    for line in lines:
        table.append(line.split(","))

    odds = dict(
        sorted(
            {k: round(v * 100 / len(perms), 2) for k, v in counts.items()}.items(),
            key=lambda t: -t[1],
        )
    )

    odds_row = [f"{k}: {v}%" for k, v in odds.items()]
    # table.append(odds_row)
    return table


def generate_lck_perms():
    data = all_data["LCK"]
    standings = data["standings"]
    combos = itertools.permutations(standings[:5], 5)
    valid_combos = []
    for combo in combos:
        valid = True
        for team, place in data["locks"].items():
            if combo.index(team) != place - 1:
                valid = False
        for i in [0, 1, 2]:
            if combo.index(standings[i]) > i + 1:
                valid = False

        if valid:
            valid_combos.append(combo)

    return valid_combos


def generate_lcs_perms():
    data = all_data["LCS"]
    standings = data["standings"]
    combos = itertools.permutations(standings[:6], 6)
    valid_combos = []
    for combo in combos:
        valid = True
        for team, place in data["locks"].items():
            if combo.index(team) != place - 1:
                valid = False
        for i in [0, 1]:
            if combo.index(standings[i]) > 3:
                valid = False

        if combo.index("TSM") != 4:
            valid = False
        if combo.index("OPT") != 5:
            valid = False
        if combo.index(" CG") not in [2, 3]:
            valid = False
        if combo.index("CLG") not in [2, 3]:
            valid = False
        if combo.index(" TL") > 1:
            valid = False

        if valid:
            valid_combos.append(combo)

    return valid_combos


def generate_lec_perms():
    data = all_data["LEC"]
    standings = data["standings"]
    combos = itertools.permutations(standings[:6], 6)
    valid_combos = []
    for combo in combos:
        valid = True
        for team, place in data["locks"].items():
            if combo.index(team) != place - 1:
                valid = False

        for i in [0, 1]:
            if combo.index(standings[i]) > 2:
                valid = False

        first = standings[0]
        second = standings[1]
        if combo.index(first) in [2, 3] and combo.index(second) in [2, 3]:
            valid = False
        #
        # a = standings[2]
        # b = standings[4]
        # c = standings[3]
        # d = standings[5]
        #
        # if combo.index(a) in [4, 5] and combo.index(b) in [4, 5]:
        #     valid = False
        # if combo.index(c) in [4, 5] and combo.index(d) in [4, 5]:
        #     valid = False
        #
        # if combo.index(a) not in [4, 5]:
        #     loserA = b
        # else:
        #     loserA = a
        #
        # if combo.index(loserA) != 4:
        #     valid = False

        if valid:
            valid_combos.append(combo)

    return valid_combos


def generate_lpl_perms():
    data = all_data["LPL"]
    standings = data["standings"]
    combos = itertools.permutations(standings[:8], 8)
    valid_combos = []
    for combo in combos:
        valid = True
        for team, place in data["locks"].items():
            if combo.index(team) != place - 1:
                valid = False

        for i in [0, 1]:
            if combo.index(standings[i]) > 3:
                valid = False

        for i in [2, 3]:
            if combo.index(standings[i]) > 5:
                valid = False

        a = standings[4]
        b = standings[7]
        c = standings[5]
        d = standings[6]

        if combo.index(a) in [6, 7] and combo.index(b) in [6, 7]:
            valid = False
        if combo.index(c) in [6, 7] and combo.index(d) in [6, 7]:
            valid = False
        #
        # if combo.index(a) not in [6, 7]:
        #     loserA = b
        # else:
        #     loserA = a

        # if combo.index(loserA) != 6:
        #     valid = False

        if valid:
            valid_combos.append(combo)

    return valid_combos


def generate_lms_perms():
    data = all_data["LMS"]
    standings = data["standings"]
    combos = itertools.permutations(standings[:5], 5)
    valid_combos = []
    for combo in combos:
        valid = True
        for team, place in data["locks"].items():
            if combo.index(team) != place - 1:
                valid = False
        for i in [0, 1, 2]:
            if combo.index(standings[i]) > i + 1:
                valid = False

        if valid:
            valid_combos.append(combo)

    return valid_combos
