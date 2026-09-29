# -*- coding: utf-8 -*-
"""
Builds all rows for the 1991 Royal Rumble — schema v2.

IMPORTANT PROVENANCE NOTE: this event's material lives in Shane's Word doc
under the "1990 Royal Rumble Stats" Heading-1 (a misfiling -- see 1990's
flags.csv F015), but its own sub-headings correctly say "1991 Rumble Stats -
Cageside" and "1991 Royal Rumble -- Dan Wahlers History", and the narrative
is unambiguously about a later, different event (Gulf War/Sgt. Slaughter
angle, Undertaker's Rumble debut, Ultimate Warrior losing the WWF Title
earlier on the card). There is NO Excel tab for 1991 at all.

SOURCES CONSULTED THIS PASS:
  S018 "1991 Rumble Stats - Cageside" section (Shane's doc)          tier 9
  S019 Dan Wahlers "History of the Royal Rumble" -- 1991 chapter     tier 9

THIS EVENT IS STRUCTURALLY DIFFERENT FROM 1988-1990 -- READ BEFORE EXTENDING:
  - Entry order (all 30) is CONFIRMED: the first two entrants (Bret Hart #1,
    Dino Bravo #2) are named explicitly by S019 ("Bret Hart and Dino Bravo
    started out #1 and #2"), and S018's "Time Between Buzzers" list gives
    the remaining 28 entrants in exact chronological buzzer order.
  - Ring/survival time for all 30 is CONFIRMED, directly stated by S018's
    Survival Times list (including Randy Savage's unique 0:00 -- see notes).
  - Elimination ORDER (who went out 1st, 2nd, 3rd...) is DERIVED, not
    directly stated. It's computed here as: (buzzer time entrant's music hit)
    + (entrance time lag, from S018's Entrance Times list) + (survival time)
    = elimination timestamp, then all 28 actually-eliminated entrants are ranked by
    that timestamp. This method was spot-verified against 4 independent
    narrative checkpoints in S018's own "Active Iron Man" paragraph (Bret
    Hart -> Valentine at 46:22, Valentine -> Martel at 60:37, Martel ->
    British Bulldog at 61:02 [exactly matching S018's stated "0m 25s" gap],
    Bulldog -> Earthquake for the final 4:15 [ending exactly at the stated
    65:17 match length]) and matched to the exact second every time. High
    confidence, but it's still a DERIVED calculation, not a directly-stated
    fact, and is labeled as such.
  - Eliminator credit (who eliminated whom) is UNKNOWN for 22 of 28
    eliminations -- S018/S019's prose only explicitly names 6: Bret Hart
    (by Undertaker), Greg Valentine (by Hogan), Rick Martel (by British
    Bulldog), Bushwhacker Luke (by Earthquake), Brian Knobbs (by Hogan), and
    Earthquake (by Hogan, the match-winning elimination). The other 22
    entrants' `eliminated_by_ids` are left blank rather than guessed, and NO
    row is written to eliminations.csv for them (writing one would require
    inventing an eliminator_wrestler_id, which the spec explicitly forbids).
    This means `wrestlers_eliminated_count` is only reliably non-zero for
    the 3 wrestlers with a credited elimination (Undertaker: 1, Hogan: 3,
    British Bulldog: 1, Earthquake: 1) -- everyone else's is left blank
    (UNKNOWN), NOT zero, since a true zero would be an unsupported claim.
    See flags.csv F0xx.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    ENTRANTS_FIELDS, ELIMINATIONS_FIELDS, EVENTS_FIELDS, slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR1991M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S018", "'1991 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring crowdedness, Active Iron Man tracking). Misfiled under 1990's Heading-1 in the .docx but is unambiguously about 1991 -- see script docstring. NOT live-fetched this pass."),
    ("S019", "Dan Wahlers, 'History of the Royal Rumble' -- 1991 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance as 16,122, full narrative history (Gulf War/Sgt. Slaughter angle), and undercard match results including the Ultimate Warrior WWF Title loss."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F021", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "Only 6 of this match's 28 real eliminations (Randy Savage's non-entry means only 28 of the 29 non-winner entrants actually had an elimination event) have an eliminator explicitly named in either source: Bret "
     "Hart (by Undertaker), Greg Valentine (by Hogan), Rick Martel (by British Bulldog), Bushwhacker Luke "
     "(by Earthquake), Brian Knobbs (by Hogan), Earthquake (by Hogan, the winning elimination). The other "
     "22 entrants' eliminated_by_ids are blank (UNKNOWN) -- no eliminations.csv row exists for them, since "
     "writing one would require inventing an eliminator. This is a structural gap in the source material, "
     "not a research shortcut -- S018 (unlike its 1988/1989 Kayfabe-Memories-style counterparts) is a pure "
     "timing analysis, not a blow-by-blow recap, so it doesn't narrate most individual eliminations. "
     "wrestlers_eliminated_count is left blank (not 0) for every entrant except the 4 with a confirmed "
     "credit, since a true zero would be an unsupported claim given how incomplete the record is.",
     "S018;S019", "open", "2026-09-15"),
    ("F022", EVENT_ID, "eliminations;entrants", "*", "elim_number", "unverified",
     "Elimination ORDER (not eliminator identity) is a DERIVED calculation: each entrant's buzzer time + "
     "entrance-time lag + survival time = an elimination timestamp, then all 28 actually-eliminated entrants are "
     "ranked by that. Spot-verified against 4 independent checkpoints in S018's own 'Active Iron Man' "
     "narrative and matched to the exact second each time (see script docstring for the specific "
     "checkpoints) -- high confidence, but still DERIVED rather than a directly-stated fact, and could in "
     "principle be off for entrants whose elimination timestamps land very close together (no exact ties "
     "were found this pass, but the underlying survival/entrance-time figures themselves carry their own "
     "small measurement uncertainty per S018's own caveats).",
     "S018", "open", "2026-09-15"),
    ("F023", EVENT_ID, "entrants", "randy-savage", "entry_number;ring_time", "unverified",
     "Randy Savage was drawn for entry #18 but, per both sources, never actually entered the match -- "
     "Gorilla Monsoon determined he was the 'missing' entrant after the field was complete, and Roddy "
     "Piper speculated on commentary that Ultimate Warrior (who Savage had just cost the WWF Title earlier "
     "that night) had him removed from the building. S018 explicitly chose to still count him as a "
     "participant with a survival time of 0m 00s. Kept exactly that way here: entry_number=18, "
     "ring_time=00:00, no elim_number/eliminated_by (he was never in the ring to be eliminated) -- flagged "
     "as a unique case rather than treated like a normal very-early elimination.",
     "S018;S019", "open", "2026-09-15"),
    ("F024", EVENT_ID, "entrants", "shane-douglas", "ring_time_status", "unverified",
     "S018 notes explicitly: 'The exact point when Douglas was eliminated was not caught on camera, so "
     "there are a couple of seconds of uncertainty with his survival time.' Kept his stated 26:31 but "
     "status is PROBABLE rather than CONFIRMED for this one entrant, per the source's own caveat.",
     "S018", "open", "2026-09-15"),
    ("F025", EVENT_ID, "wrestlers", "*", "real_name;dob;billed_height_m_at_event;billed_weight_kg_at_event;birthplace", "unverified",
     "10 wrestlers appear in this database for the first time via 1991 (The Undertaker, British Bulldog, "
     "Shane Douglas, Texas Tornado, Saba Simba, Brian Knobbs, Hawk, Animal, Tugboat, Demolition Crush) with "
     "zero bio data in either source -- names only. Left entirely UNKNOWN, same as 1990's F017. (Paul Roma "
     "already has a full bio from 1988's show_appearances -- reused, not re-added.)",
     "S018;S019", "open", "2026-09-15"),
    ("F026", EVENT_ID, "events;entrances/moves/near_eliminations", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as prior years' F005/F013/F020.",
     "", "open", "2026-09-15"),
    ("F035", EVENT_ID, "events", EVENT_ID, "attendance_reported", "conflicting_sources",
     "Fact-check pass: Wikipedia (S026) gives attendance as 16,000 (a round number), while S019 (Dan Wahlers) "
     "gives the more precise 16,122, which is what's stored in events.csv. Unlike 1992's rounded-vs-precise "
     "figures (17,000 vs 17,014, treated as consistent), this one is being logged as a genuine open conflict "
     "rather than assumed-consistent, since Wikipedia's Royal Rumble (1991) infobox figure is sourced "
     "independently of Dan Wahlers and the two could reflect genuinely different attendance countings (e.g. "
     "paid vs. total). attendance_reported is kept at 16,122 (the more precise, presumably primary-sourced "
     "figure) pending a tiebreaking third source.",
     "S019;S026", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("The Undertaker", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Royal Rumble debut. No bio data in either source this pass.", "S018;S019"),
    ("British Bulldog", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Davey Boy Smith", "", "", "No bio data in either source this pass.", "S018;S019"),
    ("Shane Douglas", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S018"),
    ("Texas Tornado", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Kerry Von Erich", "", "", "S019 refers to this person as 'Kerry Von Erich' directly; no DOB/height/weight in either source this pass.", "S018;S019"),
    ("Saba Simba", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S018"),
    ("Brian Knobbs", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S018;S019"),
    ("Hawk", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Legion of Doom", "", "", "Half of the Legion of Doom (w/ Animal), per S019. No bio data in either source this pass.", "S018;S019"),
    ("Animal", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Legion of Doom", "", "", "Half of the Legion of Doom (w/ Hawk), per S019. No bio data in either source this pass.", "S018;S019"),
    ("Tugboat", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Final (#30) entrant. No bio data in either source this pass.", "S018;S019"),
    ("Demolition Crush", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Demolition", "", "", "Third member of Demolition alongside Ax/Smash -- distinct wrestler_id from 'ax' and 'smash'. No bio data in either source this pass.", "S018;S019"),
]

reused = {
    "Greg Valentine": "greg-valentine", "Rick Martel": "rick-martel", "Bushwhacker Butch": "butch-miller",
    "Jake Roberts": "jake-roberts", "Hercules": "hercules", "Tito Santana": "tito-santana",
    "Jimmy Snuka": "jimmy-snuka", "Demolition Smash": "smash", "Jim Duggan": "jim-duggan",
    "Earthquake": "earthquake", "Mr. Perfect": "mr-perfect", "Hulk Hogan": "hulk-hogan", "Haku": "haku",
    "Jim Neidhart": "jim-neidhart", "Bushwhacker Luke": "luke-williams", "The Warlord": "the-warlord",
    "Bret Hart": "bret-hart", "Dino Bravo": "dino-bravo", "Randy Savage": "randy-savage",
    "Paul Roma": "paul-roma",
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
    m, s = t.split(":")
    return int(m) * 60 + int(s)


buzzer_gaps = [
    ("Greg Valentine", "2:01"), ("Paul Roma", "2:01"), ("Texas Tornado", "2:00"), ("Rick Martel", "2:00"),
    ("Saba Simba", "2:02"), ("Bushwhacker Butch", "2:00"), ("Jake Roberts", "2:00"), ("Hercules", "2:01"),
    ("Tito Santana", "2:00"), ("The Undertaker", "2:00"), ("Jimmy Snuka", "2:01"), ("British Bulldog", "2:00"),
    ("Demolition Smash", "2:01"), ("Hawk", "2:00"), ("Shane Douglas", "2:00"), ("Randy Savage", "2:01"),
    ("Animal", "2:00"), ("Demolition Crush", "2:01"), ("Jim Duggan", "2:00"), ("Earthquake", "2:00"),
    ("Mr. Perfect", "2:00"), ("Hulk Hogan", "2:00"), ("Haku", "2:02"), ("Jim Neidhart", "2:00"),
    ("Bushwhacker Luke", "2:01"), ("Brian Knobbs", "2:01"), ("The Warlord", "2:00"), ("Tugboat", "2:00"),
]
cum = 0
buzzer_time = {}
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("56:13"), f"buzzer checksum failed: {cum}"

entrance_lag = {
    "Mr. Perfect": "0:37", "Bushwhacker Luke": "0:25", "The Undertaker": "0:23", "Earthquake": "0:22",
    "Bushwhacker Butch": "0:17", "Jimmy Snuka": "0:16", "Jim Duggan": "0:11",
    "Hulk Hogan": "0:09", "Haku": "0:09",
    "Greg Valentine": "0:08", "Jake Roberts": "0:08", "Brian Knobbs": "0:08", "Tugboat": "0:08",
    "Saba Simba": "0:07", "Hercules": "0:07", "Tito Santana": "0:07", "Demolition Smash": "0:07",
    "Shane Douglas": "0:07", "Demolition Crush": "0:07", "Jim Neidhart": "0:07", "The Warlord": "0:07",
    "Paul Roma": "0:06", "British Bulldog": "0:06",
    "Texas Tornado": "0:05", "Rick Martel": "0:05", "Hawk": "0:05", "Animal": "0:05",
    "Randy Savage": "0:00",
}

survival = {
    "Rick Martel": "52:30", "Greg Valentine": "44:13", "Hercules": "37:45", "British Bulldog": "36:50",
    "Tito Santana": "30:31", "Shane Douglas": "26:31", "Earthquake": "24:46", "Texas Tornado": "24:21",
    "Hulk Hogan": "20:59", "Bret Hart": "20:39", "Demolition Crush": "18:38", "Demolition Smash": "18:28",
    "Mr. Perfect": "16:17", "The Undertaker": "14:19", "Paul Roma": "14:06", "Haku": "13:25",
    "Jake Roberts": "13:01", "Jim Neidhart": "11:12", "Bushwhacker Butch": "10:09", "Brian Knobbs": "10:08",
    "Jimmy Snuka": "8:09", "Animal": "6:41", "Hawk": "6:40", "Jim Duggan": "4:45", "Dino Bravo": "3:08",
    "Tugboat": "2:33", "Saba Simba": "2:28", "The Warlord": "1:37", "Bushwhacker Luke": "0:04", "Randy Savage": "0:00",
}

entry_actual = {"Bret Hart": 0, "Dino Bravo": 0}
for name in buzzer_time:
    lag = mmss(entrance_lag.get(name, "0:00"))
    entry_actual[name] = buzzer_time[name] + lag

entry_order_list = sorted(entry_actual.items(), key=lambda kv: kv[1])
entry_number = {name: i + 1 for i, (name, ts) in enumerate(entry_order_list)}

elim_ts = {}
for name, surv in survival.items():
    if name == "Hulk Hogan" or name == "Randy Savage":
        continue  # winner has no elimination; Savage never entered, handled separately (F023)
    elim_ts[name] = entry_actual[name] + mmss(surv)

elim_order_list = sorted(elim_ts.items(), key=lambda kv: kv[1])
elim_number = {name: i + 1 for i, (name, ts) in enumerate(elim_order_list)}

KNOWN_ELIMINATORS = {
    "Bret Hart": ["The Undertaker"], "Greg Valentine": ["Hulk Hogan"], "Rick Martel": ["British Bulldog"],
    "Bushwhacker Luke": ["Earthquake"], "Brian Knobbs": ["Hulk Hogan"], "Earthquake": ["Hulk Hogan"],
}

FINAL_THREE_ORDER = ["hulk-hogan", "earthquake", "brian-knobbs"]  # winner, 2nd(final elim), 3rd(2nd-to-last elim)

elim_rows = []
entrant_rows = []

for name in [n for n in entry_actual.keys() if n != "Randy Savage"] + ["Randy Savage"]:
    if name == "Randy Savage":
        entry = 18
        elim_no = ""
        ring_time = "00:00"
        elim_by = []
    else:
        entry = entry_number[name]
        ring_time = survival[name]
        elim_no = 0 if name == "Hulk Hogan" else elim_number[name]
        elim_by = KNOWN_ELIMINATORS.get(name, [])

    wid = wrestler_ids[name]
    is_winner = (name == "Hulk Hogan")
    ring_time_s = mmss_to_seconds(ring_time)

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_no,
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
            "elimination_clock_time": ring_time, "elimination_clock_seconds": ring_time_s,
            "elimination_type": "over_top_rope", "elimination_method": "UNKNOWN",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "UNKNOWN", "is_self_elimination": "FALSE",
            "is_storyline_related": "UNKNOWN", "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE", "simultaneous_group_id": "",
            "data_quality_status": "CONFIRMED", "source_ids": "S018;S019",
            "notes": "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED" if name != "Randy Savage" else "CONFIRMED",
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
        "tag_team_name": ("Legion of Doom (w/ Animal)" if name == "Hawk" else
                           "Legion of Doom (w/ Hawk)" if name == "Animal" else
                           "The Bushwackers (w/ Luke Williams)" if name == "Bushwhacker Butch" else
                           "The Bushwackers (w/ Butch Miller)" if name == "Bushwhacker Luke" else ""),
        "faction_stable": "",
        "current_champion_title": "", "championship_level": "", "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": elim_no if elim_no else "",
        "elim_number_status": "N/A" if name == "Randy Savage" else "DERIVED",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": ring_time if (not is_winner and name != "Randy Savage") else "",
        "elimination_clock_seconds": ring_time_s if (not is_winner and name != "Randy Savage") else "",
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "PROBABLE" if name == "Shane Douglas" else "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE", "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "earthquake" else "FALSE",
        "is_final_two": "TRUE" if wid in ("hulk-hogan", "earthquake") else "FALSE",
        "is_final_three": "TRUE" if wid in FINAL_THREE_ORDER else "FALSE",
        "is_final_four": "",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED" if name != "Randy Savage" else "CONFIRMED",
        "source_ids": "S018;S019",
        "notes": ("Drew #18 but never entered the match -- see flags.csv F023." if name == "Randy Savage" else
                  "Exact elimination moment not caught on camera per S018 -- see flags.csv F024." if name == "Shane Douglas" else ""),
    }
    entrant_rows.append(er)

# Back-fill wrestlers_eliminated_ids/count -- ONLY for the 4 wrestlers with a
# confirmed credit; everyone else stays blank (UNKNOWN), not 0. See F021.
elim_map = {}
for row in elim_rows:
    elim_map.setdefault(row["eliminator_wrestler_id"], []).append(row["eliminated_wrestler_id"])

CREDITED_ELIMINATORS = {"the-undertaker", "hulk-hogan", "british-bulldog", "earthquake"}
for er in entrant_rows:
    wid = er["wrestler_id"]
    if wid in CREDITED_ELIMINATORS:
        er["wrestlers_eliminated_ids"] = ";".join(elim_map.get(wid, []))
        er["wrestlers_eliminated_count"] = len(elim_map.get(wid, []))
        er["solo_eliminations_count"] = len(elim_map.get(wid, []))
        er["assisted_eliminations_count"] = 0
        er["notes"] = (er["notes"] + " " if er["notes"] else "") + \
            "This count reflects only explicitly-credited eliminations (see F021) -- likely an undercount, not a confirmed total."

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# TAG TEAMS
# ---------------------------------------------------------------------------
tag_teams = [
    ("Legion of Doom", ["Hawk", "Animal"], "TRUE"),
    ("The Bushwackers", ["Bushwhacker Butch", "Bushwhacker Luke"], "TRUE"),
]
with open(os.path.join(DATA_DIR, "tag_teams.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for team_name, members, official in tag_teams:
        writer.writerow([EVENT_ID, team_name, ";".join(wrestler_ids[m] for m in members), "", "",
                          official, "TRUE", "TRUE", "", "FALSE", "TRUE", "FALSE", "",
                          "PROBABLE", "S018;S019"])

# ---------------------------------------------------------------------------
# SHOW APPEARANCES / other card personnel not in the Rumble match
# ---------------------------------------------------------------------------
show_wrestlers = {
    "Shawn Michaels": "shawn-michaels", "Marty Jannetty": "marty-jannetty",
    "The Great Tanaka": None, "Kato": None, "Big Bossman": "big-bossman", "The Barbarian": "the-barbarian",
    "The Mountie": "jacques-rougeau", "Koko B. Ware": "koko-b-ware", "Ted DiBiase": "ted-dibiase", "Virgil": "virgil",
    "Dusty Rhodes": "dusty-rhodes", "Dustin Rhodes": None, "Sgt. Slaughter": None,
    "Ultimate Warrior": "the-ultimate-warrior",
}
for name, wid in show_wrestlers.items():
    wrestler_ids[name] = wid if wid else slugify(name)

new_people_rows = [
    ("The Great Tanaka", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Orient Express", "", "", "Half of The Orient Express (w/ Kato). No bio data in either source this pass.", "S019"),
    ("Kato", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Orient Express", "", "", "Half of The Orient Express (w/ The Great Tanaka). No bio data in either source this pass.", "S019"),
    ("Dustin Rhodes", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Per S019, teamed with his father Dusty Rhodes for the first time this event. No bio data in either source this pass.", "S019"),
    ("Sgt. Slaughter", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Won the WWF Championship from Ultimate Warrior on this card, managed by an unnamed 'Saddam Hussein look-alike' per S019 (name not given). No bio data in either source this pass.", "S019"),
]
with open(os.path.join(DATA_DIR, "wrestlers.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in new_people_rows:
        writer.writerow([slugify(row[0])] + list(row))

show_appearances = [
    ("Shawn Michaels", "Wrestler (undercard)", "", "Face", "", "Opener; The Rockers def. Orient Express, Jannetty pinned Tanaka"),
    ("Marty Jannetty", "Wrestler (undercard)", "", "Face", "", "Opener; pinned Tanaka for the win"),
    ("The Great Tanaka", "Wrestler (undercard)", "", "Heel", "", "Opener; pinned by Jannetty"),
    ("Kato", "Wrestler (undercard)", "", "Heel", "", "Opener"),
    ("Big Bossman", "Wrestler (undercard)", "", "Face", "", "Pinned The Barbarian (14:15)"),
    ("The Barbarian", "Wrestler (undercard)", "", "Heel", "", "Lost to Big Bossman (14:15)"),
    ("The Mountie", "Wrestler (undercard)", "", "Heel", "", "Pinned Koko B. Ware (9:12). 'The Mountie' is Jacques Rougeau (of 1988/1989's Fabulous Rougeaus), performing solo under a new gimmick from 1991 -- confirmed via the fact-check pass (F0xx), reusing wrestler_id jacques-rougeau rather than creating a duplicate."),
    ("Koko B. Ware", "Wrestler (undercard)", "", "Face", "", "Lost to The Mountie (9:12)"),
    ("Ted DiBiase", "Wrestler (undercard)", "", "Heel", "", "w/ Virgil defeated Dusty & Dustin Rhodes (9:57), pinned Dusty. Per S019, Virgil turned on DiBiase after this match."),
    ("Virgil", "Wrestler (undercard)", "Ted DiBiase", "Heel", "", "Turned on Ted DiBiase after this match per S019 -- his signature babyface turn."),
    ("Dusty Rhodes", "Wrestler (undercard)", "", "Face", "", "w/ son Dustin Rhodes, lost to DiBiase & Virgil (9:57); pinned by DiBiase"),
    ("Dustin Rhodes", "Wrestler (undercard)", "", "Face", "", "First time teaming with father Dusty Rhodes per S019"),
    ("Sgt. Slaughter", "Wrestler (undercard)", "", "Heel", "WWF Championship", "Pinned Ultimate Warrior (12:47) to win the WWF Title -- first time the world title was defended at a Royal Rumble event, per S019"),
    ("Ultimate Warrior", "Wrestler (undercard)", "", "Face", "WWF Championship", "Lost the WWF Title to Sgt. Slaughter (12:47); did not compete in the Rumble match itself"),
]
with open(os.path.join(DATA_DIR, "show_appearances.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for name, role, managed, align, title, notes in show_appearances:
        pid = wrestler_ids.get(name, slugify(name))
        writer.writerow([EVENT_ID, pid, name, role, managed, align, title, notes, "PROBABLE", "S019"])

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD
# ---------------------------------------------------------------------------
other_matches = [
    ("Shawn Michaels", 1, "The Great Tanaka, Kato", "Marty Jannetty", "Tag", "FALSE", "", "FALSE", "Win", "", "", "19:15", "Opener", "S019", ""),
    ("Marty Jannetty", 1, "The Great Tanaka, Kato", "Shawn Michaels", "Tag", "FALSE", "", "FALSE", "Win", "", "", "19:15", "Opener", "S019", "Pinned Tanaka."),
    ("The Great Tanaka", 1, "Shawn Michaels, Marty Jannetty", "Kato", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "19:15", "Opener", "S019", "Pinned by Jannetty."),
    ("Kato", 1, "Shawn Michaels, Marty Jannetty", "The Great Tanaka", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "19:15", "Opener", "S019", ""),
    ("Big Bossman", 2, "The Barbarian", "", "Singles", "FALSE", "", "FALSE", "Win", "", "", "14:15", "2nd match", "S019", ""),
    ("The Barbarian", 2, "Big Bossman", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "14:15", "2nd match", "S019", ""),
    ("The Mountie", 3, "Koko B. Ware", "", "Singles", "FALSE", "", "FALSE", "Win", "", "", "9:12", "3rd match", "S019", ""),
    ("Koko B. Ware", 3, "The Mountie", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "9:12", "3rd match", "S019", ""),
    ("Ted DiBiase", 4, "Dusty Rhodes, Dustin Rhodes", "Virgil", "Tag", "FALSE", "", "FALSE", "Win", "", "", "9:57", "4th match", "S019", "Pinned Dusty Rhodes. Virgil turned on DiBiase after the match."),
    ("Virgil", 4, "Dusty Rhodes, Dustin Rhodes", "Ted DiBiase", "Tag", "FALSE", "", "FALSE", "Win", "", "", "9:57", "4th match", "S019", "Turned on DiBiase after the match -- babyface turn."),
    ("Dusty Rhodes", 4, "Ted DiBiase, Virgil", "Dustin Rhodes", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "9:57", "4th match", "S019", "Pinned by DiBiase. First time teaming with son Dustin."),
    ("Dustin Rhodes", 4, "Ted DiBiase, Virgil", "Dusty Rhodes", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "9:57", "4th match", "S019", "First time teaming with father Dusty."),
    ("Sgt. Slaughter", 5, "Ultimate Warrior", "", "Singles", "TRUE", "WWF Championship", "FALSE", "Win", "TRUE", "FALSE", "12:47", "5th match", "S019", "Won via outside interference from Randy Savage per S019's narrative -- first WWF Title defended at a Royal Rumble event."),
    ("Ultimate Warrior", 5, "Sgt. Slaughter", "", "Singles", "TRUE", "WWF Championship", "TRUE", "Loss", "", "TRUE", "12:47", "5th match", "S019", "Lost the WWF Title; did not compete in the Rumble match itself."),
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
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1991", "match_name": "30-Man Royal Rumble Match",
    "match_type": "Men's", "event_date": "1991-01-19", "venue": "Miami Arena",
    "city_region": "Miami, Florida", "country": "United States",
    "attendance_official": "", "attendance_reported": 16122,
    "entry_interval_seconds": 120, "entrant_count": 30, "duration_total": "65:17",
    "duration_status": "CONFIRMED",
    "winner_id": "hulk-hogan", "runner_up_id": "earthquake",
    "final_two_ids": "hulk-hogan;earthquake", "final_three_ids": "hulk-hogan;earthquake;brian-knobbs",
    "final_four_ids": "",
    "first_entrant_id": "bret-hart", "second_entrant_id": "dino-bravo", "final_entrant_id": "tugboat",
    "first_elimination_id": "dino-bravo", "last_elimination_before_winner_id": "earthquake",
    "eliminations_count": 28, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 0,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": 2, "factions_count": "N/A",
    "commentary_team": "Gorilla Monsoon, Roddy Piper", "ring_announcer": "Howard Finkel",
    "referees": "Shane Stevens, Fred Sparta, Mike Chioda, Earl Hebner, Joey Marella per S026 (Wikipedia)",
    "special_rules": (
        "Randy Savage was drawn for entry #18 but never actually entered the match -- see flags.csv F023, "
        "this is a unique case in the database so far. Hogan's second consecutive Royal Rumble win "
        "(1990-1991). Sgt. Slaughter's Gulf War-era 'Iraqi sympathizer' storyline (with an unnamed manager "
        "styled as a Saddam Hussein look-alike per S019) generated the win over Ultimate Warrior earlier on "
        "the card -- the first time the WWF Title was defended at a Royal Rumble event. This was originally "
        "intended to build to a 100,000-fan WrestleMania VII at the LA Coliseum, but poor advance ticket "
        "sales forced a move to the much smaller LA Sports Arena, which the promotion publicly attributed "
        "to security concerns instead per S019."
    ),
    "title_on_the_line": "FALSE", "championship_implications": "None in the Rumble match itself, though the WWF Title changed hands on the same card (Slaughter over Warrior)",
    "winners_reward": "None identified this pass in either source",
    "historical_significance": "The Undertaker's first-ever Royal Rumble appearance. Rick Martel's 52:30 survival time set a new Royal Rumble record (surpassing Bret Hart's 25:42 from 1988 and Mr. Perfect's 27:58 from 1989) -- broken the following year per S018's own framing ('a record that would last only until the next year').",
    "notes": "30 confirmed entrants (including Randy Savage's unique no-show case), all identified. Eliminator credit is known for only 6 of 28 eliminations -- see flags.csv F021-F026 for the full list of what's derived vs. directly stated vs. unknown in this event. Fact-check pass (S026, Wikipedia) independently confirmed date, venue, and duration (65:17 matches exactly); filled in the referee crew; found a genuine new attendance conflict (16,000 vs 16,122 -- see F035, open).",
    "data_quality_status": "CONFIRMED", "source_ids": "S018;S019;S026",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1991 build complete (schema v2): {len(new_wrestlers) + len(new_people_rows)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows "
      f"(only {len(KNOWN_ELIMINATORS)} of 28 eliminations have a credited eliminator), "
      f"{len(tag_teams)} tag teams, {len(show_appearances)} show appearances, "
      f"{len(other_matches)} other-match rows, {len(sources)} sources logged, {len(flags)} open flags.")
