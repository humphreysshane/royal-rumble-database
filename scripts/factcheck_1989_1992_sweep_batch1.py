#!/usr/bin/env python3
"""
1989-1992 fact-check sweep, batch 1: deceased-status audit + a cluster of
long-open bio-fact conflicts, resolved against fresh external sources.

Two threads of work, both discovered while doing the "next sweep" Shane
asked for on top of the 1988 pilot pass:

(1) DECEASED-STATUS AUDIT. Shane's original complaint that kicked off this
    whole sweep was that Hulk Hogan's death wasn't reflected in the R014
    "now deceased" leaderboard (fixed earlier this session, F334). Checking
    every 1989-1992 entrant's deceased_date field for blanks turned up the
    same bug repeated many more times over -- 11 entrants across these 4
    events who are in fact deceased (some for over 20 years) but have a
    blank deceased_date, meaning R014 has been undercounting for every
    event any of them entered, not just the ones built so far. Each is
    individually confirmed via Wikipedia (S022, this database's standing
    "various wrestler biography articles" source) cross-checked against at
    least one independent news/wrestling-database source (new S130/S131).
    Three also had a genuine WWE Hall of Fame induction not yet reflected
    in hall_of_fame_year (Roddy Piper 2005, Dusty Rhodes 2007, Jimmy Snuka
    1996) -- found incidentally while confirming the same Wikipedia
    articles, confirmed via WWE.com's own Hall of Fame announcement pages
    (new S132) as a second, official-tier source. Jim Neidhart's 2019 HOF
    induction (as part of The Hart Foundation alongside Bret Hart, who
    already carries his own separate 2006 solo induction on his own row)
    is the same pattern.

    NOTE for Shane: this audit only covered the ~30 entrants of each of
    the 4 events in this batch, not the full 328-wrestler roster. Given
    how many turned up in just this slice, it's likely worth a dedicated
    future pass auditing deceased_date across the WHOLE database rather
    than only catching these as each new event gets swept -- flagged as
    an open item below (F340) rather than attempted here.

(2) LONG-OPEN BIO-FACT CONFLICTS. Several 1989-era conflicting-source
    flags (F046, F047, F049, F050) were logged during the original build
    as genuinely disputed and deliberately left open pending "a human
    look" or "a tiebreaking third source" -- exactly what this pass is
    for. Fresh independent lookups this pass supplied that missing third
    source (or, for Greg Valentine's real name, a genuine second
    independent source beyond the original Wikipedia citation) in every
    case, so these are now resolved one way or the other:
      - Greg Valentine's real name: CORRECTED to "Jonathan Anthony
        Wisniski" (Wikipedia + ewrestlingnews.com, new S130, agree;
        Shane's original doc's "Gregory Wisniski" was the outlier).
      - Brutus Beefcake's birthplace: CORRECTED to Tampa, Florida
        (Wikipedia + Cagematch agree; Shane's doc's San Francisco was the
        outlier).
      - Brutus Beefcake's DOB: the OPPOSITE outcome -- Cagematch actually
        agrees with Shane's existing 1958-04-21 (not Wikipedia's
        1957-04-21), so the existing value is UPGRADED to CONFIRMED
        rather than changed; Wikipedia's disagreement is preserved.
      - Mr. Fuji's DOB: CORRECTED to 1934-05-04 (Wikipedia already said
        this; now independently corroborated by Find a Grave and a
        wrestling-history page, new S130/S131 -- Shane's doc's 1935 was
        the outlier).
      - Gorilla Monsoon's birthplace: CORRECTED to Rochester, New York
        (Wikipedia + Cagematch already agreed per the original flag; a
        third independent source, Rochester's own city wiki, corroborates
        -- Shane's doc's "New York, New York" was the outlier).
      - Red Rooster's birthplace: CORRECTED to Greenville, South Carolina
        -- this one turns out to have ALREADY been decided the same way
        by an earlier pass (the wrestlers.csv row already reads
        Greenville, South Carolina with a full resolution note!) but the
        flags.csv F048 row was never updated to match -- a stale-flag
        bug, fixed here by marking F048 resolved to describe what the
        data actually says, not by changing the data itself.
      - F009 (Red Rooster's real name) has the same stale-flag bug: the
        wrestlers.csv row already carries the correct resolution
        (S014's "Terry Taylor" was never a competing real-name claim --
        it's the same public ring name Wikipedia also uses, alongside the
        confirmed birth name "Paul Worden Taylor III"). Marked resolved
        to match.
      - Col. Mustafa's real identity (F031) has the SAME stale-flag bug
        in a more confusing form: the wrestlers.csv row already has his
        correct, fully-CONFIRMED real bio (Hossein Khosrow Ali Vaziri --
        this is The Iron Sheik, back from a mid-career hiatus for a
        1991-92 Gulf War storyline gimmick) but the row's own notes text
        and flags.csv both still claim this is unresolved. Fixed the
        notes, added "The Iron Sheik" as a known alias so a future event
        build that meets him under that name links to the same
        wrestler_id, and -- since this IS the Iron Sheik -- also added
        his hall_of_fame_year (2005) and deceased_date (2023-06-07),
        neither of which any earlier pass had reason to add since they
        didn't realize who this row already, correctly, said he was.

New sources: S130 (a second batch of non-Wikipedia bio/obituary sites --
ewrestlingnews.com, Find a Grave, wrestling-history pages -- treated as one
reusable source the same way S022/S024 are), S131 (mainstream news
obituary coverage -- CNN, CBS News, Rolling Stone, Washington Post, etc. --
same reusable-source treatment), S132 (WWE.com's own Hall of Fame
induction-class pages, official tier).

Usage:
    python3 factcheck_1989_1992_sweep_batch1.py [data_dir]   (default: data)
"""
import csv
import sys

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


new_flag = None  # set in main()


def make_flag_factory(start_id):
    counter = {"n": start_id}

    def _new_flag(flags, event_id, table, record_id, field, issue_type, description, source_ids, status):
        flag_id = f"F{counter['n']:03d}"
        flags.append({
            "flag_id": flag_id,
            "event_id": event_id,
            "table": table,
            "record_id": record_id,
            "field": field,
            "issue_type": issue_type,
            "description": description,
            "source_ids_involved": source_ids,
            "status": status,
            "date_logged": "2026-09-18",
        })
        counter["n"] += 1
        return flag_id

    return _new_flag


def update_flag_status(flags, flag_id, new_status, appended_note):
    found = False
    for f in flags:
        if f["flag_id"] == flag_id:
            f["status"] = new_status
            f["description"] = f["description"].rstrip() + " " + appended_note
            found = True
    assert found, f"flag {flag_id} not found"


def main():
    w_fields, w_rows = load("wrestlers.csv")
    s_fields, s_rows = load("sources.csv")
    flag_fields, flags = load("flags.csv")

    add_flag = make_flag_factory(339)

    # ---- new sources ---------------------------------------------------
    s_rows.append({
        "source_id": "S130",
        "source_name": "ewrestlingnews.com wrestler profiles; Find a Grave memorial pages; assorted wrestling-history pages",
        "source_type": "wrestling_database",
        "url": "",
        "reliability_tier": "12",
        "tier_label": "Other reputable site",
        "accessed_date": "2026-09-18",
        "notes": ("1989-1992 sweep batch 1. A second reusable non-Wikipedia bio source, used "
                  "alongside/instead of Cagematch (S023) or thesmackdownhotel.com (S024) where those "
                  "specifically corroborated a real name, DOB, or death date -- treated as ONE source "
                  "regardless of how many individual pages were consulted, same convention as S022."),
    })
    s_rows.append({
        "source_id": "S131",
        "source_name": "Mainstream news obituary coverage (CNN, CBS News, Rolling Stone, Washington Post, Variety, CBC, and similar)",
        "source_type": "reputable_publication",
        "url": "",
        "reliability_tier": "12",
        "tier_label": "Other reputable site",
        "accessed_date": "2026-09-18",
        "notes": ("1989-1992 sweep batch 1. Used as independent corroboration for exact death dates "
                  "alongside Wikipedia (S022) -- mainstream outlets reporting a death within a day or "
                  "two of it happening are treated as a genuinely independent check on Wikipedia's own "
                  "figure, not a mirror of it. Treated as ONE reusable source, same convention as S022."),
    })
    s_rows.append({
        "source_id": "S132",
        "source_name": "WWE.com official Hall of Fame induction-class pages",
        "source_type": "official_wwe",
        "url": "",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-18",
        "notes": ("1989-1992 sweep batch 1. Used to confirm specific Hall of Fame induction years found "
                  "incidentally while researching deceased-status (Roddy Piper 2005, Dusty Rhodes 2007, "
                  "Jimmy Snuka 1996, The Hart Foundation/Jim Neidhart 2019)."),
    })

    by_id = {r["wrestler_id"]: r for r in w_rows}

    # ---- (1) deceased-status audit --------------------------------------
    deceased_fixes = {
        "roddy-piper":      {"deceased_date": "2015-07-31", "hall_of_fame_year": "2005"},
        "dusty-rhodes":     {"deceased_date": "2015-06-11", "hall_of_fame_year": "2007"},
        "jimmy-snuka":      {"deceased_date": "2017-01-15", "hall_of_fame_year": "1996"},
        "earthquake":       {"deceased_date": "2006-06-07"},
        "texas-tornado":    {"deceased_date": "1993-02-18"},
        "british-bulldog":  {"deceased_date": "2002-05-18"},
        "hawk":             {"deceased_date": "2003-10-19"},
        "animal":           {"deceased_date": "2020-09-22"},
        "demolition-crush": {"deceased_date": "2007-08-13"},
        "jim-neidhart":     {"deceased_date": "2018-08-13", "hall_of_fame_year": "2019"},
        "butch-miller":     {"deceased_date": "2023-04-02"},
        "col-mustafa":      {"deceased_date": "2023-06-07", "hall_of_fame_year": "2005"},
    }
    fixed_ids = []
    for wid, fields in deceased_fixes.items():
        row = by_id[wid]
        for k, v in fields.items():
            row[k] = v
        existing_src = set(filter(None, row["source_ids"].split(";")))
        existing_src.update(["S022", "S131"])
        if "hall_of_fame_year" in fields:
            existing_src.add("S132")
        row["source_ids"] = ";".join(sorted(existing_src))
        fixed_ids.append(wid)
    assert len(fixed_ids) == 12

    add_flag(
        flags, "", "wrestlers",
        ";".join(fixed_ids),
        "deceased_date;hall_of_fame_year",
        "corrected",
        ("1989-1992 fact-check sweep: audited every 1989-1992 Rumble entrant's deceased_date field "
         "(the same field Shane's original Hogan complaint, F334, was about) and found 12 more "
         "wrestlers who are confirmed deceased but had a blank deceased_date -- Roddy Piper "
         "(2015-07-31), Dusty Rhodes (2015-06-11), Jimmy Snuka (2017-01-15), Earthquake/John Tenta "
         "(2006-06-07), Texas Tornado/Kerry Von Erich (1993-02-18), British Bulldog/Davey Boy Smith "
         "(2002-05-18), Road Warrior Hawk (2003-10-19), Road Warrior Animal (2020-09-22), Demolition "
         "Crush/Brian Adams (2007-08-13), Jim Neidhart (2018-08-13), Bushwhacker Butch (2023-04-02), "
         "and Col. Mustafa/The Iron Sheik (2023-06-07, see F341/the Col. Mustafa notes fix below for "
         "why this one needed extra unpacking). Each confirmed via Wikipedia (S022) cross-checked "
         "against at least one independent news/obituary or wrestling-database source (S130/S131). "
         "Incidentally also found 3 real Hall of Fame inductions missing from hall_of_fame_year for "
         "the same reason (Piper 2005, Rhodes 2007, Snuka 1996) plus Jim Neidhart's 2019 Hart "
         "Foundation induction and Col. Mustafa/Iron Sheik's 2005 induction -- confirmed via WWE.com's "
         "own Hall of Fame pages (S132). now_deceased_count and the HOF-members leaderboards are "
         "recomputed fresh from this data on every build_derived.py run, so this corrects every "
         "Rumble any of these 12 wrestlers entered, not just 1989-1992."),
        "S022;S130;S131;S132",
        "resolved",
    )
    add_flag(
        flags, "", "wrestlers", "*", "deceased_date",
        "unverified",
        ("Flagged for Shane, not fully actioned this pass: the deceased-status audit above only "
         "covered the ~30 entrants each of RR1989M-RR1992M (this batch's 4 events) -- it found 12 "
         "missing deaths in just that slice, which strongly suggests deceased_date is incomplete "
         "across the FULL ~328-wrestler roster, not only for events built/swept so far. Worth a "
         "dedicated database-wide pass rather than only catching these incidentally as each new "
         "event's sweep happens to touch a deceased wrestler."),
        "",
        "open",
    )

    # ---- (2a) Greg Valentine real name -----------------------------------
    row = by_id["greg-valentine"]
    row["real_name"] = "Jonathan Anthony Wisniski"
    row["real_name_status"] = "CONFIRMED"
    src = set(filter(None, row["source_ids"].split(";")))
    src.update(["S022", "S130"])
    row["source_ids"] = ";".join(sorted(src))
    update_flag_status(
        flags, "F046", "resolved",
        ("UPDATE 2026-09-18 (sweep batch 1): a second independent source (ewrestlingnews.com, new "
         "S130) also gives 'Jonathan Anthony Wisniski', agreeing with Wikipedia (S022) and outweighing "
         "Shane's single-sourced 'Gregory Wisniski'. Corrected real_name to 'Jonathan Anthony "
         "Wisniski', status upgraded to CONFIRMED.")
    )

    # ---- (2b) Brutus Beefcake birthplace (corrected) + DOB (upgraded) ----
    row = by_id["brutus-beefcake"]
    row["birthplace"] = "Tampa, Florida"
    row["birthplace_status"] = "CONFIRMED"
    row["dob_status"] = "CONFIRMED"  # existing dob 1958-04-21 kept, now 2-source confirmed
    src = set(filter(None, row["source_ids"].split(";")))
    src.update(["S022", "S023"])
    row["source_ids"] = ";".join(sorted(src))
    update_flag_status(
        flags, "F047", "resolved",
        ("UPDATE 2026-09-18 (sweep batch 1): re-checked Cagematch (S023) directly for this specific "
         "wrestler (the original pass had it rate-limited for most of the roster). Cagematch "
         "independently agrees with Wikipedia (S022): Tampa, Florida. Corrected from Shane's San "
         "Francisco, status upgraded to CONFIRMED. Bonus finding while there: Cagematch's DOB for "
         "this wrestler is 1958-04-21 -- NOT 1957-04-21 like Wikipedia -- meaning it actually agrees "
         "with Shane's original document instead. dob_status upgraded from CONFLICTING to CONFIRMED "
         "in Shane's favor (existing 1958-04-21 value unchanged); Wikipedia's differing 1957 is the "
         "now-outvoted figure."),
    )

    # ---- (2c) Mr. Fuji DOB -------------------------------------------------
    row = by_id["mr-fuji"]
    row["dob"] = "1934-05-04"
    row["dob_status"] = "CONFIRMED"
    src = set(filter(None, row["source_ids"].split(";")))
    src.update(["S022", "S130"])
    row["source_ids"] = ";".join(sorted(src))
    update_flag_status(
        flags, "F049", "resolved",
        ("UPDATE 2026-09-18 (sweep batch 1): 2 more independent sources (Find a Grave and a wrestling-"
         "history page, new S130) both agree with Wikipedia (S022) on 1934, not 1935. Corrected DOB to "
         "1934-05-04, status upgraded to CONFIRMED. Shane's 1935 is the now-outvoted figure (same "
         "day/month, so almost certainly a simple year transcription slip in the original document)."),
    )

    # ---- (2d) Gorilla Monsoon birthplace -----------------------------------
    row = by_id["gorilla-monsoon"]
    row["birthplace"] = "Rochester, New York"
    row["birthplace_status"] = "CONFIRMED"
    src = set(filter(None, row["source_ids"].split(";")))
    src.add("S130")  # RocWiki, a Rochester-specific source, folded into the reusable S130
    row["source_ids"] = ";".join(sorted(src))
    update_flag_status(
        flags, "F050", "resolved",
        ("UPDATE 2026-09-18 (sweep batch 1): a third independent source -- RocWiki, a Rochester, NY "
         "specific community wiki (folded into reusable source S130) -- also confirms Rochester, New "
         "York, on top of Wikipedia (S022) and Cagematch (S023) already agreeing per the original "
         "flag. Corrected from Shane's 'New York, New York' (i.e. NYC), status upgraded to CONFIRMED."),
    )

    # ---- (2e) Red Rooster birthplace + real name -- stale-flag fixes only -
    # wrestlers.csv already holds the corrected values from an earlier pass;
    # flags.csv F009/F048 were simply never marked resolved to match. No data
    # change needed here, just synchronizing flag status with reality.
    update_flag_status(
        flags, "F009", "resolved",
        ("UPDATE 2026-09-18 (sweep batch 1): this was already resolved in wrestlers.csv (see that "
         "row's own notes -- Wikipedia confirms 'Paul Worden Taylor III' as the formal birth name, "
         "matching S015, while S014's 'Terry Taylor' is the same public ring name Wikipedia also "
         "uses, not a competing real-name claim) but this flag's status was never updated to match. "
         "Synchronized -- no data changed, just this flag's status."),
    )
    update_flag_status(
        flags, "F048", "resolved",
        ("UPDATE 2026-09-18 (sweep batch 1): same stale-flag situation as F009 -- wrestlers.csv's "
         "red-rooster row already reads 'Greenville, South Carolina' with a full resolution note from "
         "an earlier pass (Wikipedia + Cagematch, 2 independent sources, agreeing against Shane's "
         "single-sourced Vero Beach). This flag's status was simply never updated to match. "
         "Synchronized -- no data changed, just this flag's status."),
    )

    # ---- (2f) Col. Mustafa = The Iron Sheik --------------------------------
    row = by_id["col-mustafa"]
    row["aliases_ring_names"] = "The Iron Sheik"
    row["hall_of_fame_year"] = "2005"
    row["deceased_date"] = "2023-06-07"
    row["notes"] = (
        "This IS The Iron Sheik (Khosrow Vaziri), returning to the WWF in March 1991 under a new "
        "gimmick for the Gulf War-era Sgt. Slaughter storyline -- confirmed via Wikipedia's own Iron "
        "Sheik article and thesportster.com (new S130), both independently corroborating the real "
        "name/DOB/birthplace this row already carried (S022;S023 -- Cagematch was in fact one of the "
        "handful of profiles that loaded during the original pass, per S023's own notes; this row's "
        "bio fields were correct all along). Also confirmed: WWE Hall of Fame class of 2005 (S132), "
        "and died 2023-06-07 (S022;S131) -- neither was added previously because this row's own notes "
        "text incorrectly claimed his identity was still unresolved. See flags.csv F031 (now resolved) "
        "and F341."
    )
    src = set(filter(None, row["source_ids"].split(";")))
    src.update(["S130", "S131", "S132"])
    row["source_ids"] = ";".join(sorted(src))
    update_flag_status(
        flags, "F031", "resolved",
        ("UPDATE 2026-09-18 (sweep batch 1): resolved -- this is The Iron Sheik (Khosrow Vaziri), "
         "confirmed via Wikipedia + thesportster.com (new S130), corroborating the real name/DOB/"
         "birthplace this row already carried from Cagematch (S023) in the original pass. Added "
         "'The Iron Sheik' as a known alias, plus his HOF year (2005, S132) and deceased_date "
         "(2023-06-07, S022;S131) -- see F341 for why those were missing despite the identity being "
         "known."),
    )
    add_flag(
        flags, "RR1992M", "wrestlers", "col-mustafa", "notes;hall_of_fame_year;deceased_date",
        "corrected",
        ("Found while resolving F031: the col-mustafa wrestlers.csv row already had Col. Mustafa's "
         "correct real identity (Hossein Khosrow Ali Vaziri / The Iron Sheik) fully CONFIRMED with "
         "real_name/dob/birthplace filled in from an earlier pass (S020;S021;S022;S023) -- but that "
         "row's own notes text still said 'No real-identity connection stated... No bio data', "
         "flatly contradicting the data 2 rows up in the same file. Because of that self-contradiction, "
         "no later pass (including this database's Hall-of-Fame-field cleanup, F333) had reason to "
         "also add his Hall of Fame year or death date, even though both are trivially findable once "
         "you know this is the Iron Sheik. Fixed the notes text and added hall_of_fame_year (2005) "
         "and deceased_date (2023-06-07). Logged as its own flag since this is a distinct root cause "
         "(a stale/self-contradicting notes field) from the plain missing-data pattern in the main "
         "deceased-status audit flag above."),
        "S130;S131;S132",
        "resolved",
    )

    save("wrestlers.csv", w_fields, w_rows)
    save("sources.csv", s_fields, s_rows)
    save("flags.csv", flag_fields, flags)

    print(f"Updated {len(fixed_ids)} wrestlers.csv deceased-status rows.")
    print("Corrected/resolved 6 long-open bio conflicts (Valentine, Beefcake x2, Fuji, Monsoon, "
          "Col. Mustafa identity) + synchronized 2 stale flags (F009, F048).")
    print("Added 3 new sources (S130-S132).")


if __name__ == "__main__":
    main()
