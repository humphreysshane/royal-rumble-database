"""
Royal Rumble Database — schema v2.

Built around Shane's full spec: every table distinguishes CONFIRMED data
(directly supported by a cited source) from DERIVED data (calculated from
confirmed data, e.g. age from DOB) from UNKNOWN (no reliable source found
yet). Never invent a value to fill a cell — leave it blank and, if it
matters, log it in flags.csv.

STATUS VALUES (used in every *_status column):
  CONFIRMED    - directly stated by a cited source (source_ids populated)
  DERIVED      - calculated from other CONFIRMED/DERIVED fields
  PROBABLE     - stated by exactly one source, not yet independently
                 cross-checked against a second (this is where most of
                 Shane's original workbook data starts out — it's detailed
                 and was clearly carefully researched, but per his own
                 sourcing rules it isn't auto-trusted just because it's his)
  UNCERTAIN    - sources disagree, or the single source is weak/informal
  CONFLICTING  - two-plus reliable sources disagree; both are preserved,
                 see flags.csv
  UNKNOWN      - no reliable source found; field left blank on purpose
  N/A          - the field does not apply to this record

IDs:
  wrestler_id  -> slug of the ring name the person is most known by,
                  e.g. "bret-hart". Reused across every event.
  event_id     -> RR<year><M|W|G>, e.g. RR1988M (Men's), RR2018W (Women's),
                  RR2018G (Greatest Royal Rumble-style specials).
  source_id    -> S### referencing sources.csv.
"""

# ---------------------------------------------------------------------------
# Reference / registry tables
# ---------------------------------------------------------------------------

SOURCES_FIELDS = [
    "source_id", "source_name", "source_type", "url", "reliability_tier",
    "tier_label", "accessed_date", "notes",
]
# reliability_tier follows Shane's hierarchy (section 4 of the spec), 1 = highest:
# 1 WWE/official  2 official footage  3 WWE Network/Peacock footage
# 4 Cagematch  5 ProFightDB/IWD  6 WrestlingData  7 Wrestling Observer/reputable press
# 8 historical newspapers/magazines  9 contemporary wrestling publications
# 10 Wikipedia/reference sites  11 Shane's original research document  12 other reputable sites

FLAGS_FIELDS = [
    "flag_id", "event_id", "table", "record_id", "field", "issue_type",
    "description", "source_ids_involved", "status", "date_logged",
]
# issue_type: "conflicting_sources" | "unverified" | "needs_video_review" |
#             "needs_human_judgement" | "out_of_scope_no_tool"

# ---------------------------------------------------------------------------
# Core entity tables
# ---------------------------------------------------------------------------

WRESTLERS_FIELDS = [
    "wrestler_id", "ring_name", "real_name", "real_name_status", "gender",
    "dob", "dob_status", "deceased_date", "birthplace", "birthplace_status",
    "nationality", "ethnicity_heritage", "ethnicity_heritage_status", "debut_year_company", "hall_of_fame_year",
    "aliases_ring_names", "wrestling_style", "notes", "source_ids",
]

EVENTS_FIELDS = [
    "event_id", "event_name", "match_name", "match_type", "event_date",
    "venue", "city_region", "country", "attendance_official",
    "attendance_reported", "entry_interval_seconds", "entrant_count",
    "duration_total", "duration_status",
    "finish_type",
    "winner_id", "runner_up_id", "final_two_ids", "final_three_ids", "final_four_ids",
    "first_entrant_id", "second_entrant_id", "final_entrant_id",
    "first_elimination_id", "last_elimination_before_winner_id",
    "eliminations_count", "eliminators_count", "surprise_entrants_count",
    "champions_in_field_count", "hall_of_famers_in_field_count",
    "tag_teams_count", "factions_count",
    "commentary_team", "ring_announcer", "referees",
    "special_rules", "title_on_the_line", "championship_implications",
    "winners_reward", "historical_significance", "notes",
    "data_quality_status", "source_ids",
]

ENTRANTS_FIELDS = [
    "event_id", "wrestler_id", "match_id", "entry_number", "entry_number_status",
    "ring_name_at_time", "name_displayed_at_event",
    "prior_rumble_appearances_count", "rumble_appearance_no",
    "is_first_rumble_appearance", "previous_rumble_year", "previous_rumble_result",
    "previous_rumble_elimination_no", "is_rumble_debut", "is_company_debut",
    "company_debut_date", "is_returning_wrestler", "absence_length",
    "age_at_event", "age_status", "billed_height_m_at_event", "billed_weight_kg_at_event",
    "billed_from_at_event", "physical_status", "alignment", "alignment_status",
    "gimmick_at_event", "manager_at_event", "tag_team_name", "faction_stable",
    "current_champion_title", "championship_level", "championship_partner",
    "reign_number", "title_won_date", "days_into_reign_at_event",
    "title_defended_same_card", "title_lost_same_card",
    "elim_number", "elim_number_status", "eliminated_by_ids",
    "elimination_clock_time", "elimination_clock_seconds",
    "ring_time", "ring_time_seconds", "ring_time_status",
    "wrestlers_remaining_when_eliminated",
    "wrestlers_eliminated_count", "wrestlers_eliminated_ids",
    "solo_eliminations_count", "assisted_eliminations_count",
    "self_eliminated", "is_winner", "is_runner_up",
    "is_final_two", "is_final_three", "is_final_four",
    "surprise_entrant", "legend_returning", "celebrity_entrant",
    "non_full_time_wrestler", "wrestled_earlier_on_card",
    "was_hof_member_at_time",
    "promotion_at_event", "promotion_at_event_status",
    "wrestled_masked",
    "data_quality_status", "source_ids", "notes",
]

ELIMINATIONS_FIELDS = [
    "event_id", "order_in_match", "eliminated_wrestler_id",
    "eliminator_wrestler_id", "assisting_wrestler_ids",
    "entry_number_of_eliminated", "entry_number_of_eliminator",
    "elimination_clock_time", "elimination_clock_seconds",
    "elimination_type", "elimination_method", "location_side", "location_status",
    "is_solo", "is_shared", "is_accidental", "is_self_elimination",
    "is_storyline_related", "was_already_incapacitated", "is_disputed",
    "simultaneous_group_id", "data_quality_status", "source_ids", "notes",
]

TAG_TEAMS_FIELDS = [
    "event_id", "team_name", "member_wrestler_ids", "faction_stable", "manager",
    "official_team", "entered_consecutively", "cooperated_in_match",
    "eliminated_together_count", "fought_each_other", "were_allies",
    "were_tag_champions_at_time", "combined_eliminations",
    "data_quality_status", "source_ids",
]

# Family dynasties (2026-09-26, scaffolded for the external AI's research
# batch per ROYAL_RUMBLE_REMAINING_WORK_AUDIT_20260926.md Section 3). One
# row per documented family unit, not per pairwise relationship -- a
# three-generation family is one row with all member_wrestler_ids listed,
# not three separate rows. Deliberately wrestler-level, not
# event/appearance-level: a family relationship doesn't change per Rumble
# the way a tag-team pairing can.
FAMILIES_FIELDS = [
    "family_id", "family_name", "member_wrestler_ids", "relationship_type",
    "notes", "data_quality_status", "source_ids",
]

# Co-winner support (2026-09-23, per RR1994M -- Bret Hart and Lex Luger went
# over the top rope simultaneously and WWF announced both as winner live).
# events.csv:winner_id is a single wrestler_id and stays that way for every
# ordinary one-winner event; it is only EMPTY when events.csv:finish_type is
# explicitly "co_winners", in which case this table is the authoritative
# declared winner set. entrants.csv:is_winner=TRUE independently marks the
# same wrestlers (that's what career_stats.csv/records.csv/entry_number_stats
# already read, so both winners were always correctly credited a win --
# only the single-ID events.csv field and the validator's exactly-one-winner
# rule needed to catch up to that). validate_integrity.py requires this
# table's rows for an event to exactly match that event's is_winner=TRUE set,
# and requires the reverse: an event with rows here must be finish_type ==
# "co_winners", an event without rows here must not be.
EVENT_WINNERS_FIELDS = [
    "event_id", "wrestler_id", "data_quality_status", "source_ids", "notes",
]

OTHER_MATCHES_FIELDS = [
    "event_id", "wrestler_id", "match_number_on_card", "opponents",
    "partners", "match_type", "championship_match", "title_involved",
    "was_champion_entering", "result", "won_title", "lost_title",
    "match_duration", "position_on_card", "time_before_rumble",
    "data_quality_status", "source_ids", "notes",
]

SHOW_APPEARANCES_FIELDS = [
    "event_id", "person_id", "person_name", "role", "wrestlers_managed",
    "alignment", "title_involved", "notes", "data_quality_status", "source_ids",
]

NOTABLE_MOMENTS_FIELDS = [
    "moment_id", "event_id", "wrestler_ids_involved", "category", "title",
    "description", "data_quality_status", "source_ids", "notes",
]

# One raw observation per source/rater. Different scales are deliberately
# preserved rather than normalized or averaged together.
EVENT_RATINGS_FIELDS = [
    "rating_id", "event_id", "source_name", "rating_scale", "rating_value",
    "rating_type", "review_url", "rating_status", "source_ids", "notes",
]

# Career-spanning championship history. These tables are deliberately
# independent of entrants.csv:current_champion_title, which remains a
# point-in-time fact about the start of a particular Royal Rumble match.
PROMOTIONS_FIELDS = [
    "promotion_id", "promotion_name", "abbreviation", "country",
    "active_from", "active_to", "former_names", "official_url",
    "wikipedia_url", "data_quality_status", "source_ids", "notes",
]

CHAMPIONSHIPS_FIELDS = [
    "championship_id", "promotion_id", "championship_name",
    "championship_level", "division", "active_from", "active_to",
    "status", "predecessor_championship_ids", "successor_championship_ids",
    "official_history_url", "wikipedia_history_url",
    "data_quality_status", "source_ids", "notes",
]

# champion_name is the exact historical display name from the source.
# champion_wrestler_ids is an optional link to this project's wrestler
# registry; it may be blank when a champion never entered a Royal Rumble.
# record_type preserves vacancies/unifications rather than forcing them into
# a wrestler reign.
CHAMPIONSHIP_REIGNS_FIELDS = [
    "reign_id", "championship_id", "record_type", "champion_name",
    "champion_wrestler_ids", "reign_number", "won_date", "lost_date",
    "days_reported", "days_recognized_reported", "event_name", "location",
    "is_current", "notes", "data_quality_status", "source_ids",
]
# rating_type: "critic_review" | "fan_aggregate" | "match_rating"
# category (closed-ish vocabulary, extend as new kinds of finding turn up):
#   "record" | "milestone_first" | "notable_absence_or_substitution" |
#   "behind_the_scenes" | "storyline_moment" | "controversy" | "botch" |
#   "injury_or_incident" | "weapon_used" | "other"
# This table is for exactly the "weird and wonderful, doesn't reduce to a
# single leaderboard number" trivia Shane asked for -- see IDEAS.md's
# "exhaustive stats" brief. weapons_incidents.csv and a per-entrant
# promotion_at_event field remain separate, not-yet-built ideas for their
# own more structured kinds of finding (see IDEAS.md).

# ---------------------------------------------------------------------------
# Stubbed for future video-analysis work — schema exists, tables stay empty
# until a video/computer-vision tool is available. Every row would need a
# video_source, timestamp and human_verification_status per Shane's spec
# sections 12, 16, 20-22, 38.
# ---------------------------------------------------------------------------

ENTRANCES_FIELDS = [
    "event_id", "wrestler_id", "entry_number", "music_start_ts",
    "name_announced_ts", "countdown_ts", "first_movement_ts",
    "leaves_stage_ts", "reaches_ringside_ts", "enters_ring_ts",
    "entrance_duration_seconds", "posed", "ran", "walked",
    "special_entry_location", "entrance_interrupted",
    "video_source", "reviewer", "confidence", "human_verified",
]

MOVES_FIELDS = [
    "event_id", "timestamp", "wrestler_performing_id", "wrestler_receiving_id",
    "move_name", "move_category", "successful", "countered", "reversed",
    "knockdown", "elimination_attempt", "result",
    "video_source", "ai_model", "ai_confidence", "human_verified",
]

NEAR_ELIMINATIONS_FIELDS = [
    "event_id", "wrestler_id", "timestamp", "attempted_by_id",
    "how_survived", "apron_duration_seconds", "feet_touched_floor",
    "hands_touched_floor", "rope_grab", "pulled_back_in_by_id",
    "video_source", "reviewer", "confidence", "human_verified",
]

ELIMINATION_LOCATIONS_STUB_NOTE = (
    "Ring-side location of each elimination (left/right/hard-camera/corner) "
    "is captured directly on eliminations.csv (location_side, location_status) "
    "but left blank until footage review is done — see flags.csv."
)

TABLES = {
    "sources.csv": SOURCES_FIELDS,
    "flags.csv": FLAGS_FIELDS,
    "wrestlers.csv": WRESTLERS_FIELDS,
    "events.csv": EVENTS_FIELDS,
    "entrants.csv": ENTRANTS_FIELDS,
    "eliminations.csv": ELIMINATIONS_FIELDS,
    "tag_teams.csv": TAG_TEAMS_FIELDS,
    "families.csv": FAMILIES_FIELDS,
    "event_winners.csv": EVENT_WINNERS_FIELDS,
    "other_matches.csv": OTHER_MATCHES_FIELDS,
    "show_appearances.csv": SHOW_APPEARANCES_FIELDS,
    "notable_moments.csv": NOTABLE_MOMENTS_FIELDS,
    "event_ratings.csv": EVENT_RATINGS_FIELDS,
    "promotions.csv": PROMOTIONS_FIELDS,
    "championships.csv": CHAMPIONSHIPS_FIELDS,
    "championship_reigns.csv": CHAMPIONSHIP_REIGNS_FIELDS,
    "entrances.csv": ENTRANCES_FIELDS,
    "moves.csv": MOVES_FIELDS,
    "near_eliminations.csv": NEAR_ELIMINATIONS_FIELDS,
}

# Derived-only tables (not hand-populated; scripts/build_derived.py writes these)
#
# DIVISION SPLIT (2026-09-20): per Shane's instruction, Men's and Women's
# Royal Rumble stats/records must be kept "completely separate" throughout
# the derived layer and the dashboard. Division is derived per-event from
# events.csv:match_type ("Men's" / "Women's") and is never blended.
# wrestlers.csv itself stays a single shared identity table (one row per
# real performer, e.g. Beth Phoenix keeps one wrestler_id) — the split
# lives entirely in these computed tables, via a compound key that pairs
# the entity with its division. See IDEAS.md for the full write-up.
DERIVED_TABLES = {
    "career_stats.csv": [
        "wrestler_id", "division", "total_appearances", "first_rumble_year", "last_rumble_year",
        "wins", "runner_up_finishes", "final_four_count", "final_three_count",
        "final_two_count", "total_eliminations_made", "avg_eliminations_per_appearance",
        "max_eliminations_single_rumble", "total_ring_time_seconds",
        "avg_ring_time_seconds", "longest_single_appearance_seconds",
        "shortest_single_appearance_seconds", "avg_entry_number",
        "highest_entry_number", "lowest_entry_number",
        "times_entered_number_1", "times_entered_number_2", "times_entered_final_number",
        "elimination_percentage", "win_percentage", "final_four_percentage",
        "longest_consecutive_streak", "longest_gap_years",
        "distinct_eliminators_count", "most_frequent_eliminator_id",
        "distinct_wrestlers_eliminated_count", "most_frequently_eliminated_id",
        "most_frequent_tag_partner_id", "best_finish",
    ],
    "entry_number_stats.csv": [
        "division", "entry_number", "events_sample_size", "wins", "win_rate",
        "avg_survival_seconds", "median_survival_seconds", "avg_eliminations",
        "final_four_rate", "runner_up_count",
    ],
    "entry_number_bands.csv": [
        "division", "band", "band_range", "events_sample_size", "wins", "win_rate",
        "avg_survival_seconds", "avg_eliminations", "final_four_rate",
        "runner_up_count", "notes",
    ],
    "records.csv": [
        "record_id", "division", "category", "record_name", "holder_wrestler_id",
        "value", "event_id", "as_of_date", "notes",
    ],
    "records_history.csv": [
        "history_id", "division", "category", "record_name", "new_holder_wrestler_id",
        "new_value", "broke_event_id", "previous_holder_wrestler_id",
        "previous_value", "logged_date", "notes",
    ],
    "elimination_rivalries.csv": [
        "division", "eliminator_wrestler_id", "eliminated_wrestler_id", "times_eliminated",
        "first_event_id", "most_recent_event_id",
    ],
    "event_dynamic_stats.csv": [
        "event_id", "division", "as_of_date", "hof_members_at_time_count",
        "hof_members_eventually_count", "now_deceased_count",
        "future_world_champions_count", "combined_billed_weight_kg",
        "combined_age_final_four_years", "notes",
    ],
    "event_field_physical_stats.csv": [
        "event_id", "division", "actual_entrant_count",
        "billed_weight_count", "weight_coverage_percentage",
        "combined_billed_weight_kg", "average_billed_weight_kg",
        "billed_height_count", "height_coverage_percentage",
        "combined_billed_height_m", "average_billed_height_m",
        "data_quality_status", "notes",
    ],
    "ring_occupancy_stats.csv": [
        "event_id", "division", "peak_in_ring_count", "peak_start_seconds",
        "peak_end_seconds", "peak_start_time", "peak_end_time",
        "wrestler_ids_at_peak", "timed_entrant_count", "eligible_entrant_count",
        "coverage_percentage", "data_quality_status", "notes",
    ],
    "ring_crowdedness.csv": [
        "event_id", "division", "in_ring_count", "seconds_at_count",
        "time_at_count", "percentage_of_match_time", "total_match_seconds",
        "data_quality_status", "notes",
    ],
    "ring_physical_peaks.csv": [
        "event_id", "division", "metric", "peak_value", "unit",
        "peak_start_seconds", "peak_end_seconds", "peak_start_time",
        "peak_end_time", "wrestler_ids_at_peak", "timed_entrant_count",
        "eligible_entrant_count", "profiled_entrant_count",
        "profile_coverage_percentage", "data_quality_status", "notes",
    ],
    "entrance_event_stats.csv": [
        "event_id", "division", "entrance_rows_count", "timed_entrance_count",
        "median_entrance_duration_seconds", "median_entrance_duration",
        "average_entrance_duration_seconds", "shortest_entrance_seconds",
        "longest_entrance_seconds", "latest_physical_entry_seconds",
        "latest_physical_entry_time", "latest_physical_entry_wrestler_id",
        "advertised_interval_seconds", "interval_sample_size",
        "median_actual_interval_seconds", "largest_interval_variance_seconds",
        "largest_interval_variance_wrestler_id", "largest_interval_actual_seconds",
        "data_quality_status", "notes",
    ],
    "event_nationality_breakdown.csv": [
        "event_id", "division", "nationality", "entrant_count",
        "percentage_of_known", "known_nationality_count", "actual_entrant_count",
        "coverage_percentage", "data_quality_status", "notes",
    ],
}


def slugify(name):
    import re
    s = name.strip().lower()
    s = s.replace("'", "").replace(".", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def mmss_to_seconds(t):
    if not t or t in ("n/a", "N/A", ""):
        return ""
    parts = t.strip().split(":")
    parts = [int(p) for p in parts]
    if len(parts) == 2:
        m, s = parts
        return m * 60 + s
    if len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    return ""

# Legacy cleanup (2026-09-23): optional field-specific ID quality metadata.
# These are purely additive companion status columns -- when a *_ids field is
# blanked because it was holding a literal placeholder like "UNKNOWN" instead
# of a real reference, its status column records WHY it's blank rather than
# losing that information. Never a substitute for the event-wide
# data_quality_status; each field gets its own.
EVENTS_FIELDS.extend(['final_entrant_id_status', 'final_four_ids_status', 'final_three_ids_status', 'first_elimination_id_status', 'first_entrant_id_status', 'last_elimination_before_winner_id_status', 'runner_up_id_status', 'second_entrant_id_status'])
ENTRANTS_FIELDS.append("eliminated_by_ids_status")
