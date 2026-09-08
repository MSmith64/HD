from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, Iterable, List, Optional, Tuple

import swisseph as swe

WHEEL = [41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
         27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
         31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
         28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60]
WHEEL_START = 302.0
GATE_ARC = 360.0 / 64
LINE_ARC = GATE_ARC / 6
COLOR_ARC = LINE_ARC / 6
TONE_ARC = COLOR_ARC / 6
BASE_ARC = TONE_ARC / 5

CENTERS = {
    "Head": [61, 63, 64],
    "Ajna": [4, 11, 17, 24, 43, 47],
    "Throat": [8, 12, 16, 20, 23, 31, 33, 35, 45, 56, 62],
    "G": [1, 2, 7, 10, 13, 15, 25, 46],
    "Ego": [21, 26, 40, 51],
    "Sacral": [3, 5, 9, 14, 27, 29, 34, 42, 59],
    "SolarPlexus": [6, 22, 30, 36, 37, 49, 55],
    "Spleen": [18, 28, 32, 44, 48, 50, 57],
    "Root": [19, 38, 39, 41, 52, 53, 54, 58, 60],
}
CENTER_OF_GATE = {g: c for c, gates in CENTERS.items() for g in gates}

CHANNELS = [
    (1, 8, "Inspiration", "G", "Throat"),
    (2, 14, "The Beat", "G", "Sacral"),
    (3, 60, "Mutation", "Sacral", "Root"),
    (4, 63, "Logic", "Ajna", "Head"),
    (5, 15, "Rhythm", "Sacral", "G"),
    (6, 59, "Mating", "SolarPlexus", "Sacral"),
    (7, 31, "The Alpha", "G", "Throat"),
    (9, 52, "Concentration", "Sacral", "Root"),
    (10, 20, "Awakening", "G", "Throat"),
    (10, 34, "Exploration", "G", "Sacral"),
    (10, 57, "Perfected Form", "G", "Spleen"),
    (11, 56, "Curiosity", "Ajna", "Throat"),
    (12, 22, "Openness", "Throat", "SolarPlexus"),
    (13, 33, "The Prodigal", "G", "Throat"),
    (16, 48, "The Wavelength", "Throat", "Spleen"),
    (17, 62, "Acceptance", "Ajna", "Throat"),
    (18, 58, "Judgment", "Spleen", "Root"),
    (19, 49, "Synthesis", "Root", "SolarPlexus"),
    (20, 34, "Charisma", "Throat", "Sacral"),
    (20, 57, "The Brainwave", "Throat", "Spleen"),
    (21, 45, "Money", "Ego", "Throat"),
    (23, 43, "Structuring", "Throat", "Ajna"),
    (24, 61, "Awareness", "Ajna", "Head"),
    (25, 51, "Initiation", "G", "Ego"),
    (26, 44, "Surrender", "Ego", "Spleen"),
    (27, 50, "Preservation", "Sacral", "Spleen"),
    (28, 38, "Struggle", "Spleen", "Root"),
    (29, 46, "Discovery", "Sacral", "G"),
    (30, 41, "Recognition", "SolarPlexus", "Root"),
    (32, 54, "Transformation", "Spleen", "Root"),
    (34, 57, "Power", "Sacral", "Spleen"),
    (35, 36, "Transitoriness", "Throat", "SolarPlexus"),
    (37, 40, "Community", "SolarPlexus", "Ego"),
    (39, 55, "Emoting", "Root", "SolarPlexus"),
    (42, 53, "Maturation", "Sacral", "Root"),
    (47, 64, "Abstraction", "Ajna", "Head"),
]

PROFILE_LINE = {1: "Investigator", 2: "Hermit", 3: "Martyr", 4: "Opportunist", 5: "Heretic", 6: "Role Model"}
RIGHT_ANGLE = {(1, 3), (1, 4), (2, 4), (2, 5), (3, 5), (3, 6), (4, 6)}
JUXTAPOSITION = {(4, 1)}
LEFT_ANGLE = {(5, 1), (5, 2), (6, 2), (6, 3)}

TYPE_META = {
    "Manifestor": ("To Inform", "Peace", "Anger", "Manifestor aura: closed and repelling"),
    "Generator": ("To Respond", "Satisfaction", "Frustration", "Generator aura: open and enveloping"),
    "Manifesting Generator": ("To Respond, then Inform", "Satisfaction & Peace", "Frustration & Anger", "Manifesting Generator aura: open and enveloping"),
    "Projector": ("Wait for the Invitation", "Success", "Bitterness", "Projector aura: focused and absorbing"),
    "Reflector": ("Wait a Lunar Cycle", "Surprise / Delight", "Disappointment", "Reflector aura: sampling / resistant"),
}

PLANETS = [
    ("Sun", swe.SUN), ("Earth", None), ("NorthNode", swe.TRUE_NODE), ("SouthNode", None),
    ("Moon", swe.MOON), ("Mercury", swe.MERCURY), ("Venus", swe.VENUS), ("Mars", swe.MARS),
    ("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN), ("Uranus", swe.URANUS),
    ("Neptune", swe.NEPTUNE), ("Pluto", swe.PLUTO)
]
PLANET_GLYPH = {"Sun": "☉", "Earth": "⊕", "NorthNode": "☊", "SouthNode": "☋", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"}
PLANET_LABEL = {"NorthNode": "North Node", "SouthNode": "South Node"}
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def full_address(longitude: float) -> dict:
    adj = (longitude - WHEEL_START) % 360.0
    idx = int(adj // GATE_ARC)
    off = adj % GATE_ARC
    line = int(off // LINE_ARC); offl = off % LINE_ARC
    color = int(offl // COLOR_ARC); offc = offl % COLOR_ARC
    tone = int(offc // TONE_ARC); offt = offc % TONE_ARC
    base = int(offt // BASE_ARC)
    return {"gate": WHEEL[idx], "line": line + 1, "color": color + 1, "tone": tone + 1, "base": base + 1}


def gate_line(longitude: float) -> tuple[int, int]:
    a = full_address(longitude)
    return a["gate"], a["line"]


def defined_channels(active_gates: set[int]) -> list[tuple]:
    return sorted([ch for ch in CHANNELS if ch[0] in active_gates and ch[1] in active_gates], key=lambda x: (x[0], x[1]))


def defined_centers(channels: list[tuple]) -> set[str]:
    d = set()
    for _, _, _, ca, cb in channels:
        d.add(ca); d.add(cb)
    return d


def _components(centers: set[str], channels: list[tuple]) -> list[set[str]]:
    adj = {c: set() for c in centers}
    for _, _, _, ca, cb in channels:
        adj[ca].add(cb); adj[cb].add(ca)
    seen, comps = set(), []
    for c in centers:
        if c in seen: continue
        stack, comp = [c], set()
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x); comp.add(x); stack.extend(adj[x] - seen)
        comps.append(comp)
    return comps


def definition(centers: set[str], channels: list[tuple]) -> str:
    return {0:"No Definition",1:"Single Definition",2:"Split Definition",3:"Triple-Split Definition",4:"Quadruple-Split Definition"}.get(len(_components(centers, channels)), "Complex")


def _motor_reaches_throat(centers: set[str], channels: list[tuple]) -> bool:
    if "Throat" not in centers: return False
    adj = {c: set() for c in centers}
    for _, _, _, ca, cb in channels:
        adj[ca].add(cb); adj[cb].add(ca)
    for motor in {"Sacral","SolarPlexus","Ego","Root"} & centers:
        seen, stack = set(), [motor]
        while stack:
            x = stack.pop()
            if x == "Throat": return True
            if x in seen: continue
            seen.add(x); stack.extend(adj[x] - seen)
    return False


def hd_type(centers: set[str], channels: list[tuple]) -> str:
    if not centers: return "Reflector"
    reaches = _motor_reaches_throat(centers, channels)
    if "Sacral" in centers: return "Manifesting Generator" if reaches else "Generator"
    return "Manifestor" if reaches else "Projector"


def authority(centers: set[str], channels: list[tuple]) -> str:
    if "SolarPlexus" in centers: return "Emotional (Solar Plexus)"
    if "Sacral" in centers: return "Sacral"
    if "Spleen" in centers: return "Splenic"
    if "Ego" in centers: return "Ego (Heart)"
    if "G" in centers and any({ca, cb} == {"G","Throat"} for _,_,_,ca,cb in channels): return "Self-Projected (G)"
    if not centers: return "Lunar (Reflector)"
    return "Mental Projector (Environmental / No Inner Authority)"


def cross_angle(p_line: int, d_line: int) -> str:
    if (p_line, d_line) in RIGHT_ANGLE: return "Right Angle"
    if (p_line, d_line) in JUXTAPOSITION: return "Juxtaposition"
    if (p_line, d_line) in LEFT_ANGLE: return "Left Angle"
    return "Right Angle"


def jd_ut(dt_utc: datetime) -> float:
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)


def lon(jd: float, body: int) -> float:
    return swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_SPEED)[0][0] % 360.0


def design_jd(birth_jd: float) -> float:
    target = (lon(birth_jd, swe.SUN) - 88.0) % 360.0
    guess = birth_jd - 88.0 * 365.2422 / 360.0
    for _ in range(60):
        diff = (lon(guess, swe.SUN) - target + 180) % 360 - 180
        if abs(diff) < 1e-9: break
        guess -= diff / 0.985647
    return guess


def activation(jd: float) -> dict:
    lons: dict[str, float] = {}
    for name, body in PLANETS:
        if name == "Earth": L = (lons["Sun"] + 180) % 360
        elif name == "SouthNode": L = (lons["NorthNode"] + 180) % 360
        else: L = lon(jd, body)
        lons[name] = L
    out = {}
    for name, _ in PLANETS:
        L = lons[name]; addr = full_address(L)
        out[name] = {"lon": L, "gate": addr["gate"], "line": addr["line"], "color": addr["color"], "tone": addr["tone"], "base": addr["base"], "sign": SIGNS[int(L // 30)], "deg": L % 30, "glyph": PLANET_GLYPH[name], "label": PLANET_LABEL.get(name, name)}
    return out


def compute_chart(*, name: str, year: int, month: int, day: int, hour: int, minute: int, tz_name: str, place_label: str = "") -> dict:
    local = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo(tz_name))
    utc = local.astimezone(ZoneInfo("UTC"))
    b_jd = jd_ut(utc); d_jd = design_jd(b_jd)
    pers = activation(b_jd); des = activation(d_jd)
    active = {v["gate"] for v in pers.values()} | {v["gate"] for v in des.values()}
    pers_gates = {v["gate"] for v in pers.values()}; des_gates = {v["gate"] for v in des.values()}
    chans = defined_channels(active); cents = defined_centers(chans)
    t = hd_type(cents, chans)
    strategy, signature, not_self, aura = TYPE_META[t]
    au = authority(cents, chans)
    p_line, d_line = pers["Sun"]["line"], des["Sun"]["line"]
    profile = f"{p_line}/{d_line}"
    return {
        "name": name, "place": place_label, "birth_local": local.isoformat(), "birth_utc": utc.isoformat(), "design_utc_jd": d_jd,
        "personality": pers, "design": des, "active_gates": sorted(active), "type": t, "aura_type": aura,
        "strategy": strategy, "signature": signature, "not_self": not_self, "authority": au,
        "profile": profile, "profile_names": [PROFILE_LINE[p_line], PROFILE_LINE[d_line]],
        "definition": definition(cents, chans), "defined_centers": sorted(cents, key=lambda x:list(CENTERS).index(x)),
        "open_centers": sorted([c for c in CENTERS if c not in cents], key=lambda x:list(CENTERS).index(x)),
        "channels": [{"gates":[a,b],"name":n,"centers":[ca,cb]} for a,b,n,ca,cb in chans],
        "cross": {"angle": cross_angle(p_line, d_line), "gates":[pers["Sun"]["gate"], pers["Earth"]["gate"], des["Sun"]["gate"], des["Earth"]["gate"]]},
    }
