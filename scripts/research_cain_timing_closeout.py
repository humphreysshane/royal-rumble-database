#!/usr/bin/env python3
"""Harvest Cain A. Knight's complete timing sections for incomplete Rumbles."""

from __future__ import annotations

import csv
import html
import json
import re
import unicodedata
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "scripts" / "research_inputs" / "cain_timing_closeout.json"

ARTICLES = {
    "RR1988M": ("S008", "https://www.cagesideseats.com/2014/1/21/5329040/match-times-the-1988-royal-rumble"),
    "RR1989M": ("S012", "https://www.cagesideseats.com/wwe/2016/1/18/10687110/wwe-royal-rumble-1989-match-statistics-time"),
    "RR1994M": ("S1754", "https://www.cagesideseats.com/wwe/2017/1/21/14334142/wwe-royal-rumble-1994-match-time-statistics"),
    "RR2000M": ("S1757", "https://www.cagesideseats.com/wwe/2017/1/23/14347624/wwe-royal-rumble-2000-match-time-statistics"),
    "RR2002M": ("S1758", "https://www.cagesideseats.com/wwe/2017/1/6/14185306/wwe-royal-rumble-2002-match-time-statistics"),
    "RR2004M": ("S1759", "https://www.cagesideseats.com/wwe/2017/1/19/14290878/wwe-royal-rumble-2004-match-time-statistics"),
    "RR2006M": ("S1760", "https://www.cagesideseats.com/wwe/2017/1/12/14246008/wwe-royal-rumble-2006-match-time-statistics"),
    "RR2010M": ("S096", "https://www.cagesideseats.com/wwe/2017/1/22/14343366/wwe-royal-rumble-2010-match-time-statistics"),
}

ALIASES = {
    "the rock": "rocky-maivia", "rock": "rocky-maivia", "crush": "demolition-crush", "doink the clown": "doink",
    "hbk": "shawn-michaels", "tenryu": "genichiro-tenryu", "kabuki": "great-kabuki",
    "d lo": "d-lo-brown", "d lo brown": "d-lo-brown", "road dogg": "jesse-james",
    "mr ass": "billy-gunn", "grand master sexay": "brian-christopher", "scotty 2 hotty": "scott-taylor",
    "x pac": "1-2-3-kid", "viscera": "mabel", "prince albert": "prince-albert",
    "the godfather": "the-godfather", "boss man": "big-boss-man", "big boss man": "big-boss-man",
    "hardcore": "hardcore-holly", "crash": "crash-holly", "bulldog": "british-bulldog",
    "snow": "al-snow", "venis": "val-venis", "jericho": "chris-jericho",
    "the undertaker": "the-undertaker", "undertaker": "the-undertaker", "hurricane": "the-hurricane",
    "hhh": "hunter-hearst-helmsley", "triple h": "hunter-hearst-helmsley",
    "rvd": "rob-van-dam", "mysterio": "rey-mysterio", "orton": "randy-orton",
    "foley": "mick-foley", "mick foley": "mick-foley", "benoit": "chris-benoit",
    "nitro": "johnny-nitro", "mercury": "joey-mercury", "animal": "road-warrior-animal",
    "coach": "jonathan-coachman", "coachman": "jonathan-coachman", "masters": "chris-masters",
    "hbk": "shawn-michaels", "morrison": "johnny-nitro", "punk": "cm-punk",
    "khali": "the-great-khali", "ziggler": "dolph-ziggler", "bournes": "evan-bourne",
    "bourne": "evan-bourne", "dibiase": "ted-dibiase-jr", "rhodes": "cody-rhodes",
    "truth": "r-truth", "swagger": "jack-swagger", "kofi": "kofi-kingston",
    "ultimate warrior": "the-ultimate-warrior", "warrior": "the-ultimate-warrior",
    "duggan": "jim-duggan", "muraco": "don-muraco", "neidhart": "jim-neidhart",
    "reed": "butch-reed", "bass": "ron-bass", "race": "harley-race", "davis": "danny-davis",
    "roberts": "jake-roberts", "zhukov": "boris-zhukov", "blair": "b-brian-blair",
    "bravo": "dino-bravo", "jim": "hillbilly-jim", "brunzell": "jim-brunzell",
    "jyd": "junkyard-dog", "houston": "sam-houston", "volkoff": "nikolai-volkoff",
    "bushwhacker butch": "butch-miller", "bushwhacker luke": "luke-williams",
    "barbarian": "the-barbarian", "honky tonk man": "the-honky-tonk-man", "warlord": "the-warlord",
    "savage": "randy-savage", "martel": "rick-martel", "valentine": "greg-valentine",
    "jarrett": "jeff-jarrett", "backlund": "bob-backlund", "luger": "lex-luger",
    "plugg": "sparky-plugg", "jannetty": "marty-jannetty", "blackman": "steve-blackman",
    "godfather": "the-godfather", "hip hop hippo": "mabel", "hippo": "mabel",
    "ddp": "diamond-dallas-page", "angle": "kurt-angle", "palumbo": "chuck-palumbo",
    "matt hardy v1": "matt-hardy", "tajiri": "yoshihiro-tajiri", "goldberg": "bill-goldberg",
    "a train": "prince-albert", "rene dupree": "renee-dupree", "dupree": "renee-dupree",
    "henry": "mark-henry", "miller": "ernest-miller", "steiner": "scott-steiner",
    "morgan": "matt-morgan", "benjamin": "shelton-benjamin", "crazy": "super-crazy",
    "flair": "ric-flair", "chavo": "chavo-guerrero", "r truth": "r-truth",
    "great khali": "the-great-khali", "y2j": "chris-jericho", "beth": "beth-phoenix",
    "yoshi": "yoshi-tatsu",
    "butch": "butch-miller", "luke": "luke-williams", "garvin": "ronnie-garvin",
    "blanchard": "tully-blanchard", "hogan": "hulk-hogan", "rooster": "red-rooster",
    "santana": "tito-santana",
}


def norm(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    value = value.replace("&", " and ")
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return value


def seconds(text):
    match = re.fullmatch(r"(?:(\d+)m\s*)?(\d+)s", text.strip())
    if not match:
        raise ValueError(text)
    return int(match.group(1) or 0) * 60 + int(match.group(2))


def plain_page(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(request, timeout=30).read().decode("utf-8", errors="replace")
    raw = raw.replace("\\n", "\n")
    text = re.sub(r"<[^>]+>", "\n", html.unescape(raw))
    text = re.sub(r"\n+", "\n", text)
    return text


def section(text, start, end):
    a = text.find(start)
    b = text.find(end, a + len(start))
    if a < 0 or b < 0:
        return ""
    return text[a:b]


def list_after(text, marker):
    start = text.find(marker)
    if start < 0:
        return []
    result, begun = [], False
    pattern = re.compile(r"^\s*\*?\s*((?:\d+m\s*)?\d+s):\s*(.+?)\s*$")
    for line in text[start:].splitlines()[1:]:
        match = pattern.match(line)
        if match:
            begun = True
            result.append((seconds(match.group(1)), match.group(2).strip()))
        elif begun and line.strip():
            break
    return result


def split_names(value):
    value = re.sub(r"\s+and\s+", ",", value, flags=re.I)
    value = value.replace(" / ", ",")
    return [x.strip() for x in value.split(",") if x.strip()]


def main():
    with (DATA / "entrants.csv").open(encoding="utf-8-sig", newline="") as handle:
        entrants = list(csv.DictReader(handle))
    output = {}
    all_unmatched = []
    for event_id, (source_id, url) in ARTICLES.items():
        field = [r for r in entrants if r["event_id"] == event_id]
        candidates = {}
        for row in field:
            for value in (row["wrestler_id"], row["ring_name_at_time"], row["name_displayed_at_event"]):
                if value:
                    candidates[norm(value)] = row["wrestler_id"]
        text = plain_page(url)
        survival = list_after(text, "Here is the full list of survival times")
        entrance = list_after(text, "Entrance Times")
        buzzers = list_after(text, "chronological order:")
        event = {"source_id": source_id, "url": url, "survival": {}, "entrance_delay": {}, "buzzer_intervals": [], "unmatched": []}
        for target, items in (("survival", survival), ("entrance_delay", entrance)):
            for duration, grouped_names in items:
                for name in split_names(grouped_names):
                    if norm(name).startswith("buzzer "):
                        continue
                    cleaned = re.sub(r"\s+[-–—]\s+.*$", "", name).strip()
                    key = norm(cleaned)
                    wid = ALIASES.get(key) or candidates.get(key)
                    if not wid:
                        event["unmatched"].append({"section": target, "name": name, "seconds": duration})
                        all_unmatched.append((event_id, target, name, duration))
                    else:
                        event[target][wid] = duration
        for duration, label in buzzers:
            event["buzzer_intervals"].append({"seconds": duration, "label": label})
        output[event_id] = event
        print(event_id, "survival", len(event["survival"]), "entrance", len(event["entrance_delay"]), "buzzers", len(event["buzzer_intervals"]), "unmatched", len(event["unmatched"]))
    OUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for item in all_unmatched:
        print("UNMATCHED", item)
    if all_unmatched:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
