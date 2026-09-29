#!/usr/bin/env python3
"""Build a sourced, refreshable multi-promotion world-title history layer.

Wikipedia is used as the first structured observation source, not as a live
runtime dependency. Every run takes a dated snapshot into CSV, preserving the
source's wording and original reign-day values. Official histories can be
added as independent observations/cross-checks without replacing these rows.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

from schema import (
    CHAMPIONSHIPS_FIELDS,
    CHAMPIONSHIP_REIGNS_FIELDS,
    PROMOTIONS_FIELDS,
    SOURCES_FIELDS,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SNAPSHOT = ROOT / "research" / "championship_history_snapshot_20260928.json"
ACCESSED = "2026-09-29"
USER_AGENT = "RoyalRumbleResearch/1.0 (historical statistics project)"


PROMOTIONS = [
    ("wwe", "World Wrestling Entertainment", "WWE", "United States", "1953", "", "Capitol Wrestling Corporation;World Wide Wrestling Federation;World Wrestling Federation", "https://www.wwe.com/", "https://en.wikipedia.org/wiki/WWE"),
    ("wcw", "World Championship Wrestling", "WCW", "United States", "1988", "2001", "", "", "https://en.wikipedia.org/wiki/World_Championship_Wrestling"),
    ("ecw", "Extreme Championship Wrestling", "ECW", "United States", "1992", "2001", "Eastern Championship Wrestling", "", "https://en.wikipedia.org/wiki/Extreme_Championship_Wrestling"),
    ("aew", "All Elite Wrestling", "AEW", "United States", "2019", "", "", "https://www.allelitewrestling.com/", "https://en.wikipedia.org/wiki/All_Elite_Wrestling"),
    ("tna", "Total Nonstop Action Wrestling", "TNA", "United States", "2002", "", "Impact Wrestling", "https://tnawrestling.com/", "https://en.wikipedia.org/wiki/Total_Nonstop_Action_Wrestling"),
    ("roh", "Ring of Honor", "ROH", "United States", "2002", "", "", "https://www.ringofhonor.com/", "https://en.wikipedia.org/wiki/Ring_of_Honor"),
    ("njpw", "New Japan Pro-Wrestling", "NJPW", "Japan", "1972", "", "", "https://www.njpw1972.com/", "https://en.wikipedia.org/wiki/New_Japan_Pro-Wrestling"),
    ("nwa", "National Wrestling Alliance", "NWA", "United States", "1948", "", "", "https://www.nationalwrestlingalliance.com/", "https://en.wikipedia.org/wiki/National_Wrestling_Alliance"),
    ("awa", "American Wrestling Association", "AWA", "United States", "1960", "1991", "", "", "https://en.wikipedia.org/wiki/American_Wrestling_Association"),
    ("ajpw", "All Japan Pro Wrestling", "AJPW", "Japan", "1972", "", "", "https://www.all-japan.co.jp/", "https://en.wikipedia.org/wiki/All_Japan_Pro_Wrestling"),
    ("noah", "Pro Wrestling Noah", "NOAH", "Japan", "2000", "", "", "https://www.noah.co.jp/", "https://en.wikipedia.org/wiki/Pro_Wrestling_Noah"),
    ("stardom", "World Wonder Ring Stardom", "Stardom", "Japan", "2010", "", "", "https://wwr-stardom.com/", "https://en.wikipedia.org/wiki/World_Wonder_Ring_Stardom"),
    ("aaa", "Lucha Libre AAA Worldwide", "AAA", "Mexico", "1992", "", "Asistencia Asesoría y Administración", "https://www.luchalibreaaa.com/", "https://en.wikipedia.org/wiki/Lucha_Libre_AAA_Worldwide"),
    ("cmll", "Consejo Mundial de Lucha Libre", "CMLL", "Mexico", "1933", "", "Empresa Mexicana de Lucha Libre", "https://cmll.com/", "https://en.wikipedia.org/wiki/Consejo_Mundial_de_Lucha_Libre"),
    ("mlw", "Major League Wrestling", "MLW", "United States", "2002", "", "", "https://mlw.com/", "https://en.wikipedia.org/wiki/Major_League_Wrestling"),
    ("lucha-underground", "Lucha Underground", "LU", "United States", "2014", "2018", "", "", "https://en.wikipedia.org/wiki/Lucha_Underground"),
    ("wwc", "World Wrestling Council", "WWC", "Puerto Rico", "1973", "", "Capitol Sports Promotions", "https://www.superestrellaswwc.com/", "https://en.wikipedia.org/wiki/World_Wrestling_Council"),
    ("ovw", "Ohio Valley Wrestling", "OVW", "United States", "1993", "", "", "https://ovwrestling.com/", "https://en.wikipedia.org/wiki/Ohio_Valley_Wrestling"),
    ("fcw", "Florida Championship Wrestling", "FCW", "United States", "2007", "2012", "", "", "https://en.wikipedia.org/wiki/Florida_Championship_Wrestling"),
]


# One complete world-title lineage per configured page. The two WWE world
# titles are separate legal lineages, as are WCW and WWE despite later
# ownership/unification storylines.
TITLES = [
    ("wwe-championship", "wwe", "WWE Championship", "World", "Open", "1963", "", "active", "", "", "https://www.wwe.com/classics/titlehistory/wwe-world-heavyweight-championship", "List_of_WWE_Champions"),
    ("wwe-world-heavyweight-2002", "wwe", "World Heavyweight Championship (2002–2013)", "World", "Men's", "2002", "2013", "retired", "", "wwe-championship", "https://www.wwe.com/titlehistory/world-heavyweight-championship", "List_of_World_Heavyweight_Champions_(WWE,_2002%E2%80%932013)"),
    ("wcw-world-heavyweight", "wcw", "WCW World Heavyweight Championship", "World", "Men's", "1991", "2001", "retired", "", "wwe-championship", "", "List_of_WCW_World_Heavyweight_Champions"),
    ("ecw-world-heavyweight", "ecw", "ECW World Heavyweight Championship", "World", "Men's", "1992", "2010", "retired", "", "", "", "List_of_ECW_World_Heavyweight_Champions"),
    ("aew-world", "aew", "AEW World Championship", "World", "Men's", "2019", "", "active", "", "", "https://www.allelitewrestling.com/aew-world-championship-history", "List_of_AEW_World_Champions"),
    ("tna-world", "tna", "TNA World Championship", "World", "Men's", "2007", "", "active", "", "", "https://tnawrestling.com/champions/", "List_of_TNA_World_Champions"),
    ("roh-world", "roh", "ROH World Championship", "World", "Men's", "2002", "", "active", "", "", "", "List_of_ROH_World_Champions"),
    ("iwgp-heavyweight", "njpw", "IWGP Heavyweight / World Heavyweight Championship", "World", "Men's", "1987", "", "active", "", "", "", "List_of_IWGP_Heavyweight_Champions"),
    ("nwa-worlds-heavyweight", "nwa", "NWA Worlds Heavyweight Championship", "World", "Men's", "1948", "", "active", "", "", "", "List_of_NWA_World_Heavyweight_Champions"),
    ("awa-world-heavyweight", "awa", "AWA World Heavyweight Championship", "World", "Men's", "1960", "1991", "retired", "", "", "", "List_of_AWA_World_Heavyweight_Champions"),
    ("wwe-womens-1956", "wwe", "WWE Women's Championship (1956–2010)", "World", "Women's", "1956", "2010", "retired", "", "", "https://www.wwe.com/titlehistory/wwe-womens-championship", "List_of_WWE_Women%27s_Champions_(1956%E2%80%932010)"),
    ("wwe-womens", "wwe", "WWE Women's Championship", "World", "Women's", "2016", "", "active", "", "", "https://www.wwe.com/titlehistory/wwe-womens-championship", "List_of_WWE_Women%27s_Champions"),
    ("wwe-womens-world", "wwe", "Women's World Championship", "World", "Women's", "2016", "", "active", "", "", "https://www.wwe.com/titlehistory/womens-world-championship", "List_of_Women%27s_World_Champions_(WWE)"),
    ("aew-womens-world", "aew", "AEW Women's World Championship", "World", "Women's", "2019", "", "active", "", "", "https://www.allelitewrestling.com/aew-womens-championship-history", "List_of_AEW_Women%27s_World_Champions"),
    ("tna-knockouts-world", "tna", "TNA Knockouts World Championship", "World", "Women's", "2007", "", "active", "", "", "https://tnawrestling.com/champions/", "List_of_TNA_Knockouts_World_Champions"),
    ("roh-womens-world", "roh", "ROH Women's World Championship", "World", "Women's", "2021", "", "active", "", "", "", "List_of_ROH_Women%27s_World_Champions"),
    ("nwa-world-womens", "nwa", "NWA World Women's Championship", "World", "Women's", "1954", "", "active", "", "", "", "List_of_NWA_World_Women%27s_Champions"),
    ("iwgp-womens", "njpw", "IWGP Women's Championship", "World", "Women's", "2022", "", "active", "", "", "https://www.njpw1972.com/champions/iwgp-womens", "List_of_IWGP_Women%27s_Champions"),
]

# Every additional championship for which a structured, dated lineage table
# exists in the selected multi-promotion scope. Dates may stay blank where the
# lineage table, rather than a separately researched registry fact, is the
# source of truth; no approximate founding/retirement date is invented.
TITLES += [
    # WWE main roster and historical singles/tag titles
    ("wwe-intercontinental", "wwe", "WWE Intercontinental Championship", "Secondary", "Men's", "", "", "active", "", "", "https://www.wwe.com/titlehistory/intercontinental-championship", "List_of_WWE_Intercontinental_Champions"),
    ("wwe-united-states", "wwe", "WWE United States Championship", "Secondary", "Men's", "", "", "active", "", "", "https://www.wwe.com/titlehistory/united-states-championship", "List_of_WWE_United_States_Champions"),
    ("wwe-european", "wwe", "WWE European Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "List_of_WWE_European_Champions"),
    ("wwe-hardcore", "wwe", "WWE Hardcore Championship", "Specialty", "Open", "", "", "retired", "", "", "", "List_of_WWE_Hardcore_Champions"),
    ("wwe-24-7", "wwe", "WWE 24/7 Championship", "Specialty", "Open", "", "", "retired", "", "", "https://www.wwe.com/titlehistory/24-7-championship", "List_of_WWE_24%2F7_Champions"),
    ("wwf-light-heavyweight", "wwe", "WWF Light Heavyweight Championship (UWA/MPW/NJPW recognition)", "Weight class", "Men's", "1981", "1997", "retired", "", "wwf-light-heavyweight-1997", "", "List_of_WWF_Light_Heavyweight_Champions"),
    ("wwf-light-heavyweight-1997", "wwe", "WWF Light Heavyweight Championship (WWF recognition, 1997–2001)", "Weight class", "Men's", "1997", "2001", "retired", "wwf-light-heavyweight", "wwe-cruiserweight-1996", "", "List_of_WWF_Light_Heavyweight_Champions::WWF"),
    ("wwe-cruiserweight-1996", "wwe", "WWE Cruiserweight Championship (1996–2007)", "Weight class", "Open", "", "", "retired", "", "", "", "List_of_WWE_Cruiserweight_Champions_(1996%E2%80%932007)"),
    ("wwe-divas", "wwe", "WWE Divas Championship", "World", "Women's", "", "", "retired", "", "wwe-womens", "", "List_of_WWE_Divas_Champions"),
    ("wwe-world-tag", "wwe", "World Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "https://www.wwe.com/titlehistory/raw-tag-team-championship", "List_of_World_Tag_Team_Champions_(WWE)"),
    ("wwe-world-tag-1971", "wwe", "World Tag Team Championship (1971–2010)", "Tag team", "Men's", "1971-06-03", "2010-08-16", "retired", "", "wwe-world-tag", "https://www.wwe.com/titlehistory/world-tag-team-championship", "List_of_World_Tag_Team_Champions_(WWE,_1971%E2%80%932010)"),
    ("wwe-tag", "wwe", "WWE Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "https://www.wwe.com/titlehistory/smackdown-tag-team-championship", "List_of_WWE_Tag_Team_Champions"),
    ("wwe-womens-tag", "wwe", "WWE Women's Tag Team Championship", "Tag team", "Women's", "", "", "active", "", "", "https://www.wwe.com/titlehistory/wwe-womens-tag-team-championship", "List_of_WWE_Women%27s_Tag_Team_Champions"),
    ("wwf-womens-tag-1983", "wwe", "WWF Women's Tag Team Championship (1983–1989)", "Tag team", "Women's", "1983", "1989", "retired", "", "", "", "WWF_Women%27s_Tag_Team_Championship"),
    ("million-dollar", "wwe", "Million Dollar Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "List_of_Million_Dollar_Champions"),
    ("wwe-speed", "wwe", "WWE Speed Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "List_of_WWE_Speed_Champions"),
    ("wwe-womens-speed", "wwe", "WWE Women's Speed Championship", "Specialty", "Women's", "", "", "retired", "", "", "", "List_of_WWE_Women%27s_Speed_Champions"),
    ("wwe-womens-intercontinental", "wwe", "WWE Women's Intercontinental Championship", "Secondary", "Women's", "", "", "active", "", "", "", "List_of_WWE_Women%27s_Intercontinental_Champions"),
    ("wwe-womens-united-states", "wwe", "WWE Women's United States Championship", "Secondary", "Women's", "", "", "active", "", "", "", "List_of_WWE_Women%27s_United_States_Champions"),

    # NXT and NXT UK
    ("nxt-championship", "wwe", "NXT Championship", "World", "Men's", "", "", "active", "", "", "", "List_of_NXT_Champions"),
    ("nxt-womens", "wwe", "NXT Women's Championship", "World", "Women's", "", "", "active", "", "", "", "List_of_NXT_Women%27s_Champions"),
    ("nxt-tag", "wwe", "NXT Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "List_of_NXT_Tag_Team_Champions"),
    ("nxt-north-american", "wwe", "NXT North American Championship", "Secondary", "Men's", "", "", "active", "", "", "", "List_of_NXT_North_American_Champions"),
    ("nxt-womens-north-american", "wwe", "NXT Women's North American Championship", "Secondary", "Women's", "2024", "", "active", "", "", "", "NXT_Women%27s_North_American_Championship"),
    ("nxt-womens-tag", "wwe", "NXT Women's Tag Team Championship", "Tag team", "Women's", "2021", "2023", "retired", "", "wwe-womens-tag", "", "NXT_Women%27s_Tag_Team_Championship"),
    ("nxt-heritage-cup", "wwe", "NXT Heritage Cup", "Specialty", "Men's", "2020", "2025", "retired", "", "", "https://www.wwe.com/titlehistory/nxt-heritage-cup", "NXT_Heritage_Cup"),
    ("nxt-united-kingdom", "wwe", "NXT United Kingdom Championship", "World", "Men's", "", "", "retired", "", "nxt-championship", "", "List_of_NXT_United_Kingdom_Champions"),
    ("nxt-uk-womens", "wwe", "NXT UK Women's Championship", "World", "Women's", "", "", "retired", "", "nxt-womens", "", "List_of_NXT_UK_Women%27s_Champions"),
    ("nxt-uk-tag", "wwe", "NXT UK Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "nxt-tag", "", "List_of_NXT_UK_Tag_Team_Champions"),
    ("nxt-cruiserweight", "wwe", "NXT Cruiserweight Championship", "Weight class", "Men's", "", "", "retired", "", "nxt-north-american", "", "List_of_NXT_Cruiserweight_Champions"),

    # WCW and ECW
    ("wcw-world-television", "wcw", "WCW World Television Championship", "Television", "Men's", "", "", "retired", "", "", "", "List_of_WCW_World_Television_Champions"),
    ("wcw-hardcore", "wcw", "WCW Hardcore Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "List_of_WCW_Hardcore_Champions"),
    ("wcw-world-tag", "wcw", "WCW World Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "List_of_WCW_World_Tag_Team_Champions"),
    ("ecw-world-television", "ecw", "ECW World Television Championship", "Television", "Men's", "", "", "retired", "", "", "", "List_of_ECW_World_Television_Champions"),
    ("ecw-world-tag", "ecw", "ECW World Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "List_of_ECW_World_Tag_Team_Champions"),

    # AEW
    ("aew-international", "aew", "AEW International Championship", "Secondary", "Men's", "", "", "active", "", "", "", "List_of_AEW_International_Champions"),
    ("aew-tnt", "aew", "AEW TNT Championship", "Television", "Men's", "", "", "active", "", "", "", "List_of_AEW_TNT_Champions"),
    ("aew-tbs", "aew", "AEW TBS Championship", "Television", "Women's", "", "", "active", "", "", "", "List_of_AEW_TBS_Champions"),
    ("aew-continental", "aew", "AEW Continental Championship", "Secondary", "Men's", "", "", "active", "", "", "", "List_of_AEW_Continental_Champions"),
    ("aew-world-tag", "aew", "AEW World Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "List_of_AEW_World_Tag_Team_Champions"),
    ("aew-world-trios", "aew", "AEW World Trios Championship", "Trios", "Open", "", "", "active", "", "", "", "List_of_AEW_World_Trios_Champions"),

    # TNA / Impact
    ("tna-x-division", "tna", "TNA X Division Championship", "X Division", "Open", "", "", "active", "", "", "", "List_of_TNA_X_Division_Champions"),
    ("tna-television", "tna", "TNA Television Championship", "Television", "Men's", "", "", "retired", "", "", "", "List_of_TNA_Television_Champions"),
    ("tna-world-tag", "tna", "TNA World Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "List_of_TNA_World_Tag_Team_Champions"),
    ("tna-knockouts-tag", "tna", "TNA Knockouts World Tag Team Championship", "Tag team", "Women's", "", "", "active", "", "", "", "List_of_TNA_Knockouts_World_Tag_Team_Champions"),
    ("tna-digital-media", "tna", "TNA Digital Media Championship", "Secondary", "Open", "", "", "retired", "", "", "", "List_of_TNA_Digital_Media_Champions"),

    # ROH
    ("roh-world-tag", "roh", "ROH World Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "List_of_ROH_World_Tag_Team_Champions"),
    ("roh-six-man", "roh", "ROH World Six-Man Tag Team Championship", "Trios", "Men's", "", "", "retired", "", "", "", "List_of_ROH_World_Six-Man_Tag_Team_Champions"),
    ("roh-pure", "roh", "ROH Pure Championship", "Specialty", "Men's", "", "", "active", "", "", "", "List_of_ROH_Pure_Champions"),
    ("roh-world-television", "roh", "ROH World Television Championship", "Television", "Men's", "", "", "active", "", "", "", "List_of_ROH_World_Television_Champions"),
    ("roh-womens-television", "roh", "ROH Women's World Television Championship", "Television", "Women's", "", "", "active", "", "", "", "List_of_ROH_Women%27s_World_Television_Champions"),
    ("roh-womens-pure", "roh", "ROH Women's Pure Championship", "Specialty", "Women's", "", "", "active", "", "", "", "List_of_ROH_Women%27s_Pure_Champions"),

    # NJPW, NEVER and Strong
    ("iwgp-tag", "njpw", "IWGP Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "List_of_IWGP_Tag_Team_Champions"),
    ("iwgp-junior-heavyweight", "njpw", "IWGP Junior Heavyweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "List_of_IWGP_Junior_Heavyweight_Champions"),
    ("iwgp-junior-tag", "njpw", "IWGP Junior Heavyweight Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "List_of_IWGP_Junior_Heavyweight_Tag_Team_Champions"),
    ("iwgp-intercontinental", "njpw", "IWGP Intercontinental Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "List_of_IWGP_Intercontinental_Champions"),
    ("iwgp-us-heavyweight", "njpw", "IWGP United States Heavyweight Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "List_of_IWGP_United_States_Heavyweight_Champions"),
    ("never-openweight", "njpw", "NEVER Openweight Championship", "Openweight", "Open", "", "", "active", "", "", "", "List_of_NEVER_Openweight_Champions"),
    ("never-six-man", "njpw", "NEVER Openweight 6-Man Tag Team Championship", "Trios", "Open", "", "", "active", "", "", "", "List_of_NEVER_Openweight_6-Man_Tag_Team_Champions"),
    ("njpw-world-television", "njpw", "NJPW World Television Championship", "Television", "Men's", "", "", "active", "", "", "", "List_of_NJPW_World_Television_Champions"),
    ("strong-womens", "njpw", "Strong Women's Championship", "World", "Women's", "", "", "active", "", "", "", "List_of_Strong_Women%27s_Champions"),

    # NWA and AWA structured lineages
    ("nwa-world-tag", "nwa", "NWA World Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "List_of_NWA_World_Tag_Team_Champions"),
    ("nwa-world-womens-tag", "nwa", "NWA World Women's Tag Team Championship", "Tag team", "Women's", "", "", "active", "", "", "", "List_of_NWA_World_Women%27s_Tag_Team_Champions"),
    ("nwa-world-womens-television", "nwa", "NWA World Women's Television Championship", "Television", "Women's", "", "", "active", "", "", "", "List_of_NWA_World_Women%27s_Television_Champions"),
    ("awa-world-tag", "awa", "AWA World Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "List_of_AWA_World_Tag_Team_Champions"),

    # Histories embedded directly in championship articles rather than a
    # separate "List of ... Champions" article.
    ("wwe-universal", "wwe", "WWE Universal Championship", "World", "Men's", "", "", "retired", "", "wwe-championship", "https://www.wwe.com/titlehistory/universal-championship", "WWE_Universal_Championship"),
    ("wwe-world-heavyweight-current", "wwe", "World Heavyweight Championship", "World", "Men's", "", "", "active", "", "", "https://www.wwe.com/titlehistory/world-heavyweight-championship", "World_Heavyweight_Championship_(WWE)"),
    ("wwe-evolve", "wwe", "WWE Evolve Championship", "World", "Men's", "", "", "active", "", "", "", "WWE_Evolve_Championship"),
    ("wwe-evolve-womens", "wwe", "WWE Evolve Women's Championship", "World", "Women's", "", "", "active", "", "", "", "WWE_Evolve_Women%27s_Championship"),
    ("aew-national", "aew", "AEW National Championship", "Secondary", "Men's", "", "", "active", "", "", "", "AEW_National_Championship"),
    ("aew-unified", "aew", "AEW Unified Championship", "Secondary", "Men's", "", "", "active", "", "", "", "AEW_Unified_Championship"),
    ("aew-womens-tag", "aew", "AEW Women's World Tag Team Championship", "Tag team", "Women's", "", "", "active", "", "", "", "AEW_Women%27s_World_Tag_Team_Championship"),
    ("iwgp-global-heavyweight", "njpw", "IWGP Global Heavyweight Championship", "Secondary", "Men's", "", "", "active", "", "", "", "IWGP_Global_Heavyweight_Championship"),
    ("strong-openweight", "njpw", "NJPW Strong Openweight Championship", "Openweight", "Open", "", "", "active", "", "", "", "NJPW_Strong_Openweight_Championship"),
    ("strong-openweight-tag", "njpw", "Strong Openweight Tag Team Championship", "Tag team", "Open", "", "", "active", "", "", "", "Strong_Openweight_Tag_Team_Championship"),
    ("kopw", "njpw", "KOPW Championship", "Specialty", "Open", "", "", "active", "", "", "", "KOPW_(professional_wrestling_championship)"),
    ("nwa-national", "nwa", "NWA National Championship", "Secondary", "Men's", "", "", "active", "", "", "", "NWA_National_Championship"),
    ("nwa-world-junior-heavyweight", "nwa", "NWA World Junior Heavyweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "NWA_World_Junior_Heavyweight_Championship"),
    ("nwa-world-television-current", "nwa", "NWA World Television Championship", "Television", "Men's", "", "", "active", "", "", "", "NWA_World_Television_Championship"),
    ("awa-world-womens", "awa", "AWA World Women's Championship", "World", "Women's", "", "", "retired", "", "", "", "AWA_World_Women%27s_Championship"),
    ("awa-world-light-heavyweight", "awa", "AWA World Light Heavyweight Championship", "Weight class", "Men's", "", "", "retired", "", "", "", "AWA_World_Light_Heavyweight_Championship"),
    ("awa-international-television", "awa", "AWA International Television Championship", "Television", "Men's", "", "", "retired", "", "", "", "AWA_International_Television_Championship"),
    ("wcw-international-world-heavyweight", "wcw", "WCW International World Heavyweight Championship", "World", "Men's", "", "", "retired", "", "wcw-world-heavyweight", "", "WCW_International_World_Heavyweight_Championship"),
    ("wcw-cruiserweight-tag", "wcw", "WCW Cruiserweight Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "WCW_Cruiserweight_Tag_Team_Championship"),
    ("wcw-united-states-tag", "wcw", "WCW United States Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "WCW_United_States_Tag_Team_Championship"),
    ("wcw-world-six-man-tag", "wcw", "WCW World Six-Man Tag Team Championship", "Trios", "Men's", "", "", "retired", "", "", "", "WCW_World_Six-Man_Tag_Team_Championship"),

    # Remaining promotion-native and historically adopted lineages with
    # structured tables. This includes predecessor belts later carried by a
    # covered promotion; the source notes retain the exact historical context.
    ("wwf-international-heavyweight", "wwe", "WWF International Heavyweight Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "WWF_International_Heavyweight_Championship"),
    ("wwf-canadian", "wwe", "WWF Canadian Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "WWF_Canadian_Championship"),
    ("wwf-junior-heavyweight", "wwe", "WWF Junior Heavyweight Championship", "Weight class", "Men's", "", "", "retired", "", "", "", "WWF_Junior_Heavyweight_Championship"),
    ("wwf-north-american-heavyweight", "wwe", "WWF North American Heavyweight Championship", "Secondary", "Men's", "", "", "retired", "", "wwe-intercontinental", "", "WWF_North_American_Heavyweight_Championship"),
    ("wwf-world-martial-arts", "wwe", "WWF World Martial Arts Heavyweight Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "WWF_World_Martial_Arts_Heavyweight_Championship"),
    ("wwwf-united-states-heavyweight", "wwe", "WWWF United States Heavyweight Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "WWWF_United_States_Heavyweight_Championship"),
    ("wwe-id", "wwe", "WWE ID Championship", "Developmental", "Open", "", "", "active", "", "", "", "WWE_ID_Championship"),

    ("wcw-light-heavyweight", "wcw", "WCW Light Heavyweight Championship", "Weight class", "Men's", "", "", "retired", "", "", "", "WCW_Light_Heavyweight_Championship"),
    ("wcw-womens", "wcw", "WCW Women's Championship", "World", "Women's", "", "", "retired", "", "", "", "WCW_Women%27s_Championship"),
    ("wcw-womens-cruiserweight", "wcw", "WCW Women's Cruiserweight Championship", "Weight class", "Women's", "", "", "retired", "", "", "", "WCW_Women%27s_Cruiserweight_Championship"),
    ("nwa-western-states-heritage", "wcw", "NWA Western States Heritage Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "NWA_Western_States_Heritage_Championship"),

    ("ecw-maryland", "ecw", "ECW Maryland Championship", "Regional", "Men's", "", "", "retired", "", "", "", "ECW_Maryland_Championship"),
    ("ecw-pennsylvania", "ecw", "ECW Pennsylvania Championship", "Regional", "Men's", "", "", "retired", "", "", "", "ECW_Pennsylvania_Championship"),
    ("ftw", "ecw", "FTW Championship", "Specialty", "Open", "", "", "retired", "", "", "", "FTW_Championship"),

    ("impact-grand", "tna", "Impact Grand Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "Impact_Grand_Championship"),
    ("tna-international", "tna", "TNA International Championship", "Secondary", "Men's", "", "", "active", "", "", "", "TNA_International_Championship"),
    ("tna-knockouts-television", "tna", "TNA Knockouts Television Championship", "Television", "Women's", "", "", "active", "", "", "", "TNA_Knockouts_Television_Championship"),
    ("tna-beer-drinking", "tna", "TNA World Beer Drinking Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "TNA_World_Beer_Drinking_Championship"),
    ("tna-world-heavyweight-2020", "tna", "TNA World Heavyweight Championship (2020–2021)", "World", "Men's", "", "", "retired", "", "tna-world", "", "TNA_World_Heavyweight_Championship_(2020%E2%80%932021)"),
    ("canadian-international-heavyweight", "tna", "Canadian International Heavyweight Championship", "Regional", "Men's", "", "", "retired", "", "", "", "Canadian_International_Heavyweight_Championship"),

    ("roh-top-class-trophy", "roh", "ROH Top of the Class Trophy Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "ROH_Top_of_the_Class_Trophy_Championship"),
    ("women-of-honor-world", "roh", "Women of Honor World Championship", "World", "Women's", "", "", "retired", "", "roh-womens-world", "", "Women_of_Honor_World_Championship"),

    ("asia-heavyweight", "njpw", "Asia Heavyweight Championship", "Regional", "Men's", "", "", "retired", "", "", "", "Asia_Heavyweight_Championship"),
    ("asia-tag", "njpw", "Asia Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "Asia_Tag_Team_Championship"),
    ("greatest-18-club", "njpw", "Greatest 18 Club Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "Greatest_18_Club_Championship"),
    ("iwgp-heavyweight-igf", "njpw", "IWGP Heavyweight Championship (IGF)", "World", "Men's", "", "", "retired", "", "", "", "IWGP_Heavyweight_Championship_(IGF)"),
    ("iwgp-heavyweight-original", "njpw", "IWGP Heavyweight Championship (original version)", "World", "Men's", "", "", "retired", "", "iwgp-heavyweight", "", "IWGP_Heavyweight_Championship_(original_version)"),
    ("iwgp-u30", "njpw", "IWGP U-30 Openweight Championship", "Openweight", "Open", "", "", "retired", "", "", "", "IWGP_U-30_Openweight_Championship"),
    ("j-crown", "njpw", "J-Crown", "Weight class", "Men's", "", "", "retired", "", "", "", "J-Crown"),
    ("nwf-heavyweight", "njpw", "NWF Heavyweight Championship", "World", "Men's", "", "", "retired", "", "", "", "NWF_Heavyweight_Championship"),
    ("nwf-north-american-heavyweight", "njpw", "NWF North American Heavyweight Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "NWF_North_American_Heavyweight_Championship"),
    ("real-world-championship", "njpw", "Real World Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "Real_World_Championship"),

    ("awa-americas", "awa", "AWA America's Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "AWA_America%27s_Championship"),
    ("awa-brass-knuckles", "awa", "AWA Brass Knuckles Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "AWA_Brass_Knuckles_Championship"),
    ("awa-british-empire-heavyweight", "awa", "AWA British Empire Heavyweight Championship", "Regional", "Men's", "", "", "retired", "", "", "", "AWA_British_Empire_Heavyweight_Championship"),
    ("awa-international-heavyweight", "awa", "AWA International Heavyweight Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "AWA_International_Heavyweight_Championship"),
    ("awa-midwest-heavyweight", "awa", "AWA Midwest Heavyweight Championship", "Regional", "Men's", "", "", "retired", "", "", "", "AWA_Midwest_Heavyweight_Championship"),
    ("awa-midwest-tag", "awa", "AWA Midwest Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "AWA_Midwest_Tag_Team_Championship"),
    ("awa-southern-heavyweight", "awa", "AWA Southern Heavyweight Championship", "Regional", "Men's", "", "", "retired", "", "", "", "AWA_Southern_Heavyweight_Championship"),
    ("awa-southern-tag", "awa", "AWA Southern Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "AWA_Southern_Tag_Team_Championship"),
    ("awa-united-states-heavyweight", "awa", "AWA United States Heavyweight Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "AWA_United_States_Heavyweight_Championship"),
    ("cwa-awa-international-tag", "awa", "CWA/AWA International Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "CWA%2FAWA_International_Tag_Team_Championship"),
    ("omaha-world-heavyweight", "awa", "World Heavyweight Championship (Omaha)", "World", "Men's", "", "", "retired", "", "", "", "World_Heavyweight_Championship_(Omaha)"),
    ("nwa-mid-america-heavyweight", "nwa", "NWA Mid-America Heavyweight Championship", "Regional", "Men's", "", "", "active", "", "", "", "NWA_Mid-America_Heavyweight_Championship"),
    ("nwa-us-tag-lightning-one", "nwa", "NWA United States Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "NWA_United_States_Tag_Team_Championship_(Lightning_One_version)"),
    ("british-commonwealth-junior-heavyweight", "njpw", "British Commonwealth Junior Heavyweight Championship", "Weight class", "Men's", "", "", "retired", "", "", "", "British_Commonwealth_Junior_Heavyweight_Championship"),
    ("nwa-international-junior-heavyweight", "njpw", "NWA International Junior Heavyweight Championship", "Weight class", "Men's", "", "", "retired", "", "", "", "NWA_International_Junior_Heavyweight_Championship"),
    ("nwa-north-american-tag-la-japan", "njpw", "NWA North American Tag Team Championship (Los Angeles/Japan)", "Tag team", "Men's", "", "", "retired", "", "", "", "NWA_North_American_Tag_Team_Championship_(Los_Angeles%2FJapan_version)"),
    ("nwa-world-welterweight", "njpw", "NWA World Welterweight Championship", "Weight class", "Men's", "", "", "retired", "", "", "", "NWA_World_Welterweight_Championship"),
    ("uwa-world-junior-light-heavyweight", "njpw", "UWA World Junior Light Heavyweight Championship", "Weight class", "Men's", "", "", "retired", "", "", "", "UWA_World_Junior_Light_Heavyweight_Championship"),
    ("wwf-international-tag", "njpw", "WWF International Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "WWF_International_Tag_Team_Championship"),
    ("nwa-world-six-man-tag", "wcw", "NWA World Six-Man Tag Team Championship", "Trios", "Men's", "", "", "retired", "", "", "", "NWA_World_Six-Man_Tag_Team_Championship"),
    ("nwa-us-television", "wwe", "NWA United States Television Championship", "Television", "Men's", "", "", "retired", "", "", "", "NWA_United_States_Television_Championship"),
    ("nwa-world-tag-minneapolis", "awa", "NWA World Tag Team Championship (Minneapolis)", "Tag team", "Men's", "", "", "retired", "", "awa-world-tag", "", "NWA_World_Tag_Team_Championship_(Minneapolis_version)"),
    ("wwwf-united-states-tag", "wwe", "WWWF United States Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "WWWF_United_States_Tag_Team_Championship"),

    # Additional major promotions represented in Royal Rumble entrants'
    # careers. Shared/sanctioned titles are stored once, under the promotion
    # most directly associated with the configured lineage page.
    ("ajpw-tv-six-man", "ajpw", "AJPW TV Six-Man Tag Team Championship", "Trios", "Men's", "", "", "active", "", "", "", "AJPW_TV_Six-Man_Tag_Team_Championship"),
    ("all-asia-heavyweight", "ajpw", "All Asia Heavyweight Championship", "Secondary", "Men's", "", "", "active", "", "", "", "All_Asia_Heavyweight_Championship"),
    ("all-asia-tag", "ajpw", "All Asia Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "All_Asia_Tag_Team_Championship"),
    ("f1-tag", "ajpw", "F-1 Tag Team Championship", "Tag team", "Open", "", "", "retired", "", "", "", "F-1_Tag_Team_Championship"),
    ("gaora-tv", "ajpw", "Gaora TV Championship", "Television", "Men's", "", "", "active", "", "", "", "Gaora_TV_Championship"),
    ("nwa-international-tag", "ajpw", "NWA International Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "ajpw-world-tag", "", "NWA_International_Tag_Team_Championship"),
    ("ajpw-triple-crown", "ajpw", "Triple Crown Heavyweight Championship", "World", "Men's", "", "", "active", "", "", "", "Triple_Crown_Heavyweight_Championship"),
    ("ajpw-world-junior", "ajpw", "World Junior Heavyweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "World_Junior_Heavyweight_Championship_(AJPW)"),
    ("ajpw-world-tag", "ajpw", "World Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "World_Tag_Team_Championship_(AJPW)"),
    ("nwa-international-heavyweight", "ajpw", "NWA International Heavyweight Championship", "World", "Men's", "", "", "retired", "", "ajpw-triple-crown", "", "NWA_International_Heavyweight_Championship"),
    ("nwa-united-national", "ajpw", "NWA United National Championship", "Secondary", "Men's", "", "", "retired", "", "ajpw-triple-crown", "", "NWA_United_National_Championship"),
    ("pwf-united-states-heavyweight", "ajpw", "PWF United States Heavyweight Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "PWF_United_States_Heavyweight_Championship"),
    ("pwf-world-heavyweight", "ajpw", "PWF World Heavyweight Championship", "World", "Men's", "", "", "retired", "", "ajpw-triple-crown", "", "PWF_World_Heavyweight_Championship"),

    ("ghc-heavyweight", "noah", "GHC Heavyweight Championship", "World", "Men's", "", "", "active", "", "", "", "GHC_Heavyweight_Championship"),
    ("ghc-junior-heavyweight", "noah", "GHC Junior Heavyweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "GHC_Junior_Heavyweight_Championship"),
    ("ghc-junior-tag", "noah", "GHC Junior Heavyweight Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "GHC_Junior_Heavyweight_Tag_Team_Championship"),
    ("ghc-national", "noah", "GHC National Championship", "Secondary", "Men's", "", "", "active", "", "", "", "GHC_National_Championship"),
    ("ghc-openweight-hardcore", "noah", "GHC Openweight Hardcore Championship", "Specialty", "Open", "", "", "retired", "", "", "", "GHC_Openweight_Hardcore_Championship"),
    ("ghc-tag", "noah", "GHC Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "GHC_Tag_Team_Championship"),
    ("ghc-womens", "noah", "GHC Women's Championship", "World", "Women's", "", "", "active", "", "", "", "GHC_Women%27s_Championship"),
    ("ghc-200", "noah", "GHC 200 Championship", "Specialty", "Open", "", "", "retired", "", "", "", "GHC_200_Championship"),

    ("artist-of-stardom", "stardom", "Artist of Stardom Championship", "Trios", "Women's", "", "", "active", "", "", "", "Artist_of_Stardom_Championship"),
    ("future-of-stardom", "stardom", "Future of Stardom Championship", "Developmental", "Women's", "", "", "active", "", "", "", "Future_of_Stardom_Championship"),
    ("goddesses-of-stardom", "stardom", "Goddesses of Stardom Championship", "Tag team", "Women's", "", "", "active", "", "", "", "Goddesses_of_Stardom_Championship"),
    ("high-speed", "stardom", "High Speed Championship", "Specialty", "Women's", "", "", "active", "", "", "", "High_Speed_Championship"),
    ("new-blood-tag", "stardom", "New Blood Tag Team Championship", "Tag team", "Women's", "", "", "active", "", "", "", "New_Blood_Tag_Team_Championship"),
    ("swa-world", "stardom", "SWA World Championship", "World", "Women's", "", "", "retired", "", "", "", "SWA_World_Championship"),
    ("wonder-of-stardom", "stardom", "Wonder of Stardom Championship", "Secondary", "Women's", "", "", "active", "", "", "", "Wonder_of_Stardom_Championship"),
    ("world-of-stardom", "stardom", "World of Stardom Championship", "World", "Women's", "", "", "active", "", "", "", "World_of_Stardom_Championship"),

    ("aaa-americas-heavyweight", "aaa", "AAA Americas Heavyweight Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "AAA_Americas_Heavyweight_Championship"),
    ("aaa-americas-trios", "aaa", "AAA Americas Trios Championship", "Trios", "Men's", "", "", "retired", "", "", "", "AAA_Americas_Trios_Championship"),
    ("aaa-campeon-de-campeones", "aaa", "AAA Campeón de Campeones Championship", "Specialty", "Men's", "", "", "retired", "", "", "", "AAA_Campe%C3%B3n_de_Campeones_Championship"),
    ("aaa-fusion", "aaa", "AAA Fusión Championship", "Secondary", "Open", "", "", "retired", "", "", "", "AAA_Fusi%C3%B3n_Championship"),
    ("aaa-latin-american", "aaa", "AAA Latin American Championship", "Secondary", "Men's", "", "", "active", "", "", "", "AAA_Latin_American_Championship"),
    ("aaa-mascot-tag", "aaa", "AAA Mascot Tag Team Championship", "Tag team", "Open", "", "", "retired", "", "", "", "AAA_Mascot_Tag_Team_Championship"),
    ("aaa-mega", "aaa", "AAA Mega Championship", "World", "Men's", "", "", "active", "", "", "", "AAA_Mega_Championship"),
    ("aaa-northern-tag", "aaa", "AAA Northern Tag Team Championship", "Tag team", "Men's", "", "", "retired", "", "", "", "AAA_Northern_Tag_Team_Championship"),
    ("aaa-reina-de-reinas", "aaa", "AAA Reina de Reinas Championship", "World", "Women's", "", "", "active", "", "", "", "AAA_Reina_de_Reinas_Championship"),
    ("aaa-world-cruiserweight", "aaa", "AAA World Cruiserweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "AAA_World_Cruiserweight_Championship"),
    ("aaa-world-mini-estrella", "aaa", "AAA World Mini-Estrella Championship", "Weight class", "Open", "", "", "active", "", "", "", "AAA_World_Mini-Estrella_Championship"),
    ("aaa-world-mixed-tag", "aaa", "AAA World Mixed Tag Team Championship", "Tag team", "Open", "", "", "active", "", "", "", "AAA_World_Mixed_Tag_Team_Championship"),
    ("aaa-world-tag", "aaa", "AAA World Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "AAA_World_Tag_Team_Championship"),
    ("aaa-world-trios", "aaa", "AAA World Trios Championship", "Trios", "Men's", "", "", "active", "", "", "", "AAA_World_Trios_Championship"),
    ("iwc-world-heavyweight", "aaa", "IWC World Heavyweight Championship", "World", "Men's", "", "", "retired", "", "", "", "IWC_World_Heavyweight_Championship"),
    ("mexican-national-atomicos", "aaa", "Mexican National Atómicos Championship", "Trios", "Open", "", "", "retired", "", "", "", "Mexican_National_At%C3%B3micos_Championship"),
    ("mexican-national-heavyweight", "aaa", "Mexican National Heavyweight Championship", "World", "Men's", "", "", "active", "", "", "", "Mexican_National_Heavyweight_Championship"),
    ("mexican-national-middleweight", "aaa", "Mexican National Middleweight Championship", "Weight class", "Men's", "", "", "retired", "", "", "", "Mexican_National_Middleweight_Championship"),
    ("mexican-national-mini-estrella", "aaa", "Mexican National Mini-Estrella Championship", "Weight class", "Open", "", "", "active", "", "", "", "Mexican_National_Mini-Estrella_Championship"),
    ("mexican-national-tag", "aaa", "Mexican National Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "Mexican_National_Tag_Team_Championship"),
    ("mexican-national-womens", "aaa", "Mexican National Women's Championship", "World", "Women's", "", "", "retired", "", "", "", "Mexican_National_Women%27s_Championship"),
    ("uwa-world-light-heavyweight", "aaa", "UWA World Light Heavyweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "UWA_World_Light_Heavyweight_Championship"),

    ("cmll-arena-coliseo-tag", "cmll", "CMLL Arena Coliseo Tag Team Championship", "Tag team", "Men's", "", "", "active", "", "", "", "CMLL_Arena_Coliseo_Tag_Team_Championship"),
    ("cmll-world-heavyweight", "cmll", "CMLL World Heavyweight Championship", "World", "Men's", "1991", "", "active", "", "", "", "List_of_CMLL_World_Heavyweight_Champions"),
    ("cmll-world-middleweight", "cmll", "CMLL World Middleweight Championship", "Weight class", "Men's", "1991", "", "active", "", "", "", "List_of_CMLL_World_Middleweight_Champions"),
    ("cmll-world-welterweight", "cmll", "CMLL World Welterweight Championship", "Weight class", "Men's", "1992", "", "active", "", "", "", "List_of_CMLL_World_Welterweight_Champions"),
    ("cmll-world-tag", "cmll", "CMLL World Tag Team Championship", "Tag team", "Men's", "1993", "", "active", "", "", "", "List_of_CMLL_World_Tag_Team_Champions"),
    ("cmll-world-trios", "cmll", "CMLL World Trios Championship", "Trios", "Men's", "1991", "", "active", "", "", "", "List_of_CMLL_World_Trios_Champions"),
    ("cmll-japan-womens", "cmll", "CMLL Japan Women's Championship", "World", "Women's", "", "", "retired", "", "", "", "CMLL_Japan_Women%27s_Championship"),
    ("cmll-world-lightweight", "cmll", "CMLL World Lightweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "CMLL_World_Lightweight_Championship"),
    ("cmll-world-micro-estrellas", "cmll", "CMLL World Micro-Estrellas Championship", "Weight class", "Open", "", "", "active", "", "", "", "CMLL_World_Micro-Estrellas_Championship"),
    ("cmll-world-mini-estrellas", "cmll", "CMLL World Mini-Estrellas Championship", "Weight class", "Open", "", "", "active", "", "", "", "CMLL_World_Mini-Estrellas_Championship"),
    ("cmll-world-womens", "cmll", "CMLL World Women's Championship", "World", "Women's", "", "", "active", "", "", "", "CMLL_World_Women%27s_Championship"),
    ("cmll-world-womens-tag", "cmll", "CMLL World Women's Tag Team Championship", "Tag team", "Women's", "", "", "active", "", "", "", "CMLL_World_Women%27s_Tag_Team_Championship"),
    ("cmll-reina-international", "cmll", "CMLL-Reina International Championship", "World", "Women's", "", "", "retired", "", "", "", "CMLL-Reina_International_Championship"),
    ("cmll-reina-international-junior", "cmll", "CMLL-Reina International Junior Championship", "Weight class", "Women's", "", "", "retired", "", "", "", "CMLL-Reina_International_Junior_Championship"),
    ("lla-azteca", "cmll", "LLA Azteca Championship", "Secondary", "Men's", "", "", "retired", "", "", "", "LLA_Azteca_Championship"),
    ("mexican-national-lightweight", "cmll", "Mexican National Lightweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "Mexican_National_Lightweight_Championship"),
    ("mexican-national-welterweight", "cmll", "Mexican National Welterweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "Mexican_National_Welterweight_Championship"),
    ("nwa-historic-light-heavyweight", "cmll", "NWA World Historic Light Heavyweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "NWA_World_Historic_Light_Heavyweight_Championship"),
    ("nwa-historic-middleweight", "cmll", "NWA World Historic Middleweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "NWA_World_Historic_Middleweight_Championship"),
    ("nwa-historic-welterweight", "cmll", "NWA World Historic Welterweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "NWA_World_Historic_Welterweight_Championship"),
    ("nwa-world-light-heavyweight", "cmll", "NWA World Light Heavyweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "NWA_World_Light_Heavyweight_Championship"),
    ("nwa-world-middleweight", "cmll", "NWA World Middleweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "NWA_World_Middleweight_Championship"),
    ("occidente-heavyweight", "cmll", "Occidente Heavyweight Championship", "Regional", "Men's", "", "", "active", "", "", "", "Occidente_Heavyweight_Championship"),
    ("occidente-womens-tag", "cmll", "Occidente Women's Tag Team Championship", "Tag team", "Women's", "", "", "active", "", "", "", "Occidente_Women%27s_Tag_Team_Championship"),
    ("reina-world-tag", "cmll", "Reina World Tag Team Championship", "Tag team", "Women's", "", "", "retired", "", "", "", "Reina_World_Tag_Team_Championship"),

    ("iwa-pr-caribbean-heavyweight", "mlw", "IWA Puerto Rico/Caribbean Heavyweight Championship", "Regional", "Men's", "", "", "active", "", "", "", "IWA_Puerto_Rico%2FCaribbean_Heavyweight_Championship"),
    ("mlw-world-junior-heavyweight", "mlw", "MLW World Junior Heavyweight Championship", "Weight class", "Men's", "", "", "retired", "", "", "", "MLW_World_Junior_Heavyweight_Championship"),
    ("mlw-world-middleweight", "mlw", "MLW World Middleweight Championship", "Weight class", "Men's", "", "", "active", "", "", "", "MLW_World_Middleweight_Championship"),
    ("mlw-southern-crown", "mlw", "MLW Southern Crown Championship", "Regional", "Men's", "", "", "active", "", "", "", "MLW_Southern_Crown_Championship"),
    ("mlw-national-openweight", "mlw", "MLW National Openweight Championship", "Openweight", "Open", "", "", "active", "", "", "", "MLW_National_Openweight_Championship"),
    ("mlw-womens-featherweight", "mlw", "MLW World Women's Featherweight Championship", "World", "Women's", "", "", "active", "", "", "", "MLW_World_Women%27s_Featherweight_Championship"),
    ("mlw-world-heavyweight", "mlw", "MLW World Heavyweight Championship", "World", "Men's", "", "", "active", "", "", "", "MLW_World_Heavyweight_Championship"),

    ("lucha-underground", "lucha-underground", "Lucha Underground Championship", "World", "Open", "", "", "retired", "", "", "", "Lucha_Underground_Championship"),
    ("lucha-underground-gift-gods", "lucha-underground", "Lucha Underground Gift of the Gods Championship", "Specialty", "Open", "", "", "retired", "", "", "", "Lucha_Underground_Gift_of_the_Gods_Championship"),
    ("lucha-underground-trios", "lucha-underground", "Lucha Underground Trios Championship", "Trios", "Open", "", "", "retired", "", "", "", "Lucha_Underground_Trios_Championship"),

    # Puerto Rico and WWE developmental promotions represented by Rumble entrants
    ("wwc-universal-heavyweight", "wwc", "WWC Universal Heavyweight Championship", "World", "Men's", "1982", "", "active", "", "", "", "List_of_WWC_Universal_Heavyweight_Champions"),
    ("wwc-puerto-rico", "wwc", "WWC Puerto Rico Championship", "Regional", "Men's", "1974", "", "active", "", "", "", "WWC_Puerto_Rico_Championship"),
    ("wwc-world-tag", "wwc", "WWC World Tag Team Championship", "Tag team", "Men's", "1974", "", "active", "", "", "", "WWC_World_Tag_Team_Championship"),
    ("wwc-caribbean-heavyweight", "wwc", "WWC Caribbean Heavyweight Championship", "Regional", "Men's", "1975", "", "active", "", "", "", "WWC_Caribbean_Heavyweight_Championship"),
    ("ovw-heavyweight", "ovw", "OVW Heavyweight Championship", "World", "Men's", "1997", "", "active", "", "", "", "OVW_Heavyweight_Championship"),
    ("ovw-tag", "ovw", "OVW Tag Team Championship", "Tag team", "Men's", "1997", "", "active", "", "", "", "OVW_Tag_Team_Championship"),
    ("ovw-womens", "ovw", "OVW Women's Championship", "World", "Women's", "2006", "", "active", "", "", "", "OVW_Women%27s_Championship"),
    ("ovw-television", "ovw", "OVW Television Championship", "Television", "Open", "2005", "2019", "retired", "", "", "", "OVW_Television_Championship"),
    ("fcw-heavyweight", "fcw", "FCW Florida Heavyweight Championship", "World", "Men's", "2008", "2012", "retired", "", "nxt-championship", "", "FCW_Florida_Heavyweight_Championship"),
    ("fcw-tag", "fcw", "FCW Florida Tag Team Championship", "Tag team", "Men's", "2008", "2012", "retired", "", "nxt-tag", "", "FCW_Florida_Tag_Team_Championship"),
    ("fcw-divas", "fcw", "FCW Divas Championship", "World", "Women's", "2010", "2012", "retired", "", "nxt-womens", "", "FCW_Divas_Championship"),
]


MANUAL_ALIASES = {
    "a.j. styles": "aj-styles",
    "a.j styles": "aj-styles",
    "taz": "tazz",
    "koko ware": "koko-b-ware",
    "ron garvin": "ronnie-garvin",
    "christopher nowinski": "chris-nowinski",
    "psychosis": "psicosis",
    "brian kendrick": "the-brian-kendrick",
    "dory funk": "dory-funk-jr",
    "rene dupree": "renee-dupree",
    "yoshitatsu": "yoshi-tatsu",
    "sid vicious": "sid-justice",
    "sycho sid": "sid-justice",
    "justin credible": "aldo-montoya",
    "awesome kong": "kharma",
    "amazing kong": "kharma",
    "bryan clark": "adam-bomb",
    "wrath": "adam-bomb",
    "hugh morrus": "bill-demott",
    "general rection": "bill-demott",
    "general hugh g rection": "bill-demott",
    "gen rection": "bill-demott",
    "typhoon": "tugboat",
    "henry o godwinn": "henry-godwinn",
    "kenny": "kenny-dykstra",
    "nicky": "dolph-ziggler",
    "mike rotunda": "irwin-r-schyster",
    "mike rotundo": "irwin-r-schyster",
    "x pac": "1-2-3-kid",
    "syxx": "1-2-3-kid",
    "syxx pac": "1-2-3-kid",
    "hollywood hulk hogan": "hulk-hogan",
    "hollywood hogan": "hulk-hogan",
    "big van vader": "vader",
    "timeless toni storm": "toni-storm",
    "maria kanellis bennett": "maria-kanellis",
    "the texas tornado": "texas-tornado",
    "carlito caribbean cool": "carlito",
    "rey mysterio jr": "rey-mysterio",
    "chavo guerrero jr": "chavo-guerrero",
    "adrian neville": "neville",
    "the great kabuki": "great-kabuki",
    "fit finlay": "finlay",
    "tajiri": "yoshihiro-tajiri",
    "the fiend bray wyatt": "bray-wyatt",
    "hawk warrior": "hawk",
    "stone cold steve austin": "steve-austin",
    "steve austin": "steve-austin",
    "triple h": "hunter-hearst-helmsley",
    "mankind": "mick-foley",
    "cactus jack": "mick-foley",
    "the rock": "rocky-maivia",
    "the undertaker": "the-undertaker",
    "undertaker": "the-undertaker",
    "big show": "big-show",
    "the big show": "big-show",
    "jbl": "bradshaw",
    "john bradshaw layfield": "bradshaw",
    "christian cage": "christian",
    "christian": "christian",
    "booker t": "booker-t",
    "cm punk": "cm-punk",
    "chris jericho": "chris-jericho",
    "bryan danielson": "daniel-bryan",
    "daniel bryan": "daniel-bryan",
    "jon moxley": "dean-ambrose",
    "dean ambrose": "dean-ambrose",
    "samoa joe": "samoa-joe",
    "adam copeland": "edge",
    "edge": "edge",
    "mercedes mone": "sasha-banks",
    "sasha banks": "sasha-banks",
    "tyrus": "brodus-clay",
    "chris adonis": "chris-masters",
    "d angelo dinero": "elijah-burke",
    "da pope": "elijah-burke",
    "2 cold scorpio": "flash-funk",
    "earthquake": "earthquake",
    "john tenta": "earthquake",
    "the barbarian": "the-barbarian",
    "barbarian": "the-barbarian",
    "tony atlas": "saba-simba",
    "hollywood nova": "simon-dean",
    "steve keirn": "skinner",
    "john nord": "the-berzerker",
    "zip": "tom-prichard",
    "dr tom prichard": "tom-prichard",
    "ron harris": "eight-ball",
    "don harris": "skull",
    "the goodfather": "the-godfather",
    "goodfather": "the-godfather",
    "jinsei shinzaki": "hakushi",
    "paul diamond": "max-moon",
    "kato": "max-moon",
    "leo kruger": "adam-rose",
    "big bill": "big-cass",
    "w morrissey": "big-cass",
    "headhunter a": "headhunter-1",
    "headhunter b": "headhunter-2",
}

# Short or reused ring names need championship/promotion context. A global
# alias for "Jade", for example, would incorrectly steal Jade Cargill's WWE
# and AEW reigns from Mia Yim's TNA identity.
SCOPED_ALIASES = {
    ("tna-knockouts-world", "jade"): "mia-yim",
    ("wcw-world-tag", "gerald"): "eight-ball",
    ("wcw-world-tag", "patrick"): "skull",
    ("ghc-openweight-hardcore", "scorpio"): "flash-funk",
    ("ghc-tag", "scorpio"): "flash-funk",
    ("ovw-heavyweight", "nova"): "simon-dean",
    ("ovw-tag", "nova"): "simon-dean",
}

IDENTITY_ALIAS_SOURCE_IDS = {
    "a j styles": "S815",
    "taz": "S682;S1245",
    "koko ware": "S1108",
    "ron garvin": "S1096",
    "christopher nowinski": "S694",
    "psychosis": "S730",
    "brian kendrick": "S762",
    "dory funk": "S616",
    "rene dupree": "S713",
    "yoshitatsu": "S767",
    "sid vicious": "S562",
    "sycho sid": "S562",
    "justin credible": "S610",
    "awesome kong": "S788",
    "amazing kong": "S788",
    "bryan clark": "S2128",
    "wrath": "S2128",
    "hugh morrus": "S698",
    "general rection": "S698",
    "general hugh g rection": "S698",
    "gen rection": "S698",
    "typhoon": "S550",
    "henry o godwinn": "S1169",
    "kenny": "S742",
    "nicky": "S763",
    "mike rotunda": "S555",
    "mike rotundo": "S555",
    "x pac": "S1171",
    "syxx": "S1171",
    "syxx pac": "S1171",
    "hollywood hulk hogan": "S1106",
    "hollywood hogan": "S1106",
    "big van vader": "S626;S1720",
    "timeless toni storm": "S952",
    "maria kanellis bennett": "S939",
    "the texas tornado": "S541",
    "carlito caribbean cool": "S733",
    "rey mysterio jr": "S695",
    "chavo guerrero jr": "S696",
    "adrian neville": "S1696",
    "the great kabuki": "S586",
    "fit finlay": "S741",
    "tajiri": "S697",
    "the fiend bray wyatt": "S768",
    "hawk warrior": "S545",
    "tyrus": "S1686",
    "chris adonis": "S738",
    "d angelo dinero": "S755",
    "da pope": "S755",
    "2 cold scorpio": "S643",
    "earthquake": "S654",
    "john tenta": "S654",
    "the barbarian": "S604",
    "barbarian": "S604",
    "tony atlas": "S542",
    "hollywood nova": "S724",
    "steve keirn": "S2133",
    "john nord": "S556",
    "zip": "S605",
    "dr tom prichard": "S605",
    "ron harris": "S601",
    "don harris": "S601",
    "the goodfather": "S565",
    "goodfather": "S565",
    "jinsei shinzaki": "S618",
    "paul diamond": "S2134",
    "kato": "S2134",
    "leo kruger": "S814",
    "big bill": "S821",
    "w morrissey": "S821",
    "headhunter a": "S625",
    "headhunter b": "S625",
}

SCOPED_ALIAS_SOURCE_IDS = {
    ("tna-knockouts-world", "jade"): "S949",
    ("wcw-world-tag", "gerald"): "S601",
    ("wcw-world-tag", "patrick"): "S601",
    ("ghc-openweight-hardcore", "scorpio"): "S643",
    ("ghc-tag", "scorpio"): "S643",
    ("ovw-heavyweight", "nova"): "S724",
    ("ovw-tag", "nova"): "S724",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    # Match the existing project's UTF-8-without-BOM convention. The
    # validator reads headers literally, so introducing a BOM would turn the
    # first key into ``\ufeffsource_id``/``\ufeffpromotion_id``.
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    text = re.sub(r"\[[^]]*]", "", text)
    text = text.replace("†", "").replace("‡", "")
    text = re.sub(r"[^a-zA-Z0-9]+", " ", text).strip().casefold()
    return re.sub(r"\s+", " ", text)


def clean(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.casefold() == "nan" else text


def iso_date(value: object) -> str:
    text = clean(value)
    if not text:
        return ""
    parsed = pd.to_datetime(text, errors="coerce")
    return "" if pd.isna(parsed) else parsed.date().isoformat()


def source_id_number(value: str) -> int:
    match = re.fullmatch(r"S(\d+)", value or "")
    return int(match.group(1)) if match else 0


def fetch_tables(page: str) -> tuple[str, list[pd.DataFrame]]:
    base_page = page.split("::", 1)[0]
    url = "https://en.wikipedia.org/wiki/" + base_page
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as response:
        html = response.read().decode("utf-8")
    return url, pd.read_html(io.StringIO(html))


def flatten_columns(table: pd.DataFrame) -> pd.DataFrame:
    table = table.copy()
    table.columns = [
        " / ".join(str(part) for part in col if str(part) != "nan")
        if isinstance(col, tuple)
        else str(col)
        for col in table.columns
    ]
    return table


def history_table(tables: list[pd.DataFrame]) -> pd.DataFrame:
    candidates = []
    for table in tables:
        labels = " | ".join(str(col) for col in table.columns)
        if ("Champion" in labels or "Wrestler" in labels) and ("Date" in labels or "Championship change" in labels):
            candidates.append(table)
    if not candidates:
        raise ValueError("No reign-history table found")
    return flatten_columns(max(candidates, key=lambda table: table.shape[0]))


def selected_history_table(page: str, tables: list[pd.DataFrame]) -> pd.DataFrame:
    """Select a specific recognition table when one article contains two."""
    if page.endswith("::WWF"):
        for table in tables:
            flattened = flatten_columns(table)
            if any("Gillberg" in clean(value) for value in flattened.to_numpy().ravel()):
                return flattened
        raise ValueError(f"No WWF-recognized reign table found for {page}")
    return history_table(tables)


def find_col(table: pd.DataFrame, *needles: str, exclude: tuple[str, ...] = ()) -> str:
    for col in table.columns:
        label = str(col).casefold()
        if all(needle.casefold() in label for needle in needles) and not any(x.casefold() in label for x in exclude):
            return col
    return ""


def build_alias_map() -> dict[str, str]:
    aliases: dict[str, str] = {norm(name): wrestler_id for name, wrestler_id in MANUAL_ALIASES.items()}
    for row in read_csv(DATA / "wrestlers.csv"):
        wrestler_id = row["wrestler_id"]
        for name in (row.get("ring_name", ""), row.get("real_name", "")):
            if name:
                aliases.setdefault(norm(name), wrestler_id)
        for name in re.split(r"[;|]", row.get("aliases_ring_names", "")):
            if name.strip():
                aliases.setdefault(norm(name), wrestler_id)
    for row in read_csv(DATA / "entrants.csv"):
        for field in ("ring_name_at_time", "name_displayed_at_event"):
            if row.get(field):
                aliases.setdefault(norm(row[field]), row["wrestler_id"])
    return aliases


def match_wrestlers(name: str, aliases: dict[str, str], championship_id: str = "") -> str:
    key = norm(name)
    scoped = SCOPED_ALIASES.get((championship_id, key))
    if scoped:
        return scoped
    if key in aliases:
        return aliases[key]
    key = re.sub(r"\b(?:vacant|unified|deactivated|retired)\b", "", key).strip()
    if key in aliases:
        return aliases[key]
    # Team/trios tables normally put members in parentheses. Match complete
    # member segments rather than arbitrary substrings: the old substring
    # scan could read "Greg Valentine" and incorrectly attach Emma because
    # one of her aliases is simply "Valentine".
    found = []
    without_reign_counts = re.sub(r"\(\s*\d+(?:\s*,\s*\d+)*\s*\)", "", name)
    parenthetical = re.findall(r"\(([^()]*)\)", without_reign_counts)
    member_text = parenthetical[-1] if parenthetical else without_reign_counts
    if parenthetical or re.search(r"\b(?:and|&)\b|,|/", member_text, flags=re.I):
        for part in re.split(r"\s*(?:,|/|&|\band\b)\s*", member_text, flags=re.I):
            member_key = norm(part)
            if not member_key:
                continue
            wrestler_id = aliases.get(member_key)
            if wrestler_id and wrestler_id not in found:
                found.append(wrestler_id)
    return ";".join(found)


def identity_source_ids(name: str, championship_id: str = "") -> str:
    keys = [norm(name)]
    without_reign_counts = re.sub(r"\(\s*\d+(?:\s*,\s*\d+)*\s*\)", "", name)
    parenthetical = re.findall(r"\(([^()]*)\)", without_reign_counts)
    member_text = parenthetical[-1] if parenthetical else without_reign_counts
    if parenthetical or re.search(r"\b(?:and|&)\b|,|/", member_text, flags=re.I):
        keys.extend(
            norm(part)
            for part in re.split(r"\s*(?:,|/|&|\band\b)\s*", member_text, flags=re.I)
            if norm(part)
        )
    source_ids = []
    for key in keys:
        scoped = SCOPED_ALIAS_SOURCE_IDS.get((championship_id, key), "")
        for source_id in (scoped or IDENTITY_ALIAS_SOURCE_IDS.get(key, "")).split(";"):
            if source_id and source_id not in source_ids:
                source_ids.append(source_id)
    return ";".join(source_ids)


def ensure_sources(titles: list[tuple], page_urls: dict[str, str]) -> dict[str, str]:
    sources = read_csv(DATA / "sources.csv")
    by_url = {row["url"]: row["source_id"] for row in sources}
    next_num = max((source_id_number(row["source_id"]) for row in sources), default=0) + 1
    result: dict[str, str] = {}
    for title in titles:
        title_id, _, title_name, *_, page = title
        url = page_urls[page]
        source_id = by_url.get(url)
        if not source_id:
            source_id = f"S{next_num:03d}"
            next_num += 1
            sources.append({
                "source_id": source_id,
                "source_name": f"Wikipedia – {title_name} reign history",
                "source_type": "reference",
                "url": url,
                "reliability_tier": "10",
                "tier_label": "Wikipedia/reference",
                "accessed_date": ACCESSED,
                "notes": "Structured reign table snapshot; one-source observations remain PROBABLE until independently cross-checked.",
            })
        result[title_id] = source_id
    write_csv(DATA / "sources.csv", SOURCES_FIELDS, sources)
    return result


def main() -> None:
    aliases = build_alias_map()
    fetched: dict[str, tuple[str, pd.DataFrame]] = {}
    refresh = "--refresh" in sys.argv or not SNAPSHOT.exists()
    refresh_missing = "--refresh-missing" in sys.argv and SNAPSHOT.exists() and not refresh
    if refresh:
        for title in TITLES:
            page = title[-1]
            url, tables = fetch_tables(page)
            fetched[page] = (url, selected_history_table(page, tables))
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        snapshot_payload = {
            "accessed_date": ACCESSED,
            "pages": {
                page: {
                    "url": url,
                    "columns": list(table.columns),
                    "rows": [
                        [clean(value) for value in row]
                        for row in table.itertuples(index=False, name=None)
                    ],
                }
                for page, (url, table) in fetched.items()
            },
        }
        SNAPSHOT.write_text(
            json.dumps(snapshot_payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
    else:
        snapshot_payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        for page, payload in snapshot_payload["pages"].items():
            fetched[page] = (
                payload["url"],
                pd.DataFrame(payload["rows"], columns=payload["columns"]),
            )
        if refresh_missing:
            missing = sorted({title[-1] for title in TITLES} - set(fetched))
            for page in missing:
                print(f"Fetching missing championship page: {page}")
                url, tables = fetch_tables(page)
                fetched[page] = (url, selected_history_table(page, tables))
            snapshot_payload = {
                "accessed_date": ACCESSED,
                "pages": {
                    page: {
                        "url": url,
                        "columns": list(table.columns),
                        "rows": [
                            [clean(value) for value in row]
                            for row in table.itertuples(index=False, name=None)
                        ],
                    }
                    for page, (url, table) in fetched.items()
                },
            }
            SNAPSHOT.write_text(
                json.dumps(snapshot_payload, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )

    missing_pages = sorted({title[-1] for title in TITLES} - set(fetched))
    if missing_pages:
        raise ValueError(
            "Snapshot does not cover the configured title pages; rerun with "
            f"--refresh. Missing: {missing_pages}"
        )

    page_urls = {page: result[0] for page, result in fetched.items()}
    source_ids = ensure_sources(TITLES, page_urls)

    promotion_rows = []
    for row in PROMOTIONS:
        promotion_rows.append(dict(zip(PROMOTIONS_FIELDS[:9], row)) | {
            "data_quality_status": "PROBABLE",
            "source_ids": "",
            "notes": "Promotion registry entry; championship lineage sources are attached at championship/reign level.",
        })

    championship_rows = []
    reign_rows: list[dict[str, str]] = []
    for title in TITLES:
        (
            championship_id, promotion_id, title_name, level, division,
            active_from, active_to, status, predecessors, successors,
            official_url, page,
        ) = title
        wiki_url, table = fetched[page]
        source_id = source_ids[championship_id]
        championship_rows.append({
            "championship_id": championship_id,
            "promotion_id": promotion_id,
            "championship_name": title_name,
            "championship_level": level,
            "division": division,
            "active_from": active_from,
            "active_to": active_to,
            "status": status,
            "predecessor_championship_ids": predecessors,
            "successor_championship_ids": successors,
            "official_history_url": official_url,
            "wikipedia_history_url": wiki_url,
            "data_quality_status": "PROBABLE",
            "source_ids": source_id,
            "notes": "World-title lineage; dates and display names are preserved from the cited structured history.",
        })

        champion_col = find_col(table, "champion") or find_col(table, "wrestler")
        date_col = find_col(table, "date")
        number_col = find_col(table, "no.") or find_col(table, "#")
        event_col = find_col(table, "event")
        location_col = find_col(table, "location")
        reign_col = find_col(table, "reign", exclude=("days", "date"))
        days_cols = [col for col in table.columns if "days" in str(col).casefold()]
        days_col = next((col for col in days_cols if "recog" not in str(col).casefold()), "")
        recognized_col = next((col for col in days_cols if "recog" in str(col).casefold()), "")
        notes_col = find_col(table, "notes")
        if not champion_col or not date_col:
            raise ValueError(f"Missing required columns for {championship_id}: {list(table.columns)}")

        prepared = []
        for _, source_row in table.iterrows():
            champion = clean(source_row[champion_col])
            change_date = iso_date(source_row[date_col])
            if not champion or not change_date:
                continue
            no_value = clean(source_row[number_col]) if number_col else ""
            champion_key = norm(champion)
            if "vacat" in champion_key:
                record_type = "vacancy"
            elif not re.search(r"\d", no_value) or champion_key in {"unified", "deactivated", "retired"}:
                record_type = "lineage_event"
            else:
                record_type = "reign"
            prepared.append({
                "record_type": record_type,
                "champion_name": champion,
                "champion_wrestler_ids": match_wrestlers(champion, aliases, championship_id) if record_type == "reign" else "",
                "identity_source_ids": identity_source_ids(champion, championship_id) if record_type == "reign" else "",
                "reign_number": clean(source_row[reign_col]) if reign_col and record_type == "reign" else "",
                "won_date": change_date,
                "days_reported": clean(source_row[days_col]) if days_col else "",
                "days_recognized_reported": clean(source_row[recognized_col]) if recognized_col else "",
                "event_name": clean(source_row[event_col]) if event_col else "",
                "location": clean(source_row[location_col]) if location_col else "",
                "notes": clean(source_row[notes_col]) if notes_col else "",
            })

        for index, row in enumerate(prepared, start=1):
            next_date = prepared[index]["won_date"] if index < len(prepared) else ""
            reign_rows.append({
                "reign_id": f"{championship_id}-R{index:03d}",
                "championship_id": championship_id,
                **row,
                "lost_date": next_date,
                "is_current": "TRUE" if row["record_type"] == "reign" and not next_date and status == "active" else "FALSE",
                "data_quality_status": "PROBABLE",
                "source_ids": ";".join(dict.fromkeys(
                    [source_id] + [x for x in row.get("identity_source_ids", "").split(";") if x]
                )),
            })

    write_csv(DATA / "promotions.csv", PROMOTIONS_FIELDS, promotion_rows)
    write_csv(DATA / "championships.csv", CHAMPIONSHIPS_FIELDS, championship_rows)
    write_csv(DATA / "championship_reigns.csv", CHAMPIONSHIP_REIGNS_FIELDS, reign_rows)
    matched = sum(bool(row["champion_wrestler_ids"]) for row in reign_rows if row["record_type"] == "reign")
    reign_count = sum(row["record_type"] == "reign" for row in reign_rows)
    print(
        f"Wrote {len(promotion_rows)} promotions, {len(championship_rows)} championships, "
        f"and {len(reign_rows)} lineage records ({reign_count} reigns; "
        f"{matched} linked to Royal Rumble wrestler IDs). "
        f"Source mode: {'live refresh' if refresh else 'dated snapshot'}."
    )


if __name__ == "__main__":
    main()
