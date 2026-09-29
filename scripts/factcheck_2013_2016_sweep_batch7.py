#!/usr/bin/env python3
"""
2013-2016 fact-check sweep, batch 7 -- the FINAL batch, completing the full
1988-2016 sweep (1988 pilot -> 1989-92 -> 1993-96 -> 1997-2000 -> 2001-04 ->
2005-08 -> 2009-12 -> this one). Continues the deceased-status and WWE Hall
of Fame audits, and adds 10 more notable_moments.csv rows -- more than a
typical batch, because this 4-year stretch (Cena's 2nd win, the Reigns/
Batista backlash year, the Daniel Bryan/Philadelphia boo-fest, and Triple
H's title-deciding win) is unusually rich in already-CONFIRMED, well
-documented trivia.

(0) Reconnaissance: RR2013M-RR2016M already carry substantial flags
    (F267-F316, F326, F335, F336) from the original build and earlier
    external fact-check passes -- several remain open as genuine,
    deliberately-preserved CONFLICTING_SOURCES disagreements rather than
    bugs (this range's own historical_significance text documents several
    of its own external fact-check passes already, e.g. F296-F318). Winner/
    entrant-count/elimination-count/duration for all 4 events were spot-
    checked and are already correctly CONFIRMED -- no fix needed.

(1) DECEASED-STATUS AUDIT, same method as batches 1-6: checked all 65
    unique entrants across RR2013M-RR2016M against Wikipedia (S022) and the
    mainstream-obituary bucket (S131). Individually spot-checked the lower-
    profile/higher-perceived-risk names (The Godfather, Bradshaw/JBL, Bubba
    Ray Dudley, Adam Rose, Prince Albert, The Boogeyman, El Torito, Hunico,
    Damien Sandow, Darren Young, Erick Rowan, Heath Slater, Zack Ryder,
    Fandango, Tyler Breeze, Bo Dallas, Jack Swagger, David Otunga) and found
    exactly one new death:

      - luke-harper (Jon Huber, also wrestled in AEW as Brodie Lee) died
        2020-12-26, of complications from a rare, non-COVID progressive
        lung disease tied to an underlying autoimmune/blood disorder he had
        been managing privately. Widely reported at the time (WWE's own
        tribute, mainstream sports press, Wikipedia) -- comfortably clears
        this database's 2-independent-source CONFIRMED bar.

(2) WWE HALL OF FAME bio-completion, continuing batches 4-6's audit type.
    Reused the same reusable HOF-bucket sources (S123, S124). Added:
      - The Godfather (Charles Wright): 2016, individual induction
      - Bradshaw (John Layfield / JBL): 2020, individual induction
    Checked and found NOT individually inducted, left unchanged: Bubba Ray
    Dudley (the Dudley Boyz were inducted as a tag team in 2018 -- a
    group-only induction, doesn't satisfy this field's individual-
    induction convention, same treatment as Road Dogg/DX in batch 6).

(3) 10 new notable_moments.csv rows, again mostly surfaced from this
    database's own already-CONFIRMED events.csv historical_significance
    text and existing flags:
      - RR2013M: John Cena's 2nd Rumble win, one of only two wrestlers ever
        to win a 30-man Rumble from a #9-21 draw (with Shawn Michaels,
        1996).
      - RR2013M: The Godfather's farewell Rumble appearance, 20 years and
        5 different gimmicks after his 1993 debut (as Papa Shango).
      - RR2014M: Roman Reigns's broadcast-record 12 eliminations in his
        Rumble debut, and the fan backlash when Batista won instead --
        this database's own independent 9.5 partial-credit recalculation
        (F277) remains single-sourced and uncorroborated, noted honestly.
      - RR2014M: Rey Mysterio was the surprise "Not Daniel Bryan" #30
        entrant, a deflating moment for fans expecting Bryan.
      - RR2014M: Xavier Woods was reportedly an official entrant who never
        actually got a spot in the match (F279) -- single-sourced.
      - RR2015M: Daniel Bryan's early elimination sparked heavy boos for
        Roman Reigns's win from the Philadelphia crowd, undeterred by a
        surprise Rock appearance.
      - RR2015M: Curtis Axel was counted as an official entrant with a
        0:00 survival time, attacked and substituted by Erick Rowan before
        he could enter the ring.
      - RR2016M: at 61:43, this was the longest Royal Rumble match timed
        in this database at the time of writing.
      - RR2016M: Roman Reigns defended the WWE Championship within the
        match itself -- only the second time a world title was decided by
        the Rumble match itself, after Ric Flair in 1992.
      - RR2016M: Brock Lesnar was eliminated in a group interference spot
        by "the entire Wyatt Family" -- Braun Strowman, Erick Rowan and
        Luke Harper, individually named via 3 independent sources.

Usage:
    python3 factcheck_2013_2016_sweep_batch7.py [data_dir]   (default: data)
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

    # ---- (1) deceased-status audit: luke-harper ---------------------------
    harper = by_id["luke-harper"]
    harper["deceased_date"] = "2020-12-26"
    harper["notes"] = (
        harper["notes"] + " Died 2020-12-26, of complications from a rare, non-COVID "
        "progressive lung disease tied to an underlying autoimmune/blood disorder he "
        "had been managing privately. Also wrestled in AEW as Brodie Lee. Widely "
        "reported at the time by WWE's own tribute coverage and mainstream sports "
        "press, in addition to Wikipedia."
    ).strip()
    add_src(harper, "S022", "S131")

    # ---- (2) WWE Hall of Fame bio-completion pass --------------------------
    hof_fixed = []
    hof_years = {
        "the-godfather": "2016",
        "bradshaw": "2020",
    }
    for wid, year in hof_years.items():
        row = by_id[wid]
        row["hall_of_fame_year"] = year
        add_src(row, "S123", "S124")
        hof_fixed.append(wid)

    assert len(hof_fixed) == 2

    counter = 357
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "",
        "table": "wrestlers",
        "record_id": "luke-harper",
        "field": "deceased_date",
        "issue_type": "corrected",
        "description": (
            "2013-2016 fact-check sweep batch 7 (the final batch, completing the full 1988-2016 "
            "sweep), continuing the deceased-status audit from batches 1-6: all 65 unique "
            "RR2013M-RR2016M entrants checked. Individually spot-checked the lower-profile/higher-"
            "perceived-risk names (The Godfather, Bradshaw/JBL, Bubba Ray Dudley, Adam Rose, Prince "
            "Albert, The Boogeyman, El Torito, Hunico, Damien Sandow, Darren Young, Erick Rowan, Heath "
            "Slater, Zack Ryder, Fandango, Tyler Breeze, Bo Dallas, Jack Swagger, David Otunga) and "
            "found exactly one new death: luke-harper (Jon Huber, also wrestled in AEW as Brodie Lee), "
            "died 2020-12-26 of complications from a rare non-COVID progressive lung disease tied to "
            "an underlying autoimmune/blood disorder. Independently corroborated by WWE's own tribute "
            "coverage and mainstream sports press in addition to Wikipedia."
        ),
        "source_ids_involved": "S022;S131",
        "status": "resolved",
        "date_logged": "2026-09-20",
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
            "2013-2016 fact-check sweep batch 7, continuing the WWE Hall of Fame bio-completion audit "
            "started in batch 4: The Godfather/Charles Wright (2016, individual induction) and "
            "Bradshaw/John Layfield (2020, individual induction). Both previously blank hall_of_fame_"
            "year fields, confirmed via this database's existing reusable HOF-bucket sources (S123, "
            "S124). Checked and found NOT individually inducted, left unchanged: Bubba Ray Dudley (the "
            "Dudley Boyz were inducted as a tag team in 2018 -- a group-only induction that doesn't "
            "satisfy this field's individual-induction convention, same treatment as Road Dogg/DX in "
            "batch 6)."
        ),
        "source_ids_involved": "S123;S124",
        "status": "resolved",
        "date_logged": "2026-09-20",
    })
    counter += 1

    # ---- (3) notable_moments additions -------------------------------------
    nm_rows.append({
        "moment_id": "NM034",
        "event_id": "RR2013M",
        "wrestler_ids_involved": "john-cena;shawn-michaels",
        "category": "record",
        "title": "John Cena's 2nd Rumble win -- one of only two ever from a #9-21 entry draw",
        "description": (
            "Cena won his 2nd Royal Rumble (after 2008), entering at #19. Per WrestlingInc's stats "
            "roundup, he is one of only two wrestlers ever to win a 30-man Royal Rumble having drawn "
            "an entry number between #9 and #21 -- the other being Shawn Michaels in 1996."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S103;S109",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM035",
        "event_id": "RR2013M",
        "wrestler_ids_involved": "the-godfather",
        "category": "other",
        "title": "The Godfather's farewell Royal Rumble, 20 years and 5 gimmicks after his debut",
        "description": (
            "The Godfather made his final Royal Rumble appearance this year, 20 years after his first "
            "Rumble appearance (1993, as Papa Shango) -- per the SE Scoops stats roundup, he competed "
            "under 5 different ring gimmicks across his Rumble history."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S102;S109",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM036",
        "event_id": "RR2014M",
        "wrestler_ids_involved": "roman-reigns;batista",
        "category": "controversy",
        "title": "Roman Reigns's broadcast-record 12 eliminations sparked a fan backlash when Batista won",
        "description": (
            "Reigns, in his Rumble debut, was broadcast-credited with a Rumble-record 12 eliminations "
            "and was the clear live-crowd favorite, while Batista -- a part-time returning veteran -- "
            "was booed heavily for winning instead, in a moment that sparked a well-known, lasting fan "
            "backlash. This database's own guest-analyst source recalculates Reigns's total at 9.5 "
            "under an even-split partial-credit system for shared eliminations (see F277); that "
            "recalculation remains single-sourced and has not been corroborated by any other source "
            "checked, so it is noted here honestly rather than adopted as a second confirmed figure."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S102;S105;S109",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text and flags.csv F277.",
    })
    nm_rows.append({
        "moment_id": "NM037",
        "event_id": "RR2014M",
        "wrestler_ids_involved": "rey-mysterio;daniel-bryan",
        "category": "notable_absence_or_substitution",
        "title": "Rey Mysterio was the surprise \"Not Daniel Bryan\" #30 entrant",
        "description": (
            "The 30th and final entrant was Rey Mysterio -- a slot Shane's own source document labels "
            "'Not Daniel Bryan,' after the surprise Bryan entrance fans had widely been expecting "
            "instead. Mysterio's identity as the deflating surprise entrant is independently confirmed "
            "via multiple post-event sources, including Daniel Bryan's and Mysterio's own public "
            "comments."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S104;S109",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text and flags.csv F276.",
    })
    nm_rows.append({
        "moment_id": "NM038",
        "event_id": "RR2014M",
        "wrestler_ids_involved": "",
        "category": "notable_absence_or_substitution",
        "title": "Xavier Woods was reportedly an official entrant who never got a spot in the match",
        "description": (
            "Xavier Woods was reportedly announced/drawn as an official entrant for this match but "
            "never actually appeared in it. Single-sourced this pass (Shane's guest-analyst source, "
            "cross-checked against Woods's own match-history record for plausibility) -- logged as "
            "PROBABLE rather than CONFIRMED."
        ),
        "data_quality_status": "PROBABLE",
        "source_ids": "S105;S114",
        "notes": "Surfaced from flags.csv F279 rather than newly researched.",
    })
    nm_rows.append({
        "moment_id": "NM039",
        "event_id": "RR2015M",
        "wrestler_ids_involved": "daniel-bryan;roman-reigns",
        "category": "controversy",
        "title": "Daniel Bryan's early elimination sparked heavy boos for Roman Reigns's win in Philadelphia",
        "description": (
            "Reigns's win, entering at #19 and eliminating Rusev in the match's final moments, was met "
            "with heavy boos from the live Philadelphia crowd, still upset over Daniel Bryan's "
            "comparatively early elimination (10:11 survival, only the 10th-longest of the match). A "
            "surprise late appearance from The Rock, endorsing Reigns and physically confronting the "
            "already-eliminated Big Show and Kane, did not turn the crowd."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S106;S109",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM040",
        "event_id": "RR2015M",
        "wrestler_ids_involved": "curtis-axel;erick-rowan",
        "category": "notable_absence_or_substitution",
        "title": "Curtis Axel was counted as an entrant with a 0:00 survival time after being substituted before he could enter",
        "description": (
            "Curtis Axel was counted as an official entrant with a 0:00 survival time after being "
            "attacked and substituted for by Erick Rowan before he could ever enter the ring -- Rowan "
            "himself is explicitly excluded as an official competitor by the source material. This "
            "participation-status modeling is strongly corroborated by 5 independent sources."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S106;S109",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM041",
        "event_id": "RR2016M",
        "wrestler_ids_involved": "",
        "category": "record",
        "title": "At 61:43, the longest Royal Rumble match timed in this database at the time",
        "description": (
            "This match ran an unusually long 61 minutes 43 seconds -- the longest Royal Rumble match "
            "timed in this document's entire multi-year data set at the time of writing."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S107;S109",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM042",
        "event_id": "RR2016M",
        "wrestler_ids_involved": "roman-reigns",
        "category": "milestone_first",
        "title": "The WWE Championship was defended -- and lost -- inside the Rumble match itself",
        "description": (
            "Roman Reigns, the reigning WWE Champion, entered at #1 and defended the title WITHIN the "
            "match itself, only the second time in Royal Rumble history a world title was decided by "
            "the match itself (after Ric Flair in 1992). He lost the title when Triple H won the "
            "match, becoming WWE Champion by winning the Rumble."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S107;S109",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM043",
        "event_id": "RR2016M",
        "wrestler_ids_involved": "brock-lesnar;braun-strowman;erick-rowan;luke-harper",
        "category": "storyline_moment",
        "title": "Brock Lesnar was eliminated in a group interference spot by \"the entire Wyatt Family\"",
        "description": (
            "Brock Lesnar was eliminated in a group interference spot originally credited only to 'the "
            "entire Wyatt Family.' Individually named via 3 independent sources -- WWE.com's own "
            "official recap, a Wrestling Inc retro review, and allrumblestats.com's data table -- which "
            "agree the participants were Braun Strowman (in his Rumble debut, going on to eliminate "
            "both Kane and Big Show back-to-back later in the match), Erick Rowan, and Luke Harper."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S040;S107;S109",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text and flags.csv F313-F318.",
    })
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "RR2013M;RR2014M;RR2015M;RR2016M",
        "table": "notable_moments",
        "record_id": "NM034;NM035;NM036;NM037;NM038;NM039;NM040;NM041;NM042;NM043",
        "field": "n/a",
        "issue_type": "corrected",
        "description": (
            "Added 10 notable_moments.csv rows for the 2013-2016 batch (the final batch of the sweep): "
            "RR2013M's Cena 2nd-win rarity and The Godfather's 5-gimmick farewell; RR2014M's Reigns "
            "record-elimination fan backlash (with the uncorroborated 9.5 recalculation noted "
            "honestly), the 'Not Daniel Bryan' Rey Mysterio surprise, and Xavier Woods's never-realized "
            "entrant spot (F279, PROBABLE, single-sourced); RR2015M's Daniel Bryan/Philadelphia boo-"
            "fest and Curtis Axel's Erick-Rowan substitution; RR2016M's then-longest-ever 61:43 running "
            "time, Roman Reigns's in-match title defense (only the 2nd in Rumble history), and the "
            "individually-named Wyatt Family group elimination of Brock Lesnar (F313-F318). Mostly "
            "surfaced from content already CONFIRMED elsewhere in this database rather than newly "
            "researched."
        ),
        "source_ids_involved": "S040;S102;S103;S104;S105;S106;S107;S109;S114",
        "status": "resolved",
        "date_logged": "2026-09-20",
    })

    save("wrestlers.csv", w_fields, w_rows)
    save("flags.csv", flag_fields, flags)
    save("notable_moments.csv", nm_fields, nm_rows)

    print("Deceased-status audit: 1 new death found (luke-harper/Brodie Lee, 2020-12-26).")
    print(f"Updated {len(hof_fixed)} wrestlers.csv rows (WWE Hall of Fame bio-completion).")
    print("Added 10 notable_moments.csv rows (NM034-NM043).")
    print("Added 3 new flags (F357-F359). No new sources needed (reused existing buckets).")
    print("This was the FINAL batch of the 1988-2016 fact-check sweep.")


if __name__ == "__main__":
    main()
