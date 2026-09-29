#!/usr/bin/env python3
"""
1997-2000 fact-check sweep, batch 3. Continues the deceased-status audit
pattern from batches 1-2 (F339-F341, F344-F345) into the next 4 events, plus
a same-real-person bio-completion fix for the Big Boss Man split id, and 4
more notable_moments.csv rows.

(0) Reconnaissance first: dumped RR1997M-RR2000M's entrants/eliminations and
    checked RR1998M's existing flags.csv entries before assuming its
    widespread blank elim_number field was a bug. It is NOT a bug -- F112
    (already resolved) documents that, like 1994/1996 (F059/F072), 1998 has
    no Cageside-style timing-analysis source, so elim_number (a DERIVED
    field computed from that kind of source, see F080's methodology note)
    is correctly left blank for this whole event, same as 1994/2000/2002/
    2004/2006. Likewise the two rows that looked like unrecorded gaps
    (Hunter Hearst Helmsley, Skull) are both already-documented, correctly
    blank special cases, not bugs: Helmsley never took a numbered entrance
    and was never himself eliminated (F113), and Skull was attacked before
    the match and never competed (F141). No entrants/eliminations fix was
    needed for RR1998M.

(1) DECEASED-STATUS + BIO-COMPLETION AUDIT, same method as batches 1-2:
    checked every RR1997M-RR2000M entrant's deceased_date against Wikipedia
    (S022) cross-checked with an independent second source (S131's mainstream
    obituary bucket, or WWE.com's own official tribute articles, S139, where
    available). Found:
      - Chyna (2016-04-17 -- the AUTOPSY-determined date of death; she was
        not found until 2016-04-20, and some outlets report the later date,
        but Wikipedia's detailed account plus independent autopsy-report
        coverage both point to 04-17 as the actual date, so that is the one
        used).
      - Terry Funk (2023-08-23), whose WWE Hall of Fame induction year
        (2009) was also missing and has now been added.
      - Brian Christopher/Grandmaster Sexay (2018-07-29).
      - Darren 'Droz' Drozdov (2023-06-30) -- IMPORTANT CORRECTION to a
        wrong assumption almost made this pass: Droz is commonly remembered
        as 'paralyzed but alive' due to his real 1999 in-ring neck injury,
        but he actually passed away in 2023 (WWE.com's own 'Darren Drozdov
        passes away' article, corroborated by multiple independent
        mainstream outlets) -- checked via search rather than assumed,
        avoiding a false-negative version of the discipline that caught the
        big-bossman/big-boss-man and Matt Borne/Doink near-misses.
      - Golga: this database's own wrestlers.csv row already states his
        real name directly ('Golga (John Tenta)', S044) -- the SAME real
        person as this database's separately-tracked 'earthquake' id
        (already CONFIRMED, fixed in batch 1 with dob/deceased_date/
        birthplace). Filled in golga's dob (1963-06-22), deceased_date
        (2006-06-07), and birthplace (Surrey, British Columbia, Canada)
        from earthquake's own already-CONFIRMED values -- not a new
        assumption, since both rows already independently identify the same
        real person by name.
      - Big Boss Man (hyphenated 'big-boss-man', the Corporation-era id):
        this database's own F338 flag already states in its own text that
        this id is 'Ray Traylor's 1999-era Corporation Big Boss Man' -- the
        same real person as the separately-tracked non-hyphenated
        'big-bossman' id (already CONFIRMED: real_name 'Ray Washington
        Traylor Jr.', dob 1963-05-02, deceased_date 2004-09-22). Filled in
        big-boss-man's real_name/dob/deceased_date from that sibling row
        (birthplace was already independently PROBABLE-sourced as
        'Marietta, Georgia' on the big-boss-man row itself, which is in
        fact the county seat of 'Cobb County, Georgia' already CONFIRMED on
        the big-bossman row -- an independent corroboration of the same
        identity, not a conflict). Also newly found and added to BOTH ids:
        Ray Traylor's 2016 WWE Hall of Fame induction (S131 -- UPI, CBS
        Sports), previously missing from both rows.
        NOTE: this is a bio-completion, not a wrestler_id MERGE -- the two
        ids remain separate rows (this database's established convention
        for tracking distinct in-story gimmick eras), only the underlying
        real-person facts were completed on both sides using each other's
        already-sourced data.

    Checked and found NO death evidence (left unchanged): Bob Backlund,
    Jake Roberts, Jerry Lawler (an unrelated 'Jerome Charles Lawler,
    1938-2026' obituary turned up in search and was checked against
    Wikipedia directly -- different birth year, not the same person; the
    real Jerry Lawler, b. 1949, is confirmed alive as of this pass), Mil
    Mascaras, Pierroth Jr. (retired 2008 after a stroke, but alive per his
    own Wikipedia infobox), and Vince McMahon (active in 2026 WWE Hall of
    Fame news).

New source: S139 (WWE.com's own 'passes away' tribute articles for Droz and
Terry Funk, official tier). Reused existing reusable-bucket sources: S022
(Wikipedia), S131 (mainstream obituary coverage, batch 1), S041 (Scott's
Blog of Doom), S138 (whatculture.com fact-article series, batch 2).

(2) 4 new notable_moments.csv rows:
      - RR1997M: the Bret Hart/Steve Austin missed-call finish -- Hart threw
        Austin out unseen by the distracted referees, Austin snuck back in
        and won anyway. Already fully documented in this database's own
        F081 (a deliberate modeling choice, not a data gap) -- surfaced here
        for discoverability, same treatment as batch 2's Giant Gonzalez row.
      - RR1997M: Mil Mascaras eliminating himself via an apron-to-turnbuckle
        dive after his opponent was already gone -- already documented in
        F082. Surfaced here, no new research.
      - RR1999M: Vince McMahon's win -- the only authority-figure/non-
        full-time-wrestler winner in this database's coverage so far,
        immediately forfeiting his own WrestleMania title shot (a first),
        which was then awarded to runner-up Steve Austin. Newly researched,
        2 independent sources (Wikipedia; whatculture.com S138).
      - RR2000M: The Rock's botched final elimination of Big Show -- Rock's
        own feet touched the floor before Show's during the exchange that
        eliminated Show, but Rock was declared the winner anyway; WWE turned
        the botch into an ongoing angle, and The Rock himself publicly
        acknowledged years later that Big Show 'legitimately should have
        been declared the winner.' Newly researched, 2 independent sources
        (Wikipedia; Scott's Blog of Doom, S041).

Usage:
    python3 factcheck_1997_2000_sweep_batch3.py [data_dir]   (default: data)
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
    s_fields, s_rows = load("sources.csv")
    flag_fields, flags = load("flags.csv")
    try:
        nm_fields, nm_rows = load("notable_moments.csv")
    except FileNotFoundError:
        nm_fields, nm_rows = NOTABLE_MOMENTS_FIELDS, []

    by_id = {r["wrestler_id"]: r for r in w_rows}

    # ---- new source ---------------------------------------------------
    s_rows.append({
        "source_id": "S139",
        "source_name": "WWE.com -- official 'passes away' tribute articles (Darren Drozdov; Terry Funk)",
        "source_type": "official_wwe",
        "url": "",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-18",
        "notes": "1997-2000 sweep batch 3 deceased-status audit.",
    })

    # ---- (1) deceased-status + bio-completion audit --------------------
    def add_src(row, *ids):
        cur = set(filter(None, row["source_ids"].split(";")))
        cur.update(ids)
        row["source_ids"] = ";".join(sorted(cur))

    fixed_ids = []

    chyna = by_id["chyna"]
    chyna["deceased_date"] = "2016-04-17"
    add_src(chyna, "S022", "S131")
    fixed_ids.append("chyna")

    funk = by_id["terry-funk"]
    funk["deceased_date"] = "2023-08-23"
    funk["hall_of_fame_year"] = "2009"
    add_src(funk, "S022", "S131", "S139")
    fixed_ids.append("terry-funk")

    bc = by_id["brian-christopher"]
    bc["deceased_date"] = "2018-07-29"
    add_src(bc, "S022", "S131")
    fixed_ids.append("brian-christopher")

    droz = by_id["droz"]
    droz["deceased_date"] = "2023-06-30"
    add_src(droz, "S022", "S131", "S139")
    fixed_ids.append("droz")

    golga = by_id["golga"]
    golga["dob"] = "1963-06-22"
    golga["dob_status"] = "CONFIRMED"
    golga["deceased_date"] = "2006-06-07"
    golga["birthplace"] = "Surrey, British Columbia, Canada"
    golga["birthplace_status"] = "CONFIRMED"
    add_src(golga, "S022", "S131")
    fixed_ids.append("golga")

    bbm_sib = by_id["big-bossman"]
    bbm_sib["hall_of_fame_year"] = "2016"
    add_src(bbm_sib, "S131")
    fixed_ids.append("big-bossman")

    bbm = by_id["big-boss-man"]
    bbm["real_name"] = "Ray Washington Traylor Jr."
    bbm["real_name_status"] = "CONFIRMED"
    bbm["dob"] = "1963-05-02"
    bbm["dob_status"] = "CONFIRMED"
    bbm["deceased_date"] = "2004-09-22"
    bbm["hall_of_fame_year"] = "2016"
    add_src(bbm, "S131")
    fixed_ids.append("big-boss-man")

    assert len(fixed_ids) == 7

    counter = 346
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "",
        "table": "wrestlers",
        "record_id": ";".join(fixed_ids),
        "field": "deceased_date;hall_of_fame_year;real_name;dob;birthplace",
        "issue_type": "corrected",
        "description": (
            "1997-2000 fact-check sweep, continuing the deceased-status audit from batches 1-2 "
            "(F339-F341, F344-F345): 4 more wrestlers confirmed deceased with a blank deceased_date -- "
            "Chyna (2016-04-17, the autopsy-determined date, not the 2016-04-20 found-date some outlets "
            "use), Terry Funk (2023-08-23; also added his 2009 WWE Hall of Fame induction, previously "
            "missing), Brian Christopher/Grandmaster Sexay (2018-07-29), and Darren 'Droz' Drozdov "
            "(2023-06-30 -- a correction to the common assumption that Droz, paralyzed by a real 1999 "
            "in-ring injury, was still alive; verified via WWE.com's own tribute article rather than "
            "assumed). Also completed 2 same-real-person bio gaps using this database's own already-"
            "sourced sibling data rather than new assumptions: golga's dob/deceased_date/birthplace "
            "filled in from the 'earthquake' id (both rows already independently name John Tenta), and "
            "big-boss-man's real_name/dob/deceased_date filled in from the 'big-bossman' id (F338 already "
            "identifies big-boss-man as 'Ray Traylor's 1999-era Corporation Big Boss Man' in its own "
            "text; the two ids remain separate rows per this database's gimmick-era convention -- only "
            "the underlying real-person facts were completed). Also newly found and added to BOTH "
            "big-bossman and big-boss-man: Ray Traylor's 2016 WWE Hall of Fame induction, previously "
            "missing from both. Checked but found no death evidence for Bob Backlund, Jake Roberts, "
            "Jerry Lawler (an unrelated same-name 1938-2026 obituary was checked and ruled out against "
            "Wikipedia directly), Mil Mascaras, Pierroth Jr., and Vince McMahon."
        ),
        "source_ids_involved": "S022;S131;S139",
        "status": "resolved",
        "date_logged": "2026-09-18",
    })
    counter += 1

    # ---- (2) notable_moments additions ---------------------------------
    nm_rows.append({
        "moment_id": "NM008",
        "event_id": "RR1997M",
        "wrestler_ids_involved": "bret-hart;steve-austin",
        "category": "controversy",
        "title": "Bret Hart eliminated Steve Austin unseen by the referees -- who then counted Austin's win anyway",
        "description": (
            "At 50:05, Bret Hart threw Steve Austin over the top rope, but the referees were distracted "
            "by a Mankind/Terry Funk brawl outside the ring and never saw it. Austin snuck back in "
            "undetected, eliminated The Undertaker and Vader, then eliminated Hart from behind to be "
            "declared the winner -- an outcome the match's own official record still reflects today. "
            "This database deliberately models the officiated (missed-call) result rather than the true "
            "sequence of events, treating it the same way the broadcast itself did. See flags.csv F081 "
            "for the full modeling rationale."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S033;S034",
        "notes": "Already documented in this database's own F081 -- surfaced here for the notable_moments panel rather than newly researched.",
    })
    nm_rows.append({
        "moment_id": "NM009",
        "event_id": "RR1997M",
        "wrestler_ids_involved": "mil-mascaras",
        "category": "botch",
        "title": "Mil Mascaras eliminated himself with a dive he didn't need to make",
        "description": (
            "Mascaras threw his opponent outside the ring, then -- rather than simply staying in the "
            "match -- ducked through the middle rope, climbed to the turnbuckle from the ring apron, and "
            "dove onto his opponent outside, landing on his feet and eliminating himself in the process. "
            "The source narrative itself notes uncertainty about whether this even should have counted as "
            "'going over the top' by the match's usual rule, but the referees ruled it a self-elimination "
            "on landing, citing Rick Martel's earlier Rumble as precedent. See flags.csv F082."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S033",
        "notes": "Already documented in this database's own F082 -- surfaced here for the notable_moments panel rather than newly researched.",
    })
    nm_rows.append({
        "moment_id": "NM010",
        "event_id": "RR1999M",
        "wrestler_ids_involved": "vince-mcmahon;steve-austin",
        "category": "milestone_first",
        "title": "Vince McMahon won the Royal Rumble -- then immediately gave away his own title shot",
        "description": (
            "With help from a distraction by The Rock, Vince McMahon eliminated Steve Austin last to win "
            "the match himself, denying Austin what would have been an unprecedented third straight Rumble "
            "win. McMahon is the only authority-figure/non-full-time-wrestler winner in this database's "
            "coverage so far. In a first for the Rumble, the winner then forfeited his own WrestleMania "
            "title-match reward; Commissioner Shawn Michaels awarded it instead to runner-up Austin, 'much "
            "to McMahon's fury,' setting up Austin's WrestleMania XV title win."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S022;S138",
        "notes": "2 independent sources agree on the mechanics, the forfeiture, and the reassignment to Austin.",
    })
    nm_rows.append({
        "moment_id": "NM011",
        "event_id": "RR2000M",
        "wrestler_ids_involved": "rocky-maivia;big-show",
        "category": "botch",
        "title": "The Rock's feet hit the floor before Big Show's on the winning elimination -- but Rock was declared the winner anyway",
        "description": (
            "In the match's final exchange, The Rock eliminated Big Show using Show's own momentum, but in "
            "doing so The Rock's own feet touched the floor outside the ring a beat before Big Show's did -- "
            "by the match's own rules, arguably Big Show, not Rock, should have won. Referees declared The "
            "Rock the winner regardless. Big Show spent the following weeks claiming he had 'indisputable "
            "video evidence' of the real result; Triple H reviewed it on-air but the decision stood. Years "
            "later, The Rock himself publicly agreed Big Show 'legitimately should have been declared the "
            "winner.'"
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S022;S041",
        "notes": "2 independent sources (Wikipedia's detailed account; Scott Keith's Blog of Doom retrospective) agree on the sequence and the later Rock admission.",
    })
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "RR1997M;RR1999M;RR2000M",
        "table": "notable_moments",
        "record_id": "NM008;NM009;NM010;NM011",
        "field": "n/a",
        "issue_type": "corrected",
        "description": (
            "Added 4 more notable_moments.csv rows for the 1997-2000 batch: RR1997M's Bret Hart/Austin "
            "missed-call finish and Mil Mascaras' self-elimination dive (both surfacing existing, "
            "already-sourced content from F081/F082 into the new table), RR1999M's Vince McMahon win and "
            "title-shot forfeiture, and RR2000M's Rock/Big Show botched-finish controversy (both newly "
            "researched, 2 independent sources each)."
        ),
        "source_ids_involved": "S022;S033;S034;S041;S138",
        "status": "resolved",
        "date_logged": "2026-09-18",
    })

    save("wrestlers.csv", w_fields, w_rows)
    save("sources.csv", s_fields, s_rows)
    save("flags.csv", flag_fields, flags)
    save("notable_moments.csv", nm_fields, nm_rows)

    print(f"Updated {len(fixed_ids)} wrestlers.csv rows (deceased-status + bio-completion audit).")
    print("Added 4 notable_moments.csv rows (NM008-NM011).")
    print("Added 1 new source (S139), 2 new flags.")


if __name__ == "__main__":
    main()
