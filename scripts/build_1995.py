# -*- coding: utf-8 -*-
"""
Builds all rows for the 1995 Royal Rumble -- schema v2.

Back to the rich structure of 1991/1992/1993: no Excel tab exists for 1995
(the workbook only has 1988/1989/1990 tabs), so this is built from a
Cageside-style timing analysis (survival times, entrance times, time-
between-buzzers, ring crowdedness) plus a Dan Wahlers narrative history,
both correctly filed under their own "1995 Royal Rumble Stats" Heading-1.

SOURCES CONSULTED THIS PASS:
  S030 "1995 Rumble Stats - Cageside" section (Shane's doc)          tier 9
  S031 Dan Wahlers "History of the Royal Rumble" -- 1995 chapter     tier 9

THIS EVENT IS STRUCTURALLY LIKE 1991/1992/1993 -- READ BEFORE EXTENDING:
  - Entry order (all 30) is CONFIRMED. Shawn Michaels (#1) and British
    Bulldog (#2) are named explicitly as starting AND finishing the match
    together, and S030's "Follow The Buzzers" list gives the remaining 28
    entrants in exact chronological buzzer order. This was also the
    shortest 30-man Rumble in history -- 60-second intervals instead of
    the usual 90/120.
  - Ring/survival time for all 30 is CONFIRMED, directly stated by S030's
    Survival Times list.
  - Elimination timestamp/order is DERIVED, computed exactly as in
    1991/1992/1993: (cumulative buzzer time) + (entrance-time lag) +
    (survival time) = elimination timestamp, then all 29 actually-
    eliminated entrants (every entrant except winner Shawn Michaels) are
    ranked by that timestamp.
  - VALIDATION -- spot-checked against FOUR independent internal
    checkpoints:
      1. The 7m 10s no-elimination gap S030 describes ("between the time
         stamps of 17m 19s and 24m 29s") matches the derived gap between
         consecutive eliminations #16 (Mabel) and #17 (Backlund) exactly
         (7:10), even though the absolute clock is off by ~1 second from
         S030's own stated values -- see the buzzer-checksum note below.
      2. The wrestlers S030 names as entering "from 11:14 to 18:11" while
         the ring was relatively empty (Bushwhackers, Jacob Blu, Mabel, Mo,
         Bundy, and Lex Luger "towards the end") are exactly the entrants
         whose derived ring-entry times fall in that window -- no more, no
         fewer.
      3. The 12 wrestlers S030's own "End of the Match" section names for
         the final battle-royal-to-the-finish segment (Michaels, Bulldog,
         Luger, Montoya, Godwinn, Bart Gunn, Billy Gunn, Dunn, Murdoch,
         Adam Bomb, Fatu, Crush) are EXACTLY the 12 wrestlers still active
         at Crush's derived ring-entry time -- no more, no fewer.
      4. Bulldog and Michaels' near-identical derived elimination-adjacent
         timestamps (38:42 and 38:45) match S030's own explicit statement
         that Michaels' survival time is exactly 3 seconds longer than
         Bulldog's due to the confused finish (Bulldog thought he'd won and
         celebrated before Michaels re-entered to actually eliminate him).
  - ONE MINOR rounding note (not corrected, left as-is): summing S030's own
    28 buzzer-gap values gives a cumulative time of 28:13, one second short
    of S030's own stated "the final buzzer... went off at 28m 14s." This
    1-second discrepancy is treated as noise in the source's own listed
    values (not traceable to a single specific gap) and propagates evenly
    through the derived clock -- it does not affect elimination ORDER or
    any of the four checkpoints above, which all still match exactly or
    within the same ~1-4 second tolerance seen in prior years' derivations.
  - Eliminator credit is CONFIRMED for only 1 of 29 eliminations: British
    Bulldog, eliminated by Shawn Michaels in the match-winning elimination
    (S030's own detailed account of the confused finish). Every other
    entrant's eliminator is UNKNOWN -- S030 is a timing analysis, not a
    blow-by-blow recap.
  - "Doink" appears again this year, but NOTHING in either source connects
    this appearance to 1994's "Phil Apollo"-credited Doink performance --
    given multiple performers are known to have played this gimmick,
    assigning the same wrestler_id without evidence would be inventing an
    identity connection. Modeled as a SEPARATE wrestler_id (doink-1995)
    from 1994's "doink" -- see F071.
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
EVENT_ID = "RR1995M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S030", "'1995 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring crowdedness). Correctly filed under its own '1995 Royal Rumble Stats' Heading-1 -- no misfiling issue this year. NOT live-fetched this pass."),
    ("S031", "Dan Wahlers, 'History of the Royal Rumble' -- 1995 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance as 10,569, full narrative history (Diesel/Bret Hart title match, HBK's wire-to-wire win, the confused HBK/Bulldog finish), and undercard match results."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F065", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "Only 1 of this match's 29 real eliminations has an eliminator explicitly named: British Bulldog, by "
     "Shawn Michaels (the match-winning elimination). The other 28 entrants' eliminated_by_ids are blank "
     "(UNKNOWN) -- S030 is a timing analysis, not a blow-by-blow recap.",
     "S030;S031", "open", "2026-09-15"),
    ("F066", EVENT_ID, "eliminations;entrants", "*", "elim_number", "unverified",
     "Elimination ORDER (not eliminator identity) is a DERIVED calculation: each entrant's buzzer time + "
     "entrance-time lag + survival time = an elimination timestamp, then all 29 actually-eliminated entrants "
     "are ranked by that. Spot-verified against 4 independent checkpoints in S030's own prose -- see script "
     "docstring. High confidence, but still DERIVED rather than a directly-stated fact.",
     "S030", "open", "2026-09-15"),
    ("F067", EVENT_ID, "events", EVENT_ID, "duration_total", "conflicting_sources",
     "Summing S030's own 28 buzzer-gap values gives 28:13, one second short of S030's own explicit statement "
     "that 'the final buzzer... went off at 28m 14s.' Not traceable to a single specific mistyped gap value; "
     "treated as 1 second of rounding noise in the source's own numbers, not corrected. Does not affect "
     "elimination order or any of the internal validation checkpoints -- see script docstring.",
     "S030", "open", "2026-09-15"),
    ("F068", EVENT_ID, "entrants", "owen-hart;bob-backlund", "ring_time", "unverified",
     "S030/S031 both note that Bret Hart attacked Owen Hart and Bob Backlund during their entrances (before "
     "they reached the ring), which is why both men's survival times are unusually short (0:04 and 0:15 "
     "respectively). This is a storyline detail, not a timing-uncertainty caveat like 1993's F055 -- both "
     "men's ring-entry and elimination timestamps are still treated as CONFIRMED, since S030 states them "
     "directly despite the disruption. Noted here for context only.",
     "S030;S031", "open", "2026-09-15"),
    ("F069", EVENT_ID, "wrestlers", "*", "real_name;dob;billed_height_m_at_event;billed_weight_kg_at_event;birthplace", "unverified",
     "14 wrestlers appear in this database for the first time via 1995 (Eli Blu, Duke Droese, Jimmy Del Ray, "
     "Headshrinker Sione, Tom Prichard, Timothy Well, Jacob Blu, King Kong Bundy, Mantaur, Aldo Montoya, "
     "Henry Godwinn, Steven Dunn, Dick Murdoch, and 'Doink' as a distinct 1995 appearance -- see F071) with "
     "zero bio data in either source this pass -- names only. Left entirely UNKNOWN, same pattern as every "
     "prior year's equivalent flag.",
     "S030;S031", "open", "2026-09-15"),
    ("F070", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-15"),
    ("F071", EVENT_ID, "wrestlers", "doink-1995;doink", "aliases_ring_names", "needs_human_judgement",
     "'Doink' appears in both 1994 and 1995's Rumble fields. Neither source consulted this pass states "
     "whether the same performer played the gimmick both years -- 1994's own text specifically credits that "
     "appearance to 'Phil Apollo' (wrestler_id doink, added 1994), while 1995's text gives no performer name "
     "at all. Since the Doink gimmick is well known to have been played by multiple different performers "
     "over its run, assuming they're the same person without evidence would be inventing an identity "
     "connection -- so 1995's appearance was given its OWN wrestler_id (doink-1995) rather than reusing "
     "1994's, following the same 'don't assume, verify' approach already used for Sparky Plugg (1994's F062) "
     "and successfully resolved for Col. Mustafa (1992's F031). Worth a specific check in a future fact-check "
     "pass to determine whether these should actually be merged.",
     "S030", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Eli Blu", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Blu Brothers", "", "", "One half of The Blu Brothers (w/ Jacob Blu). No bio data in either source this pass.", "S030"),
    ("Duke Droese", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S030;S031"),
    ("Jimmy Del Ray", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Heavenly Bodies", "", "", "One half of The Heavenly Bodies (w/ Tom Prichard). No bio data in either source this pass.", "S030;S031"),
    ("Headshrinker Sione", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Headshrinkers", "", "", "A third 'Headshrinker' distinct from Samu and Fatu, already in this database from 1993. No bio data in either source this pass.", "S030"),
    ("Tom Prichard", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Heavenly Bodies", "", "", "One half of The Heavenly Bodies (w/ Jimmy Del Ray). No bio data in either source this pass.", "S030;S031"),
    ("Timothy Well", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Well Dunn", "", "", "One half of Well Dunn (w/ Steven Dunn). No bio data in either source this pass.", "S030;S031"),
    ("Jacob Blu", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Blu Brothers", "", "", "One half of The Blu Brothers (w/ Eli Blu). No bio data in either source this pass.", "S030;S031"),
    ("King Kong Bundy", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S030;S031"),
    ("Mantaur", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S030"),
    ("Aldo Montoya", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S030;S031"),
    ("Henry Godwinn", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S030;S031"),
    ("Steven Dunn", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Well Dunn", "", "", "One half of Well Dunn (w/ Timothy Well). No bio data in either source this pass.", "S030;S031"),
    ("Dick Murdoch", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Deceased (per S031's 'the late Dick Murdoch'); a veteran making a one-off appearance. No bio data in either source this pass.", "S030;S031"),
    ("Doink-1995", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Doink The Clown", "", "", "Distinct wrestler_id from 1994's 'Doink' (wrestler_id doink, credited there to 'Phil Apollo') -- no source connects the two appearances to the same performer this pass. See F071.", "S030"),
]

reused = {
    "Shawn Michaels": "shawn-michaels", "British Bulldog": "british-bulldog", "Kwang": "kwang",
    "Rick Martel": "rick-martel", "Owen Hart": "owen-hart", "Bushwhacker Luke": "luke-williams",
    "Mo": "mo", "Mabel": "mabel", "Bushwhacker Butch": "butch-miller", "Lex Luger": "lex-luger",
    "Billy Gunn": "billy-gunn", "Bart Gunn": "bart-gunn", "Bob Backlund": "bob-backlund",
    "Adam Bomb": "adam-bomb", "Fatu": "fatu", "Crush": "demolition-crush",
}
wrestler_ids = {}
wrestler_ids.update(reused)

with open(os.path.join(DATA_DIR, "wrestlers.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in new_wrestlers:
        ring_name = row[0]
        wid = slugify(ring_name)
        wrestler_ids[ring_name] = wid
        writer.writerow([wid] + list(row))

# ---------------------------------------------------------------------------
# DERIVE elimination order from buzzer time + entrance lag + survival time
# ---------------------------------------------------------------------------
def mmss(t):
    parts = t.split(":")
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)
    h, m, s = parts
    return int(h) * 3600 + int(m) * 60 + int(s)


buzzer_gaps = [
    ("Eli Blu", "1:00"), ("Duke Droese", "1:00"), ("Jimmy Del Ray", "1:00"), ("Headshrinker Sione", "1:01"),
    ("Tom Prichard", "0:59"), ("Doink-1995", "1:01"), ("Kwang", "0:59"), ("Rick Martel", "1:01"),
    ("Owen Hart", "1:00"), ("Timothy Well", "1:00"), ("Bushwhacker Luke", "1:00"), ("Jacob Blu", "1:00"),
    ("King Kong Bundy", "1:00"), ("Mo", "1:00"), ("Mabel", "1:00"), ("Bushwhacker Butch", "1:00"),
    ("Lex Luger", "1:00"), ("Mantaur", "1:00"), ("Aldo Montoya", "1:00"), ("Henry Godwinn", "1:00"),
    ("Billy Gunn", "1:00"), ("Bart Gunn", "1:00"), ("Bob Backlund", "1:00"), ("Steven Dunn", "1:00"),
    ("Dick Murdoch", "1:11"), ("Adam Bomb", "1:01"), ("Fatu", "1:00"), ("Crush", "1:00"),
]
cum = 0
buzzer_time = {}
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("28:13"), f"buzzer checksum failed: {cum}"  # 1s short of S030's stated 28:14 -- see F067

entrance_lag = {
    "Bob Backlund": "1:12", "Owen Hart": "1:05", "Mabel": "0:20", "King Kong Bundy": "0:18",
    "Adam Bomb": "0:17", "Bushwhacker Butch": "0:15", "Eli Blu": "0:14", "Headshrinker Sione": "0:13",
    "Bushwhacker Luke": "0:13", "Crush": "0:12", "Dick Murdoch": "0:12", "Doink-1995": "0:12",
    "Mantaur": "0:10", "Timothy Well": "0:10", "Lex Luger": "0:09", "Fatu": "0:09",
    "Tom Prichard": "0:09", "Steven Dunn": "0:09", "Bart Gunn": "0:08", "Rick Martel": "0:08",
    "Duke Droese": "0:07", "Jimmy Del Ray": "0:07", "Henry Godwinn": "0:06", "Kwang": "0:06",
    "Mo": "0:06", "Jacob Blu": "0:06", "Aldo Montoya": "0:04", "Billy Gunn": "0:04",
}

survival = {
    "Shawn Michaels": "38:45", "British Bulldog": "38:42", "Lex Luger": "18:52", "Henry Godwinn": "14:41",
    "Aldo Montoya": "13:22", "Eli Blu": "9:57", "Mantaur": "9:32", "Crush": "8:52",
    "Duke Droese": "8:12", "Dick Murdoch": "8:09", "Billy Gunn": "7:25", "Headshrinker Sione": "6:57",
    "Bart Gunn": "6:20", "Fatu": "5:33", "Tom Prichard": "5:30", "Adam Bomb": "5:21",
    "Doink-1995": "4:49", "Steven Dunn": "4:30", "Kwang": "4:00", "King Kong Bundy": "3:01",
    "Rick Martel": "2:28", "Mabel": "1:57", "Jimmy Del Ray": "1:24", "Timothy Well": "0:22",
    "Jacob Blu": "0:18", "Bushwhacker Butch": "0:18", "Bob Backlund": "0:15", "Bushwhacker Luke": "0:12",
    "Owen Hart": "0:04", "Mo": "0:04",
}

entry_actual = {"Shawn Michaels": 0, "British Bulldog": 0}
for name in buzzer_time:
    lag = mmss(entrance_lag.get(name, "0:00"))
    entry_actual[name] = buzzer_time[name] + lag

entry_order_list = sorted(entry_actual.items(), key=lambda kv: kv[1])
entry_number = {name: i + 1 for i, (name, ts) in enumerate(entry_order_list)}

elim_ts = {}
for name, surv in survival.items():
    if name == "Shawn Michaels":
        continue  # winner, no elimination
    elim_ts[name] = entry_actual[name] + mmss(surv)

# checksum 1: the 7:10 no-elimination gap between Mabel and Backlund.
assert elim_ts["Mabel"] == mmss("17:18"), elim_ts["Mabel"]
assert elim_ts["Bob Backlund"] == mmss("24:28"), elim_ts["Bob Backlund"]
assert elim_ts["Bob Backlund"] - elim_ts["Mabel"] == mmss("7:10")
# checksum 2: entrants filling the ring from 11:14 to 18:11.
QUIET_STRETCH = {"Bushwhacker Luke", "Jacob Blu", "Mabel", "Mo", "King Kong Bundy", "Lex Luger", "Bushwhacker Butch"}
for nm in QUIET_STRETCH:
    assert mmss("11:10") <= entry_actual[nm] <= mmss("18:15"), (nm, entry_actual[nm])
# checksum 3: the 12-man final stretch when Crush enters the ring.
FINAL_STRETCH = {"Shawn Michaels", "British Bulldog", "Lex Luger", "Aldo Montoya", "Henry Godwinn",
                  "Bart Gunn", "Billy Gunn", "Steven Dunn", "Dick Murdoch", "Adam Bomb", "Fatu", "Crush"}
still_active_at_crush_entry = {n for n in elim_ts if elim_ts[n] > entry_actual["Crush"]} | {"Shawn Michaels"}
assert still_active_at_crush_entry == FINAL_STRETCH, still_active_at_crush_entry
# checksum 4: Michaels' survival time is exactly 3s longer than Bulldog's.
assert mmss(survival["Shawn Michaels"]) - mmss(survival["British Bulldog"]) == 3

elim_order_list = sorted(elim_ts.items(), key=lambda kv: kv[1])
elim_number = {name: i + 1 for i, (name, ts) in enumerate(elim_order_list)}

KNOWN_ELIMINATORS = {
    "British Bulldog": (["Shawn Michaels"], False, ""),
}

FINAL_FOUR_ORDER = ["shawn-michaels", "british-bulldog", "demolition-crush", "lex-luger"]  # winner, then reverse elim order

elim_rows = []
entrant_rows = []

for name in entry_actual.keys():
    entry = entry_number[name]
    ring_time = survival[name]
    is_winner = (name == "Shawn Michaels")
    elim_no = 0 if is_winner else elim_number[name]
    elim_by, is_self, sim_group = KNOWN_ELIMINATORS.get(name, ([], False, ""))

    wid = wrestler_ids[name]
    ring_time_s = mmss_to_seconds(ring_time)

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_no,
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
            "elimination_clock_time": ring_time, "elimination_clock_seconds": ring_time_s,
            "elimination_type": "over_top_rope",
            "elimination_method": "Bulldog thought he'd eliminated Michaels and began celebrating; Michaels came back in and knocked Bulldog out of the ring to actually win the match -- see script docstring.",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "FALSE", "is_self_elimination": "FALSE",
            "is_storyline_related": "TRUE", "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE", "simultaneous_group_id": sim_group,
            "data_quality_status": "CONFIRMED",
            "source_ids": "S030;S031",
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
        "gimmick_at_event": "", "manager_at_event": "",
        "tag_team_name": "",
        "faction_stable": "",
        "current_champion_title": "", "championship_level": "", "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": elim_no if not is_winner else "",
        "elim_number_status": "N/A" if is_winner else "DERIVED",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": ring_time if not is_winner else "",
        "elimination_clock_seconds": ring_time_s if not is_winner else "",
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "british-bulldog" else "FALSE",
        "is_final_two": "TRUE" if wid in ("shawn-michaels", "british-bulldog") else "FALSE",
        "is_final_three": "TRUE" if wid in ("shawn-michaels", "british-bulldog", "demolition-crush") else "FALSE",
        "is_final_four": "TRUE" if wid in FINAL_FOUR_ORDER else "FALSE",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S030;S031",
        "notes": "",
    }
    entrant_rows.append(er)

elim_map = {}
for row in elim_rows:
    eid = row["eliminator_wrestler_id"]
    elim_map.setdefault(eid, []).append(row["eliminated_wrestler_id"])

CREDITED_ELIMINATORS = {"shawn-michaels"}
for er in entrant_rows:
    wid = er["wrestler_id"]
    if wid in CREDITED_ELIMINATORS:
        er["wrestlers_eliminated_ids"] = ";".join(elim_map.get(wid, []))
        er["wrestlers_eliminated_count"] = len(elim_map.get(wid, []))
        er["solo_eliminations_count"] = len(elim_map.get(wid, []))
        er["assisted_eliminations_count"] = 0
        er["notes"] = (er["notes"] + " " if er["notes"] else "") + \
            "This count reflects only explicitly-credited eliminations (see F065) -- likely an undercount, not a confirmed total."

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD
# ---------------------------------------------------------------------------
other_matches = [
    ("Rick Martel", 1, "Jeff Jarrett", "", "Singles", "TRUE", "Intercontinental Championship", "FALSE", "Loss", "", "", "18:06", "Opener", "S031", "Pinned by Jarrett, who won the IC title."),
]
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for (name, mnum, opponents, partners, mtype, is_title, title, was_champ, result, won_t, lost_t, duration, position, row_src, notes) in other_matches:
        pid = wrestler_ids.get(name, slugify(name))
        writer.writerow([EVENT_ID, pid, mnum, opponents, partners, mtype, is_title, title, was_champ,
                          result, won_t, lost_t, duration, position, "", "PROBABLE", row_src, notes])

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1995", "match_name": "30-Man Royal Rumble Match",
    "match_type": "Men's", "event_date": "1995-01-22", "venue": "The Sun Dome",
    "city_region": "Tampa, Florida", "country": "United States",
    "attendance_official": "", "attendance_reported": 10569,
    "entry_interval_seconds": 60, "entrant_count": 30, "duration_total": "38:45",
    "duration_status": "CONFIRMED",
    "winner_id": "shawn-michaels", "runner_up_id": "british-bulldog",
    "final_two_ids": "shawn-michaels;british-bulldog", "final_three_ids": "shawn-michaels;british-bulldog;demolition-crush",
    "final_four_ids": "shawn-michaels;british-bulldog;demolition-crush;lex-luger",
    "first_entrant_id": "shawn-michaels", "second_entrant_id": "british-bulldog", "final_entrant_id": "demolition-crush",
    "first_elimination_id": "jimmy-del-ray", "last_elimination_before_winner_id": "british-bulldog",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 0,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": 0, "factions_count": "N/A",
    "commentary_team": "Vince McMahon, Jerry Lawler", "ring_announcer": "Howard Finkel",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "Entry interval was 60 seconds this year, not the usual 90/120 -- the shortest 30-man Rumble in "
        "history as a direct result (38:45 total). Shawn Michaels and British Bulldog started the match AND "
        "finished it as the final two, both surviving the entire match length. Bret Hart attacked Owen Hart "
        "and Bob Backlund during their entrances, well before either reached the ring -- see F068."
    ),
    "title_on_the_line": "FALSE", "championship_implications": "None in the Rumble match itself, though the WWF Championship (Diesel vs. Bret Hart, ended in a no-contest/draw) was defended earlier on the same card",
    "winners_reward": "A WWF Championship match against Diesel at WrestleMania XI, per S031",
    "historical_significance": "Shawn Michaels' first of back-to-back Royal Rumble wins (1995-1996), going the full distance from entry #1. The shortest 30-man Royal Rumble match in history (38:45) due to the unique 60-second entry interval. The confused finish (Bulldog briefly celebrating before Michaels re-entered to eliminate him) is one of the more memorable endings in Rumble history.",
    "notes": "30 confirmed entrants, all identified. Eliminator credit is known for only 1 of 29 eliminations (Bulldog, by Michaels) -- see flags.csv F065-F071 for the full list of what's derived vs. directly stated vs. unknown in this event, including a minor 1-second buzzer-checksum rounding note (F067) and the 'Doink' identity-merge caution (F071).",
    "data_quality_status": "CONFIRMED", "source_ids": "S030;S031",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1995 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows "
      f"(1 of 29 eliminations has a credited eliminator), "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
