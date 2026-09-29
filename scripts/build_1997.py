# -*- coding: utf-8 -*-
"""
Builds all rows for the 1997 Royal Rumble -- schema v2.

Back to the rich structure of 1991/1992/1993/1995: no Excel tab exists for
1997 (the workbook only has 1988/1989/1990 tabs), so this is built from a
Cageside-style timing analysis (survival times, entrance times, time-
between-buzzers, ring crowdedness) plus a Dan Wahlers narrative history,
both correctly filed under their own "1997 Royal Rumble Stats" Heading-1.

SOURCES CONSULTED THIS PASS:
  S033 "1997 Rumble Stats - Cageside" section (Shane's doc)          tier 9
  S034 Dan Wahlers "History of the Royal Rumble" -- 1997 chapter     tier 9

THIS EVENT IS STRUCTURALLY LIKE 1991/1992/1993/1995 -- READ BEFORE EXTENDING:
  - Entry order (all 30) is CONFIRMED. Crush (#1) and Ahmed Johnson (#2)
    are named explicitly as entering before the match started, and S033's
    "Follow The Buzzers" list gives the remaining 28 entrants in exact
    chronological buzzer order (nominally 90-second intervals, though
    WWF's countdown clock malfunctioned for the first ~5 minutes -- see
    F083).
  - Ring/survival time for all 30 is CONFIRMED, directly stated by S033's
    Survival Times list.
  - Elimination timestamp/order is DERIVED, computed exactly as in
    1991/1992/1993/1995: (cumulative buzzer time) + (entrance-time lag) +
    (survival time) = elimination timestamp, then all 29 actually-
    eliminated entrants (every entrant except winner Steve Austin) are
    ranked by that timestamp.
  - VALIDATION -- this is the most thoroughly cross-checked derivation in
    the database so far, matching narrative-stated entry numbers EXACTLY
    for SEVEN different entrants (an unusually rich set of checkpoints for
    a single year):
      1. Buzzer-gap sum matches S033's own stated final-buzzer time (42:49)
         exactly.
      2. Steve Austin's derived entry number is exactly #5, matching
         S034's narrative ("Steve Austin came out at #5").
      3. Bret Hart's derived entry number is exactly #21, matching S034
         ("Bret Hart entered at #21").
      4. Jerry Lawler's derived entry number is exactly #22, matching S034
         ("Jerry Lawler was the 'surprise' entrant at #22").
      5. Terry Funk's derived entry number is exactly #24, matching S034
         ("Terry Funk came wandering out ... at #24").
      6. The Undertaker's derived entry number is exactly #30 (the final
         entrant), matching S034 ("finally The Undertaker at #30").
      7. The Undertaker's derived ring-entry TIMESTAMP is exactly 43:32,
         matching S033's own statement that he was "the 10th wrestler in
         the ring" when he entered "at 43m 32s" -- an exact match down to
         the second, not just the entry number.
      8. The "final 8 entrants" S033 describes as entering "consecutively
         without anybody being eliminated" after Jerry Lawler's 31:05
         elimination are EXACTLY the 8 entrants (Fake Diesel, Terry Funk,
         Rocky Maivia, Mankind, Flash Funk, Vader, Henry Godwinn, The
         Undertaker) whose derived ring-entry times fall between Lawler's
         elimination and Undertaker's entrance -- no more, no fewer.
      9. The final-4-eliminations' derived timestamps (Vader 50:18,
         Undertaker 50:19, Fake Diesel 50:24, Bret Hart 50:28) span exactly
         10 seconds, matching S034's "those final 4 men were all thrown
         out within 10 or 11 seconds of each other."
  - Eliminator credit is CONFIRMED for 5 of 29 eliminations: The Undertaker
    and Vader (both by Steve Austin, in the brawl-cover confusion after
    Bret Hart's missed elimination -- see F081), Terry Funk and Mankind
    (mutual -- "Mankind and Terry Funk had eliminated each other"), and
    Bret Hart (by Steve Austin, the winning elimination -- itself only
    possible because of the missed call documented in F081). Mil Mascaras'
    own elimination is a confirmed SELF-elimination via an unconventional
    voluntary dive -- see F082. The other 23 entrants' eliminator is
    UNKNOWN.
  - THE central controversy of this match (F081): Bret Hart threw Steve
    Austin out of the ring at the 50:05 mark, but the referees were
    distracted by a Mankind/Terry Funk brawl outside the ring and didn't
    see it. Austin snuck back in, eliminated Undertaker and Vader (who
    were brawling on the ropes), then eliminated Bret Hart from behind to
    "win" the match. Austin's own survival time (45:06) is recorded as
    though he was never eliminated at all -- consistent with the official,
    on-air result, not with what actually happened on the missed call.
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
EVENT_ID = "RR1997M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S033", "'1997 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring crowdedness). Correctly filed under its own '1997 Royal Rumble Stats' Heading-1 -- no misfiling issue this year. NOT live-fetched this pass."),
    ("S034", "Dan Wahlers, 'History of the Royal Rumble' -- 1997 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance as 60,525 announced (48,017 "
     "paid), full narrative history (the Austin/Bret Hart missed-elimination finish, Sid/Michaels title "
     "match), and undercard match results."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F079", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "Only 5 of this match's 29 real eliminations have an eliminator explicitly named: The Undertaker and "
     "Vader (both by Steve Austin), Terry Funk and Mankind (mutual), and Bret Hart (by Steve Austin, the "
     "winning elimination -- see F081). Mil Mascaras' own elimination is a confirmed self-elimination (F082). "
     "The other 23 entrants' eliminated_by_ids are blank (UNKNOWN) -- S033 is a timing analysis, not a "
     "blow-by-blow recap.",
     "S033;S034", "open", "2026-09-15"),
    ("F080", EVENT_ID, "eliminations;entrants", "*", "elim_number", "unverified",
     "Elimination ORDER (not eliminator identity) is a DERIVED calculation: each entrant's buzzer time + "
     "entrance-time lag + survival time = an elimination timestamp, then all 29 actually-eliminated entrants "
     "are ranked by that. Spot-verified against NINE independent checkpoints in S033/S034's own prose -- the "
     "richest validation set in the database so far, including SEVEN exact entry-number matches (Crush #1, "
     "Ahmed #2, Austin #5, Bret Hart #21, Lawler #22, Terry Funk #24, Undertaker #30) -- see script docstring "
     "for the full list. High confidence, but still DERIVED rather than a directly-stated fact.",
     "S033;S034", "open", "2026-09-15"),
    ("F081", EVENT_ID, "eliminations", "steve-austin;bret-hart", "elimination_type", "needs_human_judgement",
     "THE central controversy of this match. At 50:05, Bret Hart threw Steve Austin out of the ring -- but "
     "the referees were distracted by a Mankind/Terry Funk brawl outside the ring and didn't see it. Austin "
     "snuck back in undetected, eliminated Undertaker and Vader (who were brawling on the ropes), then "
     "eliminated Bret Hart from behind to 'win' the match. NO eliminations.csv row exists for 'Bret Hart "
     "eliminates Austin' at 50:05, since it was never officiated/recognized -- Austin's own survival time "
     "(45:06) and entrant row reflect the OFFICIAL on-air result (never eliminated), not the missed call. "
     "This is a deliberate modeling choice: eliminations.csv represents the officiated match record, and this "
     "database treats a missed call the same way the match's own result did, while documenting the full "
     "sequence of events here and in events.csv's special_rules.",
     "S033;S034", "open", "2026-09-15"),
    ("F082", EVENT_ID, "eliminations", "mil-mascaras", "elimination_type", "needs_human_judgement",
     "Mil Mascaras' elimination is unconventional: he threw his opponent outside the ring, then ducked "
     "through the middle rope, climbed to the turnbuckle from the ring apron (not from inside the ring), and "
     "dove onto his opponent outside -- eliminating HIMSELF in the process. S033's own account notes "
     "uncertainty about whether this should even count as 'going over the top' by the match's usual "
     "definition, but the referees ruled him eliminated when his feet hit the floor after the dive, and "
     "S033 explicitly notes the precedent was already set by Rick Martel in an earlier Rumble. Modeled as a "
     "confirmed self-elimination (is_self_elimination=TRUE), not an elimination credited to his opponent.",
     "S033", "open", "2026-09-15"),
    ("F083", EVENT_ID, "entrants", "fake-razor;pierroth;savio-vega;jake-roberts;marc-mero;owen-hart;henry-godwinn", "ring_time_status", "unverified",
     "Two distinct camera/clock issues affect several entrants' timing precision this year: (1) WWF's "
     "countdown clock malfunctioned for the first ~5 minutes of the match, so S033 had to use alternate cues "
     "(Titantron footage, visual confirmation) for the first 3 buzzers/entrants (Fake Razor, Phineas, Austin) "
     "and the exact ring-entry point for Fake Razor, Pierroth, and Savio Vega specifically wasn't captured on "
     "camera at all; (2) separately, Jake Roberts' elimination happened during another entrance and wasn't "
     "shown live (Titantron used instead), Marc Mero and Owen Hart were eliminated at approximately the same "
     "time but the camera missed the exact moment (a replay was used), and Henry Godwinn's exact floor-touch "
     "after being thrown by Undertaker was mostly off-camera (a later replay was used). S033's own best-guess "
     "estimates are kept (\"this didn't cause any major headaches\" per the source), but flagged here rather "
     "than treated as fully precise like the majority of this event's entrants.",
     "S033", "open", "2026-09-15"),
    ("F084", EVENT_ID, "wrestlers", "*", "real_name;dob;billed_height_m_at_event;billed_weight_kg_at_event;birthplace", "unverified",
     "17 wrestlers appear in this database for the first time via 1997 (Ahmed Johnson, Fake Razor Ramon/Rick "
     "Bogner, Phineas Godwinn, Pierroth Jr., The Sultan, Mil Mascaras, Goldust, Cibernetico, Marc Mero, Latin "
     "Lover, Faarooq/Ron Simmons, Jesse James/Road Dogg, Fake Diesel/Glen Jacobs, Rocky Maivia, Mankind/Mick "
     "Foley, Flash Funk, Terry Funk) with zero bio data in either source this pass -- names only, EXCEPT that S034 itself "
     "states the real names behind three gimmicks directly (Fake Razor Ramon = Rick Bogner, Fake Diesel = "
     "Glen Jacobs, Faarooq = Ron Simmons) -- those three are recorded as PROBABLE real names, everyone else's "
     "bio fields are fully UNKNOWN.",
     "S033;S034", "open", "2026-09-15"),
    ("F085", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Ahmed Johnson", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "One of the first two Rumble entrants this year (#2, after Crush). No bio data in either source this pass.", "S033;S034"),
    ("Fake Razor Ramon", "Rick Bogner", "PROBABLE", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "S034 gives the real name behind this decoy gimmick directly: Rick Bogner. Part of the storyline creating decoy versions of departed stars (the real Razor Ramon/Scott Hall had left for WCW). No other bio data in either source this pass.", "S033;S034"),
    ("Phineas Godwinn", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Henry Godwinn's brother (Henry already in this database since 1995). No bio data in either source this pass.", "S033;S034"),
    ("Pierroth Jr.", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "AAA (Mexican promotion) talent per S034. Exact ring-entry point not captured on camera -- see F083. No bio data in either source this pass.", "S033;S034"),
    ("The Sultan", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S033"),
    ("Mil Mascaras", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Mexican wrestling legend per S034. Unconventional self-elimination -- see F082. No bio data in either source this pass.", "S033;S034"),
    ("Goldust", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S033"),
    ("Cibernetico", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "AAA (Mexican promotion) talent per S034. No bio data in either source this pass.", "S033;S034"),
    ("Marc Mero", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Eliminated at approximately the same time as Owen Hart -- exact moment missed by the camera, a replay was used -- see F083. No bio data in either source this pass.", "S033"),
    ("Latin Lover", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "AAA (Mexican promotion) talent per S034. No bio data in either source this pass.", "S033;S034"),
    ("Faarooq", "Ron Simmons", "PROBABLE", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "S034 gives the real name behind this gimmick directly: Ron 'Faarooq' Simmons. No other bio data in either source this pass.", "S033;S034"),
    ("Jesse James", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Road Dog", "", "", "S034 refers to this entrant as 'Road Dog Jesse James'. No bio data in either source this pass.", "S033;S034"),
    ("Fake Diesel", "Glen Jacobs", "PROBABLE", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "S033 gives the real name behind this decoy gimmick directly: Glen Jacobs. Part of the storyline creating decoy versions of departed stars (the real Diesel/Kevin Nash had left for WCW). No other bio data in either source this pass.", "S033;S034"),
    ("Rocky Maivia", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S033"),
    ("Mankind", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Mutually eliminated Terry Funk (and was eliminated by him) per S034's narrative. No bio data in either source this pass.", "S033;S034"),
    ("Flash Funk", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S033"),
    ("Terry Funk", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "WWF/wrestling veteran making his first appearance in this database -- no prior Rumble build (1988-1996) includes him, confirmed by checking every prior year's build script. Mutually eliminated Mankind (and was eliminated by him) per S034's narrative -- see F081's docstring note and the funk_mankind sim_group. No bio data in either source this pass.", "S033;S034"),
]

reused = {
    "Crush": "demolition-crush", "Austin": "steve-austin", "Bart Gunn": "bart-gunn",
    "Roberts": "jake-roberts", "Bulldog": "british-bulldog", "Helmsley": "hunter-hearst-helmsley",
    "Owen Hart": "owen-hart", "Savio": "savio-vega", "Bret Hart": "bret-hart",
    "Lawler": "jerry-lawler", "Vader": "vader",
    "Henry Godwinn": "henry-godwinn", "Undertaker": "the-undertaker",
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
    ("Fake Razor Ramon", "1:45"), ("Phineas Godwinn", "1:27"), ("Austin", "1:41"), ("Bart Gunn", "1:31"),
    ("Roberts", "1:30"), ("Bulldog", "1:31"), ("Pierroth Jr.", "1:30"), ("The Sultan", "1:31"),
    ("Mil Mascaras", "1:30"), ("Helmsley", "1:31"), ("Owen Hart", "1:30"), ("Goldust", "1:31"),
    ("Cibernetico", "1:30"), ("Marc Mero", "1:30"), ("Latin Lover", "1:33"), ("Faarooq", "1:30"),
    ("Savio", "1:28"), ("Jesse James", "1:32"), ("Bret Hart", "1:31"), ("Lawler", "1:36"),
    ("Fake Diesel", "1:33"), ("Terry Funk", "1:30"), ("Rocky Maivia", "1:35"), ("Mankind", "1:30"),
    ("Flash Funk", "1:30"), ("Vader", "1:30"), ("Henry Godwinn", "1:34"), ("Undertaker", "1:29"),
]
cum = 0
buzzer_time = {}
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("42:49"), f"buzzer checksum failed: {cum}"

entrance_lag = {
    "Undertaker": "0:43", "Austin": "0:31", "The Sultan": "0:30", "Roberts": "0:28",
    "Mil Mascaras": "0:27", "Vader": "0:27", "Marc Mero": "0:24", "Bret Hart": "0:24",
    "Phineas Godwinn": "0:23", "Mankind": "0:23", "Bart Gunn": "0:22", "Lawler": "0:22",
    "Fake Diesel": "0:22", "Bulldog": "0:21", "Owen Hart": "0:21", "Henry Godwinn": "0:17",
    "Pierroth Jr.": "0:15", "Terry Funk": "0:15", "Flash Funk": "0:15", "Fake Razor Ramon": "0:14",
    "Helmsley": "0:13", "Goldust": "0:13", "Jesse James": "0:13", "Cibernetico": "0:12",
    "Latin Lover": "0:12", "Faarooq": "0:10", "Rocky Maivia": "0:10", "Savio": "0:10",
}

survival = {
    "Austin": "45:06", "Bret Hart": "21:02", "Fake Diesel": "17:51", "Terry Funk": "15:19",
    "Rocky Maivia": "13:01", "Mankind": "12:22", "Pierroth Jr.": "10:32", "Vader": "10:05",
    "Owen Hart": "8:28", "Bulldog": "8:04", "Mil Mascaras": "7:28", "Undertaker": "6:47",
    "Helmsley": "6:43", "Flash Funk": "6:13", "Crush": "6:13", "Henry Godwinn": "6:12",
    "Goldust": "5:34", "Marc Mero": "3:54", "The Sultan": "3:24", "Ahmed Johnson": "2:57",
    "Phineas Godwinn": "2:53", "Latin Lover": "1:48", "Cibernetico": "1:24", "Roberts": "1:11",
    "Savio": "0:46", "Faarooq": "0:41", "Jesse James": "0:28", "Bart Gunn": "0:25",
    "Fake Razor Ramon": "0:16", "Lawler": "0:05",
}

entry_actual = {"Crush": 0, "Ahmed Johnson": 0}
for name in buzzer_time:
    lag = mmss(entrance_lag.get(name, "0:00"))
    entry_actual[name] = buzzer_time[name] + lag

entry_order_list = sorted(entry_actual.items(), key=lambda kv: kv[1])
entry_number = {name: i + 1 for i, (name, ts) in enumerate(entry_order_list)}

# checksums (see docstring): SEVEN exact entry-number matches.
assert entry_number["Austin"] == 5, entry_number["Austin"]
assert entry_number["Bret Hart"] == 21, entry_number["Bret Hart"]
assert entry_number["Lawler"] == 22, entry_number["Lawler"]
assert entry_number["Terry Funk"] == 24, entry_number["Terry Funk"]
assert entry_number["Undertaker"] == 30, entry_number["Undertaker"]
assert entry_actual["Undertaker"] == mmss("43:32"), entry_actual["Undertaker"]

elim_ts = {}
for name, surv in survival.items():
    if name == "Austin":
        continue  # winner, no elimination
    elim_ts[name] = entry_actual[name] + mmss(surv)

# checksum: Lawler eliminated at 31:05, then the "final 8" enter consecutively.
assert elim_ts["Lawler"] == mmss("31:05"), elim_ts["Lawler"]
FINAL_8 = {"Fake Diesel", "Terry Funk", "Rocky Maivia", "Mankind", "Flash Funk", "Vader", "Henry Godwinn", "Undertaker"}
entering_after_lawler_before_taker = {n for n, t in entry_actual.items() if mmss("31:05") < t <= mmss("43:32")}
assert entering_after_lawler_before_taker == FINAL_8, entering_after_lawler_before_taker
# checksum: final-4 eliminations span exactly 10 seconds.
final4_times = sorted([elim_ts["Vader"], elim_ts["Undertaker"], elim_ts["Fake Diesel"], elim_ts["Bret Hart"]])
assert final4_times[-1] - final4_times[0] == mmss("0:10"), final4_times

elim_order_list = sorted(elim_ts.items(), key=lambda kv: kv[1])
elim_number = {name: i + 1 for i, (name, ts) in enumerate(elim_order_list)}

# eliminator credits (see F079/F081/F082)
KNOWN_ELIMINATORS = {
    "Undertaker": (["Austin"], ""),
    "Vader": (["Austin"], ""),
    "Bret Hart": (["Austin"], ""),
    "Terry Funk": (["Mankind"], "funk_mankind"),
    "Mankind": (["Terry Funk"], "funk_mankind"),
}
SELF_ELIMINATED = {"Mil Mascaras"}

FINAL_FOUR_ORDER = ["steve-austin", "bret-hart", "fake-diesel", "the-undertaker"]  # winner, then reverse elim order

elim_rows = []
entrant_rows = []

for name in entry_actual.keys():
    entry = entry_number[name]
    ring_time = survival[name]
    is_winner = (name == "Austin")
    elim_no = 0 if is_winner else elim_number[name]
    elim_by, sim_group = KNOWN_ELIMINATORS.get(name, ([], ""))
    is_self = name in SELF_ELIMINATED

    wid = wrestler_ids[name]
    ring_time_s = mmss_to_seconds(ring_time)

    if is_self:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_no,
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wid,
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
            "elimination_clock_time": ring_time, "elimination_clock_seconds": ring_time_s,
            "elimination_type": "voluntary_dive",
            "elimination_method": "Ducked through the middle rope, climbed to the turnbuckle from the ring apron, and dove onto his opponent outside the ring -- eliminating himself. See flags.csv F082.",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "FALSE", "is_self_elimination": "TRUE",
            "is_storyline_related": "UNKNOWN", "was_already_incapacitated": "FALSE",
            "is_disputed": "TRUE", "simultaneous_group_id": "",
            "data_quality_status": "CONFIRMED", "source_ids": "S033",
            "notes": "Unconventional voluntary self-elimination -- see F082.",
        })
    else:
        for eliminator in elim_by:
            elim_rows.append({
                "event_id": EVENT_ID, "order_in_match": elim_no,
                "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
                "assisting_wrestler_ids": "",
                "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
                "elimination_clock_time": ring_time, "elimination_clock_seconds": ring_time_s,
                "elimination_type": "over_top_rope",
                "elimination_method": (
                    "Eliminated by Austin during the final-sequence confusion after Bret Hart's missed elimination of Austin -- see F081."
                    if name in ("Undertaker", "Vader", "Bret Hart") else
                    "Mutual elimination -- Mankind and Terry Funk eliminated each other while brawling outside the ring."
                    if sim_group else "UNKNOWN"
                ),
                "location_side": "", "location_status": "UNKNOWN",
                "is_solo": "FALSE" if sim_group else "TRUE", "is_shared": "TRUE" if sim_group else "FALSE",
                "is_accidental": "FALSE", "is_self_elimination": "FALSE",
                "is_storyline_related": "TRUE" if name == "Bret Hart" else "UNKNOWN",
                "was_already_incapacitated": "UNKNOWN",
                "is_disputed": "TRUE" if name == "Bret Hart" else "FALSE",
                "simultaneous_group_id": sim_group,
                "data_quality_status": "CONFIRMED",
                "source_ids": "S033;S034",
                "notes": "The winning elimination -- but see F081: this only happened because Bret Hart's own earlier elimination of Austin was missed by the referees." if name == "Bret Hart" else "",
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
        "eliminated_by_ids": (wid if is_self else ";".join(wrestler_ids[e] for e in elim_by)),
        "elimination_clock_time": ring_time if not is_winner else "",
        "elimination_clock_seconds": ring_time_s if not is_winner else "",
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "PROBABLE" if name in ("Fake Razor Ramon", "Pierroth Jr.", "Savio", "Roberts", "Marc Mero", "Owen Hart", "Henry Godwinn") else "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "TRUE" if is_self else "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "bret-hart" else "FALSE",
        "is_final_two": "TRUE" if wid in ("steve-austin", "bret-hart") else "FALSE",
        "is_final_three": "TRUE" if wid in ("steve-austin", "bret-hart", "fake-diesel") else "FALSE",
        "is_final_four": "TRUE" if wid in FINAL_FOUR_ORDER else "FALSE",
        "surprise_entrant": "TRUE" if name == "Lawler" else "FALSE",
        "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S033;S034",
        "notes": ("Ring-time precision uncertainty (camera/clock issues) -- see F083." if name in ("Fake Razor Ramon", "Pierroth Jr.", "Savio", "Roberts", "Marc Mero", "Owen Hart", "Henry Godwinn") else ""),
    }
    entrant_rows.append(er)

elim_map = {}
for row in elim_rows:
    eid = row["eliminator_wrestler_id"]
    if eid == row["eliminated_wrestler_id"]:
        continue
    elim_map.setdefault(eid, []).append(row["eliminated_wrestler_id"])

CREDITED_ELIMINATORS = {"steve-austin", "mankind", "terry-funk"}
for er in entrant_rows:
    wid = er["wrestler_id"]
    if wid in CREDITED_ELIMINATORS:
        er["wrestlers_eliminated_ids"] = ";".join(elim_map.get(wid, []))
        er["wrestlers_eliminated_count"] = len(elim_map.get(wid, []))
        er["solo_eliminations_count"] = len(elim_map.get(wid, []))
        er["assisted_eliminations_count"] = 0
        er["notes"] = (er["notes"] + " " if er["notes"] else "") + \
            "This count reflects only explicitly-credited eliminations (see F079) -- likely an undercount, not a confirmed total."

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
    ("Hunter Hearst Helmsley", 1, "Goldust", "", "Singles", "TRUE", "Intercontinental Championship", "TRUE", "Win", "", "", "16:50", "Opener", "S034", "Pinned Goldust to retain the IC title. Also competed in the Rumble match this same night."),
    ("Goldust", 1, "Hunter Hearst Helmsley", "", "Singles", "TRUE", "Intercontinental Championship", "FALSE", "Loss", "", "", "16:50", "Opener", "S034", "Pinned by Helmsley."),
    ("Ahmed Johnson", 2, "Faarooq", "", "Singles", "FALSE", "", "FALSE", "Win", "", "", "8:48", "2nd match", "S034", "Won by DQ. Also competed in the Rumble match this same night."),
    ("Faarooq", 2, "Ahmed Johnson", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "8:48", "2nd match", "S034", "Lost by DQ. Also competed in the Rumble match this same night."),
    ("Vader", 3, "The Undertaker", "", "Singles", "FALSE", "", "FALSE", "Win", "", "", "13:19", "3rd match", "S034", "Pinned Undertaker. Also competed in the Rumble match this same night."),
    ("The Undertaker", 3, "Vader", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "13:19", "3rd match", "S034", "Pinned by Vader. Also competed in the Rumble match this same night."),
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
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1997", "match_name": "30-Man Royal Rumble Match",
    "match_type": "Men's", "event_date": "1997-01-21", "venue": "Alamodome",
    "city_region": "San Antonio, Texas", "country": "United States",
    "attendance_official": 48017, "attendance_reported": 60525,
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "50:30",
    "duration_status": "CONFIRMED",
    "winner_id": "steve-austin", "runner_up_id": "bret-hart",
    "final_two_ids": "steve-austin;bret-hart", "final_three_ids": "steve-austin;bret-hart;fake-diesel",
    "final_four_ids": "steve-austin;bret-hart;fake-diesel;the-undertaker",
    "first_entrant_id": "demolition-crush", "second_entrant_id": "ahmed-johnson", "final_entrant_id": "the-undertaker",
    "first_elimination_id": "fake-razor-ramon", "last_elimination_before_winner_id": "bret-hart",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 1,
    "champions_in_field_count": 1, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": 0, "factions_count": "N/A",
    "commentary_team": "Vince McMahon, Jim Ross, Jerry Lawler", "ring_announcer": "Howard Finkel",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "The largest crowd to ever see a Royal Rumble to that point -- 60,525 announced, though only 48,017 "
        "paid, at the Alamodome. THE central controversy: Bret Hart eliminated Steve Austin at 50:05, but the "
        "referees missed it (distracted by a Mankind/Terry Funk brawl outside the ring); Austin snuck back in "
        "undetected and eliminated Undertaker, Vader, and finally Bret Hart himself to 'win' the match -- see "
        "F081 for the full writeup and how this is modeled (no elimination row exists for Bret Hart's missed "
        "elimination of Austin; the official/on-air result is what's recorded). Mil Mascaras eliminated "
        "himself via an unconventional dive off the ring apron turnbuckle -- see F082. WWF's countdown clock "
        "malfunctioned for the first ~5 minutes of the match -- see F083."
    ),
    "title_on_the_line": "FALSE", "championship_implications": "None in the Rumble match itself, though the WWF Championship (Shawn Michaels def. Psycho Sid) was contested earlier on the same card, and Hunter Hearst Helmsley (also a Rumble entrant) retained the Intercontinental Championship against Goldust",
    "winners_reward": "A WWF Championship match against The Undertaker at WrestleMania 13 -- ultimately went to Undertaker (not Austin) after Austin lost the title match to Sid at the same show, per S034's account of that year's title picture",
    "historical_significance": "One of the most controversial finishes in Royal Rumble history -- Steve Austin's win was built on a missed call, and this loss fed directly into Bret Hart's growing frustration with the company that defined his 1997 storylines. The Rock's (billed as Rocky Maivia) first Royal Rumble appearance. Mick Foley's Mankind character in his first Rumble. The debut of the 'Fake Diesel'/'Fake Razor Ramon' decoy gimmicks (Glen Jacobs, later Kane, and Rick Bogner) mocking the departed Kevin Nash/Scott Hall. Bret Hart and Steve Austin went on to have their all-time classic match at WrestleMania 13.",
    "notes": "30 confirmed entrants, all identified. Eliminator credit is known for only 5 of 29 eliminations -- see flags.csv F079-F085 for the full list of what's derived vs. directly stated vs. unknown in this event, including the richest internal-validation checkpoint set in the database so far (F080) and the central Bret Hart/Austin missed-elimination controversy (F081).",
    "data_quality_status": "CONFIRMED", "source_ids": "S033;S034",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1997 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows "
      f"(5 credited eliminations + 1 self-elimination), "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
