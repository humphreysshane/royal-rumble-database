# -*- coding: utf-8 -*-
"""
Builds all rows for the 1993 Royal Rumble -- schema v2.

Structurally identical to 1991/1992: no Excel tab exists for 1993 (the
workbook only has 1988/1989/1990 tabs), so this is built from a Cageside-
style timing analysis (survival times, entrance times, time-between-
buzzers, ring crowdedness) plus a Dan Wahlers narrative history, both
correctly filed under their own "1993 Royal Rumble Stats" Heading-1 -- no
misfiling issue like 1991.

SOURCES CONSULTED THIS PASS:
  S027 "1993 Rumble Stats - Cageside" section (Shane's doc)          tier 9
  S028 Dan Wahlers "History of the Royal Rumble" -- 1993 chapter     tier 9

THIS EVENT IS STRUCTURALLY LIKE 1991/1992 -- READ BEFORE EXTENDING:
  - Entry order (all 30) is CONFIRMED. The first two entrants (Ric Flair
    #1, Bob Backlund #2) are named explicitly ("entrances took place prior
    to the start of the match"), and S027's "Time Between Buzzers" list
    gives the remaining 28 entrants in exact chronological buzzer order.
  - Ring/survival time for all 30 is CONFIRMED, directly stated by S027's
    Survival Times list.
  - Elimination timestamp/order is DERIVED, computed exactly as in
    1991/1992: (cumulative buzzer time) + (entrance-time lag) + (survival
    time) = elimination timestamp, then all 29 actually-eliminated entrants
    (every entrant except winner Yokozuna) are ranked by that timestamp.
  - VALIDATION -- spot-checked against SIX independent internal checkpoints,
    every one matching the derived clock exactly:
      1. The buzzer-gap list sums to 57:25, matching S027's own statement
         that "the final buzzer (signaling Macho Man's entrance) ... went
         off at 57m 25s" (vs. a theoretical perfectly-timed 56:00).
      2. The Undertaker's buzzer-derived entry number is exactly #15,
         matching S028's narrative ("The Undertaker came in at #15").
      3. The longest gap between eliminations is derived as 13:01 between
         the 30:52 and 43:53 timestamps -- matching S027's own statement of
         a "13m 01s" gap between those exact same two timestamps.
      4. The 7 entrants S027 names as having "consecutively entered the
         match with nobody being eliminated" during that gap (Demento, IRS,
         Tatanka, Sags, Typhoon, Fatu, Earthquake) are exactly entries
         17-23 in the derived entry order -- no more, no fewer.
      5. Yokozuna's own derived elimination-adjacent timestamp (his ring
         entry + survival time) lands at exactly 66:40, matching S027's
         stated total match duration of "66 minutes and 40 seconds" to the
         second -- consistent with his being the winner (last man standing
         when the bell rings).
      6. The 8 wrestlers still active when Randy Savage enters the ring
         (derived ring-entry time 57:37) are exactly the 8 names S027's own
         "End of the Match" section lists for the final battle-royal-to-the
         -finish segment (Backlund, Sags, El Matador, Martel, Yokozuna,
         Owen Hart, Repo Man, Savage) -- no more, no fewer.
  - One MINOR narrative discrepancy (not corrected, just noted): S028's
    prose says "Hennig came in at #11", but the buzzer-derived entry number
    for Mr. Perfect (Curt Hennig) is #10. Kept the buzzer-derived value
    (same methodology basis as the Undertaker checkpoint above, which
    matched exactly), flagged as a minor narrative-approximation mismatch
    rather than a hard conflict -- see F056.
  - Identity merges (NOT new wrestlers): "El Matador" is Tito Santana's
    1993+ gimmick change (wrestler_id tito-santana, already in this
    database since 1988) -- confirmed by S028's own match-results text
    listing "Tito Santana" by name in the same breath as "El Matador"'s
    survival-time entry, and by the character being a well-documented Tito
    Santana repackaging. "Terry Taylor" is Red Rooster's own real name,
    already logged as an alias on his wrestler_id (red-rooster) during the
    prior fact-check pass -- he's wrestling here as himself, not the Red
    Rooster gimmick, same person.
  - Eliminator credit is CONFIRMED/PROBABLE for only 4 of 29 eliminations:
    Ric Flair (by Mr. Perfect/Curt Hennig, "dumped Flair after the hottest
    sequence"), The Undertaker (by Giant Gonzalez -- a non-entrant
    interloper, not an official Rumble participant, who ran in specifically
    to attack Undertaker), Bob Backlund (by Yokozuna, "Backlund got tossed
    by Yoko"), and Randy Savage (by Yokozuna, though flagged as disputed --
    see F054). The other 25 entrants' eliminator is UNKNOWN.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    ENTRANTS_FIELDS, ELIMINATIONS_FIELDS, EVENTS_FIELDS, NEAR_ELIMINATIONS_FIELDS,
    slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR1993M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S027", "'1993 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring crowdedness). Correctly filed under its own '1993 Royal Rumble Stats' Heading-1 -- no misfiling issue this year. NOT live-fetched this pass."),
    ("S028", "Dan Wahlers, 'History of the Royal Rumble' -- 1993 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance as 16,000, full narrative history (Giant Gonzalez angle, Backlund's iron-man run, Yokozuna's title-shot stipulation win), and undercard match results."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F051", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "Only 4 of this match's 29 real eliminations have an eliminator explicitly named: Ric Flair (by Mr. "
     "Perfect/Curt Hennig), The Undertaker (by Giant Gonzalez, a non-entrant interloper -- see F053), Bob "
     "Backlund (by Yokozuna), and Randy Savage (by Yokozuna, though disputed -- see F054). The other 25 "
     "entrants' eliminated_by_ids are blank (UNKNOWN) -- S027 is a timing analysis, not a blow-by-blow recap, "
     "so most individual eliminations aren't narrated. wrestlers_eliminated_count is only populated for "
     "wrestlers with a confirmed credit, since a true zero would be an unsupported claim.",
     "S027;S028", "open", "2026-09-15"),
    ("F052", EVENT_ID, "eliminations;entrants", "*", "elim_number", "unverified",
     "Elimination ORDER (not eliminator identity) is a DERIVED calculation: each entrant's buzzer time + "
     "entrance-time lag + survival time = an elimination timestamp, then all 29 actually-eliminated entrants "
     "are ranked by that. Spot-verified against 6 independent checkpoints in S027/S028's own prose, all "
     "matching to the exact second -- see script docstring for the specific checkpoints. High confidence, but "
     "still DERIVED rather than a directly-stated fact.",
     "S027;S028", "open", "2026-09-15"),
    ("F053", EVENT_ID, "eliminations", "the-undertaker", "eliminator_wrestler_id", "needs_human_judgement",
     "The Undertaker's elimination is credited to Giant Gonzalez, who ran in specifically to attack him -- but "
     "Gonzalez was NOT an official Rumble entrant (S027 explicitly excludes him from the 'Active Wrestlers' "
     "ring-crowdedness count: 'these numbers do not count Giant Gonzalez as an active wrestler in the "
     "match'). Modeled here as a real eliminator credit (a new wrestler row was added for Giant Gonzalez) "
     "since he's a real, named, identifiable person who caused the elimination, not an unknown quantity -- "
     "but flagged since it's a genuinely unusual case (an outside-interference elimination by a non-entrant, "
     "distinct from every prior year's 'illegally-assisted' cases which at least involved a listed entrant).",
     "S027;S028", "open", "2026-09-15"),
    ("F054", EVENT_ID, "eliminations", "randy-savage", "elimination_type", "needs_human_judgement",
     "Randy Savage's own elimination (the last of the match, before Yokozuna's win) is ambiguous. S028's "
     "narrative: 'Savage somehow got Yoko down, and went for his patented flying elbow. When he landed he "
     "went for the cover, and Yokozuna pushed him off, and Savage essentially jumped over the top rope.' This "
     "reads as Savage's own momentum/jump carrying him out after being pushed off a cover attempt, closer to "
     "a self-elimination than a clean toss -- but since it was directly triggered by Yokozuna's shove, it's "
     "credited to Yokozuna here (not modeled as self_eliminated) with is_disputed=TRUE and the narrative "
     "framing preserved in notes, rather than silently picking one interpretation.",
     "S028", "open", "2026-09-15"),
    ("F055", EVENT_ID, "entrants", "damien-demento;irwin-r-schyster;bob-backlund", "ring_time_status", "unverified",
     "S027 itself flags substantial timing uncertainty for these three during the Giant Gonzalez angle: "
     "Demento and IRS's ring-entry point was obscured because the camera stayed on Gonzalez as he walked back "
     "up the aisle ('I don't know the exact point that all three of those men entered the ring... there is at "
     "least a chance that Demento and IRS quietly entered the ring maybe up to a minute earlier than I "
     "indicated'), and Backlund's ~6m 54s spent outside the ring during the same angle is folded into his "
     "listed survival time without a fully precise re-entry point. The source's own best-guess estimate "
     "('probably no more than 10 seconds off') is kept as PROBABLE rather than CONFIRMED for these three "
     "entrants' ring/elimination timestamps, unlike the rest of the match's entrants.",
     "S027", "open", "2026-09-15"),
    ("F056", EVENT_ID, "entrants", "mr-perfect", "entry_number", "conflicting_sources",
     "S027's buzzer-derived entry number for Mr. Perfect (Curt Hennig) is #10 (buzzer 8, two slots after "
     "Flair/Backlund). S028's narrative prose says 'Hennig came in at #11' instead. Since the same "
     "buzzer-derivation methodology independently matched the Undertaker's narrative-stated entry number "
     "(#15) exactly elsewhere in this same build, the buzzer-derived #10 is kept as CONFIRMED and the "
     "narrative's '#11' is treated as an approximation/rounding in Dan Wahlers' prose, not a hard conflict "
     "worth overriding the more precise timing-analysis source for.",
     "S027;S028", "open", "2026-09-15"),
    ("F057", EVENT_ID, "wrestlers", "*", "real_name;dob;billed_height_m_at_event;billed_weight_kg_at_event;birthplace", "unverified",
     "12 wrestlers appear in this database for the first time via 1993 (Tatanka, Yokozuna, Jerry Lawler, "
     "Genichiro Tenryu, Damien Demento, Carlos Colon, Fatu, Samu, Max Moon, Papa Shango, Bob Backlund, and "
     "Giant Gonzalez -- the last a non-entrant interloper, see F053) with zero bio data in either source this "
     "pass -- names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S027;S028", "open", "2026-09-15"),
    ("F058", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only (Rumble entrants + Giant Gonzalez interloper).
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Tatanka", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S027;S028"),
    ("Yokozuna", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Winner of this match; billed at 505lbs per S028. No bio data in either source this pass.", "S027;S028"),
    ("Jerry Lawler", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S027"),
    ("Genichiro Tenryu", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S027"),
    ("Damien Demento", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Ring-time uncertainty during the Giant Gonzalez angle -- see F055. No bio data in either source this pass.", "S027"),
    ("Carlos Colon", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S027;S028"),
    ("Fatu", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S027;S028"),
    ("Samu", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S027;S028"),
    ("Max Moon", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S027"),
    ("Papa Shango", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S027"),
    ("Bob Backlund", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Iron-man performance, survived 61m 16s -- see F055 for the ring-time uncertainty during the Giant Gonzalez angle. No bio data in either source this pass.", "S027;S028"),
    ("Giant Gonzalez", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "El Gigante (WCW)", "", "", "NOT an official Rumble entrant -- ran in specifically to attack The Undertaker (see F053), explicitly excluded from S027's own 'Active Wrestlers' ring-crowdedness count. Former Argentine basketball player billed at 7'7\" per S028; wrestled as El Gigante in WCW prior. No bio data in either source this pass.", "S027;S028"),
]

reused = {
    "Ted DiBiase": "ted-dibiase", "Jerry Sags": "jerry-sags", "Ric Flair": "ric-flair",
    "Virgil": "virgil", "Irwin R. Schyster": "irwin-r-schyster", "Rick Martel": "rick-martel",
    "Earthquake": "earthquake", "Mr. Perfect": "mr-perfect", "Randy Savage": "randy-savage",
    "Koko B. Ware": "koko-b-ware", "Owen Hart": "owen-hart", "Berzerker": "the-berzerker",
    "Typhoon": "tugboat", "Undertaker": "the-undertaker", "Skinner": "skinner",
    "Brian Knobbs": "brian-knobbs",
    # "Repo Man" is Barry Darsow -- already in this database as "Smash" (wrestler_id smash).
    "Repo Man": "smash",
    # "El Matador" is Tito Santana's 1993+ gimmick change -- same person, wrestler_id tito-santana
    # (already in this database since 1988). Confirmed by S028's own match-results text naming
    # "Tito Santana" in the participant list alongside "El Matador"'s survival-time entry.
    "El Matador": "tito-santana",
    # "Terry Taylor" is Red Rooster's real name -- he's wrestling as himself here, same person,
    # wrestler_id red-rooster (already logged with "Terry Taylor" as an alias from the fact-check pass).
    "Taylor": "red-rooster",
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
    ("Papa Shango", "2:01"), ("Ted DiBiase", "2:03"), ("Brian Knobbs", "1:54"), ("Virgil", "2:03"),
    ("Jerry Lawler", "2:05"), ("Max Moon", "1:53"), ("Genichiro Tenryu", "2:07"), ("Mr. Perfect", "2:01"),
    ("Skinner", "2:01"), ("Koko B. Ware", "2:02"), ("Samu", "2:00"), ("Berzerker", "2:00"),
    ("Undertaker", "2:02"), ("Taylor", "2:04"), ("Damien Demento", "2:03"), ("Irwin R. Schyster", "2:06"),
    ("Tatanka", "2:03"), ("Jerry Sags", "2:02"), ("Typhoon", "2:03"), ("Fatu", "2:04"),
    ("Earthquake", "2:05"), ("Carlos Colon", "2:12"), ("El Matador", "2:06"), ("Rick Martel", "2:03"),
    ("Yokozuna", "2:05"), ("Owen Hart", "2:04"), ("Repo Man", "2:08"), ("Randy Savage", "2:05"),
]
cum = 0
buzzer_time = {}
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("57:25"), f"buzzer checksum failed: {cum}"

entrance_lag = {
    "Damien Demento": "3:21", "Irwin R. Schyster": "1:15", "Yokozuna": "0:37", "Undertaker": "0:26",
    "Jerry Lawler": "0:14", "Earthquake": "0:13", "Fatu": "0:13", "Randy Savage": "0:12",
    "Berzerker": "0:12", "Repo Man": "0:10", "Carlos Colon": "0:09", "Samu": "0:09",
    "Genichiro Tenryu": "0:08", "Mr. Perfect": "0:08", "Skinner": "0:08", "Papa Shango": "0:08", "Taylor": "0:08",
    "Ted DiBiase": "0:07", "Rick Martel": "0:07", "Koko B. Ware": "0:07", "Typhoon": "0:07",
    "Jerry Sags": "0:06", "El Matador": "0:06", "Owen Hart": "0:06", "Max Moon": "0:06",
    "Tatanka": "0:05", "Virgil": "0:05", "Brian Knobbs": "0:05",
}

survival = {
    "Bob Backlund": "61:16", "Ted DiBiase": "24:57", "Jerry Sags": "21:51", "Ric Flair": "18:41",
    "Tatanka": "17:37", "Virgil": "17:10", "Irwin R. Schyster": "15:56", "Yokozuna": "14:55",
    "Jerry Lawler": "14:36", "Genichiro Tenryu": "13:17", "Damien Demento": "12:21", "Rick Martel": "11:23",
    "El Matador": "11:03", "Earthquake": "11:02", "Mr. Perfect": "9:15", "Randy Savage": "9:02",
    "Koko B. Ware": "8:31", "Carlos Colon": "7:25", "Fatu": "6:31", "Owen Hart": "5:39",
    "Berzerker": "5:21", "Typhoon": "5:13", "Samu": "4:50", "Undertaker": "4:14",
    "Repo Man": "3:33", "Skinner": "3:05", "Brian Knobbs": "2:59", "Max Moon": "1:59",
    "Papa Shango": "0:27", "Taylor": "0:24",
}

entry_actual = {"Ric Flair": 0, "Bob Backlund": 0}
for name in buzzer_time:
    lag = mmss(entrance_lag.get(name, "0:00"))
    entry_actual[name] = buzzer_time[name] + lag

# checksums (see docstring): Undertaker's entry number is #15.
entry_order_list = sorted(entry_actual.items(), key=lambda kv: kv[1])
entry_number = {name: i + 1 for i, (name, ts) in enumerate(entry_order_list)}
assert entry_number["Undertaker"] == 15, entry_number["Undertaker"]
assert entry_number["Mr. Perfect"] == 10, entry_number["Mr. Perfect"]  # see F056

elim_ts = {}
for name, surv in survival.items():
    if name == "Yokozuna":
        continue  # winner, no elimination
    elim_ts[name] = entry_actual[name] + mmss(surv)

# checksums: longest gap between eliminations (13:01, between Undertaker's
# 30:52 and Typhoon's 43:53); the 7-entrant no-elimination stretch is
# exactly entries 17-23.
assert elim_ts["Undertaker"] == mmss("30:52"), elim_ts["Undertaker"]
assert elim_ts["Typhoon"] == mmss("43:53"), elim_ts["Typhoon"]
assert elim_ts["Typhoon"] - elim_ts["Undertaker"] == mmss("13:01")
for nm in ("Damien Demento", "Irwin R. Schyster", "Tatanka", "Jerry Sags", "Typhoon", "Fatu", "Earthquake"):
    assert 17 <= entry_number[nm] <= 23, (nm, entry_number[nm])
# Yokozuna's ring-entry + survival lands exactly on total match duration.
assert entry_actual["Yokozuna"] + mmss(survival["Yokozuna"]) == mmss("66:40")
# the 8-man final stretch when Savage enters the ring.
FINAL_STRETCH = {"Bob Backlund", "Jerry Sags", "El Matador", "Rick Martel", "Yokozuna", "Owen Hart", "Repo Man", "Randy Savage"}
still_active_at_savage_entry = {n for n in elim_ts if elim_ts[n] > entry_actual["Randy Savage"]} | {"Yokozuna"}
assert still_active_at_savage_entry == FINAL_STRETCH, still_active_at_savage_entry

elim_order_list = sorted(elim_ts.items(), key=lambda kv: kv[1])
elim_number = {name: i + 1 for i, (name, ts) in enumerate(elim_order_list)}

# eliminator credits (see F051/F053/F054)
KNOWN_ELIMINATORS = {
    "Ric Flair": (["Mr. Perfect"], False, ""),
    "Undertaker": (["Giant Gonzalez"], False, ""),
    "Bob Backlund": (["Yokozuna"], False, ""),
    "Randy Savage": (["Yokozuna"], False, ""),
}
DISPUTED = {"Randy Savage"}

FINAL_FOUR_ORDER = ["yokozuna", "randy-savage", "bob-backlund", "rick-martel"]  # winner, then reverse elim order

elim_rows = []
entrant_rows = []

for name in entry_actual.keys():
    entry = entry_number[name]
    ring_time = survival[name]
    is_winner = (name == "Yokozuna")
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
            "elimination_method": (
                "Giant Gonzalez (a non-entrant interloper) ran in and attacked Undertaker, knocking him out of the ring -- see flags.csv F053."
                if name == "Undertaker" else
                "Yokozuna pushed Savage off a pin attempt; Savage's momentum carried him over the top rope -- see flags.csv F054 for the self-elimination-adjacent ambiguity."
                if name == "Randy Savage" else "UNKNOWN"
            ),
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "FALSE", "is_self_elimination": "FALSE",
            "is_storyline_related": "TRUE" if name in ("Undertaker", "Randy Savage") else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "TRUE" if name in DISPUTED else "FALSE", "simultaneous_group_id": sim_group,
            "data_quality_status": "CONFIRMED" if name in ("Ric Flair", "Bob Backlund") else "PROBABLE",
            "source_ids": "S027;S028",
            "notes": ("Savage's own momentum/jump after being pushed off a cover attempt reads closer to a "
                      "self-elimination than a clean toss; credited to Yokozuna since his shove directly "
                      "triggered it, but flagged as disputed -- see F054." if name == "Randy Savage" else
                      "Giant Gonzalez was not an official Rumble entrant -- see F053." if name == "Undertaker" else ""),
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED" if name != "Mr. Perfect" else "CONFLICTING",
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
        "ring_time_status": "PROBABLE" if name in ("Damien Demento", "Irwin R. Schyster", "Bob Backlund") else "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "randy-savage" else "FALSE",
        "is_final_two": "TRUE" if wid in ("yokozuna", "randy-savage") else "FALSE",
        "is_final_three": "TRUE" if wid in ("yokozuna", "randy-savage", "bob-backlund") else "FALSE",
        "is_final_four": "TRUE" if wid in FINAL_FOUR_ORDER else "FALSE",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S027;S028",
        "notes": "Entry-number status CONFLICTING: buzzer-derived #10 vs. narrative's '#11' -- see F056." if name == "Mr. Perfect" else "",
    }
    entrant_rows.append(er)

# Giant Gonzalez is NOT a Rumble entrant -- no entrants.csv row for him,
# only the eliminations.csv credit above and his own wrestlers.csv row.

# Back-fill wrestlers_eliminated_ids/count -- ONLY for wrestlers with a
# confirmed/probable credit; everyone else stays blank (UNKNOWN). See F051.
elim_map = {}
for row in elim_rows:
    eid = row["eliminator_wrestler_id"]
    elim_map.setdefault(eid, []).append(row["eliminated_wrestler_id"])

CREDITED_ELIMINATORS = {"mr-perfect", "giant-gonzalez", "yokozuna"}
for er in entrant_rows:
    wid = er["wrestler_id"]
    if wid in CREDITED_ELIMINATORS:
        er["wrestlers_eliminated_ids"] = ";".join(elim_map.get(wid, []))
        er["wrestlers_eliminated_count"] = len(elim_map.get(wid, []))
        er["solo_eliminations_count"] = len(elim_map.get(wid, []))
        er["assisted_eliminations_count"] = 0
        er["notes"] = (er["notes"] + " " if er["notes"] else "") + \
            "This count reflects only explicitly-credited eliminations (see F051) -- likely an undercount, not a confirmed total."

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1993", "match_name": "30-Man Royal Rumble Match",
    "match_type": "Men's", "event_date": "1993-01-24", "venue": "Arco Arena",
    "city_region": "Sacramento, California", "country": "United States",
    "attendance_official": "", "attendance_reported": 16000,
    "entry_interval_seconds": 120, "entrant_count": 30, "duration_total": "66:40",
    "duration_status": "CONFIRMED",
    "winner_id": "yokozuna", "runner_up_id": "randy-savage",
    "final_two_ids": "yokozuna;randy-savage", "final_three_ids": "yokozuna;randy-savage;bob-backlund",
    "final_four_ids": "yokozuna;randy-savage;bob-backlund;rick-martel",
    "first_entrant_id": "ric-flair", "second_entrant_id": "bob-backlund", "final_entrant_id": "randy-savage",
    "first_elimination_id": "papa-shango", "last_elimination_before_winner_id": "randy-savage",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 0,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": 0, "factions_count": "N/A",
    "commentary_team": "Gorilla Monsoon, Bobby Heenan", "ring_announcer": "Howard Finkel",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "This was the first Royal Rumble with the stipulation that the winner earns an automatic WWF "
        "Championship match at WrestleMania (per S028). Giant Gonzalez, NOT an official entrant, ran in "
        "partway through the match to attack The Undertaker, interrupting the match for about 4m 17s -- see "
        "F053. Bob Backlund was dragged outside the ring and assaulted by Berzerker (at Gonzalez's behest) "
        "during that stretch but was not eliminated; his listed survival time (61:16) spans this period -- "
        "see F055."
    ),
    "title_on_the_line": "FALSE", "championship_implications": "None in the Rumble match itself, though the winner (Yokozuna) earned a title match at WrestleMania IX per the new stipulation",
    "winners_reward": "An automatic WWF Championship match at WrestleMania IX -- the first year this stipulation existed",
    "historical_significance": "First Royal Rumble with the WrestleMania title-shot stipulation for the winner. Bob Backlund's 61:16 survival time broke Ric Flair's 59:31 record from the prior year. Rick and Scott Steiner's WWF debut occurred on the undercard. Yokozuna went on to win the WWF Championship from Bret Hart at WrestleMania IX, then lost it two minutes later to Hulk Hogan the same night.",
    "notes": "30 confirmed entrants, all identified. Eliminator credit is known for only 4 of 29 eliminations -- see flags.csv F051-F058 for the full list of what's derived vs. directly stated vs. unknown in this event, including the unusual Giant Gonzalez interloper-elimination case (F053) and the Randy Savage self-elimination-adjacent controversy (F054).",
    "data_quality_status": "CONFIRMED", "source_ids": "S027;S028",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1993 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows "
      f"(4 of 29 eliminations have a credited eliminator), "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
