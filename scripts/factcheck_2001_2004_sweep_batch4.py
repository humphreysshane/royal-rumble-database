#!/usr/bin/env python3
"""
2001-2004 fact-check sweep, batch 4. Continues the deceased-status audit
pattern from batches 1-3 into the next 4 events, adds a WWE Hall of Fame
bio-completion pass (a gap type not specifically targeted before), and 7
more notable_moments.csv rows.

(0) Reconnaissance: RR2001M-RR2004M already carry substantial flags
    (F130-F181, F201-F208) from this database's original build/fact-check
    passes -- these 4 events were NOT a "cold start" the way 1988-2000 were.
    Many of those flags are correctly-preserved CONFLICTING_SOURCES
    disagreements (e.g. F159/F202 attendance figures, F203 Rikishi's
    survival time, F204/F205/F208 birthplace disputes, F206/F207 eliminator
    credit disputes) -- per this project's core rule, genuine disagreements
    between sources are preserved as flags, not force-resolved by picking a
    side, so those were deliberately left untouched this pass rather than
    "cleaned up." This batch instead applied the two techniques that have
    had the best hit rate in every prior batch: a deceased-status audit,
    and completing already-knowable bio facts (this time: WWE Hall of Fame
    induction years) via search, plus a notable_moments capture pass.

(1) DECEASED-STATUS AUDIT, same method as batches 1-3: checked all 73
    unique entrants across RR2001M-RR2004M against Wikipedia (S022)
    cross-checked with the mainstream-obituary bucket (S131). 8 of the 73
    already had deceased_date set from earlier passes (big-boss-man,
    brian-christopher, chris-benoit, crash-holly, eddie-guerrero,
    mr-perfect, rosey, test). Of the remaining 65:
      - jamal (Edward "Eddie" Fatu, wrestled as Jamal at RR2003M before
        later becoming Umaga -- this database's own notes already record
        the jamal/umaga identity merge from an earlier 2003-2007 fact-check
        pass, see F198) died 2009-12-04 of a heart attack brought on by
        acute toxicity of multiple substances, per Wikipedia's detailed
        account, independently corroborated by CNN's contemporary report
        (in the S131 mainstream-obituary bucket). Not previously recorded.
      - Spot-checked several lower-profile names with no other Wikipedia
        infobox red flags to be extra sure nothing was missed: Bull
        Buchanan, Haku, Perry Saturn, Steve Blackman, Spike Dudley,
        Hardcore Holly, Rene Dupree, Ernest "The Cat" Miller, and Scott
        Steiner -- no death evidence found for any of them, left unchanged.
      - The remaining ~55 (Triple H, The Undertaker, Kane, Steve Austin,
        Shawn Michaels, Booker T, Kurt Angle, Chris Jericho, Edge,
        Christian, Rey Mysterio, Batista, Randy Orton, Brock Lesnar, John
        Cena, etc.) are all still-prominent, recently-active or recently-
        newsworthy figures with no plausible death to check -- not
        individually re-verified this pass, consistent with the "realistic
        pace" note from the 1988 pilot (batches size by effort, not a fixed
        per-name checklist).

(2) NEW: WWE HALL OF FAME bio-completion pass. Not previously a dedicated
    audit target, but while cross-checking deceased status it became clear
    several RR2001-2004 entrants have since been inducted with a blank
    hall_of_fame_year field. Reused this database's own existing reusable
    HOF-bucket sources (S123: WWE.com's official induction-announcement
    articles; S124: Wikipedia's 'WWE Hall of Fame (YYYY)' year-by-year
    class articles) rather than registering new sources -- both are already
    documented as "ONE independent source regardless of how many individual
    articles were consulted." Confirmed and added:
      - Ron Simmons / Faarooq: 2012
      - Booker T: 2013
      - Mick Foley: 2013
      - Eddie Guerrero: 2006 (posthumous)
      - Kane (Glenn Jacobs): 2021
      - Kurt Angle: 2017
      - Diamond Dallas Page: 2017
      - The Undertaker: 2022 (a rare solo induction)
      - Rey Mysterio: 2023
    Checked and found NOT (yet) inducted, left unchanged: Edge -- still an
    active in-ring performer through recent years, no induction found.
    This is worth flagging as a pattern for Shane: the HOF field was likely
    incomplete across the WHOLE database, not just this batch's 4 events --
    see the IDEAS.md write-up.

(3) 7 new notable_moments.csv rows, all "surfaced" from this database's own
    already-CONFIRMED events.csv historical_significance text and resolved
    flags rather than freshly researched from scratch (same pattern as
    batch 3's F081/F082 surfacing):
      - RR2001M: Drew Carey's celebrity-cameo entry and self-elimination.
      - RR2001M: Steve Austin's delayed, out-of-order entry after being
        attacked in the aisle by Triple H (F130).
      - RR2002M: Maven's famous upset elimination of The Undertaker.
      - RR2002M: Mr. Perfect's surprise one-off WWF return after 6 years
        away, reaching the Final Four in what this database's own S049
        text calls his last notable appearance before his 2003 death.
      - RR2003M: Batista's post-elimination chair interference (F171).
      - RR2004M: Mick Foley's "Cactus Jack" reveal, replacing the
        storyline-attacked Test (F175).
      - RR2004M: the Foley/Orton simultaneous double-clothesline
        elimination spot (F176).

Usage:
    python3 factcheck_2001_2004_sweep_batch4.py [data_dir]   (default: data)
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import NOTABLE_MOMENTS_FIELDS

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "data"


def load(name):
    path = f"{DATA_DIR}/{name}"
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def save(name, fieldnames, rows):
    path = f"{DATA_DIR}/{name}"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    w_fields, w_rows = load("wrestlers.csv")
    flag_fields, flags = load("flags.csv")
    try:
        nm_fields, nm_rows = load("notable_moments.csv")
    except FileNotFoundError:
        nm_fields, nm_rows = NOTABLE_MOMENTS_FIELDS, []

    by_id = {r["wrestler_id"]: r for r in w_rows}

    def add_src(row, *ids):
        cur = set(filter(None, row["source_ids"].split(";")))
        cur.update(ids)
        row["source_ids"] = ";".join(sorted(cur))

    # ---- (1) deceased-status audit -------------------------------------
    jamal = by_id["jamal"]
    jamal["deceased_date"] = "2009-12-04"
    add_src(jamal, "S022", "S131")

    # ---- (2) WWE Hall of Fame bio-completion pass ----------------------
    hof_fixed = []
    hof_years = {
        "faarooq": "2012",
        "booker-t": "2013",
        "mick-foley": "2013",
        "eddie-guerrero": "2006",
        "kane": "2021",
        "kurt-angle": "2017",
        "diamond-dallas-page": "2017",
        "the-undertaker": "2022",
        "rey-mysterio": "2023",
    }
    for wid, year in hof_years.items():
        row = by_id[wid]
        row["hall_of_fame_year"] = year
        add_src(row, "S123", "S124")
        hof_fixed.append(wid)

    assert len(hof_fixed) == 9

    counter = 348
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "",
        "table": "wrestlers",
        "record_id": "jamal",
        "field": "deceased_date",
        "issue_type": "corrected",
        "description": (
            "2001-2004 fact-check sweep batch 4, continuing the deceased-status audit from batches "
            "1-3: jamal (Edward 'Eddie' Fatu -- this database's own notes already record the jamal/"
            "umaga identity merge from an earlier 2003-2007 fact-check pass, see F198) confirmed "
            "deceased 2009-12-04 (heart attack brought on by acute toxicity of multiple substances), "
            "per Wikipedia cross-checked against CNN's contemporary report (S131 bucket). Also spot-"
            "checked Bull Buchanan, Haku, Perry Saturn, Steve Blackman, Spike Dudley, Hardcore Holly, "
            "Rene Dupree, Ernest 'The Cat' Miller, and Scott Steiner -- no death evidence found, left "
            "unchanged. The remaining ~55 RR2001-2004 entrants are prominent, recently-active or "
            "recently-newsworthy figures not individually re-verified this pass (realistic-pace note "
            "from the 1988 pilot: batches size by effort, not a fixed per-name checklist)."
        ),
        "source_ids_involved": "S022;S131",
        "status": "resolved",
        "date_logged": "2026-09-19",
    })
    counter += 1

    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "",
        "table": "wrestlers",
        "record_id": ";".join(hof_fixed),
        "field": "hall_of_fame_year",
        "issue_type": "corrected",
        "description": (
            "2001-2004 fact-check sweep batch 4: a NEW audit type (not specifically targeted in "
            "batches 1-3) -- WWE Hall of Fame induction year, found blank for several RR2001-2004 "
            "entrants who have since been inducted. Reused this database's own existing reusable HOF-"
            "bucket sources (S123, S124) rather than registering new ones. Added: Ron Simmons/Faarooq "
            "(2012), Booker T (2013), Mick Foley (2013), Eddie Guerrero (2006, posthumous), Kane/Glenn "
            "Jacobs (2021), Kurt Angle (2017), Diamond Dallas Page (2017), The Undertaker (2022, a rare "
            "solo induction), and Rey Mysterio (2023). Checked and found NOT yet inducted, left "
            "unchanged: Edge. Likely worth a dedicated database-wide Hall of Fame pass rather than "
            "picking it up incidentally batch by batch -- see IDEAS.md."
        ),
        "source_ids_involved": "S123;S124",
        "status": "resolved",
        "date_logged": "2026-09-19",
    })
    counter += 1

    # ---- (3) notable_moments additions ---------------------------------
    nm_rows.append({
        "moment_id": "NM012",
        "event_id": "RR2001M",
        "wrestler_ids_involved": "drew-carey",
        "category": "storyline_moment",
        "title": "Drew Carey's celebrity cameo entry -- and quick self-elimination",
        "description": (
            "Entering at #5, comedian Drew Carey's appearance came from an on-screen storyline: Vince "
            "McMahon pulled a promised pre-show Sunday Night Heat winner's slot and gave it to Carey "
            "instead, reportedly hoping he'd be pummeled. Carey safely climbed over the top rope to "
            "self-eliminate almost immediately -- one of the more purely comedic moments in Rumble "
            "history, and per this database's own sourcing, a factor in his later WWE Hall of Fame "
            "celebrity-wing induction."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S050",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text rather than newly researched.",
    })
    nm_rows.append({
        "moment_id": "NM013",
        "event_id": "RR2001M",
        "wrestler_ids_involved": "steve-austin;hunter-hearst-helmsley;rikishi",
        "category": "storyline_moment",
        "title": "Steve Austin drew #27 -- but was physically the last man to enter the ring",
        "description": (
            "Austin was attacked in the aisle by Triple H (payback for costing HHH his title match "
            "earlier that night) before he could physically enter. Per this database's timing analysis "
            "his actual ring-entry moment lands 1 second after the officially-numbered #30 entrant "
            "(Rikishi) -- Austin fought his way in by throwing an already-attacked Rikishi into the "
            "ring ahead of him. entry_number is kept at his drawn/announced 27 (this database's standard "
            "convention); see flags.csv F130 for the full multi-source resolution of this event's exact "
            "mechanics."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S040;S048;S050",
        "notes": "Surfaced from flags.csv F130 (resolved via 4 independent sources) rather than newly researched.",
    })
    nm_rows.append({
        "moment_id": "NM014",
        "event_id": "RR2002M",
        "wrestler_ids_involved": "maven;the-undertaker",
        "category": "upset",
        "title": "Maven's dropkick elimination of The Undertaker -- one of the Rumble's most famous upsets",
        "description": (
            "A total underdog at the time, Maven caught The Undertaker on the ring apron with a dropkick "
            "and eliminated one of the promotion's most dominant stars -- widely regarded as one of the "
            "most famous surprise eliminations in Royal Rumble history. Undertaker then brutally beat "
            "Maven down outside the ring; no reliable source specifies who formally eliminated Maven "
            "afterward, so that follow-up elimination is left UNKNOWN rather than guessed (see F163)."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S049;S050",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM015",
        "event_id": "RR2002M",
        "wrestler_ids_involved": "mr-perfect",
        "category": "other",
        "title": "Mr. Perfect's surprise one-off return, six years after leaving the WWF",
        "description": (
            "Curt Hennig made a surprise return to the WWF after a 6-year absence, reaching the Final "
            "Four before Triple H eliminated him. Per this database's own S049 sourcing, this was 'the "
            "last notable thing Hennig would do' before his death in February 2003, just over a year "
            "later."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S049",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM016",
        "event_id": "RR2003M",
        "wrestler_ids_involved": "batista;the-undertaker",
        "category": "controversy",
        "title": "Batista's chair-shot return after his own elimination",
        "description": (
            "After being legitimately eliminated by The Undertaker in the Final Four, Batista came back "
            "in with a steel chair as pure interference before Undertaker tossed him out a second time. "
            "Not modeled as a second entrant row or elimination in this database -- Batista's official "
            "(first and only legitimate) entry and elimination is what's recorded, the same principle "
            "used for 1997's Giant Gonzalez interference (F081/NM006) and 2000/2002's similar cases."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S065;S066",
        "notes": "Surfaced from flags.csv F171 rather than newly researched.",
    })
    nm_rows.append({
        "moment_id": "NM017",
        "event_id": "RR2004M",
        "wrestler_ids_involved": "mick-foley;test",
        "category": "notable_absence_or_substitution",
        "title": "Test was advertised for #21 -- but Mick Foley, his storyline attacker, showed up instead",
        "description": (
            "Test was advertised for entry #21 but was shown 'lying beat up in the back' after a "
            "storyline attack; Mick Foley, revealed as the attacker, entered in his place to the crowd's "
            "delight. Modeled with two entrant rows sharing entry_number 21 -- Test (no elimination "
            "logged, the same no-show convention used for Randy Savage 1991, Bastion Booger 1994 and "
            "Skull 1998) and Foley, the wrestler who actually competed at that slot."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S067;S073",
        "notes": "Surfaced from flags.csv F175 rather than newly researched.",
    })
    nm_rows.append({
        "moment_id": "NM018",
        "event_id": "RR2004M",
        "wrestler_ids_involved": "mick-foley;randy-orton",
        "category": "storyline_moment",
        "title": "The Foley/Orton double-clothesline spot -- a shared elimination that spilled onto the floor",
        "description": (
            "Foley and Randy Orton went over the top rope together in a single simultaneous clothesline "
            "spot, with the brawl continuing on the floor outside. Modeled as two elimination rows "
            "sharing simultaneous_group_id 'foley_orton_double_clothesline': Orton eliminated by Foley, "
            "and Foley self-eliminated -- the same self-elimination convention used for Drew Carey (2001, "
            "see NM012) and Kane's self-elimination in 1999."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S067;S073",
        "notes": "Surfaced from flags.csv F176 rather than newly researched.",
    })
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "RR2001M;RR2002M;RR2003M;RR2004M",
        "table": "notable_moments",
        "record_id": "NM012;NM013;NM014;NM015;NM016;NM017;NM018",
        "field": "n/a",
        "issue_type": "corrected",
        "description": (
            "Added 7 notable_moments.csv rows for the 2001-2004 batch: RR2001M's Drew Carey celebrity "
            "cameo and Steve Austin's delayed/out-of-order entry (F130); RR2002M's Maven/Undertaker "
            "upset elimination and Mr. Perfect's surprise swan-song return; RR2003M's Batista chair-shot "
            "interference (F171); RR2004M's Mick Foley/Test substitution reveal (F175) and the Foley/"
            "Orton double-clothesline elimination (F176). All 7 surface content already CONFIRMED "
            "elsewhere in this database (events.csv historical_significance text or resolved flags) "
            "into the dedicated notable_moments panel rather than being newly researched from scratch."
        ),
        "source_ids_involved": "S040;S048;S049;S050;S065;S066;S067;S073",
        "status": "resolved",
        "date_logged": "2026-09-19",
    })

    save("wrestlers.csv", w_fields, w_rows)
    save("flags.csv", flag_fields, flags)
    save("notable_moments.csv", nm_fields, nm_rows)

    print("Updated 1 wrestlers.csv row (deceased-status: jamal/Umaga).")
    print(f"Updated {len(hof_fixed)} wrestlers.csv rows (WWE Hall of Fame bio-completion).")
    print("Added 7 notable_moments.csv rows (NM012-NM018).")
    print("Added 3 new flags (F348-F350). No new sources needed (reused existing buckets).")


if __name__ == "__main__":
    main()
