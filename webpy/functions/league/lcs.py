import inspect
import itertools
from collections import defaultdict

from cache import cache_frame
from webpy.manager import expose

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
        "rewards": [90, 70, 40, 20, 0, 0, 0, 0, 0],
        "gauntlet_teams": 4,
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
        "rewards": [100, 70, 40, 20, 20, 0, 0, 0, 0],
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
        "rewards": [90, 70, 40, 20, 20, 0, 0, 0, 0],
    },
}


@expose(name="Foldy Sheet Generator", url="worlds-foldy-sheet")
def worlds_foldy_sheet(region: str):
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

    return perms_to_foldy(region, perms)


def perms_to_foldy(region, perms):
    headers = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
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
            pts[team] += all_data[region]["rewards"][i]

        sorted_pts = sorted(pts.items(), key=lambda t: -t[1])
        pts_winner = sorted_pts[0][0]
        if split_winner == pts_winner:
            pts_winner = sorted_pts[1][0]
        newline += f"{pts_winner},"

        c = 0
        for team, _ in sorted_pts:
            if c == all_data[region]["gauntlet_teams"]:
                break
            if team not in [split_winner, pts_winner]:
                newline += f"{team},"
                c += 1
        lines.append(newline)

    return lines


def generate_lck_perms():
    data = all_data["LCK"]
    standings = data["standings"]
    combos = itertools.permutations(standings[:5], 5)
    valid_combos = []
    for combo in combos:
        valid = True
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

        for i in [0, 1]:
            if combo.index(standings[i]) > 3:
                valid = False

        first = standings[0]
        second = standings[1]
        if combo.index(first) in [2, 3] and combo.index(second) in [2, 3]:
            valid = False

        a = standings[2]
        b = standings[4]
        c = standings[3]
        d = standings[5]

        if combo.index(a) in [4, 5] and combo.index(b) in [4, 5]:
            valid = False
        if combo.index(c) in [4, 5] and combo.index(d) in [4, 5]:
            valid = False

        if combo.index(a) not in [4, 5]:
            loserA = b
        else:
            loserA = a

        if combo.index(loserA) != 4:
            valid = False

        if valid:
            valid_combos.append(combo)

    return valid_combos
