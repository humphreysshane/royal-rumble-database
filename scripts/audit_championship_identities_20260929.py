"""Build deterministic queues for championship-performer identity review.

This is an audit only. It never edits the source CSVs.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "research" / "championship_identity_audit_20260929"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    value = re.sub(r"\[[^]]*]", "", value)
    value = re.sub(r"\([^)]*\b(?:reign|current)\b[^)]*\)", "", value, flags=re.I)
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().casefold()
    return re.sub(r"\s+", " ", value)


def aliases(row: dict[str, str]) -> set[str]:
    values = {row.get("ring_name", ""), row.get("real_name", "")}
    values.update(re.split(r"[;|]", row.get("aliases_ring_names", "")))
    return {norm(v) for v in values if norm(v)}


def main() -> None:
    wrestlers = read_csv("wrestlers.csv")
    entrants = read_csv("entrants.csv")
    reigns = read_csv("championship_reigns.csv")
    championships = {r["championship_id"]: r for r in read_csv("championships.csv")}

    entrant_ids = {r["wrestler_id"] for r in entrants}
    wrestler_by_id = {r["wrestler_id"]: r for r in wrestlers}
    alias_to_ids: dict[str, set[str]] = defaultdict(set)
    for wrestler in wrestlers:
        for alias in aliases(wrestler):
            alias_to_ids[alias].add(wrestler["wrestler_id"])
    for entrant in entrants:
        for field in ("ring_name_at_time", "name_displayed_at_event"):
            alias = norm(entrant.get(field, ""))
            if alias:
                alias_to_ids[alias].add(entrant["wrestler_id"])

    duplicate_rows: list[dict[str, object]] = []
    duplicate_pairs: set[tuple[str, str, str]] = set()
    for key_type, getter in (
        ("real_name", lambda r: norm(r.get("real_name", ""))),
        ("date_of_birth", lambda r: r.get("date_of_birth", "").strip()),
    ):
        groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for wrestler in wrestlers:
            key = getter(wrestler)
            if key:
                groups[key].append(wrestler)
        for key, group in groups.items():
            if len(group) < 2:
                continue
            for i, left in enumerate(group):
                for right in group[i + 1 :]:
                    pair = tuple(sorted((left["wrestler_id"], right["wrestler_id"]))) + (key_type,)
                    if pair in duplicate_pairs:
                        continue
                    duplicate_pairs.add(pair)
                    duplicate_rows.append({
                        "match_basis": key_type,
                        "match_value": key,
                        "wrestler_id_1": left["wrestler_id"],
                        "ring_name_1": left.get("ring_name", ""),
                        "is_entrant_1": str(left["wrestler_id"] in entrant_ids).upper(),
                        "wrestler_id_2": right["wrestler_id"],
                        "ring_name_2": right.get("ring_name", ""),
                        "is_entrant_2": str(right["wrestler_id"] in entrant_ids).upper(),
                    })

    unlinked_names = Counter(
        r["champion_name"].strip()
        for r in reigns
        if r.get("record_type") == "reign" and not r.get("champion_wrestler_ids", "").strip()
    )
    rumble_aliases = {
        alias: ids & entrant_ids for alias, ids in alias_to_ids.items() if ids & entrant_ids
    }
    unlinked_rows: list[dict[str, object]] = []
    for champion_name, row_count in sorted(unlinked_names.items(), key=lambda item: (-item[1], item[0])):
        key = norm(champion_name)
        exact = sorted(rumble_aliases.get(key, set()))
        fuzzy: list[tuple[float, str, str]] = []
        if not exact and key:
            for alias, ids in rumble_aliases.items():
                # Cheap guards keep this deterministic audit fast across
                # thousands of historical team/champion strings.
                if alias[:1] != key[:1] or abs(len(alias) - len(key)) > 8:
                    continue
                score = SequenceMatcher(None, key, alias).ratio()
                if score >= 0.82:
                    for wrestler_id in ids:
                        fuzzy.append((score, wrestler_id, alias))
        fuzzy.sort(reverse=True)
        unlinked_rows.append({
            "champion_name": champion_name,
            "reign_row_count": row_count,
            "exact_rumble_wrestler_ids": ";".join(exact),
            "top_fuzzy_candidates": ";".join(
                f"{wid}|{alias}|{score:.3f}" for score, wid, alias in fuzzy[:5]
            ),
            "review_status": "AUTO_EXACT" if exact else "RESEARCH",
        })

    linked_ids = Counter()
    for reign in reigns:
        for wrestler_id in reign.get("champion_wrestler_ids", "").split(";"):
            if wrestler_id:
                linked_ids[wrestler_id] += 1

    # A wrestler_id represents a presentation/gimmick, not always a unique
    # person.  Build conservative performer groups from an exact sourced real
    # name or exact DOB so a linked Syxx/X-Pac reign, for example, satisfies
    # the 1-2-3 Kid identity as well without rewriting historical ring names.
    parent = {w["wrestler_id"]: w["wrestler_id"] for w in wrestlers}

    def find(wid: str) -> str:
        while parent[wid] != wid:
            parent[wid] = parent[parent[wid]]
            wid = parent[wid]
        return wid

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    for getter in (
        lambda w: norm(w.get("real_name", "")),
        lambda w: w.get("date_of_birth", "").strip(),
    ):
        groups: dict[str, list[str]] = defaultdict(list)
        for wrestler in wrestlers:
            key = getter(wrestler)
            if key:
                groups[key].append(wrestler["wrestler_id"])
        for ids in groups.values():
            for wid in ids[1:]:
                union(ids[0], wid)

    performer_ids: dict[str, set[str]] = defaultdict(set)
    for wid in parent:
        performer_ids[find(wid)].add(wid)
    entrant_performers = {find(wid) for wid in entrant_ids}
    linked_performers = {find(wid) for wid in linked_ids}
    no_link_performer_rows = []
    for root in sorted(entrant_performers - linked_performers):
        ids = sorted(performer_ids[root])
        entrant_group_ids = sorted(set(ids) & entrant_ids)
        no_link_performer_rows.append({
            "performer_group_id": root,
            "entrant_wrestler_ids": ";".join(entrant_group_ids),
            "ring_names": ";".join(wrestler_by_id[x].get("ring_name", "") for x in entrant_group_ids),
            "real_names": ";".join(sorted({wrestler_by_id[x].get("real_name", "") for x in ids if wrestler_by_id[x].get("real_name", "")})),
            "entrant_rows": sum(1 for r in entrants if r["wrestler_id"] in entrant_group_ids),
            "review_status": "RESEARCH_NON_CHAMPION_OR_MISSING",
        })
    no_link_rows = []
    for wrestler_id in sorted(entrant_ids - set(linked_ids)):
        wrestler = wrestler_by_id[wrestler_id]
        no_link_rows.append({
            "wrestler_id": wrestler_id,
            "ring_name": wrestler.get("ring_name", ""),
            "real_name": wrestler.get("real_name", ""),
            "aliases_ring_names": wrestler.get("aliases_ring_names", ""),
            "entrant_rows": sum(1 for r in entrants if r["wrestler_id"] == wrestler_id),
            "review_status": "RESEARCH_NON_CHAMPION_OR_MISSING",
        })

    # For each unlinked Rumble wrestler, rank source-preserved champion labels
    # against every known alias. These are candidates only, never automatic
    # links; promotion-specific gimmicks and family names need research.
    champion_labels = sorted(unlinked_names)
    candidate_rows = []
    for row in no_link_rows:
        wrestler = wrestler_by_id[row["wrestler_id"]]
        wrestler_aliases = aliases(wrestler)
        scored = []
        for label in champion_labels:
            label_key = norm(label)
            if not label_key:
                continue
            score = max(
                (SequenceMatcher(None, alias, label_key).ratio() for alias in wrestler_aliases),
                default=0,
            )
            if score >= 0.55:
                scored.append((score, label, unlinked_names[label]))
        scored.sort(key=lambda item: (-item[0], -item[2], item[1]))
        candidate_rows.append({
            "wrestler_id": row["wrestler_id"],
            "ring_name": row["ring_name"],
            "top_unlinked_champion_candidates": ";".join(
                f"{label}|rows={count}|score={score:.3f}" for score, label, count in scored[:10]
            ),
        })

    ambiguous_alias_rows = []
    for alias, ids in sorted(alias_to_ids.items()):
        if len(ids) > 1:
            ambiguous_alias_rows.append({
                "normalized_alias": alias,
                "wrestler_ids": ";".join(sorted(ids)),
                "ring_names": ";".join(wrestler_by_id[x].get("ring_name", "") for x in sorted(ids)),
                "entrant_ids": ";".join(sorted(ids & entrant_ids)),
            })

    linked_to_nonentrant = []
    for wrestler_id, count in sorted(linked_ids.items()):
        if wrestler_id not in entrant_ids:
            linked_to_nonentrant.append({
                "wrestler_id": wrestler_id,
                "ring_name": wrestler_by_id.get(wrestler_id, {}).get("ring_name", ""),
                "linked_reign_rows": count,
                "review_status": "POSSIBLE_DUPLICATE_OR_NON_RUMBLE_MASTER_ROW",
            })

    write_csv("duplicate_identity_candidates.csv", list(duplicate_rows[0]) if duplicate_rows else ["match_basis"], duplicate_rows)
    write_csv("unlinked_champion_names.csv", list(unlinked_rows[0]) if unlinked_rows else ["champion_name"], unlinked_rows)
    write_csv("rumble_wrestlers_without_linked_reigns.csv", list(no_link_rows[0]) if no_link_rows else ["wrestler_id"], no_link_rows)
    write_csv("rumble_performers_without_linked_reigns.csv", list(no_link_performer_rows[0]) if no_link_performer_rows else ["performer_group_id"], no_link_performer_rows)
    write_csv("rumble_wrestler_unlinked_name_candidates.csv", list(candidate_rows[0]) if candidate_rows else ["wrestler_id"], candidate_rows)
    write_csv("ambiguous_aliases.csv", list(ambiguous_alias_rows[0]) if ambiguous_alias_rows else ["normalized_alias"], ambiguous_alias_rows)
    write_csv("reigns_linked_to_nonentrant_ids.csv", list(linked_to_nonentrant[0]) if linked_to_nonentrant else ["wrestler_id"], linked_to_nonentrant)

    summary = {
        "wrestler_master_rows": len(wrestlers),
        "distinct_rumble_entrant_ids": len(entrant_ids),
        "championship_reign_rows": sum(r.get("record_type") == "reign" for r in reigns),
        "linked_rumble_wrestler_ids": len(set(linked_ids) & entrant_ids),
        "rumble_wrestlers_without_linked_reigns": len(no_link_rows),
        "distinct_rumble_performers": len(entrant_performers),
        "rumble_performers_without_linked_reigns": len(no_link_performer_rows),
        "distinct_unlinked_champion_names": len(unlinked_rows),
        "unlinked_reign_rows": sum(unlinked_names.values()),
        "duplicate_identity_candidates": len(duplicate_rows),
        "ambiguous_normalized_aliases": len(ambiguous_alias_rows),
        "linked_nonentrant_master_ids": len(linked_to_nonentrant),
        "championships": len(championships),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
