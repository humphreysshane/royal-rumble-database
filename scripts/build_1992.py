# -*- coding: utf-8 -*-
"""
Builds all rows for the 1992 Royal Rumble — schema v2.

Unlike 1991, this event's material sits under its own correct Heading-1
("1992 Royal Rumble Stats") in Shane's Word doc -- no misfiling issue.
There is still no Excel tab for 1992 (the workbook only has 1988/1989/1990
tabs), so this is built the same way as 1991: from a Cageside-style timing
analysis (survival times, entrance times, time-between-buzzers, ring
crowdedness) plus a Dan Wahlers narrative history.

SOURCES CONSULTED THIS PASS:
  S020 "1992 Rumble Stats - Cageside" section (Shane's doc)          tier 9
  S021 Dan Wahlers "History of the Royal Rumble" -- 1992 chapter     tier 9

THIS EVENT IS STRUCTURALLY LIKE 1991 -- READ BEFORE EXTENDING:
  - Entry order (all 30) is CONFIRMED. The first two entrants (British
    Bulldog #1, Ted DiBiase #2) are named explicitly ("entrances took place
    prior to the start of the match"), and S020's "Time Between Buzzers"
    list gives the remaining 28 entrants in exact chronological buzzer
    order.
  - Ring/survival time for all 30 is CONFIRMED, directly stated by S020's
    Survival Times list.
  - Elimination timestamp/order is DERIVED, computed exactly as in 1991:
    (cumulative buzzer time) + (entrance-time lag) + (survival time) =
    elimination timestamp, then all 29 actually-eliminated entrants (every
    entrant except winner Ric Flair) are ranked by that timestamp.
  - VALIDATION -- this method was spot-checked against FIVE independent
    internal checkpoints this time (more than 1991's four), and every one
    matched the derived clock to the exact second:
      1. Flair (3rd entrant) enters the ring at 2:31 per S020's own prose.
      2. Piper (15th entrant) enters the ring at 26:31 per S020's own prose.
      3. Big Boss Man's elimination at 25:53, per S020's own "lone man in
         the ring" framing.
      4. Sid Justice's elimination (the match-ending one) computes to
         exactly 62:02 -- matching S020's stated total match duration of
         "1h 02m 02s" precisely.
      5. A genuinely interesting discovery: S020's own "Miscellaneous
         Notes" subsection states FOUR elimination timestamps (Michaels/
         Santana's mutual elimination at "31:47", Duggan/Virgil's mutual
         elimination at "59:08", Savage eliminating Roberts at "47:10", and
         Sid's elimination of Piper/Martel at "1:08:18"/"1:08:19") that all
         *disagree* with the derived clock by the exact same offset: +7:40
         in every single case. This is not four separate errors -- it's one
         systematic clock offset, most plausibly because the "Miscellaneous
         Notes" subsection was timed from broadcast/video start rather than
         from the opening bell (when British Bulldog/DiBiase were already
         in the ring). Once each of those four narrative timestamps is
         corrected by -7:40, all four land EXACTLY on the derived clock's
         own elimination timestamps -- including the disputed "33m 33s"
         Big Boss Man reference in the same subsection, which normalizes to
         25:53 and turns out to be the SAME event already independently
         confirmed by checkpoint #3 above, not a different wrestler or a
         real inconsistency as first suspected while reading the raw text.
         All elimination_clock_time values stored in this build use the
         derived/normalized clock (consistent throughout the rest of the
         event's data), not the raw "Miscellaneous Notes" text. See F029.
  - Eliminator credit is CONFIRMED for 11 of 29 eliminations (DiBiase by
    British Bulldog; Roberts by Savage; Michaels<->Santana mutual; Duggan
    <->Virgil mutual; Savage, Hogan, Martel, and Piper all by Sid Justice;
    Sid by Flair, the winning elimination) plus one self-elimination (Big
    Boss Man, untouched, missed a mid-air attack on Flair). The other 17
    entrants' eliminator is UNKNOWN -- S020 is a timing analysis, not a
    blow-by-blow recap, so most individual eliminations aren't narrated.
    wrestlers_eliminated_count is only populated for wrestlers with a
    confirmed credit; everyone else is left blank (UNKNOWN), not 0.
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
EVENT_ID = "RR1992M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S020", "'1992 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring crowdedness, miscellaneous notes). Correctly filed under its own '1992 Royal Rumble Stats' Heading-1 -- no misfiling issue this year, unlike 1991. NOT live-fetched this pass."),
    ("S021", "Dan Wahlers, 'History of the Royal Rumble' -- 1992 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance as 17,014, full narrative history (Ric Flair's WWF entrance and Rumble win storyline, vacant-title stipulation), and undercard match results."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F027", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "Only 11 of this match's 29 real eliminations have an eliminator explicitly named: Ted DiBiase (by "
     "British Bulldog), Jake Roberts (by Randy Savage), Shawn Michaels and Tito Santana (mutual -- 'threw "
     "each other out of the ring'), Jim Duggan and Virgil (mutual, same wording), Randy Savage, Hulk Hogan, "
     "Rick Martel, and Roddy Piper (all four by Sid Justice), and Sid Justice himself (by Ric Flair, the "
     "winning elimination). One more (Big Boss Man) is a confirmed self-elimination with no opposing "
     "eliminator. The other 17 entrants' eliminated_by_ids are blank (UNKNOWN) -- no eliminations.csv row "
     "exists for them, since writing one would require inventing an eliminator. wrestlers_eliminated_count "
     "is left blank (not 0) for every entrant except the 5 with a confirmed credit (British Bulldog, Randy "
     "Savage, Shawn Michaels, Tito Santana, Jim Duggan, Virgil, Sid Justice, Ric Flair), since a true zero "
     "would be an unsupported claim.",
     "S020;S021", "open", "2026-09-15"),
    ("F028", EVENT_ID, "eliminations;entrants", "*", "elim_number", "unverified",
     "Elimination ORDER (not eliminator identity) is a DERIVED calculation: each entrant's buzzer time + "
     "entrance-time lag + survival time = an elimination timestamp, then all 29 actually-eliminated entrants "
     "are ranked by that. Spot-verified against 5 independent checkpoints in S020's own prose, all matching "
     "to the exact second -- see script docstring for the specific checkpoints, including the clock-offset "
     "discovery in F029. High confidence, but still DERIVED rather than a directly-stated fact.",
     "S020", "open", "2026-09-15"),
    ("F029", EVENT_ID, "eliminations", "big-bossman;shawn-michaels;tito-santana;jim-duggan;virgil;randy-savage;rick-martel;roddy-piper", "elimination_clock_time", "conflicting_sources",
     "S020's own 'Miscellaneous Notes' subsection states four elimination timestamps that are each exactly "
     "7 minutes 40 seconds LATER than the same events' timestamps computed from the same document's own "
     "Survival Times / buzzer-interval data (which independently checksums against the stated total match "
     "duration of 62:02 and two other in-text entrance-time checkpoints -- see docstring). Affected: "
     "Michaels/Santana's mutual elimination ('31:47' in prose vs. derived 24:07), Duggan/Virgil's mutual "
     "elimination ('59:08' vs. derived 51:28), Savage eliminating Roberts ('47:10' vs. derived 39:30), Sid "
     "eliminating Piper/Martel ('1:08:18'/'1:08:19' vs. derived 60:38/60:39), and a 'Big Boss Man' self-"
     "elimination reference ('33:33' vs. derived/independently-stated 25:53). Because all five instances "
     "share the identical +7:40 offset, this looks like one systematic clock-convention difference (most "
     "likely: this subsection was timed from broadcast/video start rather than the opening bell) rather than "
     "five unrelated transcription errors -- and because the derived clock is independently checksummed "
     "elsewhere in the same document while the raw 'Miscellaneous Notes' timestamps are not (one of them, "
     "1:08:19, is literally later than the document's own stated total match length of 62:02, which is "
     "impossible), the derived/normalized clock is used as elimination_clock_time throughout this build. "
     "Flagged as conflicting rather than silently corrected, since it rests on an inference (the +7:40 "
     "broadcast-start theory) rather than a directly-stated fact -- worth confirming during the post-1992 "
     "fact-check pass if an independent timing source can be found.",
     "S020", "open", "2026-09-15"),
    ("F030", EVENT_ID, "entrants", "randy-savage", "elimination_type", "needs_human_judgement",
     "Near-elimination controversy, logged to near_eliminations.csv: after eliminating Jake Roberts (~39:30 "
     "derived), Randy Savage intentionally jumped over the top rope in pursuit of Roberts, with both feet "
     "touching the floor outside the ring at ~39:32. Announcers Gorilla Monsoon and Bobby Heenan initially "
     "called it a self-elimination blunder, then reversed course and ruled Savage was not eliminated because "
     "no opponent propelled him over the ropes. S020 itself points out the announcers didn't apply this same "
     "standard ~7 minutes later when Big Boss Man went over the top untouched (see F029/near_eliminations.csv "
     "for the full incident and S020's own editorializing about the inconsistent ruling).",
     "S020", "open", "2026-09-15"),
    ("F031", EVENT_ID, "wrestlers", "col-mustafa", "real_name;aliases_ring_names", "unverified",
     "'Col. Mustafa' entered as the 24th entrant, per S020/S021. Neither source in this pass states his real "
     "identity or connects this ring name to any other wrestler already in this database. Left as a fully "
     "distinct, fully UNKNOWN-bio new wrestler for now rather than assumed to be a renamed/returning wrestler "
     "-- worth specifically checking during the post-1992 fact-check pass, since gimmick gulf-war-era renames "
     "of returning wrestlers were common around this period per the general shape of 1990/1991's storylines "
     "already in this database (e.g. Sgt. Slaughter's own angle, per RR1991M's notes).",
     "S020;S021", "open", "2026-09-15"),
    ("F032", EVENT_ID, "wrestlers", "*", "real_name;dob;billed_height_m_at_event;billed_weight_kg_at_event;birthplace", "unverified",
     "7 wrestlers appear in this database for the first time via 1992 (Ric Flair, Jerry Sags, "
     "Irwin R. Schyster, The Berzerker, Col. Mustafa, Skinner, Sid Justice) with zero bio data in either "
     "source -- names only. Left entirely UNKNOWN, same pattern as 1990/1991's equivalent flags. Owen Hart "
     "and Beau/Blake Beverly (non-Rumble undercard entrants) are the same -- see show_appearances.csv. "
     "'Repo Man' and 'Typhoon' were initially treated as new wrestlers too but are actually Barry Darsow "
     "(this database's 'Smash') and Fred Ottman (this database's 'Tugboat') under new gimmick names -- "
     "corrected during the fact-check pass, see the reused-id notes in this script.",
     "S020;S021", "open", "2026-09-15"),
    ("F033", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as prior years' F005/F013/F020/F026.",
     "", "open", "2026-09-15"),
    ("F034", EVENT_ID, "events;eliminations;entrants", "*", "n/a", "out_of_scope_no_tool",
     "Cross-event fact-check tool limitation, referenced from 1989's F011 and from S026's own description in "
     "sources.csv: the AI web-fetch tool used this pass visibly scrambles long ordered Wikipedia tables when "
     "asked to reproduce them in bulk. Observed most clearly on this event -- the fetched 'Royal Rumble (1992)' "
     "entry table conflated a 'Draw' column with a separate 'Entry #' column inconsistently row to row, and "
     "1988's equivalent fetch came back with duplicate 'entry order' labels consistent with the source having "
     "been silently re-sorted alphabetically by wrestler name rather than preserving entry order. Attempts to "
     "work around this by requesting raw wikitext via '?action=raw' URLs failed outright (PROVENANCE_REQUIRED "
     "permission-timeout errors on all 5 parallel attempts); Cagematch match pages and prowrestlinghistory.com "
     "were tried as alternatives and found to either lack detailed entry/elimination breakdowns or be equally "
     "lossy/summarized. Resolution adopted for this whole pass: WebFetch was trusted only for single-scalar "
     "facts (attendance, date, venue, winner, duration, referees, commentary team) and explicitly NOT trusted "
     "for bulk-extracted entry-order/elimination-order data for ANY of the five events (1988-1992) built so "
     "far -- that detail remains cross-checked only within Shane's own document's internal sources, not "
     "against Wikipedia's tables. A full row-by-row Wikipedia table cross-check for all five events remains "
     "open for a future pass, ideally with a different extraction tool/method.",
     "S026", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only (Rumble entrants).
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Ric Flair", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Royal Rumble debut and win -- entered the WWF in summer 1991 after leaving the NWA. Won the vacant WWF Championship in this match per S021. No bio data in either source this pass.", "S020;S021"),
    ("Jerry Sags", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Nasty Boy", "", "", "One half of The Nasty Boys (w/ Brian Knobbs, who is not in this year's Rumble field). No bio data in either source this pass.", "S020"),
    ("Irwin R. Schyster", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "IRS", "", "", "Referred to as 'IRS' throughout S020's timing lists. No bio data in either source this pass.", "S020"),
    ("The Berzerker", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Berserker", "", "", "S021's match-results text spells this 'The Berserker'; S020's timing lists consistently use 'The Berzerker' -- treated as the same person, cosmetic spelling variance only. No bio data in either source this pass.", "S020;S021"),
    ("Col. Mustafa", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No real-identity connection stated in either source this pass -- see flags.csv F031. No bio data in either source this pass.", "S020;S021"),
    ("Skinner", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S020"),
    ("Sid Justice", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Final entrant among the final four; eliminated Savage, Hogan, Piper and Martel before being eliminated by Flair for the win. No bio data in either source this pass.", "S020;S021"),
]

reused = {
    "British Bulldog": "british-bulldog", "Ted DiBiase": "ted-dibiase", "Haku": "haku",
    "Shawn Michaels": "shawn-michaels", "Tito Santana": "tito-santana", "The Barbarian": "the-barbarian",
    "Texas Tornado": "texas-tornado", "Greg Valentine": "greg-valentine", "Nikolai Volkoff": "nikolai-volkoff",
    "Big Boss Man": "big-bossman", "Hercules": "hercules", "Roddy Piper": "roddy-piper",
    "Jake Roberts": "jake-roberts", "Jim Duggan": "jim-duggan", "Jimmy Snuka": "jimmy-snuka",
    "The Undertaker": "the-undertaker", "Randy Savage": "randy-savage", "Virgil": "virgil",
    "Rick Martel": "rick-martel", "Hulk Hogan": "hulk-hogan", "Sgt. Slaughter": "sgt-slaughter",
    "The Warlord": "the-warlord",
    # "Repo Man" is Barry Darsow -- the same performer already in this database as "Smash" of
    # Demolition (wrestler_id smash, added 1989). Confirmed via the fact-check pass (F0xx);
    # reusing his existing id rather than creating a duplicate "repo-man" id.
    "Repo Man": "smash",
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
    ("Ric Flair", "1:49"), ("Jerry Sags", "2:08"), ("Haku", "2:01"), ("Shawn Michaels", "2:06"),
    ("Tito Santana", "1:59"), ("The Barbarian", "2:02"), ("Texas Tornado", "2:02"), ("Repo Man", "2:00"),
    ("Greg Valentine", "2:01"), ("Nikolai Volkoff", "2:01"), ("Big Boss Man", "2:00"), ("Hercules", "2:01"),
    ("Roddy Piper", "2:11"), ("Jake Roberts", "2:00"), ("Jim Duggan", "2:02"), ("Irwin R. Schyster", "2:01"),
    ("Jimmy Snuka", "2:01"), ("The Undertaker", "2:02"), ("Randy Savage", "2:01"), ("The Berzerker", "3:21"),
    ("Virgil", "2:02"), ("Col. Mustafa", "2:00"), ("Rick Martel", "2:01"), ("Hulk Hogan", "2:00"),
    ("Skinner", "2:01"), ("Sgt. Slaughter", "2:03"), ("Sid Justice", "2:00"), ("The Warlord", "2:03"),
]
cum = 0
buzzer_time = {}
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("57:59"), f"buzzer checksum failed: {cum}"

entrance_lag = {
    "Ric Flair": "0:42", "The Undertaker": "0:39", "The Warlord": "0:32", "Repo Man": "0:25",
    "Jerry Sags": "0:23", "Irwin R. Schyster": "0:23", "Sgt. Slaughter": "0:23", "Col. Mustafa": "0:21",
    "Jimmy Snuka": "0:20", "Texas Tornado": "0:19", "Jim Duggan": "0:18", "The Berzerker": "0:17",
    "Shawn Michaels": "0:15", "Nikolai Volkoff": "0:14", "Jake Roberts": "0:13", "The Barbarian": "0:12",
    "Hercules": "0:11", "Skinner": "0:11", "Haku": "0:10", "Roddy Piper": "0:10", "Hulk Hogan": "0:10",
    "Sid Justice": "0:10", "Tito Santana": "0:08", "Greg Valentine": "0:08", "Randy Savage": "0:07",
    "Virgil": "0:07", "Rick Martel": "0:07", "Big Boss Man": "0:06",
}

survival = {
    "Ric Flair": "59:31", "Roddy Piper": "34:08", "Irwin R. Schyster": "27:03", "British Bulldog": "23:27",
    "Randy Savage": "22:27", "Jim Duggan": "20:47", "Shawn Michaels": "15:48", "Tito Santana": "13:56",
    "The Undertaker": "13:52", "The Barbarian": "12:57", "Rick Martel": "12:39", "Hulk Hogan": "11:30",
    "Jake Roberts": "10:56", "Texas Tornado": "9:21", "The Berzerker": "9:00", "Virgil": "7:30",
    "Repo Man": "6:26", "Sid Justice": "5:56", "Sgt. Slaughter": "4:37", "Greg Valentine": "4:14",
    "Big Boss Man": "3:38", "Col. Mustafa": "2:36", "Jimmy Snuka": "2:28", "Skinner": "2:13",
    "Haku": "1:52", "The Warlord": "1:43", "Ted DiBiase": "1:19", "Jerry Sags": "1:05",
    "Nikolai Volkoff": "1:04", "Hercules": "0:56",
}

entry_actual = {"British Bulldog": 0, "Ted DiBiase": 0}
for name in buzzer_time:
    lag = mmss(entrance_lag.get(name, "0:00"))
    entry_actual[name] = buzzer_time[name] + lag

# checksums (see docstring): Flair enters at 2:31, Piper enters at 26:31.
assert entry_actual["Ric Flair"] == mmss("2:31"), entry_actual["Ric Flair"]
assert entry_actual["Roddy Piper"] == mmss("26:31"), entry_actual["Roddy Piper"]

entry_order_list = sorted(entry_actual.items(), key=lambda kv: kv[1])
entry_number = {name: i + 1 for i, (name, ts) in enumerate(entry_order_list)}

elim_ts = {}
for name, surv in survival.items():
    if name == "Ric Flair":
        continue  # winner, no elimination
    elim_ts[name] = entry_actual[name] + mmss(surv)

# checksums: Big Boss Man's self-elimination at 25:53; Sid's match-ending
# elimination matches the stated total match duration of 62:02 exactly.
assert elim_ts["Big Boss Man"] == mmss("25:53"), elim_ts["Big Boss Man"]
assert elim_ts["Sid Justice"] == mmss("1:02:02"), elim_ts["Sid Justice"]
# the four "Miscellaneous Notes" mutual/credited eliminations, normalized
# by -7:40 from the raw prose, land exactly on the independently-derived
# clock -- see F029.
assert elim_ts["Shawn Michaels"] == elim_ts["Tito Santana"] == mmss("24:07")
assert elim_ts["Jim Duggan"] == elim_ts["Virgil"] == mmss("51:28")
assert elim_ts["Jake Roberts"] == mmss("39:30")
assert elim_ts["Rick Martel"] == mmss("1:00:38") and elim_ts["Roddy Piper"] == mmss("1:00:39")

elim_order_list = sorted(elim_ts.items(), key=lambda kv: kv[1])
elim_number = {name: i + 1 for i, (name, ts) in enumerate(elim_order_list)}

# eliminator credits: name -> (list_of_eliminator_names, is_self, sim_group_label)
KNOWN_ELIMINATORS = {
    "Ted DiBiase": (["British Bulldog"], False, ""),
    "Jake Roberts": (["Randy Savage"], False, ""),
    "Shawn Michaels": (["Tito Santana"], False, "michaels_santana"),
    "Tito Santana": (["Shawn Michaels"], False, "michaels_santana"),
    "Jim Duggan": (["Virgil"], False, "duggan_virgil"),
    "Virgil": (["Jim Duggan"], False, "duggan_virgil"),
    "Randy Savage": (["Sid Justice"], False, ""),
    "Hulk Hogan": (["Sid Justice"], False, ""),
    "Rick Martel": (["Sid Justice"], False, "sid_piper_martel"),
    "Roddy Piper": (["Sid Justice"], False, "sid_piper_martel"),
    "Sid Justice": (["Ric Flair"], False, ""),
    "Big Boss Man": ([], True, ""),
}

FINAL_FOUR_ORDER = ["ric-flair", "sid-justice", "hulk-hogan", "randy-savage"]  # winner, then reverse elim order

elim_rows = []
entrant_rows = []

for name in entry_actual.keys():
    entry = entry_number[name]
    ring_time = survival[name]
    is_winner = (name == "Ric Flair")
    elim_no = 0 if is_winner else elim_number[name]
    elim_by, is_self, sim_group = KNOWN_ELIMINATORS.get(name, ([], False, ""))

    wid = wrestler_ids[name]
    ring_time_s = mmss_to_seconds(ring_time)

    if is_self:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_no,
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wid,
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
            "elimination_clock_time": ring_time,
            "elimination_clock_seconds": ring_time_s,
            "elimination_type": "over_top_rope", "elimination_method": "Lunged mid-air at Ric Flair and missed, went over the top rope untouched",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "TRUE", "is_self_elimination": "TRUE",
            "is_storyline_related": "UNKNOWN", "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE", "simultaneous_group_id": "",
            "data_quality_status": "DERIVED", "source_ids": "S020",
            "notes": "Elimination timestamp derived/normalized -- see flags.csv F029.",
        })
    else:
        for eliminator in elim_by:
            elim_rows.append({
                "event_id": EVENT_ID, "order_in_match": elim_no,
                "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
                "assisting_wrestler_ids": "",
                "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
                "elimination_clock_time": ring_time, "elimination_clock_seconds": ring_time_s,
                "elimination_type": "over_top_rope", "elimination_method": "UNKNOWN",
                "location_side": "", "location_status": "UNKNOWN",
                "is_solo": "FALSE" if sim_group else "TRUE", "is_shared": "TRUE" if sim_group else "FALSE",
                "is_accidental": "FALSE", "is_self_elimination": "FALSE",
                "is_storyline_related": "TRUE" if name in ("Jake Roberts", "Randy Savage") else "UNKNOWN",
                "was_already_incapacitated": "UNKNOWN",
                "is_disputed": "FALSE", "simultaneous_group_id": sim_group,
                "data_quality_status": "CONFIRMED" if name in ("Ted DiBiase",) else "DERIVED",
                "source_ids": "S020;S021",
                "notes": "Elimination timestamp derived/normalized against the +7:40 'Miscellaneous Notes' clock offset -- see flags.csv F029." if sim_group or name in ("Jake Roberts", "Randy Savage", "Rick Martel", "Roddy Piper") else "",
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
        "ring_time_status": "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "TRUE" if is_self else "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "sid-justice" else "FALSE",
        "is_final_two": "TRUE" if wid in ("ric-flair", "sid-justice") else "FALSE",
        "is_final_three": "TRUE" if wid in ("ric-flair", "sid-justice", "hulk-hogan") else "FALSE",
        "is_final_four": "TRUE" if wid in FINAL_FOUR_ORDER else "FALSE",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S020;S021",
        "notes": "",
    }
    entrant_rows.append(er)

# Back-fill wrestlers_eliminated_ids/count -- ONLY for wrestlers with a
# confirmed credit; everyone else stays blank (UNKNOWN), not 0. See F027.
elim_map = {}
for row in elim_rows:
    eid = row["eliminator_wrestler_id"]
    if eid == row["eliminated_wrestler_id"]:
        continue  # self-eliminations don't count toward the "eliminator's" tally
    elim_map.setdefault(eid, []).append(row["eliminated_wrestler_id"])

CREDITED_ELIMINATORS = {"british-bulldog", "randy-savage", "shawn-michaels", "tito-santana",
                         "jim-duggan", "virgil", "sid-justice", "ric-flair"}
for er in entrant_rows:
    wid = er["wrestler_id"]
    if wid in CREDITED_ELIMINATORS:
        er["wrestlers_eliminated_ids"] = ";".join(elim_map.get(wid, []))
        er["wrestlers_eliminated_count"] = len(elim_map.get(wid, []))
        er["solo_eliminations_count"] = len(elim_map.get(wid, []))
        er["assisted_eliminations_count"] = 0
        er["notes"] = (er["notes"] + " " if er["notes"] else "") + \
            "This count reflects only explicitly-credited eliminations (see F027) -- likely an undercount, not a confirmed total."

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# NEAR ELIMINATIONS -- Randy Savage's controversial rope-jump (see F030)
# ---------------------------------------------------------------------------
near_elim_row = {
    "event_id": EVENT_ID, "wrestler_id": "randy-savage", "timestamp": "39:32",
    "attempted_by_id": "", "how_survived": "Intentionally jumped over the top rope in pursuit of Jake Roberts (just eliminated); announcers initially called it a self-elimination blunder, then ruled he was not eliminated since no opponent propelled him over the ropes -- see flags.csv F030.",
    "apron_duration_seconds": "", "feet_touched_floor": "TRUE", "hands_touched_floor": "UNKNOWN",
    "rope_grab": "UNKNOWN", "pulled_back_in_by_id": "",
    "video_source": "", "reviewer": "", "confidence": "", "human_verified": "FALSE",
}
with open(os.path.join(DATA_DIR, "near_eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=NEAR_ELIMINATIONS_FIELDS)
    writer.writerow(near_elim_row)

# ---------------------------------------------------------------------------
# SHOW APPEARANCES / other card personnel not in the Rumble match
# ---------------------------------------------------------------------------
show_wrestlers = {
    "Owen Hart": None, "Jim Neidhart": "jim-neidhart", "The Great Tanaka": "the-great-tanaka",
    "Kato": "kato", "The Mountie": "jacques-rougeau", "Beau Beverly": None, "Blake Beverly": None,
    "Bushwhacker Luke": "luke-williams", "Bushwhacker Butch": "butch-miller",
    # "Typhoon" is Fred Ottman -- the same performer already in this database as "Tugboat"
    # (wrestler_id tugboat, added 1990). Confirmed via the fact-check pass (F0xx); reusing his
    # existing id rather than creating a duplicate "typhoon" id.
    "Earthquake": "earthquake", "Typhoon": "tugboat", "Hawk": "hawk", "Animal": "animal",
}
for name, wid in show_wrestlers.items():
    wrestler_ids[name] = wid if wid else slugify(name)

new_people_rows = [
    ("Owen Hart", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S021"),
    ("Beau Beverly", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Beverly Brothers", "", "", "Half of The Beverly Brothers (w/ Blake Beverly). No bio data in either source this pass.", "S021"),
    ("Blake Beverly", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Beverly Brothers", "", "", "Half of The Beverly Brothers (w/ Beau Beverly). No bio data in either source this pass.", "S021"),
]
with open(os.path.join(DATA_DIR, "wrestlers.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in new_people_rows:
        writer.writerow([slugify(row[0])] + list(row))

show_appearances = [
    ("Owen Hart", "Wrestler (undercard)", "", "Face", "", "w/ Jim Neidhart def. The Orient Express (Tanaka & Kato) (17:18); Hart pinned Tanaka"),
    ("Jim Neidhart", "Wrestler (undercard)", "", "Face", "", "w/ Owen Hart def. The Orient Express (17:18)"),
    ("The Great Tanaka", "Wrestler (undercard)", "", "Heel", "", "w/ Kato lost to Hart & Neidhart (17:18); pinned by Hart"),
    ("Kato", "Wrestler (undercard)", "", "Heel", "", "w/ Tanaka lost to Hart & Neidhart (17:18)"),
    ("The Mountie", "Wrestler (undercard)", "Intercontinental Championship", "Heel", "Intercontinental Championship", "Lost the IC Title to Roddy Piper (5:22) via sleeper hold"),
    ("Beau Beverly", "Wrestler (undercard)", "", "Heel", "", "w/ Blake def. The Bushwhackers (14:56); Blake pinned Butch"),
    ("Blake Beverly", "Wrestler (undercard)", "", "Heel", "", "w/ Beau def. The Bushwhackers (14:56); pinned Butch"),
    ("Bushwhacker Luke", "Wrestler (undercard)", "", "Face", "", "w/ Butch lost to The Beverly Brothers (14:56)"),
    ("Bushwhacker Butch", "Wrestler (undercard)", "", "Face", "", "w/ Luke lost to The Beverly Brothers (14:56); pinned by Blake"),
    ("Earthquake", "Wrestler (undercard)", "World Tag Team Championship", "Heel", "World Tag Team Championship", "w/ Typhoon def. Legion of Doom (9:24) by count-out to retain the WWF Tag Team Titles -- did NOT compete in this year's Rumble match"),
    ("Typhoon", "Wrestler (undercard)", "World Tag Team Championship", "Heel", "World Tag Team Championship", "w/ Earthquake def. Legion of Doom (9:24) by count-out, retained the titles. 'Typhoon' is Fred Ottman (this database's 'Tugboat' from 1990), turned heel and renamed -- confirmed via the fact-check pass (F0xx), reusing wrestler_id tugboat rather than creating a duplicate."),
    ("Hawk", "Wrestler (undercard)", "", "Face", "", "w/ Animal lost to The Natural Disasters (9:24) by count-out -- did NOT compete in this year's Rumble match"),
    ("Animal", "Wrestler (undercard)", "", "Face", "", "w/ Hawk lost to The Natural Disasters (9:24) by count-out"),
]
with open(os.path.join(DATA_DIR, "show_appearances.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for name, role, managed, align, title, notes in show_appearances:
        pid = wrestler_ids.get(name, slugify(name))
        writer.writerow([EVENT_ID, pid, name, role, managed, align, title, notes, "PROBABLE", "S021"])

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD
# ---------------------------------------------------------------------------
other_matches = [
    ("Owen Hart", 1, "The Great Tanaka, Kato", "Jim Neidhart", "Tag", "FALSE", "", "FALSE", "Win", "", "", "17:18", "Opener", "S021", "Pinned Tanaka."),
    ("Jim Neidhart", 1, "The Great Tanaka, Kato", "Owen Hart", "Tag", "FALSE", "", "FALSE", "Win", "", "", "17:18", "Opener", "S021", ""),
    ("The Great Tanaka", 1, "Owen Hart, Jim Neidhart", "Kato", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "17:18", "Opener", "S021", "Pinned by Hart."),
    ("Kato", 1, "Owen Hart, Jim Neidhart", "The Great Tanaka", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "17:18", "Opener", "S021", ""),
    ("Roddy Piper", 2, "The Mountie", "", "Singles", "TRUE", "Intercontinental Championship", "FALSE", "Win", "TRUE", "FALSE", "5:22", "2nd match", "S021", "Won via sleeper hold to win the only title of his WWF career, subbing for the injured Bret Hart -- also competed in the Rumble match this same night."),
    ("The Mountie", 2, "Roddy Piper", "", "Singles", "TRUE", "Intercontinental Championship", "TRUE", "Loss", "", "TRUE", "5:22", "2nd match", "S021", "Lost the IC Title to Piper."),
    ("Beau Beverly", 3, "Bushwhacker Luke, Bushwhacker Butch", "Blake Beverly", "Tag", "FALSE", "", "FALSE", "Win", "", "", "14:56", "3rd match", "S021", "Blake pinned Butch."),
    ("Blake Beverly", 3, "Bushwhacker Luke, Bushwhacker Butch", "Beau Beverly", "Tag", "FALSE", "", "FALSE", "Win", "", "", "14:56", "3rd match", "S021", "Pinned Butch."),
    ("Bushwhacker Luke", 3, "Beau Beverly, Blake Beverly", "Bushwhacker Butch", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "14:56", "3rd match", "S021", ""),
    ("Bushwhacker Butch", 3, "Beau Beverly, Blake Beverly", "Bushwhacker Luke", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "14:56", "3rd match", "S021", "Pinned by Blake."),
    ("Earthquake", 4, "Hawk, Animal", "Typhoon", "Tag", "TRUE", "World Tag Team Championship", "TRUE", "Win", "", "FALSE", "9:24", "4th match", "S021", "Won by count-out, retained the titles. Did NOT compete in the Rumble match this year."),
    ("Typhoon", 4, "Hawk, Animal", "Earthquake", "Tag", "TRUE", "World Tag Team Championship", "TRUE", "Win", "", "FALSE", "9:24", "4th match", "S021", "Won by count-out, retained the titles."),
    ("Hawk", 4, "Earthquake, Typhoon", "Animal", "Tag", "TRUE", "World Tag Team Championship", "FALSE", "Loss", "", "", "9:24", "4th match", "S021", "Lost by count-out. Did NOT compete in the Rumble match this year."),
    ("Animal", 4, "Earthquake, Typhoon", "Hawk", "Tag", "TRUE", "World Tag Team Championship", "FALSE", "Loss", "", "", "9:24", "4th match", "S021", "Lost by count-out."),
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
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1992", "match_name": "30-Man Royal Rumble Match",
    "match_type": "Men's", "event_date": "1992-01-19", "venue": "Knickerbocker Arena",
    "city_region": "Albany, New York", "country": "United States",
    "attendance_official": "", "attendance_reported": 17014,
    "entry_interval_seconds": 120, "entrant_count": 30, "duration_total": "62:02",
    "duration_status": "CONFIRMED",
    "winner_id": "ric-flair", "runner_up_id": "sid-justice",
    "final_two_ids": "ric-flair;sid-justice", "final_three_ids": "ric-flair;sid-justice;hulk-hogan",
    "final_four_ids": "ric-flair;sid-justice;hulk-hogan;randy-savage",
    "first_entrant_id": "british-bulldog", "second_entrant_id": "ted-dibiase", "final_entrant_id": "the-warlord",
    "first_elimination_id": "ted-dibiase", "last_elimination_before_winner_id": "sid-justice",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 0,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": 0, "factions_count": "N/A",
    "commentary_team": "Gorilla Monsoon, Bobby Heenan", "ring_announcer": "Howard Finkel",
    "referees": "John Bonello, Danny Davis, Earl Hebner, Joey Marella per S026 (Wikipedia)",
    "special_rules": (
        "The WWF Championship was vacant and on the line in the Rumble match itself -- the only Royal Rumble "
        "before or since where the winner became champion that same night. Hulk Hogan had been stripped of "
        "the title a week earlier by President Jack Tunney after cheating to regain it from The Undertaker at "
        "'Tuesday Night in Texas', per S021's narrative."
    ),
    "title_on_the_line": "TRUE", "championship_implications": "WWF Championship, vacant, won by Ric Flair",
    "winners_reward": "The vacant WWF Championship itself, not a title shot -- unique among the events in this database so far",
    "historical_significance": "Widely regarded (per S021's own framing) as one of the greatest single-performer Royal Rumble showings ever -- Ric Flair lasted 59:31 of the 62:02 match, an iron-man performance topping Rick Martel's 52:30 record from the prior year. Roddy Piper won the only title of his WWF career (Intercontinental) earlier on the same card. Sid Justice eliminated four wrestlers (Savage, Hogan, Martel, Piper) before being eliminated by Flair for the win.",
    "notes": "30 confirmed entrants, all identified. Eliminator credit is known for 11 of 29 eliminations plus one confirmed self-elimination (Big Boss Man) -- see flags.csv F027-F034 for the full list of what's derived vs. directly stated vs. unknown in this event, including a genuinely interesting +7:40 clock-offset discovery (F029) in the source's own 'Miscellaneous Notes' subsection. Fact-check pass (S026, Wikipedia): confirmed venue and winner; independently confirms the event date as 1992-01-19, resolving an apparent typo in S021 (Dan Wahlers), whose own narrative text says 'January 18' -- the database's date field was already correct, but this explains the discrepancy rather than leaving it silently unaddressed; attendance is reported by Wikipedia as a rounded 17,000 against this database's more precise 17,014 (S020/S021) -- treated as consistent, not conflicting, unlike 1991's genuine attendance conflict (see F035 in 1991's flags); filled in the referee crew.",
    "data_quality_status": "CONFIRMED", "source_ids": "S020;S021;S026",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1992 build complete (schema v2): {len(new_wrestlers) + len(new_people_rows)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows "
      f"(11 of 29 eliminations have a credited eliminator, plus 1 confirmed self-elimination), "
      f"{len(show_appearances)} show appearances, "
      f"{len(other_matches)} other-match rows, {len(sources)} sources logged, {len(flags)} open flags.")
