# -*- coding: utf-8 -*-
"""
Builds all rows for the 2007 Royal Rumble -- schema v2.

Rich year like 1999/2001/2003/2005: Shane's doc has a full "2007 Rumble
Stats - Cageside" frame-by-frame timing analysis (survival times, entrance
times, time-between-buzzers, ring crowdedness) PLUS the Dan Wahlers
narrative history section, both under the "2007 Royal Rumble Stats"
Heading-1.

SOURCES CONSULTED THIS PASS:
  S071 '2007 Rumble Stats - Cageside' section (Shane's doc)              tier 9
  S072 Dan Wahlers, 'History of the Royal Rumble' -- 2007 chapter        tier 9

METHODOLOGY (mirrors 1999/2001/2003/2005's DERIVED elimination-order
pattern): entry_actual[name] = cumulative buzzer-gap time + entrance_lag
[name]. elim_ts[name] = entry_actual[name] + survival_time[name]. Ric
Flair and Finlay (the first two entrants) both start at entry_actual=0.
Checksums: the cumulative buzzer sum lands exactly on the stated "42:34"
final-buzzer mark (Undertaker's entrance); The Undertaker's (the winner's)
own survival time of 13:16 is exactly (match total 56:20) minus his entry_
actual; Shawn Michaels' computed elim_ts lands exactly on the total match
duration (56:20), confirming he is the winning elimination's victim; and
Kane, HBK, and Khali's narrated multi-victim eliminations (see below) all
land within tight, source-corroborated timing clusters. See asserts below.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival ("ring") time are known to the second for ALL
    30 entrants -- ring_time_status is CONFIRMED throughout.
  - CM Punk's entry number: this script's Cageside-buzzer derivation gives
    #11, but S072's narrative states 'CM Punk at #12' -- a 1-slot
    discrepancy resolved in favor of the more rigorous, purpose-built
    Cageside source, the same preference applied to 2001's Austin/HHH
    draw-number conflict (F130). Every other narrative-stated entry number
    this year (Edge #5, Kane #10, Jeff Hardy #14, Orton #16, Benoit #17,
    HBK #23, Khali #28, Undertaker #30) matches this derivation exactly.
    See F195.
  - Eliminator credit is unusually rich: Kane eliminated Tommy Dreamer and
    Sabu right after his #10 entrance; Shawn Michaels eliminated Finlay
    and Shelton Benjamin right after his #23 entrance, then Randy Orton
    and Edge together in the Final Four, before winning-eliminating The
    Undertaker's opponent... rather, being eliminated BY The Undertaker
    for the win; The Great Khali eliminated 7 men (Hardcore Holly, Chris
    Benoit, The Miz, Rob Van Dam, Carlito, and Chavo Guerrero are
    individually named by S072, with CM Punk DERIVED as the unnamed 7th --
    see F196) before being eliminated by The Undertaker, who also
    eliminated MVP.
  - THE GREAT KHALI'S 7TH ELIMINATION, DERIVED (new situation -- see
    F196): both S071 and S072 state Khali eliminated 7 men in a 44-second
    span, but S072's narrative individually names only 6 (Holly, Miz,
    RVD, Benoit, Carlito, Chavo). Cross-referencing this script's own
    elim_ts derivation, CM Punk's computed elimination timestamp (41:24)
    falls squarely inside the exact 44-second window (40:54-41:38)
    spanned by the 6 named victims, and Punk has no other credited
    eliminator this match -- CM Punk is DERIVED as the unnamed 7th victim.
  - Match duration: S071's precise Cageside derivation gives 56:20; the
    Match Results summary line instead states '(56:17)' -- a 3-second,
    rounding-level discrepancy. The Cageside figure (56:20) is used. See
    F197.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    ENTRANTS_FIELDS, ELIMINATIONS_FIELDS, EVENTS_FIELDS,
    slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR2007M"


def mmss(t):
    parts = [int(p) for p in t.split(":")]
    return parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]


def secs_to_mmss(s):
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"


# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S071", "'2007 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring "
     "crowdedness) filed under the '2007 Royal Rumble Stats' Heading-1. States match duration as 56:20, vs. "
     "the Match Results line's '(56:17)' -- see F197. Explicitly documents The Great Khali eliminating 7 men "
     "in a 44-second span. NOT live-fetched this pass."),
    ("S072", "Dan Wahlers, 'History of the Royal Rumble' -- 2007 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance (15,566), full narrative "
     "history (Khali's dominant 7-elimination stretch, the MVP chair spot, the Edge/Orton double-elimination "
     "by HBK, and the acclaimed Undertaker/Michaels final segment), and undercard match results. Individually "
     "names only 6 of Khali's 7 eliminations -- see F196."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("Kenny Dykstra", "1:31"), ("Matt Hardy", "1:30"), ("Edge", "1:30"), ("Tommy Dreamer", "1:30"),
    ("Sabu", "1:30"), ("Gregory Helms", "1:30"), ("Shelton Benjamin", "1:31"), ("Kane", "1:32"),
    ("CM Punk", "1:52"), ("King Booker", "1:30"), ("Super Crazy", "1:31"), ("Jeff Hardy", "1:20"),
    ("The Sandman", "1:31"), ("Randy Orton", "1:32"), ("Chris Benoit", "1:39"), ("Rob Van Dam", "1:34"),
    ("Viscera", "1:30"), ("Johnny Nitro", "1:32"), ("Kevin Thorn", "1:20"), ("Hardcore Holly", "1:30"),
    ("Shawn Michaels", "1:32"), ("Chris Masters", "1:30"), ("Chavo Guerrero", "1:32"), ("MVP", "1:31"),
    ("Carlito", "1:30"), ("The Great Khali", "1:31"), ("The Miz", "1:24"), ("The Undertaker", "1:39"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("42:34"), f"buzzer checksum failed: {cum}"

# Entrance times. Ric Flair and Finlay excluded (pre-bell).
entrance_lag = {
    "The Sandman": "0:33", "The Great Khali": "0:32", "Viscera": "0:30", "The Undertaker": "0:30",
    "Sabu": "0:26", "King Booker": "0:23", "MVP": "0:19", "Kane": "0:19", "Rob Van Dam": "0:15",
    "Chavo Guerrero": "0:15", "Johnny Nitro": "0:13", "Kenny Dykstra": "0:12", "Kevin Thorn": "0:12",
    "Shawn Michaels": "0:12", "Chris Masters": "0:12", "CM Punk": "0:11", "Carlito": "0:11",
    "Tommy Dreamer": "0:10", "Matt Hardy": "0:10", "Jeff Hardy": "0:10", "Edge": "0:09", "Gregory Helms": "0:09",
    "Super Crazy": "0:08", "Chris Benoit": "0:08", "Shelton Benjamin": "0:08", "Randy Orton": "0:07",
    "Hardcore Holly": "0:07", "The Miz": "0:07",
}

entry_actual = {"Ric Flair": 0, "Finlay": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])
assert entry_actual["The Undertaker"] == mmss("43:04")

# Survival ("ring") times, as stated directly by S071. The Undertaker (the
# winner) is included with a survival time that is his entry-to-match-end
# span, not an elimination -- excluded from elim_ts below.
survival = {
    "Edge": "44:06", "Finlay": "32:34", "CM Punk": "27:17", "Randy Orton": "27:16", "Shawn Michaels": "24:11",
    "Shelton Benjamin": "22:23", "Matt Hardy": "18:56", "Chris Benoit": "17:54", "Rob Van Dam": "16:28",
    "Kane": "13:22", "The Undertaker": "13:16", "Hardcore Holly": "10:22", "King Booker": "9:23",
    "MVP": "7:33", "Gregory Helms": "6:50", "Tommy Dreamer": "6:42", "Chavo Guerrero": "6:24",
    "Viscera": "6:18", "Johnny Nitro": "6:18", "Kevin Thorn": "6:16", "Ric Flair": "5:41", "Sabu": "5:27",
    "Super Crazy": "4:33", "Kenny Dykstra": "4:05", "The Great Khali": "3:45", "Jeff Hardy": "3:38",
    "Chris Masters": "3:32", "Carlito": "3:20", "The Sandman": "0:13", "The Miz": "0:07",
}
assert mmss(survival["The Undertaker"]) == mmss("56:20") - entry_actual["The Undertaker"]

elim_ts = {}
for name, t in survival.items():
    if name == "The Undertaker":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)

assert elim_ts["Shawn Michaels"] == mmss("56:20")  # the winning elimination, by The Undertaker

# Cross-check: Khali's stated 7-man, 44-second elimination span.
KHALI_NAMED = {"Hardcore Holly", "Chris Benoit", "The Miz", "Rob Van Dam", "Carlito", "Chavo Guerrero"}
khali_named_ts = sorted(elim_ts[n] for n in KHALI_NAMED)
assert khali_named_ts[-1] - khali_named_ts[0] == mmss("0:44")
assert khali_named_ts[0] <= elim_ts["CM Punk"] <= khali_named_ts[-1]  # Punk's computed elim falls inside the span

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Ric Flair"] == 1
assert elim_number["Shawn Michaels"] == 29

ENTRY_NUMBERS = {"Ric Flair": 1, "Finlay": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["Edge"] == 5 and ENTRY_NUMBERS["Kane"] == 10
assert ENTRY_NUMBERS["CM Punk"] == 11  # S072's narrative instead says #12 -- see F195
assert ENTRY_NUMBERS["Shawn Michaels"] == 23 and ENTRY_NUMBERS["The Great Khali"] == 28
assert ENTRY_NUMBERS["The Undertaker"] == 30

FINAL_FOUR = {"The Undertaker", "Shawn Michaels", "Edge", "Randy Orton"}
FINAL_THREE = {"The Undertaker", "Shawn Michaels", "Edge"}
FINAL_TWO = {"The Undertaker", "Shawn Michaels"}

# name -> (eliminator names, data_quality_status, elimination_method, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Tommy Dreamer": (["Kane"], "CONFIRMED", "Eliminated by Kane right after his #10 entrance, alongside Sabu.", False, "kane_dreamer_sabu"),
    "Sabu": (["Kane"], "CONFIRMED", "Unceremoniously chokeslammed to the floor through a table he had set up himself, by Kane right after his #10 entrance, alongside Tommy Dreamer.", False, "kane_dreamer_sabu"),
    "Finlay": (["Shawn Michaels"], "CONFIRMED", "Had been in the match since the opening bell before being eliminated by HBK, alongside Shelton Benjamin.", False, "hbk_finlay_benjamin"),
    "Shelton Benjamin": (["Shawn Michaels"], "CONFIRMED", "Eliminated by HBK, alongside Finlay.", False, "hbk_finlay_benjamin"),
    "Hardcore Holly": (["The Great Khali"], "CONFIRMED", "One of 7 eliminated by Khali in a 44-second span -- 6 individually named by S072, with CM Punk DERIVED as the unnamed 7th. See F196.", False, "khali_seven"),
    "Chris Benoit": (["The Great Khali"], "CONFIRMED", "One of 7 eliminated by Khali in a 44-second span. See F196.", False, "khali_seven"),
    "The Miz": (["The Great Khali"], "CONFIRMED", "One of 7 eliminated by Khali in a 44-second span. See F196.", False, "khali_seven"),
    "Rob Van Dam": (["The Great Khali"], "CONFIRMED", "One of 7 eliminated by Khali in a 44-second span. See F196.", False, "khali_seven"),
    "Carlito": (["The Great Khali"], "CONFIRMED", "One of 7 eliminated by Khali in a 44-second span. See F196.", False, "khali_seven"),
    "Chavo Guerrero": (["The Great Khali"], "CONFIRMED", "One of 7 eliminated by Khali in a 44-second span. See F196.", False, "khali_seven"),
    "CM Punk": (["The Great Khali"], "DERIVED", "DERIVED as the unnamed 7th of Khali's 7 eliminations -- Punk's computed elimination timestamp (41:24) falls squarely inside the exact 44-second span (40:54-41:38) of the 6 named victims, and Punk has no other credited eliminator this match. See F196.", False, "khali_seven"),
    "The Great Khali": (["The Undertaker"], "CONFIRMED", "Clotheslined out by The Undertaker after his dominant 7-elimination stretch.", False, ""),
    "MVP": (["The Undertaker"], "CONFIRMED", "Eliminated by Undertaker, leaving the Final Four of Undertaker, Michaels, Edge, and Orton.", False, ""),
    "Randy Orton": (["Shawn Michaels"], "CONFIRMED", "Cracked Undertaker in the face with a chair (brought in by MVP), then double-teamed him with Edge, before HBK got back in the ring and eliminated both Edge and Orton together.", False, "hbk_edge_orton"),
    "Edge": (["Shawn Michaels"], "CONFIRMED", "Double-teamed Undertaker with Orton, before HBK got back in the ring and eliminated both together. Edge was the match's 'Iron Man,' lasting 44:06.", False, "hbk_edge_orton"),
    "Shawn Michaels": (["The Undertaker"], "CONFIRMED", "The winning elimination, capping a widely-praised ~7-minute final one-on-one segment -- Michaels landed a Superkick, both men went down, and as HBK went for a second Superkick, Undertaker ducked and hoisted him up and over the top rope for the win.", False, ""),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Kenny Dykstra", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #3. No individually-named elimination credit either way this pass.", "S071;S072"),
    ("Sabu", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "One of the first-ever ECW Originals to appear in a Royal Rumble, entering #7. Set up a table under the ring during his entrance before eliminating -- being eliminated by Kane through that same table.", "S071;S072"),
    ("CM Punk", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #11 per this script's Cageside-buzzer derivation (S072's narrative instead states #12 -- see F195). DERIVED as the unnamed 7th of The Great Khali's 7 eliminations -- see F196.", "S071;S072"),
    ("The Sandman", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "One of the first-ever ECW Originals to appear in a Royal Rumble, entering #15. Had the shortest survival time of any entrant besides The Miz (0:13), after his trademark long, beer-smashing entrance through the crowd.", "S071;S072"),
    ("Kevin Thorn", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S071;S072"),
    ("MVP", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Billed as Montel Vontavious Porter. Brought a chair back into the ring in the Final Four, setting up Orton's chair shot to Undertaker's face, before being eliminated by The Undertaker.", "S071;S072"),
    ("The Great Khali", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #28 and eliminated 7 men in a 44-second span (see F196) before being clotheslined out by The Undertaker.", "S071;S072"),
    ("The Miz", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #29, the shortest survival time of any entrant (0:07) -- eliminated by The Great Khali almost immediately.", "S071;S072"),
]

reused = {
    "Ric Flair": "ric-flair", "Edge": "edge", "Tommy Dreamer": "tommy-dreamer", "Gregory Helms": "the-hurricane",
    "Shelton Benjamin": "shelton-benjamin", "Kane": "kane", "King Booker": "booker-t", "Jeff Hardy": "jeff-hardy",
    "Randy Orton": "randy-orton", "Chris Benoit": "chris-benoit", "Rob Van Dam": "rob-van-dam",
    "Viscera": "mabel", "Johnny Nitro": "johnny-nitro", "Hardcore Holly": "hardcore-holly",
    "Shawn Michaels": "shawn-michaels", "Chris Masters": "chris-masters", "Chavo Guerrero": "chavo-guerrero",
    "Carlito": "carlito", "The Undertaker": "the-undertaker", "Matt Hardy": "matt-hardy",
    "Super Crazy": "super-crazy", "Finlay": None,
    # Non-entrant reused ids used only in other_matches this year.
    "Joey Mercury": "joey-mercury", "Bobby Lashley": "bobby-lashley", "Test": "test", "Batista": "batista",
    "John Cena": "john-cena",
}
del reused["Finlay"]  # new -- see below

wrestler_ids = {}
wrestler_ids.update(reused)

with open(os.path.join(DATA_DIR, "wrestlers.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in new_wrestlers:
        ring_name = row[0]
        wid = wrestler_ids.get(ring_name) or slugify(ring_name)
        wrestler_ids[ring_name] = wid
        writer.writerow([wid] + list(row))
    # Finlay and Umaga -- added here rather than the main new_wrestlers list
    # since they need explicit notes distinct from the standard template.
    extra = [
        ("Finlay", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #2 (billed as 'Fit Finlay') and lasted 32:34, eliminated by Shawn Michaels.", "S071;S072"),
        ("Umaga", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Not a Rumble entrant this year -- lost a widely-praised Last Man Standing match to John Cena earlier on the same card. Very likely the same performer (Eddie Fatu) as this database's existing 'jamal' wrestler_id (2003 Rumble entrant), but not stated directly by any source consulted this pass -- left unmerged. See F198.", "S072"),
    ]
    for row in extra:
        ring_name = row[0]
        wid = slugify(ring_name)
        wrestler_ids[ring_name] = wid
        writer.writerow([wid] + list(row))

# ---------------------------------------------------------------------------
# ENTRANTS -- all 30, full entry order and survival time known.
# ---------------------------------------------------------------------------
all_names = [
    "Ric Flair", "Finlay", "Kenny Dykstra", "Matt Hardy", "Edge", "Tommy Dreamer", "Sabu", "Gregory Helms",
    "Shelton Benjamin", "Kane", "CM Punk", "King Booker", "Super Crazy", "Jeff Hardy", "The Sandman",
    "Randy Orton", "Chris Benoit", "Rob Van Dam", "Viscera", "Johnny Nitro", "Kevin Thorn", "Hardcore Holly",
    "Shawn Michaels", "Chris Masters", "Chavo Guerrero", "MVP", "Carlito", "The Great Khali", "The Miz",
    "The Undertaker",
]
assert len(all_names) == 30

WRESTLED_EARLIER = {"Bobby Lashley"}  # Test also appears -- but Test is not a Rumble entrant this year

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "The Undertaker")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "The Undertaker":
        notes_parts.append("Entered #30 and won his first career Royal Rumble, eliminating Khali, MVP, and Shawn Michaels (the winning elimination) after a widely-praised final one-on-one segment.")
    elif name == "CM Punk":
        notes_parts.append("Entry number per Cageside derivation is #11; S072's narrative instead states #12 -- see F195. DERIVED as the unnamed 7th of Khali's 7 eliminations -- see F196.")
    elif name == "The Great Khali":
        notes_parts.append("Eliminated a stated 7 men in a 44-second span (6 individually named, 1 DERIVED -- see F196) before being clotheslined out by The Undertaker.")
    elif name == "Shawn Michaels":
        notes_parts.append("Eliminated Finlay and Shelton Benjamin, then Edge and Randy Orton together in the Final Four, before being eliminated by The Undertaker for the win in an acclaimed final segment.")
    elif name == "King Booker":
        notes_parts.append("Reuses this database's existing 'booker-t' wrestler_id (same performer, evolved gimmick/name after winning the 2006 King of the Ring, not a new identity).")
    elif name == "Viscera":
        notes_parts.append("Reuses this database's existing 'mabel' wrestler_id (also used as 'Mabel' and 'Big Daddy V').")
    elif name in ("Sabu", "The Sandman"):
        notes_parts.append("One of the first-ever ECW Originals to compete in a Royal Rumble match, alongside Tommy Dreamer.")
    note = " ".join(notes_parts)

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_number[name],
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": secs_to_mmss(elim_ts[name]),
            "elimination_clock_seconds": elim_ts[name],
            "elimination_type": "over_top_rope",
            "elimination_method": method,
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_shared else "TRUE", "is_shared": "TRUE" if is_shared else "FALSE",
            "is_accidental": "FALSE",
            "is_self_elimination": "FALSE",
            "is_storyline_related": "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": group_id,
            "data_quality_status": dq,
            "source_ids": "S071;S072",
            "notes": "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": "", "rumble_appearance_no": "",
        "is_first_rumble_appearance": "", "previous_rumble_year": "",
        "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "", "is_company_debut": "UNKNOWN", "company_debut_date": "",
        "is_returning_wrestler": "", "absence_length": "",
        "age_at_event": "", "age_status": "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "King Booker" if name == "King Booker" else "",
        "manager_at_event": "",
        "tag_team_name": "",
        "faction_stable": "",
        "current_champion_title": "", "championship_level": "", "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": "" if is_winner else elim_number[name], "elim_number_status": "N/A" if is_winner else "CONFIRMED",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": "" if is_winner else secs_to_mmss(elim_ts[name]),
        "elimination_clock_seconds": "" if is_winner else elim_ts[name],
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Shawn Michaels" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S071;S072",
        "notes": note,
    }
    entrant_rows.append(er)

# Fill in each eliminator's wrestlers_eliminated_ids / counts from elim_rows.
elim_credit = {}
for row in elim_rows:
    elim_credit.setdefault(row["eliminator_wrestler_id"], []).append(row["eliminated_wrestler_id"])
for er in entrant_rows:
    credited = elim_credit.get(er["wrestler_id"], [])
    if credited:
        er["wrestlers_eliminated_count"] = len(credited)
        er["wrestlers_eliminated_ids"] = ";".join(credited)
        er["solo_eliminations_count"] = len(credited)
        er["assisted_eliminations_count"] = 0

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD (only wrestlers already carrying a
# wrestler_id in this database; opponents without one are still recorded
# as free text in the 'opponents' field).
# ---------------------------------------------------------------------------
other_matches = [
    ("Matt Hardy", 1, "MNM (Johnny Nitro and Joey Mercury)", "Jeff Hardy", "Tag Team", "FALSE", "", "FALSE", "Win", "", "", "15:25", "Opener", "S072", "The Hardy Boyz defeated MNM when Jeff pinned Nitro. Also a Rumble entrant this year -- see entrants.csv."),
    ("Jeff Hardy", 1, "MNM (Johnny Nitro and Joey Mercury)", "Matt Hardy", "Tag Team", "FALSE", "", "FALSE", "Win", "", "", "15:25", "Opener", "S072", "The Hardy Boyz defeated MNM -- Jeff pinned Nitro. Also a Rumble entrant this year -- see entrants.csv."),
    ("Johnny Nitro", 1, "The Hardy Boyz (Matt and Jeff Hardy)", "Joey Mercury", "Tag Team", "FALSE", "", "FALSE", "Loss", "", "", "15:25", "Opener", "S072", "Pinned by Jeff Hardy. Also a Rumble entrant this year -- see entrants.csv."),
    ("Joey Mercury", 1, "The Hardy Boyz (Matt and Jeff Hardy)", "Johnny Nitro", "Tag Team", "FALSE", "", "FALSE", "Loss", "", "", "15:25", "Opener", "S072", "Lost alongside Nitro. Not a Rumble entrant this year."),
    ("Bobby Lashley", 2, "Test", "", "Singles", "TRUE", "ECW World Heavyweight Championship", "TRUE", "Win", "", "TRUE", "7:09", "2nd match", "S072", "Retained the ECW Championship by Count Out. Not a Rumble entrant this year."),
    ("Test", 2, "Bobby Lashley", "", "Singles", "TRUE", "ECW World Heavyweight Championship", "FALSE", "Loss", "", "", "7:09", "2nd match", "S072", "Lost to Lashley by Count Out; S072 notes Test was released from WWE not long after. Not a Rumble entrant this year."),
    ("Batista", 3, "Mr. Ken Kennedy", "", "Singles", "TRUE", "World Heavyweight Championship", "TRUE", "Win", "", "TRUE", "10:29", "3rd match", "S072", "Retained the World Heavyweight Championship with a Batista Bomb. Not a Rumble entrant this year."),
    ("John Cena", 4, "Umaga", "", "Singles (Last Man Standing)", "TRUE", "WWE Championship", "TRUE", "Win", "", "TRUE", "23:10", "4th match", "S072", "Retained the WWE Championship in a widely-praised Last Man Standing match, choking Umaga out twice with the STFU. Not a Rumble entrant this year."),
    ("Umaga", 4, "John Cena", "", "Singles (Last Man Standing)", "TRUE", "WWE Championship", "FALSE", "Loss", "", "", "23:10", "4th match", "S072", "Lost to Cena in a widely-praised Last Man Standing match. Not a Rumble entrant this year -- see F198 for a possible unconfirmed identity connection to this database's 2003 'jamal' wrestler_id."),
]
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in other_matches:
        name = row[0]
        mnum, opponents, partners, mtype, is_title, title, was_champ, result, won_t, lost_t, duration, position, row_src, notes = row[1:]
        pid = wrestler_ids[name]
        writer.writerow([EVENT_ID, pid, mnum, opponents, partners, mtype, is_title, title, was_champ,
                          result, won_t, lost_t, duration, position, "", "PROBABLE", row_src, notes])

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F195", EVENT_ID, "entrants", "cm-punk", "entry_number", "conflicting_sources",
     "This script's Cageside-buzzer derivation gives CM Punk's entry number as #11; S072's narrative instead "
     "states 'CM Punk at #12.' Every other narrative-stated entry number this year matches the Cageside "
     "derivation exactly (Edge #5, Kane #10, Jeff Hardy #14, Orton #16, Benoit #17, HBK #23, Khali #28, "
     "Undertaker #30), so this single discrepancy is resolved in favor of the more rigorous, purpose-built "
     "Cageside source, the same preference applied to 2001's Austin/HHH draw-number conflict (F130).",
     "S071;S072", "open", "2026-09-16"),
    ("F196", EVENT_ID, "eliminations", "cm-punk;the-great-khali", "eliminator_wrestler_id", "unverified",
     "Both S071 and S072 state The Great Khali eliminated 7 men in a 44-second span, but S072's narrative "
     "individually names only 6 (Hardcore Holly, Chris Benoit, The Miz, Rob Van Dam, Carlito, Chavo Guerrero). "
     "Cross-referencing this script's own elim_ts derivation, CM Punk's computed elimination timestamp (41:24) "
     "falls squarely inside the exact 44-second window (40:54-41:38) spanned by the 6 named victims, and Punk "
     "has no other credited eliminator this match. DERIVED (not directly named) but tightly corroborated -- "
     "the same derivation pattern used for Muhammad Hassan's 2005 8-man group elimination (F183).",
     "S071;S072", "open", "2026-09-16"),
    ("F197", EVENT_ID, "events", "RR2007M", "duration_total", "conflicting_sources",
     "S071's precise Cageside derivation gives a match duration of 56:20; the Match Results summary line "
     "instead states '(56:17)' -- a 3-second, rounding-level discrepancy. The Cageside figure (56:20) is used "
     "as duration_total, the same preference applied to 2003's F167 and 2004's F179.",
     "S071;S072", "open", "2026-09-16"),
    ("F198", EVENT_ID, "wrestlers", "umaga", "wrestler_id", "needs_human_judgement",
     "Umaga (Eddie Fatu) is very likely the same performer as this database's existing 'jamal' wrestler_id (a "
     "2003 Royal Rumble entrant), but neither source consulted this pass states that connection directly. Left "
     "as a separate, new wrestler_id pending a future fact-check pass with 2 independent sources -- same "
     "caution class as A-Train/Prince-Albert (2003's F170) and Scotty 2 Hotty/Scott Taylor (2001's F132).",
     "S072", "open", "2026-09-16"),
    ("F199", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 10 previously-unseen wrestlers this pass (Finlay, Kenny Dykstra, Sabu, CM Punk, The "
     "Sandman, Kevin Thorn, MVP, The Great Khali, The Miz, Umaga) with zero bio data in this pass's sources -- "
     "names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S071;S072", "open", "2026-09-16"),
    ("F200", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2007", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2007-01-28", "venue": "AT&T Center",
    "city_region": "San Antonio, Texas", "country": "United States",
    "attendance_official": "", "attendance_reported": 15566,
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "56:20",
    "duration_status": "CONFIRMED",
    "winner_id": "the-undertaker", "runner_up_id": "shawn-michaels",
    "final_two_ids": "the-undertaker;shawn-michaels",
    "final_three_ids": "the-undertaker;shawn-michaels;edge",
    "final_four_ids": "the-undertaker;shawn-michaels;edge;randy-orton",
    "first_entrant_id": "ric-flair", "second_entrant_id": "finlay", "final_entrant_id": "the-undertaker",
    "first_elimination_id": "ric-flair", "last_elimination_before_winner_id": "shawn-michaels",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Jim Ross and Jerry Lawler (RAW); Michael Cole and JBL (SmackDown!); Joey Styles and Tazz (ECW)",
    "ring_announcer": "UNKNOWN",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "The first Royal Rumble to feature ECW-brand representation, with ECW Originals Tommy Dreamer, Sabu, "
        "and The Sandman all appearing. The Great Khali eliminated 7 men in a 44-second span -- see F196."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though Bobby Lashley retained the ECW Championship over Test, Batista retained the World Heavyweight Championship over Mr. Kennedy, and John Cena retained the WWE Championship over Umaga in a widely-praised Last Man Standing match, all earlier on the same card.",
    "winners_reward": "A World Heavyweight Championship match against Batista at WrestleMania 23, which Undertaker won, per S072",
    "historical_significance": (
        "The Undertaker's first career Royal Rumble win, capped by a widely-praised final one-on-one segment "
        "against Shawn Michaels that S072 calls 'one of the best finishing sequences to a Royal Rumble ever.' "
        "Set up Undertaker's WrestleMania 23 World Heavyweight Championship win over Batista. Edge was the "
        "match's 'Iron Man' at 44:06. The first Royal Rumble with ECW-brand representation following the "
        "2006 ECW revival."
    ),
    "notes": (
        "One of this database's richest entry/survival-timing datasets, with all 30 entrants timed to the "
        "second. CM Punk's entry number has a 1-slot discrepancy between the Cageside derivation (#11) and the "
        "narrative (#12) -- see F195. The Great Khali's 7th elimination victim is DERIVED via tight timing-"
        "cluster cross-reference -- see F196."
    ),
    "data_quality_status": "CONFIRMED", "source_ids": "S071;S072",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2007 build complete (schema v2): {len(new_wrestlers) + 2} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
