# -*- coding: utf-8 -*-
"""Build RR2024M. Researched 2026-09-22.
Uses the section order and row-construction pattern of build_2020_men.py;
self-elimination handling follows build_2020_women.py. Flags explain all
identity/credit precedents and source discrepancies. Single-source times and
biography fields remain PROBABLE. Unknown/not-applicable fields are blank
except the documented no-show sentinel. Global IDs are allocated afresh.
Run against a copy first, rebuild derived tables, validate, then apply the
identical script to live data. Refuses to append an already-present event.
"""
SPEC = {'event_id': 'RR2024M',
 'division': 'M',
 'date': '2024-01-27',
 'venue': 'Tropicana Field',
 'city': 'St. Petersburg, Florida',
 'country': 'United States',
 'duration': '1:08:12',
 'duration_status': 'CONFLICTING',
 'winner': 'Cody Rhodes',
 'reward': 'World championship match at WrestleMania XL.',
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
              "Cageside Seats: independently timed 2024 men's Royal Rumble",
              'reference_site',
              'https://www.cagesideseats.com/wwe/2024/1/30/24055281/wwe-royal-rumble-2024-mens-survival-times-complete-list-iron-man-jey-uso-mcdonagh-low-cm-punk-return',
              7,
              'Reputable wrestling publication',
              ''],
             ['tag',
              'WWE: World Tag Team Championship history',
              'official_wwe',
              'https://www.wwe.com/titlehistory/raw-tag-team-championship',
              1,
              'WWE / official sources',
              ''],
             ['ic',
              'WWE: Intercontinental Championship history',
              'official_wwe',
              'https://www.wwe.com/titlehistory/intercontinental-championship',
              1,
              'WWE / official sources',
              ''],
             ['bio0',
              'Grayson Waller — individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Grayson_Waller',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio1',
              'Carmelo Hayes — individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Carmelo_Hayes',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio2',
              'Ludwig Kaiser — individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Ludwig_Kaiser',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio3',
              'Bronson Reed — individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Bronson_Reed',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio4',
              'Ivar — individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Ivar_(wrestler)',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio5',
              'Bron Breakker — individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Bron_Breakker',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio6',
              'Pat McAfee — individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Pat_McAfee',
              10,
              'Wikipedia/reference sites',
              ''],
             ['bio7',
              'JD McDonagh — individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/JD_McDonagh',
              10,
              'Wikipedia/reference sites',
              ''],
             ['hayes',
              'Carmelo Hayes: dedicated profile',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/carmelo-hayes',
              12,
              'Other statistical/history site',
              ''],
             ['hayesdebut',
              'Carmelo Hayes career biography',
              'reference_site',
              'https://realprowrestling.com/carmelo-hayes-career-biography-statistics-accomplishments-and-information/',
              12,
              'Other statistical/history site',
              ''],
             ['hayesconflict',
              'German Wikipedia: Carmelo Hayes',
              'reference_site',
              'https://de.wikipedia.org/wiki/Carmelo_Hayes',
              10,
              'Wikipedia/reference sites',
              ''],
             ['jddebut',
              'OWW: Jordan Devlin career results',
              'reference_site',
              'https://www.onlineworldofwrestling.com/profile/jordan-devlin/',
              12,
              'Other statistical/history site',
              ''],
             ['patdebut',
              'IWTV: IWA East Coast Scarcade, March 22 2009',
              'reference_site',
              'https://independentwrestling.tv/events/iwa-east-coast-scarcade-dZvMjBZ4la',
              12,
              'Other statistical/history site',
              ''],
             ['patbio',
              'Pro Football Reference: Pat McAfee',
              'reference_site',
              'https://www.pro-football-reference.com/players/M/McAfPa44.htm',
              12,
              'Other statistical/history site',
              ''],
             ['punk',
              'WWE Raw results January 29 2024',
              'official_wwe',
              'https://www.wwe.com/shows/raw/2024-01-29/article/results',
              1,
              'WWE / official sources',
              ''],
             ['hof',
              'WWE Hall of Fame registry',
              'reference_site',
              'https://en.wikipedia.org/wiki/WWE_Hall_of_Fame',
              10,
              'Wikipedia/reference sites',
              '']],
 'match_sources': ['official', 'wiki', 'recap'],
 'event_sources': ['official', 'wiki', 'recap', 'timing'],
 'rows': [['Jey Uso', 23, '50:55', ['Gunther']],
          ['Jimmy Uso', 12, '34:09', ['Bron Breakker']],
          ['Grayson Waller', 1, '04:05', ['Carmelo Hayes']],
          ['Andrade', 8, '22:59', ['Bronson Reed']],
          ['Carmelo Hayes', 6, '17:06', ['Finn Balor']],
          ['Shinsuke Nakamura', 9, '20:51', ['Cody Rhodes']],
          ['Santos Escobar', 2, '06:37', ['Carlito']],
          ['Karrion Kross', 4, '06:20', ['Bobby Lashley']],
          ['Dominik Mysterio', 21, '33:19', ['CM Punk']],
          ['Carlito', 3, '02:23', ['Bobby Lashley']],
          ['Bobby Lashley', 5, '01:34', ['Karrion Kross']],
          ['Ludwig Kaiser', 10, '09:29', ['Kofi Kingston']],
          ['Austin Theory', 7, '03:58', ['Cody Rhodes']],
          ['Finn Balor', 13, '11:21', ['Bron Breakker']],
          ['Cody Rhodes', None, '43:21', []],
          ['Bronson Reed', 14, '10:39', ['Omos']],
          ['Kofi Kingston', 11, '03:34', ['Gunther']],
          ['Gunther', 28, '30:10', ['Cody Rhodes']],
          ['Ivar', 15, '04:57', ['Bron Breakker']],
          ['Bron Breakker', 18, '05:19', ['Dominik Mysterio']],
          ['Omos', 17, '02:43', ['Bron Breakker']],
          ['Pat McAfee', 16, '00:38', ['Pat McAfee']],
          ['JD McDonagh', 19, '00:03', ['Jey Uso']],
          ['R-Truth', 20, '02:56', ['Damian Priest']],
          ['The Miz', 22, '06:06', ['Gunther']],
          ['Damian Priest', 25, '10:24', ['Sami Zayn']],
          ['CM Punk', 29, '21:45', ['Cody Rhodes']],
          ['Ricochet', 24, '05:10', ['Drew McIntyre']],
          ['Drew McIntyre', 27, '09:52', ['CM Punk']],
          ['Sami Zayn', 26, '03:19', ['Drew McIntyre']]],
 'bios': {'Grayson Waller': {'wrestler_id': 'grayson-waller',
                             'real_name': 'Matthew Farrelly',
                             'dob': '1990-03-21',
                             'birthplace': 'Sydney, New South Wales, Australia',
                             'nationality': 'Australian',
                             'debut_year_company': '2017-04-15, Newcastle Pro Wrestling',
                             'aliases_ring_names': 'Matty Wahlberg',
                             'notes': 'Individual real-name, DOB, birthplace, nationality and debut research '
                                      'completed 2026-09-22.',
                             'sources': ['bio0']},
          'Carmelo Hayes': {'wrestler_id': 'carmelo-hayes',
                            'real_name': 'Christian Brigham',
                            'dob': '1994-08-01',
                            'birthplace': 'Framingham, Massachusetts, United States',
                            'nationality': 'American',
                            'debut_year_company': '2014-04-12, Chaotic Wrestling',
                            'aliases_ring_names': 'Christian Casanova',
                            'notes': 'Individual real-name, DOB, birthplace, nationality and debut research '
                                     'completed 2026-09-22.',
                            'sources': ['bio1', 'hayes', 'hayesdebut', 'hayesconflict'],
                            'birthplace_status': 'CONFLICTING'},
          'Ludwig Kaiser': {'wrestler_id': 'ludwig-kaiser',
                            'real_name': 'Marcel Barthel',
                            'dob': '1990-07-08',
                            'birthplace': 'Pinneberg, Schleswig-Holstein, Germany',
                            'nationality': 'German',
                            'debut_year_company': '2008-03-01, NFC New Years Fight Night II',
                            'aliases_ring_names': 'Marcel Barthel;Axel Dieter Jr.',
                            'notes': 'Individual real-name, DOB, birthplace, nationality and debut research '
                                     'completed 2026-09-22.',
                            'sources': ['bio2']},
          'Bronson Reed': {'wrestler_id': 'bronson-reed',
                           'real_name': 'Jermaine Haley',
                           'dob': '1988-08-25',
                           'birthplace': 'Adelaide, South Australia, Australia',
                           'nationality': 'Australian',
                           'debut_year_company': '2007; Australian independent circuit (first promotion not '
                                                 'established)',
                           'aliases_ring_names': 'Jonah;Jonah Rock;J-Rock',
                           'notes': 'Individual real-name, DOB, birthplace, nationality and debut research '
                                    'completed 2026-09-22.',
                           'sources': ['bio3']},
          'Ivar': {'wrestler_id': 'ivar',
                   'real_name': 'Todd James Smith',
                   'dob': '1984-03-03',
                   'birthplace': 'Lynn, Massachusetts, United States',
                   'nationality': 'American',
                   'debut_year_company': '2001; New England independent circuit (first promotion not '
                                         'established)',
                   'aliases_ring_names': 'Hanson;Todd Smith;Handsome Johnny',
                   'notes': 'Individual real-name, DOB, birthplace, nationality and debut research completed '
                            '2026-09-22.',
                   'sources': ['bio4']},
          'Bron Breakker': {'wrestler_id': 'bron-breakker',
                            'real_name': 'Bronson Rechsteiner',
                            'dob': '1997-10-24',
                            'birthplace': 'Woodstock, Georgia, United States',
                            'nationality': 'American',
                            'debut_year_company': '2020-10-08, AWF/WOW WrestleJam 8',
                            'aliases_ring_names': 'Bronson Rechsteiner',
                            'notes': 'Individual real-name, DOB, birthplace, nationality and debut research '
                                     'completed 2026-09-22.',
                            'sources': ['bio5']},
          'Pat McAfee': {'wrestler_id': 'pat-mcafee',
                         'real_name': 'Patrick Justin McAfee',
                         'dob': '1987-05-02',
                         'birthplace': 'Plum, Pennsylvania, United States',
                         'nationality': 'American',
                         'debut_year_company': '2009-03-22, IWA East Coast',
                         'aliases_ring_names': '',
                         'notes': 'Individual real-name, DOB, birthplace, nationality and debut research '
                                  'completed 2026-09-22.',
                         'sources': ['bio6', 'patdebut', 'patbio']},
          'JD McDonagh': {'wrestler_id': 'jd-mcdonagh',
                          'real_name': 'Jordan Devlin',
                          'dob': '1990-03-15',
                          'birthplace': 'Bray, County Wicklow, Ireland',
                          'nationality': 'Irish',
                          'debut_year_company': '2006-05-28, NWA Ireland',
                          'aliases_ring_names': 'Jordan Devlin;Frank David;Aguila II',
                          'notes': 'Individual real-name, DOB, birthplace, nationality and debut research '
                                   'completed 2026-09-22.',
                          'sources': ['bio7', 'jddebut']}},
 'reused': {'Jey Uso': 'jey-uso',
            'Jimmy Uso': 'jimmy-uso',
            'Andrade': 'andrade',
            'Shinsuke Nakamura': 'shinsuke-nakamura',
            'Santos Escobar': 'santos-escobar',
            'Karrion Kross': 'karrion-kross',
            'Dominik Mysterio': 'dominik-mysterio',
            'Carlito': 'carlito',
            'Bobby Lashley': 'bobby-lashley',
            'Austin Theory': 'austin-theory',
            'Finn Balor': 'finn-balor',
            'Cody Rhodes': 'cody-rhodes',
            'Kofi Kingston': 'kofi-kingston',
            'Gunther': 'gunther',
            'Omos': 'omos',
            'R-Truth': 'r-truth',
            'The Miz': 'the-miz',
            'Damian Priest': 'damian-priest',
            'CM Punk': 'cm-punk',
            'Ricochet': 'ricochet',
            'Drew McIntyre': 'drew-mcintyre',
            'Sami Zayn': 'sami-zayn'},
 'champions': {'Finn Balor': ['Undisputed WWE Tag Team Championship',
                              'Tag Team',
                              '2023-10-16',
                              'damian-priest'],
               'Damian Priest': ['Undisputed WWE Tag Team Championship',
                                 'Tag Team',
                                 '2023-10-16',
                                 'finn-balor'],
               'Gunther': ['Intercontinental Championship', 'Intercontinental/United States', '2022-06-10']},
 'champions_complete': True,
 'champion_sources': ['tag', 'ic'],
 'surprises': ['Andrade', 'Carmelo Hayes', 'Bron Breakker', 'Omos', 'Pat McAfee', 'Sami Zayn'],
 'non_full_time': ['Pat McAfee'],
 'celebrities': ['Pat McAfee'],
 'time_status': {'Jey Uso': 'CONFIRMED',
                 'Jimmy Uso': 'CONFLICTING',
                 'Grayson Waller': 'CONFLICTING',
                 'Andrade': 'CONFLICTING',
                 'Carmelo Hayes': 'CONFIRMED',
                 'Shinsuke Nakamura': 'CONFLICTING',
                 'Santos Escobar': 'CONFIRMED',
                 'Karrion Kross': 'CONFLICTING',
                 'Dominik Mysterio': 'CONFLICTING',
                 'Carlito': 'CONFIRMED',
                 'Bobby Lashley': 'CONFIRMED',
                 'Ludwig Kaiser': 'CONFIRMED',
                 'Austin Theory': 'CONFLICTING',
                 'Finn Balor': 'CONFIRMED',
                 'Cody Rhodes': 'CONFLICTING',
                 'Bronson Reed': 'CONFIRMED',
                 'Kofi Kingston': 'CONFIRMED',
                 'Gunther': 'CONFLICTING',
                 'Ivar': 'CONFLICTING',
                 'Bron Breakker': 'CONFIRMED',
                 'Omos': 'CONFLICTING',
                 'Pat McAfee': 'CONFIRMED',
                 'JD McDonagh': 'CONFIRMED',
                 'R-Truth': 'CONFLICTING',
                 'The Miz': 'CONFLICTING',
                 'Damian Priest': 'CONFIRMED',
                 'CM Punk': 'CONFIRMED',
                 'Ricochet': 'CONFLICTING',
                 'Drew McIntyre': 'CONFLICTING',
                 'Sami Zayn': 'CONFIRMED'},
 'order_status': 'PROBABLE',
 'flags': [{'table': 'eliminations',
            'record': 'bobby-lashley',
            'field': 'eliminator_wrestler_id',
            'type': 'needs_human_judgement',
            'description': 'Kross eliminated Lashley after Kross had already been eliminated. WWE explicitly '
                           'credits Kross, so retain that credit following Finn Balor/Edge RR2023M (F427) '
                           'and Omos RR2021M. Unlike AOP RR2020M (F397), this is an official '
                           'eliminator-of-record, not uncredited narrative assistance.',
            'sources': ['official', 'wiki', 'recap'],
            'status': 'resolved'},
           {'table': 'eliminations;entrants',
            'record': 'pat-mcafee',
            'field': 'self_eliminated;wrestlers_eliminated_count',
            'type': 'needs_human_judgement',
            'description': 'McAfee entered and then jumped out: a self-elimination, not a no-show. Follow '
                           'Santina RR2020W: self-referential elimination row, is_self_elimination TRUE, '
                           "is_solo FALSE, zero credit for eliminating another wrestler. Wikipedia's tally "
                           'gives McAfee one; database credits deliberately exclude self-eliminations. Event '
                           'eliminators_count also excludes self-only eliminators.',
            'sources': ['official', 'wiki', 'recap'],
            'status': 'resolved'},
           {'table': 'eliminations',
            'record': 'bron-breakker;omos',
            'field': 'eliminator_wrestler_id',
            'type': 'conflicting_sources',
            'description': "WWE's Bron Breakker Eliminated cell lists Bron Breakker himself instead of Omos. "
                           "WWE's Omos Eliminated By cell says Bron Breakker, and the independent event "
                           'table agrees. Use victim-level credits: Breakker eliminates Jimmy Uso, Finn '
                           'Balor, Ivar and Omos; Dominik eliminates Breakker. No Breakker self-elimination '
                           'row.',
            'sources': ['official', 'wiki'],
            'status': 'resolved'},
           {'table': 'entrants;events',
            'record': 'RR2024M',
            'field': 'ring_time;duration_total',
            'type': 'conflicting_sources',
            'description': 'WWE official versus independent Cageside timing, respectively: Jimmy Uso '
                           '34:09/34:08; Grayson Waller 04:05/04:06; Andrade 22:59/23:00; Shinsuke Nakamura '
                           '20:51/20:50; Karrion Kross 06:20/06:21; Dominik Mysterio 33:19/33:20; Austin '
                           'Theory 03:58/03:56; Cody Rhodes 43:21/43:20; Gunther 30:10/30:11; Ivar '
                           '04:57/04:58; Omos 02:43/02:42; R-Truth 02:56/02:57; The Miz 06:06/06:07; '
                           'Ricochet 05:10/05:11; Drew McIntyre 09:52/09:51. Retain WWE individual times. '
                           'Cageside full-match duration 68:12 versus Wikipedia 68:25; use footage-derived '
                           '68:12 (tier 7 above tier 10). Cageside states a roughly two-second measurement '
                           'margin.',
            'sources': ['official', 'wiki', 'timing'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'carmelo-hayes',
            'field': 'birthplace',
            'type': 'conflicting_sources',
            'description': 'English Wikipedia and SmackDown Hotel give Framingham; German Wikipedia gives '
                           'Worcester, also a billed hometown. Store Framingham; preserve the competing '
                           'birthplace claim.',
            'sources': ['bio1', 'hayes', 'hayesconflict'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'pat-mcafee',
            'field': 'debut_year_company',
            'type': 'conflicting_sources',
            'description': "Wikipedia infobox gives 2020, but its narrative and IWTV's dated Scarcade card "
                           'establish an earlier match against Warpig on 2009-03-22. Store the earliest '
                           'documented wrestling match (IWA East Coast), distinguishing it from his 2020 WWE '
                           'in-ring debut.',
            'sources': ['bio6', 'patdebut'],
            'status': 'resolved'},
           {'table': 'wrestlers',
            'record': 'bronson-reed;ivar',
            'field': 'debut_year_company',
            'type': 'unverified',
            'description': "Dedicated debut searches established Reed's 2007 Australian independent debut "
                           "and Ivar's 2001 New England debut, but did not firmly establish either exact "
                           'first promotion. Retain the sourced year/circuit without naming an unverified '
                           'company.',
            'sources': ['bio3', 'bio4'],
            'status': 'open'},
           {'table': 'entrants',
            'record': 'RR2024M',
            'field': 'surprise_entrant;ring_time_status',
            'type': 'needs_human_judgement',
            'description': 'Surprise classification includes unadvertised return, NXT and commentator '
                           'entries: Andrade, Carmelo Hayes, Bron Breakker, Omos, Pat McAfee and Sami Zayn. '
                           'CM Punk was advertised and is not a surprise merely because this was his first '
                           'televised WWE match in a decade. Wikipedia reproduces WWE times, so only '
                           'independent Cageside agreement counts toward CONFIRMED timing.',
            'sources': ['official', 'wiki', 'recap', 'timing'],
            'status': 'resolved'}],
 'moments': [{'category': 'record',
              'title': 'Cody Rhodes wins consecutive Rumbles',
              'people': ['Cody Rhodes'],
              'description': 'Rhodes followed his 2023 victory by last eliminating CM Punk.',
              'sources': ['recap', 'wiki'],
              'status': 'CONFIRMED'},
             {'category': 'storyline_moment',
              'title': 'The Usos open against each other',
              'people': ['Jey Uso', 'Jimmy Uso'],
              'description': 'The brothers started at entries one and two after their split.',
              'sources': ['recap'],
              'status': 'PROBABLE'},
             {'category': 'other',
              'title': 'Pat McAfee enters, then eliminates himself',
              'people': ['Pat McAfee', 'Omos'],
              'description': 'McAfee left commentary for entry 22, entered the ring and jumped out.',
              'sources': ['official', 'recap']},
             {'category': 'injury_or_incident',
              'title': 'CM Punk suffers a triceps injury',
              'people': ['CM Punk'],
              'description': 'Punk reached the final two; on the following Raw he disclosed a triceps injury '
                             'sustained in the Rumble.',
              'sources': ['punk', 'wiki'],
              'status': 'CONFIRMED'}],
 'notes': 'Original through-2023 records preserved. Exact elimination order from event reference table is '
          'PROBABLE; official victim-level elimination credits cross-checked. No footage-derived entrance or '
          'elimination-clock values invented.'}

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
        assert wid not in existing_ids and not matches, (name,matches)
        same_person=[r['wrestler_id'] for r in existing if b.get('real_name') and norm(r['real_name'])==norm(b['real_name'])]
        assert not same_person or b.get('character_split'), (name,'unreviewed same-person identity',same_person)
        values={k:v for k,v in b.items() if k in TABLES['wrestlers.csv']}
        values.update(ring_name=name,gender=SPEC['division'],source_ids=refs(b['sources']))
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
