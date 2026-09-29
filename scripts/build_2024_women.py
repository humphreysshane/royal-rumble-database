# -*- coding: utf-8 -*-
"""Build RR2024W. Researched 2026-09-22.
Uses the section order and row-construction pattern of build_2020_men.py;
self-elimination handling follows build_2020_women.py. Flags explain all
identity/credit precedents and source discrepancies. Single-source times and
biography fields remain PROBABLE. Unknown/not-applicable fields are blank
except the documented no-show sentinel. Global IDs are allocated afresh.
Run against a copy first, rebuild derived tables, validate, then apply the
identical script to live data. Refuses to append an already-present event.
"""
SPEC = {'event_id': 'RR2024W',
 'division': 'W',
 'date': '2024-01-27',
 'venue': 'Tropicana Field',
 'city': 'St. Petersburg, Florida',
 'country': 'United States',
 'duration': '1:04:57',
 'duration_status': 'CONFLICTING',
 'winner': 'Bayley',
 'reward': "Women's world championship match at WrestleMania XL.",
 'sources': [['official',
              'WWE: Royal Rumble Match stats 2024',
              'official_wwe',
              'https://www.wwe.com/shows/royalrumble/2024/royal-rumble-match-stats-2024',
              1,
              'WWE / official sources',
              'Official entry numbers, times and Eliminated By column; internal Breakker typo flagged.'],
             ['wiki',
              'Royal Rumble (2024): event and chronological elimination tables',
              'reference_site',
              'https://en.wikipedia.org/wiki/Royal_Rumble_(2024)',
              10,
              'Wikipedia/reference sites',
              'Times cite WWE and are not treated as independent timing.'],
             ['recap',
              'WWE: Complete Royal Rumble results 2024',
              'official_wwe',
              'https://www.wwe.com/shows/royalrumble/2024/results',
              1,
              'WWE / official sources',
              ''],
             ['timing',
              "Cageside Seats: independently timed 2024 women's Rumble",
              'reference_site',
              'https://www.cagesideseats.com/wwe/2024/1/28/24053642/wwe-royal-rumble-2024-womens-survival-times-complete-list-iron-woman-bayley-naomi-valhalla-record',
              7,
              'Reputable wrestling publication',
              ''],
             ['tag',
              'WWE SmackDown January 26 2024: Kabuki Warriors win titles',
              'official_wwe',
              'https://www.wwe.com/shows/smackdown/2024-01-26',
              1,
              'WWE / official sources',
              ''],
             ['tna',
              'TNA Hard To Kill January 13 2024 live review',
              'reference_site',
              'https://prowrestling.net/site/2024/01/13/tna-hard-to-kill-results-powells-live-review-of-alex-shelley-vs-moose-for-the-tna-title-trinity-vs-jordynne-grace-for-the-knockouts-title-josh-alexander-vs-alex-hammerstone/',
              7,
              'Reputable wrestling publication',
              ''],
             ['bio0',
              'Jordynne Grace individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Jordynne_Grace',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio1',
              'Ivy Nile individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Ivy_Nile',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio2',
              'Kayden Carter individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Lacey_Lane',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio3',
              'Maxxine Dupri individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Maxxine_Dupri',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio4',
              'Alba Fyre individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Alba_Fyre',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio5',
              'Jade Cargill individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Jade_Cargill',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio6',
              'Tiffany Stratton individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Tiffany_Stratton',
              10,
              'Wikipedia/reference sites',
              ''],
             ['gracecm',
              'Cagematch: Jordynne Grace',
              'reference_site',
              'https://www.cagematch.net/?id=2&nr=14365',
              4,
              'Wikipedia/reference sites',
              ''],
             ['gracesdh',
              'SmackDown Hotel: Jordynne Grace',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/jordynne-grace',
              12,
              'Other statistical/history site',
              ''],
             ['carter',
              'Gerweck: Kayden Carter / Lacey Lane',
              'reference_site',
              'https://gerweck.net/2020/01/16/kayden-carter/',
              12,
              'Other statistical/history site',
              ''],
             ['carteralt',
              'Pro Wrestling Wiki: Kayden Carter',
              'reference_site',
              'https://prowrestling.fandom.com/wiki/Kayden_Carter',
              10,
              'Wikipedia/reference sites',
              ''],
             ['maxdebut',
              'WWE Raw July 3 2023: Maxxine in-ring debut',
              'official_wwe',
              'https://www.wwe.com/shows/raw/2023-07-03',
              1,
              'WWE / official sources',
              ''],
             ['maxbp',
              'TV Insider: Maxxine Dupri',
              'reference_site',
              'https://www.tvinsider.com/people/maxxine-dupri/',
              12,
              'Other statistical/history site',
              ''],
             ['alba',
              'SmackDown Hotel: Kay Lee Ray / Alba Fyre',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/kay-lee-ray',
              12,
              'Other statistical/history site',
              ''],
             ['albadebut',
              'Superluchas: May 30 wrestling history',
              'reference_site',
              'https://superluchas.com/hoy-historia-30-mayo-lucha-libre/',
              9,
              'Wikipedia/reference sites',
              ''],
             ['valhalla',
              'WWE: Valhalla biography',
              'official_wwe',
              'https://www.wwe.com/superstars/valhalla',
              1,
              'WWE / official sources',
              '']],
 'match_sources': ['official', 'wiki', 'recap'],
 'event_sources': ['official', 'wiki', 'recap', 'timing'],
 'rows': [['Natalya', 3, '20:57', ['Tegan Nox']],
          ['Naomi', 25, '1:02:18', ['Jade Cargill']],
          ['Bayley', None, '1:03:03', []],
          ['Candice LeRae', 2, '15:23', ['Asuka', 'Bayley', 'Kairi Sane']],
          ['Jordynne Grace', 7, '19:10', ['Bianca Belair']],
          ['Indi Hartwell', 1, '03:23', ['Bayley']],
          ['Asuka', 6, '12:59', ['Katana Chance', 'Kayden Carter']],
          ['Ivy Nile', 10, '23:27', ['Nia Jax']],
          ['Katana Chance', 13, '25:48', ['Nia Jax']],
          ['Bianca Belair', 26, '47:46', ['Bayley']],
          ['Kairi Sane', 5, '05:00', ['Kayden Carter']],
          ['Tegan Nox', 4, '01:22', ['Bayley']],
          ['Kayden Carter', 8, '11:48', ['Piper Niven']],
          ['Chelsea Green', 14, '17:32', ['Becky Lynch']],
          ['Piper Niven', 12, '12:39', ['Nia Jax']],
          ['Xia Li', 9, '06:46', ['Nia Jax']],
          ['Zelina Vega', 17, '20:00', ['Zoey Stark', 'Shayna Baszler']],
          ['Maxxine Dupri', 11, '06:39', ['Bayley']],
          ['Nia Jax', 21, '20:15', ['Jade Cargill']],
          ['Shotzi', 20, '15:14', ['Nia Jax']],
          ['Becky Lynch', 24, '22:29', ['Naomi', 'Jade Cargill']],
          ['Alba Fyre', 16, '06:21', ['Naomi']],
          ['Shayna Baszler', 18, '08:27', ['Nia Jax']],
          ['Valhalla', 15, '00:05', ['Nia Jax']],
          ['Michin', 19, '05:02', ['Nia Jax']],
          ['Zoey Stark', 22, '09:58', ['Liv Morgan']],
          ['Roxanne Perez', 23, '08:29', ['Tiffany Stratton']],
          ['Jade Cargill', 28, '11:03', ['Liv Morgan']],
          ['Tiffany Stratton', 27, '06:52', ['Bayley']],
          ['Liv Morgan', 29, '06:26', ['Bayley']]],
 'bios': {'Jordynne Grace': {'wrestler_id': 'jordynne-grace',
                             'real_name': 'Patricia Forrest Parker',
                             'dob': '1996-03-05',
                             'birthplace': 'Austin, Texas, United States',
                             'nationality': 'American',
                             'debut_year_company': '2011-01-23; independent circuit (first promotion '
                                                   'unverified)',
                             'aliases_ring_names': 'Jordynne Grace;Patricia Forrest Gresham',
                             'sources': ['bio0', 'gracecm', 'gracesdh'],
                             'notes': 'Dedicated person-specific bio lookup completed 2026-09-22; '
                                      'discrepancies retained in event flags.',
                             'birthplace_status': 'CONFLICTING'},
          'Ivy Nile': {'wrestler_id': 'ivy-nile',
                       'real_name': 'Emily Andzulis',
                       'dob': '1992-02-26',
                       'birthplace': 'Knoxville, Tennessee, United States',
                       'nationality': 'American',
                       'debut_year_company': '2020-02-21, WWE NXT',
                       'aliases_ring_names': 'Emily Andzulis',
                       'sources': ['bio1'],
                       'notes': 'Dedicated person-specific bio lookup completed 2026-09-22; discrepancies '
                                'retained in event flags.'},
          'Kayden Carter': {'wrestler_id': 'kayden-carter',
                            'real_name': 'Allyssa Lyn Lane',
                            'dob': '1988-05-20',
                            'birthplace': 'Winter Park, Florida, United States',
                            'nationality': 'American',
                            'debut_year_company': '2016-08-20, Go Wrestle',
                            'aliases_ring_names': 'Lacey Lane',
                            'sources': ['bio2', 'carter', 'carteralt'],
                            'notes': 'Dedicated person-specific bio lookup completed 2026-09-22; '
                                     'discrepancies retained in event flags.',
                            'real_name_status': 'CONFLICTING'},
          'Maxxine Dupri': {'wrestler_id': 'maxxine-dupri',
                            'real_name': 'Sydney Jeannine Zmrzel',
                            'dob': '1997-05-19',
                            'birthplace': 'Loomis, California, United States',
                            'nationality': 'American',
                            'debut_year_company': '2023-07-03, WWE Raw (first in-ring match; valet debut '
                                                  '2022)',
                            'aliases_ring_names': 'Sofia Cromwell',
                            'sources': ['bio3', 'maxdebut', 'maxbp'],
                            'notes': 'Dedicated person-specific bio lookup completed 2026-09-22; '
                                     'discrepancies retained in event flags.',
                            'birthplace_status': 'CONFLICTING'},
          'Alba Fyre': {'wrestler_id': 'alba-fyre',
                        'real_name': 'Kayleigh Rae',
                        'dob': '1992-08-11',
                        'birthplace': 'Paisley, Renfrewshire, Scotland',
                        'nationality': 'Scottish',
                        'debut_year_company': '2009-05-30, Scottish Wrestling Alliance',
                        'aliases_ring_names': 'Kay Lee Ray;Kayleigh Kerr',
                        'sources': ['bio4', 'alba', 'albadebut'],
                        'notes': 'Dedicated person-specific bio lookup completed 2026-09-22; discrepancies '
                                 'retained in event flags.',
                        'birthplace_status': 'CONFLICTING'},
          'Jade Cargill': {'wrestler_id': 'jade-cargill',
                           'real_name': 'Jade Cargill',
                           'dob': '1992-06-03',
                           'birthplace': 'Gifford, Florida, United States',
                           'nationality': 'American',
                           'debut_year_company': '2021-03-03, All Elite Wrestling',
                           'aliases_ring_names': 'Jade Cargill',
                           'sources': ['bio5'],
                           'notes': 'Dedicated person-specific bio lookup completed 2026-09-22; '
                                    'discrepancies retained in event flags.'},
          'Tiffany Stratton': {'wrestler_id': 'tiffany-stratton',
                               'real_name': 'Jessica Lynn Woynilko',
                               'dob': '1999-05-01',
                               'birthplace': 'Prior Lake, Minnesota, United States',
                               'nationality': 'American',
                               'debut_year_company': '2021-11-16, WWE 205 Live (taping)',
                               'aliases_ring_names': 'Tiffany Stratton',
                               'sources': ['bio6'],
                               'notes': 'Dedicated person-specific bio lookup completed 2026-09-22; '
                                        'discrepancies retained in event flags.'}},
 'reused': {'Natalya': 'natalya',
            'Naomi': 'naomi',
            'Bayley': 'bayley',
            'Candice LeRae': 'candice-lerae',
            'Indi Hartwell': 'indi-hartwell',
            'Asuka': 'asuka',
            'Katana Chance': 'kacy-catanzaro',
            'Bianca Belair': 'bianca-belair',
            'Kairi Sane': 'kairi-sane',
            'Tegan Nox': 'tegan-nox',
            'Chelsea Green': 'chelsea-green',
            'Piper Niven': 'piper-niven',
            'Xia Li': 'xia-li',
            'Zelina Vega': 'zelina-vega',
            'Nia Jax': 'nia-jax',
            'Shotzi': 'shotzi-blackheart',
            'Becky Lynch': 'becky-lynch',
            'Shayna Baszler': 'shayna-baszler',
            'Valhalla': 'sarah-logan',
            'Michin': 'mia-yim',
            'Zoey Stark': 'zoey-stark',
            'Roxanne Perez': 'roxanne-perez',
            'Liv Morgan': 'liv-morgan'},
 'dismissed_alias_matches': {'Kayden Carter': ['kacy-catanzaro']},
 'champions': {'Asuka': ["WWE Women's Tag Team Championship", 'Tag Team', '2024-01-26', 'kairi-sane'],
               'Kairi Sane': ["WWE Women's Tag Team Championship", 'Tag Team', '2024-01-26', 'asuka'],
               'Jordynne Grace': ['TNA Knockouts World Championship', 'World', '2024-01-13']},
 'champions_complete': True,
 'champion_sources': ['tag', 'tna'],
 'surprises': ['Naomi', 'Jordynne Grace', 'Roxanne Perez', 'Jade Cargill', 'Tiffany Stratton', 'Liv Morgan'],
 'order_status': 'PROBABLE',
 'time_status': {'Natalya': 'CONFIRMED',
                 'Naomi': 'CONFIRMED',
                 'Bayley': 'CONFLICTING',
                 'Candice LeRae': 'CONFLICTING',
                 'Jordynne Grace': 'CONFIRMED',
                 'Indi Hartwell': 'CONFIRMED',
                 'Asuka': 'CONFLICTING',
                 'Ivy Nile': 'CONFLICTING',
                 'Katana Chance': 'CONFIRMED',
                 'Bianca Belair': 'CONFIRMED',
                 'Kairi Sane': 'CONFIRMED',
                 'Tegan Nox': 'CONFIRMED',
                 'Kayden Carter': 'CONFIRMED',
                 'Chelsea Green': 'CONFLICTING',
                 'Piper Niven': 'CONFIRMED',
                 'Xia Li': 'CONFLICTING',
                 'Zelina Vega': 'CONFLICTING',
                 'Maxxine Dupri': 'CONFIRMED',
                 'Nia Jax': 'CONFLICTING',
                 'Shotzi': 'CONFLICTING',
                 'Becky Lynch': 'CONFIRMED',
                 'Alba Fyre': 'CONFIRMED',
                 'Shayna Baszler': 'CONFIRMED',
                 'Valhalla': 'CONFIRMED',
                 'Michin': 'CONFLICTING',
                 'Zoey Stark': 'CONFLICTING',
                 'Roxanne Perez': 'CONFLICTING',
                 'Jade Cargill': 'CONFIRMED',
                 'Tiffany Stratton': 'CONFLICTING',
                 'Liv Morgan': 'CONFIRMED'},
 'flags': [{'table': 'wrestlers;entrants',
            'record': 'kacy-catanzaro;kayden-carter;shotzi-blackheart;mia-yim',
            'field': 'wrestler_id',
            'type': 'needs_human_judgement',
            'description': 'Katana Chance reuses kacy-catanzaro. The apparent Kayden Carter alias hit is a '
                           "prose warning in Kacy's aliases saying NOT the same person; it is not an alias. "
                           'Kayden is separately researched and added. Shotzi and Michin reuse '
                           'shotzi-blackheart and mia-yim, following the RR2023W same-person precedent.',
            'sources': ['bio2', 'carter', 'official'],
            'status': 'resolved'},
           {'table': 'entrants',
            'record': 'sarah-logan',
            'field': 'wrestler_id',
            'type': 'needs_human_judgement',
            'description': "Valhalla reuses sarah-logan: WWE's official profile explicitly presents Sarah "
                           'Logan now known as Valhalla and retains the same woods-raised hunter/survivalist '
                           'backstory. Treat as continued persona with changed name/presentation, like King '
                           'Corbin/baron-corbin, rather than a distinct identity such as Husky Harris/Bray '
                           'Wyatt. The event name remains Valhalla.',
            'sources': ['valhalla', 'official'],
            'status': 'resolved'},
           {'table': 'entrants;eliminations',
            'record': 'r-truth',
            'field': 'entry_number;eliminator_wrestler_id',
            'type': 'needs_human_judgement',
            'description': "R-Truth mistakenly entered the women's ring but was not an official entrant. No "
                           '31st entrant or elimination row is created, and Nia Jax gets no ninth structured '
                           'elimination. Unlike Rey Mysterio RR2023M, Truth was never assigned a slot in '
                           'THIS match; unlike Omos RR2021M, he is not an official eliminator of record '
                           'either. Document only as a notable moment.',
            'sources': ['official', 'recap', 'timing'],
            'status': 'resolved'},
           {'table': 'entrants;events',
            'record': 'RR2024W',
            'field': 'ring_time;duration_total',
            'type': 'conflicting_sources',
            'description': 'WWE/Cageside seconds differ: Bayley 1:03:03/1:03:02; Candice LeRae 15:23/15:24; '
                           'Asuka 12:59/13:00; Ivy Nile 23:27/23:28; Chelsea Green 17:32/17:31; Xia Li '
                           '06:46/06:47; Zelina Vega 20:00/20:01; Nia Jax 20:15/20:14; Shotzi 15:14/15:15; '
                           'Michin 05:02/05:03; Zoey Stark 09:58/09:59; Roxanne Perez 08:29/08:28; Tiffany '
                           'Stratton 06:52/06:53. Store official individual times, mark these CONFLICTING; '
                           "preserve Cageside's approximate two-second margin. Full duration Cageside 64:57 "
                           'versus Wikipedia 65:00: use higher-tier independent footage timing 64:57.',
            'sources': ['official', 'wiki', 'timing'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'jordynne-grace',
            'field': 'birthplace;debut_year_company',
            'type': 'conflicting_sources',
            'description': 'Cagematch gives Austin and 2011-01-23 debut; English Wikipedia gives Austin but '
                           '2012-09-22 debut; SmackDown Hotel gives St. Louis and 2011-01-23. Use '
                           'higher-tier Cagematch birthplace/date. A person-specific first-promotion search '
                           'did not establish the 2011 promoter; Metroplex is documented for the 2012 match '
                           'and is not retroactively assigned to 2011.',
            'sources': ['bio0', 'gracecm', 'gracesdh'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'kayden-carter',
            'field': 'real_name;debut_year_company',
            'type': 'conflicting_sources',
            'description': 'Store Allyssa Lyn Lane (Gerweck and Wikipedia narrative); Wikipedia infobox '
                           'spells Allysa. Gerweck gives 2016-08-20 Go Wrestle debut, whereas Pro Wrestling '
                           'Wiki gives 2016-08-25. Store August 20 based on dedicated career chronology; '
                           'preserve the five-day disagreement.',
            'sources': ['bio2', 'carter', 'carteralt'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'maxxine-dupri',
            'field': 'birthplace;debut_year_company',
            'type': 'conflicting_sources',
            'description': 'Wikipedia gives Loomis, California; TV Insider gives Phoenix, Arizona. Store '
                           "higher-tier Wikipedia birthplace with CONFLICTING status. Wikipedia's 2022 debut "
                           'refers to valet work; WWE expressly identifies 2023-07-03 as her in-ring debut, '
                           'stored with the managerial distinction. Company appearance and first wrestling '
                           'match are not interchangeable.',
            'sources': ['bio3', 'maxbp', 'maxdebut'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'alba-fyre',
            'field': 'birthplace;debut_year_company',
            'type': 'conflicting_sources',
            'description': 'English Wikipedia gives Paisley and an anomalous 1999 debut; SmackDown Hotel '
                           'gives Glasgow and 2009-05-30. Superluchas independently identifies SWA '
                           'Battlezone on 2009-05-30. Store Paisley by source hierarchy and the corroborated '
                           '2009 debut; retain Glasgow/1999 alternatives.',
            'sources': ['bio4', 'alba', 'albadebut'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'jade-cargill',
            'field': 'debut_year_company',
            'type': 'conflicting_sources',
            'description': "Wikipedia's opening prose mentions 2018 as a debut/training start, while its "
                           'infobox and detailed match account identify 2021-03-03 AEW Dynamite with '
                           "Shaquille O'Neal as the wrestling debut. Store 2021 in-ring debut; WWE in-ring "
                           'debut in this 2024 Rumble is distinct from her 2023 WWE appearances.',
            'sources': ['bio5', 'recap'],
            'status': 'resolved'}],
 'moments': [{'category': 'record',
              'title': "Bayley sets women's survival record",
              'people': ['Bayley', 'Naomi'],
              'description': 'Naomi exceeded the previous mark before Bayley finished with the official '
                             '63:03 record.',
              'sources': ['official', 'timing'],
              'status': 'CONFIRMED'},
             {'category': 'milestone_first',
              'title': "Jade Cargill's first WWE match",
              'people': ['Jade Cargill', 'Nia Jax'],
              'description': 'Cargill entered at 28 and eliminated Jax.',
              'sources': ['recap', 'wiki'],
              'status': 'CONFIRMED'},
             {'category': 'storyline_moment',
              'title': "R-Truth mistakes the women's Rumble for his match",
              'people': ['r-truth', 'Nia Jax', 'Valhalla'],
              'description': "Truth's interruption preceded Valhalla's entry; he was not an official "
                             'competitor.',
              'sources': ['recap', 'timing'],
              'status': 'CONFIRMED'},
             {'category': 'record',
              'title': 'Valhalla lasts five seconds',
              'people': ['Valhalla'],
              'description': "Her official five-second duration matched Chelsea Green's 2023 low.",
              'sources': ['official', 'timing'],
              'status': 'CONFIRMED'},
             {'category': 'other',
              'title': 'TNA champion crosses into WWE',
              'people': ['Jordynne Grace'],
              'description': 'Grace entered while holding the TNA Knockouts World Championship.',
              'sources': ['official', 'recap'],
              'status': 'PROBABLE'}],
 'notes': 'Source timing and biography disagreements are preserved in flags; attendance and footage-only '
          'detail remain blank. Exact elimination sequence is PROBABLE from the chronological reference '
          'table.'}

import csv, sys, re, unicodedata
from pathlib import Path
from datetime import date
sys.path.insert(0, str(Path(__file__).parent))
from schema import TABLES, mmss_to_seconds
DATA_DIR = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent/'data'
EVENT_ID = SPEC['event_id']
ACCESSED = '2026-09-22'
def read(fn):
    with (DATA_DIR/fn).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))
def blank(fn, **values):
    assert set(values)<=set(TABLES[fn]), (fn,set(values)-set(TABLES[fn]))
    return {k:values.get(k,'') for k in TABLES[fn]}
def truth(v): return 'TRUE' if v else 'FALSE'
def norm(s): return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))
def allocate(fn,col,prefix,n):
    start=max([int(r[col][len(prefix):]) for r in read(fn) if r[col]] or [0])+1
    print(f'FRESH IDS {fn}: next={prefix}{start}, allocated={n}')
    return [prefix+str(i) for i in range(start,start+n)]
assert EVENT_ID not in {r['event_id'] for r in read('events.csv')}, 'Event already exists; refusing duplicate append'
# Fresh global IDs are allocated against the actual target, immediately before this build.
source_ids=allocate('sources.csv','source_id','S',len(SPEC['sources']))
flag_ids=allocate('flags.csv','flag_id','F',len(SPEC['flags']))
moment_ids=allocate('notable_moments.csv','moment_id','NM',len(SPEC['moments']))
sid={r[0]:s for r,s in zip(SPEC['sources'],source_ids)}
def refs(keys): return ';'.join(sid[k] for k in keys)
sources=[blank('sources.csv',source_id=sid[key],source_name=title,source_type=kind,url=url,reliability_tier=tier,tier_label=label,accessed_date=ACCESSED,notes=notes) for key,title,kind,url,tier,label,notes in SPEC['sources']]

# Template sequence: ordered entrants, survival times, elimination order, final sets, eliminators.
all_names=[r[0] for r in SPEC['rows']]
ENTRY_NUMBERS={n:i+1 for i,n in enumerate(all_names)}
survival={r[0]:r[2] for r in SPEC['rows']}
ELIM_ORDER=[r[0] for r in sorted([r for r in SPEC['rows'] if isinstance(r[1],int)],key=lambda r:r[1])]
elim_number={n:i+1 for i,n in enumerate(ELIM_ORDER)}
assert all(elim_number[r[0]]==r[1] for r in SPEC['rows'] if isinstance(r[1],int))
NO_SHOWS=set(SPEC.get('no_shows',[])); WINNER=SPEC['winner']
assert len(all_names)==len(set(all_names))==30
assert len(ELIM_ORDER)==len(all_names)-1-len(NO_SHOWS)
FINAL_TWO={WINNER,*ELIM_ORDER[-1:]}; FINAL_THREE={WINNER,*ELIM_ORDER[-2:]}; FINAL_FOUR={WINNER,*ELIM_ORDER[-3:]}
ELIMINATORS={r[0]:(r[3],len(r[3])>1,'') for r in SPEC['rows']}
DISPUTED_ELIM_CREDIT=set(SPEC.get('disputed_credit',[]))
CHAMP_INFO=SPEC.get('champions',{}); CHAMPS_AT_ENTRY=set(CHAMP_INFO)
SURPRISE_ENTRANTS=set(SPEC.get('surprises',[])); LEGENDS=set(SPEC.get('legends',[])); NON_FULL_TIME=set(SPEC.get('non_full_time',[]))

# Individual identity lookup includes real names, aliases, and explicit reviewed mappings.
existing=read('wrestlers.csv'); existing_ids={r['wrestler_id'] for r in existing}
reused=SPEC['reused']; new_wrestlers=[]; wrestler_ids=dict(reused)
for name in all_names:
    matches=[r['wrestler_id'] for r in existing if norm(name)==norm(r['ring_name']) or norm(name) in norm(r['aliases_ring_names'])]
    if name in reused:
        assert reused[name] in existing_ids
        print(f'LOOKUP {name} -> {reused[name]} (reuse; direct/alias candidates={matches})')
    else:
        b=SPEC['bios'][name]; wid=b['wrestler_id']
        assert wid not in existing_ids and (not matches or set(matches)<=set(SPEC.get('dismissed_alias_matches',{}).get(name,[]))), (name,matches)
        same_person=[r['wrestler_id'] for r in existing if b.get('real_name') and norm(r['real_name'])==norm(b['real_name'])]
        assert not same_person or b.get('character_split'), (name,'unreviewed same-person identity',same_person)
        values={k:v for k,v in b.items() if k in TABLES['wrestlers.csv']}
        values.update(ring_name=name,gender='M' if SPEC['division']=='M' else 'F',source_ids=refs(b['sources']))
        for fld in ['real_name','dob','birthplace']:
            values[fld+'_status']=b.get(fld+'_status','PROBABLE') if b.get(fld) else ''
        new_wrestlers.append(blank('wrestlers.csv',**values)); wrestler_ids[name]=wid
        print(f'LOOKUP {name} -> {wid} (new; same-person candidates={same_person})')
assert set(wrestler_ids)==set(all_names)

# Entrant/elimination construction follows build_2020_men.py and the women's self-elimination convention.
entrant_rows=[]; elim_rows=[]
for name in all_names:
    wid=wrestler_ids[name]; entry=ENTRY_NUMBERS[name]; winner=name==WINNER; no_show=name in NO_SHOWS
    elim_by,is_shared,_=ELIMINATORS[name]; is_self=elim_by==[name]
    quality='CONFLICTING' if name in DISPUTED_ELIM_CREDIT else SPEC.get('credit_status','CONFIRMED')
    for eliminator in elim_by:
        elim_rows.append(blank('eliminations.csv',event_id=EVENT_ID,order_in_match=elim_number[name],eliminated_wrestler_id=wid,eliminator_wrestler_id=wrestler_ids[eliminator],assisting_wrestler_ids=';'.join(wrestler_ids[e] for e in elim_by if e!=eliminator) if is_shared else '',entry_number_of_eliminated=entry,entry_number_of_eliminator=ENTRY_NUMBERS.get(eliminator,''),elimination_type='self_elimination' if is_self else 'over_top_rope',is_solo=truth(not(is_shared or is_self)),is_shared=truth(is_shared),is_self_elimination=truth(is_self),is_disputed=truth(name in DISPUTED_ELIM_CREDIT),simultaneous_group_id=f'{EVENT_ID}-E{elim_number[name]}' if is_shared else '',data_quality_status=quality,source_ids=refs(SPEC['match_sources']),notes=SPEC.get('entrant_notes',{}).get(name,'')))
    er=blank('entrants.csv',event_id=EVENT_ID,wrestler_id=wid,match_id=EVENT_ID,entry_number=entry,entry_number_status=SPEC.get('entry_status','CONFIRMED'),ring_name_at_time=name,name_displayed_at_event=name,elim_number='' if winner or no_show else elim_number[name],elim_number_status='N/A' if no_show else ('' if winner else SPEC.get('order_status','CONFIRMED')),eliminated_by_ids=';'.join(wrestler_ids[e] for e in elim_by),ring_time=survival[name],ring_time_seconds=mmss_to_seconds(survival[name]),ring_time_status=SPEC.get('time_status',{}).get(name,SPEC.get('default_time_status','PROBABLE')) if survival[name] else '',self_eliminated=truth(is_self),is_winner=truth(winner),is_runner_up=truth(name==ELIM_ORDER[-1]),is_final_two=truth(name in FINAL_TWO),is_final_three=truth(name in FINAL_THREE),is_final_four=truth(name in FINAL_FOUR),surprise_entrant=truth(name in SURPRISE_ENTRANTS),legend_returning='TRUE' if name in LEGENDS else '',non_full_time_wrestler='TRUE' if name in NON_FULL_TIME else '',celebrity_entrant='TRUE' if name in SPEC.get('celebrities',[]) else '',data_quality_status=quality,source_ids=refs(SPEC['match_sources']),notes=SPEC.get('entrant_notes',{}).get(name,''))
    if name in CHAMP_INFO:
        c=CHAMP_INFO[name]; er.update(current_champion_title=c[0],championship_level=c[1],title_won_date=c[2],days_into_reign_at_event=(date.fromisoformat(SPEC['date'])-date.fromisoformat(c[2])).days if c[2] else '',championship_partner=c[3] if len(c)>3 else '')
        er['source_ids']=refs(list(dict.fromkeys(SPEC['match_sources']+SPEC.get('champion_sources',[]))))
    entrant_rows.append(er)
for er in entrant_rows:
    credited=[r for r in elim_rows if r['eliminator_wrestler_id']==er['wrestler_id'] and r['eliminated_wrestler_id']!=er['wrestler_id']]
    er.update(wrestlers_eliminated_count=len(credited),wrestlers_eliminated_ids=';'.join(r['eliminated_wrestler_id'] for r in credited),solo_eliminations_count=sum(r['is_solo']=='TRUE' for r in credited),assisted_eliminations_count=sum(r['is_shared']=='TRUE' for r in credited))
flags=[blank('flags.csv',flag_id=fid,event_id=EVENT_ID,table=f['table'],record_id=f.get('record',EVENT_ID),field=f['field'],issue_type=f['type'],description=f['description'],source_ids_involved=refs(f.get('sources',SPEC['match_sources'])),status=f.get('status','open'),date_logged=ACCESSED) for fid,f in zip(flag_ids,SPEC['flags'])]
nm_rows=[blank('notable_moments.csv',moment_id=mid,event_id=EVENT_ID,wrestler_ids_involved=';'.join(wrestler_ids.get(n,n) for n in m['people']),category=m['category'],title=m['title'],description=m['description'],data_quality_status=m.get('status','PROBABLE'),source_ids=refs(m.get('sources',SPEC['match_sources']))) for mid,m in zip(moment_ids,SPEC['moments'])]
event_row=blank('events.csv',event_id=EVENT_ID,event_name='Royal Rumble '+SPEC['date'][:4],match_name='Royal Rumble Match',match_type="Men's" if SPEC['division']=='M' else "Women's",event_date=SPEC['date'],venue=SPEC['venue'],city_region=SPEC['city'],country=SPEC['country'],duration_total=SPEC['duration'],duration_status=SPEC.get('duration_status','PROBABLE'),entrant_count=len(entrant_rows),winner_id=wrestler_ids[WINNER],runner_up_id=wrestler_ids[ELIM_ORDER[-1]],final_two_ids=';'.join(wrestler_ids[n] for n in [WINNER]+ELIM_ORDER[-1:][::-1]),final_three_ids=';'.join(wrestler_ids[n] for n in [WINNER]+ELIM_ORDER[-2:][::-1]),final_four_ids=';'.join(wrestler_ids[n] for n in [WINNER]+ELIM_ORDER[-3:][::-1]),first_entrant_id=wrestler_ids[all_names[0]],second_entrant_id=wrestler_ids[all_names[1]],final_entrant_id=wrestler_ids[all_names[-1]],first_elimination_id=wrestler_ids[ELIM_ORDER[0]],last_elimination_before_winner_id=wrestler_ids[ELIM_ORDER[-1]],eliminations_count=len({r['eliminated_wrestler_id'] for r in elim_rows}),eliminators_count=len({r['eliminator_wrestler_id'] for r in elim_rows if r['is_self_elimination']!='TRUE'}),surprise_entrants_count=sum(r['surprise_entrant']=='TRUE' for r in entrant_rows),champions_in_field_count=sum(bool(r['current_champion_title']) for r in entrant_rows) if SPEC.get('champions_complete') else '',title_on_the_line='FALSE',championship_implications=SPEC['reward'],winners_reward=SPEC['reward'],data_quality_status='CONFLICTING' if DISPUTED_ELIM_CREDIT else 'CONFIRMED',source_ids=refs(SPEC['event_sources']),notes=SPEC.get('notes',''))
event_row.update(SPEC.get('event_extra',{}))
to_write={'sources.csv':sources,'wrestlers.csv':new_wrestlers,'entrants.csv':entrant_rows,'eliminations.csv':elim_rows,'flags.csv':flags,'notable_moments.csv':nm_rows,'events.csv':[event_row]}
valid_categories={'record','milestone_first','notable_absence_or_substitution','behind_the_scenes','storyline_moment','controversy','botch','injury_or_incident','weapon_used','other'}
for fn,rows in to_write.items():
    for r in rows:
        assert set(r)==set(TABLES[fn])
        for k,v in r.items():
            assert str(v).strip().upper() not in {'UNKNOWN','N/A','TBD','NONE','NULL'} or (fn=='entrants.csv' and k=='elim_number_status' and r['wrestler_id'] in {wrestler_ids[n] for n in NO_SHOWS}), (fn,k,v)
for r in nm_rows: assert r['category'] in valid_categories
for fn,rows in to_write.items():
    with (DATA_DIR/fn).open('a',encoding='utf-8',newline='') as f: csv.DictWriter(f,fieldnames=TABLES[fn]).writerows(rows)
# Independent read-back self-check: declared fields versus CSV rows actually written.
en=[r for r in read('entrants.csv') if r['event_id']==EVENT_ID]
el=[r for r in read('eliminations.csv') if r['event_id']==EVENT_ID]
ev=next(r for r in read('events.csv') if r['event_id']==EVENT_ID)
checks={'entrant_count':len(en),'eliminations_count':len({r['eliminated_wrestler_id'] for r in el}),'eliminators_count':len({r['eliminator_wrestler_id'] for r in el if r['is_self_elimination']!='TRUE'}),'surprise_entrants_count':sum(r['surprise_entrant']=='TRUE' for r in en)}
if ev['champions_in_field_count']: checks['champions_in_field_count']=sum(bool(r['current_champion_title']) for r in en)
print('SELF-CHECK',EVENT_ID)
for k,v in checks.items():
    print(f'{k}: declared={ev[k]} recomputed={v} match={str(v)==ev[k]}'); assert str(v)==ev[k]
for er in en:
    cr=[r for r in el if r['eliminator_wrestler_id']==er['wrestler_id'] and r['eliminated_wrestler_id']!=er['wrestler_id']]
    for k,v in [('wrestlers_eliminated_count',len(cr)),('solo_eliminations_count',sum(r['is_solo']=='TRUE' for r in cr)),('assisted_eliminations_count',sum(r['is_shared']=='TRUE' for r in cr))]: assert er[k]==str(v),(er['wrestler_id'],k)
    assert er['wrestlers_eliminated_ids']==';'.join(r['eliminated_wrestler_id'] for r in cr)
    assert mmss_to_seconds(er['ring_time'])==('' if not er['ring_time_seconds'] else int(er['ring_time_seconds']))
    if er['days_into_reign_at_event']: assert int(er['days_into_reign_at_event'])==(date.fromisoformat(SPEC['date'])-date.fromisoformat(er['title_won_date'])).days
assert sum(int(r['wrestlers_eliminated_count']) for r in en)==sum(r['is_self_elimination']!='TRUE' for r in el)
print(f'All {len(en)} entrant credit totals and populated time/reign derivations verified from persisted rows.')
print(f'{EVENT_ID} build complete: {len(new_wrestlers)} new wrestlers, {len(en)} entrants, {len(el)} elimination rows, {len(sources)} sources, {len(flags)} flags, {len(nm_rows)} moments.')
