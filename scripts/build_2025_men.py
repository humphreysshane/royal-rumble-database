# -*- coding: utf-8 -*-
"""Build RR2025M. Researched 2026-09-22.
Uses the section order and row-construction pattern of build_2020_men.py;
self-elimination handling follows build_2020_women.py. Flags explain all
identity/credit precedents and source discrepancies. Single-source times and
biography fields remain PROBABLE. Unknown/not-applicable fields are blank
except the documented no-show sentinel. Global IDs are allocated afresh.
Run against a copy first, rebuild derived tables, validate, then apply the
identical script to live data. Refuses to append an already-present event.
"""
SPEC = {'event_id': 'RR2025M',
 'division': 'M',
 'date': '2025-02-01',
 'venue': 'Lucas Oil Stadium',
 'city': 'Indianapolis, Indiana',
 'country': 'United States',
 'duration': '1:20:10',
 'duration_status': 'CONFLICTING',
 'winner': 'Jey Uso',
 'reward': 'World championship match at WrestleMania 41.',
 'sources': [['official',
              'WWE Royal Rumble 2025 results and statistics',
              'official',
              'https://www.wwe.com/shows/royalrumble/2025',
              1,
              'WWE / official sources',
              ''],
             ['recap',
              'WWE Royal Rumble 2025 recap',
              'official',
              'https://www.wwe.com/shows/royalrumble/2025/results',
              1,
              'WWE / official sources',
              ''],
             ['wiki',
              'Royal Rumble 2025 event table',
              'reference_site',
              'https://en.wikipedia.org/wiki/Royal_Rumble_(2025)',
              10,
              'Wikipedia/reference sites',
              ''],
             ['f4w',
              'F4W 2025 men entrant and elimination order',
              'reference_site',
              'https://www.f4wonline.com/news/wwe/wwe-royal-rumble-mens-entrant-order-and-eliminations/',
              7,
              'Reputable wrestling publications',
              ''],
             ['timing',
              'Independent 2025 men survival times',
              'reference_site',
              'https://www.cagesideseats.com/wwe/2025/2/3/24357462/wwe-royal-rumble-2025-mens-survival-times-complete-list-iron-man-penta-elimination-controversy-cena',
              7,
              'Reputable wrestling publications',
              ''],
             ['attendance',
              'WWE 2025 event gate and attendance release',
              'official',
              'https://www.wwe.com/article/royal-rumble-2025-generates-largest-gate-for-any-single-night-event-in-wwe-history',
              1,
              'WWE / official sources',
              ''],
             ['ic',
              'WWE IC title history',
              'official',
              'https://www.wwe.com/titlehistory/intercontinental-championship',
              1,
              'WWE / official sources',
              ''],
             ['us',
              'WWE US title history',
              'official',
              'https://www.wwe.com/titlehistory/united-states-championship',
              1,
              'WWE / official sources',
              ''],
             ['tna',
              'Genesis 2025 results',
              'reference_site',
              'https://www.postwrestling.com/2025/01/19/tna-genesis-results-nic-nemeth-vs-joe-hendry-hardys-vs-rascalz-nxt-partnership-begins/',
              7,
              'Reputable wrestling publications',
              ''],
             ['penta',
              'Penta biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Pentag%C3%B3n_Jr.',
              10,
              'Wikipedia/reference sites',
              ''],
             ['speed',
              'IShowSpeed biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/IShowSpeed',
              10,
              'Wikipedia/reference sites',
              ''],
             ['speedbio',
              'IShowSpeed IMDb biography',
              'reference_site',
              'https://www.imdb.com/name/nm12964938/bio/',
              10,
              'Wikipedia/reference sites',
              ''],
             ['fatu',
              'Jacob Fatu biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Jacob_Fatu',
              10,
              'Wikipedia/reference sites',
              ''],
             ['fatubio',
              'Jacob Fatu SDH profile',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/jacob-fatu',
              12,
              'Other statistical/history sites',
              ''],
             ['fatuother',
              'Jacob Fatu German biography',
              'reference_site',
              'https://de.wikipedia.org/wiki/Jacob_Fatu',
              10,
              'Wikipedia/reference sites',
              ''],
             ['fatudebut',
              'Jacob Fatu career profile',
              'reference_site',
              'https://gerweck.net/2019/12/01/jacob-fatu/',
              7,
              'Reputable wrestling publications',
              ''],
             ['hendry',
              'Joe Hendry biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Joe_Hendry',
              10,
              'Wikipedia/reference sites',
              ''],
             ['hendrybio',
              'Joe Hendry career profile',
              'reference_site',
              'https://wrestlingprofiles.com/wrestler/joe-hendry/',
              12,
              'Other statistical/history sites',
              ''],
             ['hendryother',
              'Joe Hendry SDH profile',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/joe-hendry',
              12,
              'Other statistical/history sites',
              ''],
             ['knight',
              'LA Knight biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/LA_Knight',
              10,
              'Wikipedia/reference sites',
              ''],
             ['knightbio',
              'LA Knight career profile',
              'reference_site',
              'https://wrestlingprofiles.com/wrestler/la-knight/',
              12,
              'Other statistical/history sites',
              ''],
             ['tozawa',
              'Akira Tozawa biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Akira_Tozawa',
              10,
              'Wikipedia/reference sites',
              ''],
             ['tozawabio',
              'Dragon Gate roster biographies',
              'reference_site',
              'https://puroresuspirit.wordpress.com/dragon-gate/roster/',
              12,
              'Other statistical/history sites',
              '']],
 'match_sources': ['official', 'f4w', 'wiki'],
 'event_sources': ['official', 'wiki', 'timing', 'attendance'],
 'rows': [['Rey Mysterio', 6, '24:41', ['Jacob Fatu']],
          ['Penta', 14, '42:05', ['Finn Balor']],
          ['Chad Gable', 5, '21:38', ['Jacob Fatu']],
          ['Carmelo Hayes', 1, '06:59', ['Bron Breakker']],
          ['Santos Escobar', 2, '05:42', ['Bron Breakker']],
          ['Otis', 3, '09:43', ['Bron Breakker', 'IShowSpeed']],
          ['Bron Breakker', 12, '22:26', ['Roman Reigns']],
          ['IShowSpeed', 4, '00:56', ['Otis']],
          ['Sheamus', 10, '15:38', ['Roman Reigns']],
          ['Jimmy Uso', 13, '15:34', ['Jacob Fatu']],
          ['Andrade', 7, '03:17', ['Jacob Fatu']],
          ['Jacob Fatu', 16, '24:16', ['Braun Strowman']],
          ['Ludwig Kaiser', 8, '00:06', ['Penta']],
          ['The Miz', 9, '05:25', ['Roman Reigns']],
          ['Joe Hendry', 11, '03:35', ['Roman Reigns']],
          ['Roman Reigns', 26, '37:15', ['CM Punk']],
          ['Drew McIntyre', 21, '26:55', ['Damian Priest']],
          ['Finn Balor', 18, '11:10', ['John Cena']],
          ['Shinsuke Nakamura', 15, '03:17', ['Jey Uso']],
          ['Jey Uso', None, '36:59', []],
          ['AJ Styles', 24, '21:02', ['Logan Paul']],
          ['Braun Strowman', 17, '02:12', ['John Cena']],
          ['John Cena', 29, '30:31', ['Jey Uso']],
          ['CM Punk', 27, '18:46', ['Logan Paul']],
          ['Seth Rollins', 25, '17:14', ['CM Punk']],
          ['Dominik Mysterio', 19, '04:09', ['Damian Priest']],
          ['Sami Zayn', 20, '05:22', ['Jey Uso']],
          ['Damian Priest', 22, '06:14', ['LA Knight']],
          ['LA Knight', 23, '05:06', ['AJ Styles']],
          ['Logan Paul', 28, '11:19', ['John Cena']],
          ['Akira Tozawa', None, '', []]],
 'bios': {'Penta': {'wrestler_id': 'penta',
                    'real_name': '',
                    'dob': '1985-02-05',
                    'birthplace': 'Ecatepec de Morelos, State of Mexico, Mexico',
                    'nationality': 'Mexican',
                    'debut_year_company': '2007; Mexican independent circuit (first promotion unverified)',
                    'sources': ['penta'],
                    'notes': 'Person-specific biography research completed 2026-09-22.'},
          'IShowSpeed': {'wrestler_id': 'ishowspeed',
                         'real_name': 'Darren Jason Watkins Jr.',
                         'dob': '2005-01-21',
                         'birthplace': 'Cincinnati, Ohio, United States',
                         'nationality': 'American',
                         'debut_year_company': '2025-02-01, WWE',
                         'sources': ['speed', 'speedbio', 'official'],
                         'notes': 'Person-specific biography research completed 2026-09-22.',
                         'real_name_status': 'CONFIRMED',
                         'dob_status': 'CONFIRMED',
                         'birthplace_status': 'CONFIRMED'},
          'Jacob Fatu': {'wrestler_id': 'jacob-fatu',
                         'real_name': 'Jacob Samuel Fatu',
                         'dob': '1992-04-18',
                         'birthplace': 'Sacramento, California, United States',
                         'nationality': 'American',
                         'debut_year_company': '2012-09-22, KnokX Pro Academy',
                         'sources': ['fatu', 'fatubio', 'fatuother', 'fatudebut'],
                         'notes': 'Person-specific biography research completed 2026-09-22.',
                         'dob_status': 'CONFLICTING',
                         'birthplace_status': 'CONFLICTING'},
          'Joe Hendry': {'wrestler_id': 'joe-hendry',
                         'real_name': 'Joe Samuel Hendry',
                         'dob': '1988-05-01',
                         'birthplace': 'Edinburgh, Scotland, United Kingdom',
                         'nationality': 'Scottish',
                         'debut_year_company': '2013-10-12, Scottish Wrestling Alliance',
                         'sources': ['hendry', 'hendrybio', 'hendryother'],
                         'notes': 'Person-specific biography research completed 2026-09-22.',
                         'real_name_status': 'CONFLICTING',
                         'dob_status': 'CONFIRMED',
                         'birthplace_status': 'CONFIRMED'},
          'LA Knight': {'wrestler_id': 'la-knight',
                        'real_name': 'Shaun Edward Ricker',
                        'dob': '1982-11-01',
                        'birthplace': 'Hagerstown, Maryland, United States',
                        'nationality': 'American',
                        'debut_year_company': '2003, Heartland Wrestling Association (early promotion; exact '
                                              'first match unverified)',
                        'sources': ['knight', 'knightbio'],
                        'notes': 'Person-specific biography research completed 2026-09-22.',
                        'aliases_ring_names': 'Eli Drake;Shaun Ricker;Slate Randall;Max Dupri;Deuce'},
          'Akira Tozawa': {'wrestler_id': 'akira-tozawa',
                           'real_name': 'Akira Tozawa',
                           'dob': '1985-07-22',
                           'birthplace': 'Nishinomiya, Hyogo, Japan',
                           'nationality': 'Japanese',
                           'debut_year_company': '2005-04-03, Dragon Gate',
                           'sources': ['tozawa', 'tozawabio'],
                           'notes': 'Person-specific biography research completed 2026-09-22.',
                           'aliases_ring_names': 'Tozawa;Tozawa Kengai'}},
 'reused': {'Rey Mysterio': 'rey-mysterio',
            'Chad Gable': 'chad-gable',
            'Carmelo Hayes': 'carmelo-hayes',
            'Santos Escobar': 'santos-escobar',
            'Otis': 'otis',
            'Bron Breakker': 'bron-breakker',
            'Sheamus': 'sheamus',
            'Jimmy Uso': 'jimmy-uso',
            'Andrade': 'andrade',
            'Ludwig Kaiser': 'ludwig-kaiser',
            'The Miz': 'the-miz',
            'Roman Reigns': 'roman-reigns',
            'Drew McIntyre': 'drew-mcintyre',
            'Finn Balor': 'finn-balor',
            'Shinsuke Nakamura': 'shinsuke-nakamura',
            'Jey Uso': 'jey-uso',
            'AJ Styles': 'aj-styles',
            'Braun Strowman': 'braun-strowman',
            'John Cena': 'john-cena',
            'CM Punk': 'cm-punk',
            'Seth Rollins': 'seth-rollins',
            'Dominik Mysterio': 'dominik-mysterio',
            'Sami Zayn': 'sami-zayn',
            'Damian Priest': 'damian-priest',
            'Logan Paul': 'logan-paul'},
 'no_shows': ['Akira Tozawa'],
 'entry_numbers': {'Akira Tozawa': 8},
 'entrant_notes': {'Akira Tozawa': '[substituted_by=ishowspeed] Assigned No.8; attacked before entry, '
                                   'replaced; no ring time or elimination.',
                   'IShowSpeed': 'Replaced Akira Tozawa at No.8.'},
 'disputed_credit': ['IShowSpeed', 'Sami Zayn'],
 'time_status': {'Rey Mysterio': 'CONFLICTING',
                 'Penta': 'CONFLICTING',
                 'Chad Gable': 'CONFIRMED',
                 'Carmelo Hayes': 'CONFLICTING',
                 'Santos Escobar': 'CONFLICTING',
                 'Otis': 'CONFLICTING',
                 'Bron Breakker': 'CONFLICTING',
                 'IShowSpeed': 'CONFLICTING',
                 'Sheamus': 'CONFLICTING',
                 'Jimmy Uso': 'CONFIRMED',
                 'Andrade': 'CONFLICTING',
                 'Jacob Fatu': 'CONFIRMED',
                 'Ludwig Kaiser': 'CONFLICTING',
                 'The Miz': 'CONFLICTING',
                 'Joe Hendry': 'CONFIRMED',
                 'Roman Reigns': 'CONFLICTING',
                 'Drew McIntyre': 'CONFIRMED',
                 'Finn Balor': 'CONFIRMED',
                 'Shinsuke Nakamura': 'CONFLICTING',
                 'Jey Uso': 'CONFLICTING',
                 'AJ Styles': 'CONFIRMED',
                 'Braun Strowman': 'CONFLICTING',
                 'John Cena': 'CONFIRMED',
                 'CM Punk': 'CONFLICTING',
                 'Seth Rollins': 'CONFIRMED',
                 'Dominik Mysterio': 'CONFLICTING',
                 'Sami Zayn': 'CONFIRMED',
                 'Damian Priest': 'CONFLICTING',
                 'LA Knight': 'CONFIRMED',
                 'Logan Paul': 'CONFLICTING'},
 'order_status': 'CONFIRMED',
 'champions': {'Bron Breakker': ['Intercontinental Championship',
                                 'Intercontinental/United States',
                                 '2024-10-21'],
               'Shinsuke Nakamura': ['United States Championship',
                                     'Intercontinental/United States',
                                     '2024-11-30'],
               'Joe Hendry': ['TNA World Championship', 'World', '2025-01-19']},
 'champions_complete': True,
 'champion_sources': ['ic', 'us', 'tna'],
 'surprises': ['IShowSpeed', 'Joe Hendry', 'AJ Styles'],
 'celebrities': ['IShowSpeed'],
 'non_full_time': ['IShowSpeed', 'John Cena', 'Logan Paul', 'Roman Reigns'],
 'flags': [{'table': 'entrants',
            'record': 'akira-tozawa;ishowspeed',
            'field': 'documented_substitution',
            'type': 'needs_human_judgement',
            'description': 'Tozawa was assigned slot8 but attacked before entering; IShowSpeed replaced him. '
                           'Retain both at8, Tozawa elim_number_status=N/A and no time/elimination row, per '
                           'latest user rule6 and Test/Foley F175. This supersedes replacement-only '
                           'Lana/Lynch F392 for this new event. Unlike Rey2023 F426, the slot was filled. '
                           'Approved continuation after proposing this representation. Validator explicitly '
                           'checks sourced substitution marker. 31 records,30 slots,30 actual competitors. '
                           'WWE recap says Tozawa7, an internal typo against Breakker7 and Speed8 in its '
                           'stats.',
            'sources': ['official', 'recap', 'f4w'],
            'status': 'resolved'},
           {'table': 'eliminations',
            'record': 'ishowspeed;sami-zayn',
            'field': 'eliminator_wrestler_id',
            'type': 'conflicting_sources',
            'description': 'WWE credits Otis alone for Speed and Jey Uso alone for Sami. F4W credits '
                           'Breakker+Otis for Speed and Jimmy Uso+AJ Styles for Sami. Retain WWE '
                           'victim-level credits and preserve alternatives.',
            'sources': ['official', 'f4w'],
            'status': 'open'},
           {'table': 'eliminations',
            'record': 'ishowspeed',
            'field': 'eliminator_wrestler_id',
            'type': 'needs_human_judgement',
            'description': 'Already-eliminated Otis receives official credit for eliminating Speed, '
                           'following Kross/Lashley2024 F431 and Finn/Edge2023 F427, unlike uncredited AOP '
                           'narrative interference2020.',
            'sources': ['official', 'f4w'],
            'status': 'resolved'},
           {'table': 'entrants;events',
            'record': 'RR2025M',
            'field': 'ring_time;duration_total',
            'type': 'conflicting_sources',
            'description': 'WWE/independent Cageside times: Rey Mysterio 24:41/24:39; Penta 42:05/42:04; '
                           'Carmelo Hayes 06:59/06:58; Santos Escobar 05:42/05:41; Otis 09:43/05:41; Bron '
                           'Breakker 22:26/22:25; IShowSpeed 00:56/00:57; Sheamus 15:38/15:40; Andrade '
                           '03:17/03:18; Ludwig Kaiser 00:06/00:05; The Miz 05:25/05:24; Roman Reigns '
                           '37:15/37:14; Shinsuke Nakamura 03:17/03:20; Jey Uso 36:59/37:01; Braun Strowman '
                           '02:12/02:16; CM Punk 18:46/18:45; Dominik Mysterio 04:09/04:10; Damian Priest '
                           '06:14/06:15; Logan Paul 11:19/11:20. Retain WWE times including Otis09:43 '
                           'versus05:41. Independent duration80:10 versus Wikipedia80:15; use higher-tier '
                           'Cageside80:10.',
            'sources': ['official', 'timing', 'wiki'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'penta',
            'field': 'real_name;debut_year_company',
            'type': 'unverified',
            'description': 'Dedicated searches did not find a reliably disclosed real name or exact first '
                           'promotion. Store sourced2007 independent debut; real_name blank. Masked identity '
                           'is not another historic Pentagon performer.',
            'sources': ['penta'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'jacob-fatu',
            'field': 'dob;birthplace',
            'type': 'conflicting_sources',
            'description': 'English Wikipedia lead gives March7 but infobox and SDH April18,1992. English '
                           'gives Sacramento while German gives San Francisco; SDH gives only California. '
                           'Retain April18 and Sacramento, flag both conflicts.',
            'sources': ['fatu', 'fatubio', 'fatuother'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'joe-hendry',
            'field': 'real_name',
            'type': 'conflicting_sources',
            'description': 'Wikipedia and WrestlingProfiles give Joe Samuel Hendry; SDH expands to Joseph '
                           'Samuel Hendry. Store Joe Samuel per higher-tier reference.',
            'sources': ['hendry', 'hendrybio', 'hendryother'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'la-knight',
            'field': 'debut_year_company',
            'type': 'unverified',
            'description': '2003 and early HWA work corroborated. Wikipedia February15 debut precedes its '
                           'March17 training-start narrative; retain year and early company without an '
                           'unsupported exact first-match date.',
            'sources': ['knight', 'knightbio'],
            'status': 'open'},
           {'table': 'events',
            'record': 'RR2025M',
            'field': 'attendance_official',
            'type': 'conflicting_sources',
            'description': 'WWE release reports70,342; event reference/broadcast figure70,347. Retain '
                           'official press release70,342; do not treat ticket distribution as actual '
                           'attendance.',
            'sources': ['attendance', 'wiki'],
            'status': 'open'},
           {'table': 'entrants',
            'record': 'RR2025M',
            'field': 'surprise_entrant',
            'type': 'needs_human_judgement',
            'description': 'Classify unadvertised replacement Speed, TNA crossover Hendry and injury return '
                           'AJ Styles as surprises; advertised Penta and John Cena are not surprise entries. '
                           'Follow2024 F438 distinction.',
            'sources': ['official', 'recap'],
            'status': 'resolved'}],
 'event_extra': {'attendance_official': '70342'},
 'moments': [{'category': 'notable_absence_or_substitution',
              'title': 'IShowSpeed replaces attacked Akira Tozawa',
              'people': ['Akira Tozawa', 'IShowSpeed'],
              'description': 'Both assigned and actual entrant retained at slot8.',
              'sources': ['official', 'recap']},
             {'category': 'milestone_first',
              'title': 'Jey Uso wins his first Royal Rumble',
              'people': ['Jey Uso', 'John Cena'],
              'description': 'Uso last eliminated Cena to earn a WrestleMania title match.',
              'sources': ['official', 'wiki']},
             {'category': 'record',
              'title': 'Longest Royal Rumble match to date',
              'people': ['Jey Uso'],
              'description': 'Independent timing80:10 exceeds the2018 Greatest Royal Rumble; duration '
                             'disagreement flagged.',
              'sources': ['timing']},
             {'category': 'controversy',
              'title': 'Penta early floor-contact dispute',
              'people': ['Penta', 'Rey Mysterio'],
              'description': 'Independent analysis questions an early apparent two-foot contact; no official '
                             'elimination was ruled, so retain later Finn Balor elimination.',
              'sources': ['timing', 'official']},
             {'category': 'storyline_moment',
              'title': 'Rollins attacks Reigns after elimination',
              'people': ['Seth Rollins', 'Roman Reigns', 'CM Punk'],
              'description': 'Punk eliminated Rollins and Reigns; Rollins attacked Reigns afterward.',
              'sources': ['official', 'recap']}],
 'notes': '31 entrant records include scheduled no-show Tozawa and replacement Speed sharing slot8;30 '
          'physical competitors. No historical records changed.'}

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
ENTRY_NUMBERS.update(SPEC.get('entry_numbers',{}))
survival={r[0]:r[2] for r in SPEC['rows']}
ELIM_ORDER=[r[0] for r in sorted([r for r in SPEC['rows'] if isinstance(r[1],int)],key=lambda r:r[1])]
elim_number={n:i+1 for i,n in enumerate(ELIM_ORDER)}
assert all(elim_number[r[0]]==r[1] for r in SPEC['rows'] if isinstance(r[1],int))
NO_SHOWS=set(SPEC.get('no_shows',[])); WINNER=SPEC['winner']
assert len(all_names)==len(set(all_names))
assert set(ENTRY_NUMBERS.values())==set(range(1,31))
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
# A substituted scheduled entrant may be appended after the 30 physical entrants.
event_row['final_entrant_id']=wrestler_ids[next(n for n in all_names if ENTRY_NUMBERS[n]==max(ENTRY_NUMBERS.values()) and n not in NO_SHOWS)]
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
