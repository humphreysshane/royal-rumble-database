# -*- coding: utf-8 -*-
"""Build RR2025W. Researched 2026-09-22.
Uses the section order and row-construction pattern of build_2020_men.py;
self-elimination handling follows build_2020_women.py. Flags explain all
identity/credit precedents and source discrepancies. Single-source times and
biography fields remain PROBABLE. Unknown/not-applicable fields are blank
except the documented no-show sentinel. Global IDs are allocated afresh.
Run against a copy first, rebuild derived tables, validate, then apply the
identical script to live data. Refuses to append an already-present event.
"""
SPEC = {'event_id': 'RR2025W',
 'division': 'W',
 'date': '2025-02-01',
 'venue': 'Lucas Oil Stadium',
 'city': 'Indianapolis, Indiana',
 'country': 'United States',
 'duration': '1:10:20',
 'duration_status': 'CONFLICTING',
 'winner': 'Charlotte Flair',
 'reward': 'World championship match at WrestleMania41.',
 'sources': [['official',
              'WWE official2025 match statistics',
              'official',
              'https://www.wwe.com/shows/royalrumble/article/2025-royal-rumble-match-stats',
              1,
              'WWE / official sources',
              ''],
             ['recap',
              'WWE2025 event recap',
              'official',
              'https://www.wwe.com/shows/royalrumble/2025/results',
              1,
              'WWE / official sources',
              ''],
             ['wiki',
              'Royal Rumble2025 table',
              'reference_site',
              'https://en.wikipedia.org/wiki/Royal_Rumble_(2025)',
              10,
              'Wikipedia/reference sites',
              ''],
             ['order',
              'F4W2025 women entry and elimination order',
              'reference_site',
              'https://www.f4wonline.com/news/wwe/wwe-royal-rumble-womens-entrant-order-and-eliminations/',
              7,
              'Reputable wrestling publications',
              ''],
             ['sdh',
              'SDH2025 event table',
              'reference_site',
              'https://www.thesmackdownhotel.com/events-results/ppv-special/wwe-royal-rumble-2025',
              12,
              'Other statistical/history sites',
              ''],
             ['timing',
              'Independent2025 women survival times',
              'reference_site',
              'https://www.cagesideseats.com/wwe/2025/2/2/24357454/wwe-royal-rumble-2025-womens-survival-times-complete-list-iron-woman-roxanne-perez-new-record-liv',
              7,
              'Reputable wrestling publications',
              ''],
             ['cm',
              'Cagematch2025 event',
              'reference_site',
              'https://www.cagematch.net/?id=1&nr=398090',
              4,
              'Cagematch',
              ''],
             ['attendance',
              'WWE2025 attendance release',
              'official',
              'https://www.wwe.com/article/royal-rumble-2025-generates-largest-gate-for-any-single-night-event-in-wwe-history',
              1,
              'WWE / official sources',
              ''],
             ['lyra',
              'Lyra biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Lyra_Valkyria',
              10,
              'Wikipedia/reference sites',
              ''],
             ['lyraalt',
              'Lyra alternate debut promotion spelling',
              'reference_site',
              'https://prowrestling.fandom.com/wiki/Lyra_Valkyria',
              10,
              'Wikipedia/reference sites',
              ''],
             ['lash',
              'Lash biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Lash_Legend',
              10,
              'Wikipedia/reference sites',
              ''],
             ['lashdebut',
              'Lash debut WWE205Live',
              'official',
              'https://www.wwe.com/shows/wwe-205-live/article/wwe-205-live-results-dec-10-2021',
              1,
              'WWE / official sources',
              ''],
             ['jaida',
              'Jaida biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Jaida_Parker',
              10,
              'Wikipedia/reference sites',
              ''],
             ['jaidabio',
              'Jaida SDH profile',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/jaida-parker',
              12,
              'Other statistical/history sites',
              ''],
             ['vaquer',
              'Vaquer biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Stephanie_Vaquer',
              10,
              'Wikipedia/reference sites',
              ''],
             ['vaquerbio',
              'Vaquer Luchawiki',
              'reference_site',
              'https://www.luchawiki.org/index.php/Stephanie_Vaquer',
              10,
              'Wikipedia/reference sites',
              ''],
             ['vaqueralt',
              'Vaquer alternate debut',
              'reference_site',
              'https://de.wikipedia.org/wiki/Stephanie_Vaquer',
              10,
              'Wikipedia/reference sites',
              ''],
             ['giulia',
              'Giulia biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Giulia_(wrestler)',
              10,
              'Wikipedia/reference sites',
              ''],
             ['giuliaalt',
              'Giulia alternate real-name transliteration',
              'reference_site',
              'https://de.wikipedia.org/wiki/Giulia_(Wrestlerin)',
              10,
              'Wikipedia/reference sites',
              ''],
             ['wic',
              'Lyra inaugural IC title win',
              'official',
              'https://www.youtube.com/watch?v=2cFk_XGFbx8',
              1,
              'WWE / official sources',
              ''],
             ['wus',
              'Chelsea inaugural US title win',
              'official',
              'https://www.youtube.com/watch?v=TIf0L1THAW4',
              1,
              'WWE / official sources',
              ''],
             ['nxt',
              'NXT Womens championship history',
              'official',
              'https://www.wwe.com/titlehistory/nxt-womens-championship',
              1,
              'WWE / official sources',
              ''],
             ['tag',
              'WWE Womens Tag championship history',
              'official',
              'https://www.wwe.com/classics/titlehistory/wwe-womens-tag-team-championship',
              1,
              'WWE / official sources',
              ''],
             ['naomi',
              'Naomi joins tag reign',
              'reference_site',
              'https://www.tpww.net/2024/12/wwe-smackdown-results-dec-20-2024-naomi-bianca-belair-vs-nia-jax-candice-lerae/',
              7,
              'Reputable wrestling publications',
              ''],
             ['speed',
              'Candice inaugural Speed title win',
              'official',
              'https://www.wwe.com/shows/wwe-speed/article/candice-lerae-first-ever-wwe-womens-speed-champion',
              1,
              'WWE / official sources',
              ''],
             ['speedtap',
              'Candice biography with taping date',
              'reference_site',
              'https://en.wikipedia.org/wiki/Candice_LeRae',
              10,
              'Wikipedia/reference sites',
              '']],
 'match_sources': ['official', 'order', 'wiki'],
 'event_sources': ['official', 'wiki', 'cm', 'attendance'],
 'rows': [['IYO SKY', 21, '1:06:45', ['Nia Jax']],
          ['Liv Morgan', 24, '1:07:00', ['Nia Jax']],
          ['Roxanne Perez', 29, '1:07:47', ['Charlotte Flair']],
          ['Lyra Valkyria', 2, '16:13', ['Ivy Nile']],
          ['Chelsea Green', 9, '26:52', ['Piper Niven']],
          ['B-Fab', 1, '07:20', ['Chelsea Green']],
          ['Ivy Nile', 3, '16:29', ['Maxxine Dupri']],
          ['Zoey Stark', 5, '16:58', ['Bianca Belair', 'Naomi']],
          ['Lash Legend', 8, '17:22', ['Chelsea Green']],
          ['Bianca Belair', 23, '49:17', ['Nia Jax']],
          ['Shayna Baszler', 6, '10:12', ['Bayley']],
          ['Bayley', 26, '46:59', ['Nikki Bella']],
          ['Sonya Deville', 7, '06:04', ['IYO SKY']],
          ['Maxxine Dupri', 4, '01:20', ['Zoey Stark', 'Shayna Baszler', 'Sonya Deville']],
          ['Naomi', 22, '38:04', ['Nia Jax']],
          ['Jaida Parker', 10, '06:54', ['Jordynne Grace']],
          ['Piper Niven', 14, '24:10', ['Charlotte Flair']],
          ['Natalya', 11, '17:14', ['Liv Morgan']],
          ['Jordynne Grace', 15, '22:41', ['Giulia']],
          ['Michin', 13, '16:59', ['Charlotte Flair']],
          ['Alexa Bliss', 12, '11:01', ['Liv Morgan']],
          ['Zelina Vega', 16, '18:04', ['Nia Jax']],
          ['Candice LeRae', 17, '16:32', ['Trish Stratus']],
          ['Stephanie Vaquer', 20, '19:02', ['Nia Jax']],
          ['Trish Stratus', 18, '13:13', ['Nia Jax']],
          ['Raquel Rodriguez', 19, '15:02', ['Nia Jax']],
          ['Charlotte Flair', None, '15:04', []],
          ['Giulia', 25, '10:08', ['Roxanne Perez']],
          ['Nia Jax', 28, '08:13', ['Charlotte Flair']],
          ['Nikki Bella', 27, '03:04', ['Nia Jax']]],
 'bios': {'Lyra Valkyria': {'wrestler_id': 'lyra-valkyria',
                            'real_name': 'Aoife Marie Cusack',
                            'dob': '1996-10-23',
                            'birthplace': 'Dublin, Ireland',
                            'nationality': 'Irish',
                            'debut_year_company': '2015-05-02, CCW (Celtic Cross/Celtic Championship '
                                                  'Wrestling; naming disputed)',
                            'sources': ['lyra', 'lyraalt'],
                            'notes': 'Person-specific biography research completed 2026-09-22.',
                            'aliases_ring_names': 'Aoife Valkyrie;Lady Valkyrie;Valkyrie'},
          'Lash Legend': {'wrestler_id': 'lash-legend',
                          'real_name': 'Anriel Howard',
                          'dob': '1997-05-06',
                          'birthplace': 'Atlanta, Georgia, United States',
                          'nationality': 'American',
                          'debut_year_company': '2021-12-07, WWE 205 Live (taped; aired December10)',
                          'sources': ['lash', 'lashdebut'],
                          'notes': 'Person-specific biography research completed 2026-09-22.'},
          'Jaida Parker': {'wrestler_id': 'jaida-parker',
                           'real_name': 'Tiana Lillian Marie Caffey',
                           'dob': '1999-02-12',
                           'birthplace': 'Port St. Lucie, Florida, United States',
                           'nationality': 'American',
                           'debut_year_company': '2022-10-28, WWE NXT',
                           'sources': ['jaida', 'jaidabio'],
                           'notes': 'Person-specific biography research completed 2026-09-22.',
                           'aliases_ring_names': 'Tiana Caffey',
                           'real_name_status': 'CONFIRMED',
                           'dob_status': 'CONFIRMED',
                           'birthplace_status': 'CONFIRMED'},
          'Stephanie Vaquer': {'wrestler_id': 'stephanie-vaquer',
                               'real_name': 'Ana Stephanie Vaquer González',
                               'dob': '1993-03-29',
                               'birthplace': 'San Fernando, Chile',
                               'nationality': 'Chilean',
                               'debut_year_company': '2009; Chilean independent circuit (exact first '
                                                     'promotion disputed)',
                               'sources': ['vaquer', 'vaquerbio', 'vaqueralt'],
                               'notes': 'Person-specific biography research completed 2026-09-22.',
                               'aliases_ring_names': 'Dark Angel'},
          'Giulia': {'wrestler_id': 'giulia',
                     'real_name': 'Eimi Gloria Matsudo',
                     'dob': '1994-02-21',
                     'birthplace': 'London, England, United Kingdom',
                     'nationality': 'Japanese',
                     'debut_year_company': '2017-10-29, Ice Ribbon',
                     'sources': ['giulia', 'giuliaalt'],
                     'notes': 'Person-specific biography research completed 2026-09-22.',
                     'real_name_status': 'CONFLICTING'}},
 'reused': {'IYO SKY': 'io-shirai',
            'Liv Morgan': 'liv-morgan',
            'Roxanne Perez': 'roxanne-perez',
            'Chelsea Green': 'chelsea-green',
            'B-Fab': 'b-fab',
            'Ivy Nile': 'ivy-nile',
            'Zoey Stark': 'zoey-stark',
            'Bianca Belair': 'bianca-belair',
            'Shayna Baszler': 'shayna-baszler',
            'Bayley': 'bayley',
            'Sonya Deville': 'sonya-deville',
            'Maxxine Dupri': 'maxxine-dupri',
            'Naomi': 'naomi',
            'Piper Niven': 'piper-niven',
            'Natalya': 'natalya',
            'Jordynne Grace': 'jordynne-grace',
            'Michin': 'mia-yim',
            'Alexa Bliss': 'alexa-bliss',
            'Zelina Vega': 'zelina-vega',
            'Candice LeRae': 'candice-lerae',
            'Trish Stratus': 'trish-stratus',
            'Raquel Rodriguez': 'raquel-rodriguez',
            'Charlotte Flair': 'charlotte-flair',
            'Nia Jax': 'nia-jax',
            'Nikki Bella': 'nikki-bella'},
 'disputed_credit': ['Maxxine Dupri'],
 'time_status': {'IYO SKY': 'CONFLICTING',
                 'Liv Morgan': 'CONFLICTING',
                 'Roxanne Perez': 'CONFIRMED',
                 'Lyra Valkyria': 'CONFLICTING',
                 'Chelsea Green': 'CONFLICTING',
                 'B-Fab': 'CONFLICTING',
                 'Ivy Nile': 'CONFLICTING',
                 'Zoey Stark': 'CONFLICTING',
                 'Lash Legend': 'CONFLICTING',
                 'Bianca Belair': 'CONFIRMED',
                 'Shayna Baszler': 'CONFLICTING',
                 'Bayley': 'CONFLICTING',
                 'Sonya Deville': 'CONFIRMED',
                 'Maxxine Dupri': 'CONFLICTING',
                 'Naomi': 'CONFIRMED',
                 'Jaida Parker': 'CONFIRMED',
                 'Piper Niven': 'CONFIRMED',
                 'Natalya': 'CONFIRMED',
                 'Jordynne Grace': 'CONFLICTING',
                 'Michin': 'CONFLICTING',
                 'Alexa Bliss': 'CONFIRMED',
                 'Zelina Vega': 'CONFIRMED',
                 'Candice LeRae': 'CONFLICTING',
                 'Stephanie Vaquer': 'CONFLICTING',
                 'Trish Stratus': 'CONFIRMED',
                 'Raquel Rodriguez': 'CONFLICTING',
                 'Charlotte Flair': 'CONFLICTING',
                 'Giulia': 'CONFLICTING',
                 'Nia Jax': 'CONFIRMED',
                 'Nikki Bella': 'CONFLICTING'},
 'order_status': 'CONFLICTING',
 'champions': {'Lyra Valkyria': ["Women's Intercontinental Championship",
                                 'Intercontinental/United States',
                                 '2025-01-13'],
               'Chelsea Green': ["Women's United States Championship",
                                 'Intercontinental/United States',
                                 '2024-12-14'],
               'Giulia': ["NXT Women's Championship", 'NXT', '2025-01-07'],
               'Bianca Belair': ["WWE Women's Tag Team Championship", 'Tag Team', '2024-08-31', 'naomi'],
               'Naomi': ["WWE Women's Tag Team Championship", 'Tag Team', '2024-12-20', 'bianca-belair'],
               'Candice LeRae': ["WWE Women's Speed Championship", 'Other', '2024-10-04']},
 'champions_complete': True,
 'champion_sources': ['wic', 'wus', 'nxt', 'tag', 'naomi', 'speed', 'speedtap'],
 'surprises': ['Roxanne Perez',
               'Lash Legend',
               'Jaida Parker',
               'Stephanie Vaquer',
               'Giulia',
               'Jordynne Grace',
               'Alexa Bliss',
               'Trish Stratus',
               'Nikki Bella'],
 'legends': ['Trish Stratus', 'Nikki Bella'],
 'non_full_time': ['Trish Stratus', 'Nikki Bella'],
 'flags': [{'table': 'entrants;eliminations',
            'record': 'stephanie-vaquer;naomi;raquel-rodriguez',
            'field': 'elim_number;order_in_match',
            'type': 'conflicting_sources',
            'description': 'Five-woman Nia Jax sweep: F4W/SDH order19 Raquel,20 Vaquer,21 IYO,22 Naomi,23 '
                           'Bianca. Wikipedia instead19 Vaquer,20 Naomi,21 IYO,22 Raquel,23 Bianca. Retain '
                           'higher-tier F4W sequence; credits to Nia agree.',
            'sources': ['order', 'sdh', 'wiki'],
            'status': 'open'},
           {'table': 'eliminations',
            'record': 'maxxine-dupri',
            'field': 'eliminator_wrestler_id',
            'type': 'conflicting_sources',
            'description': 'WWE explicitly names all three Pure Fusion Collective members; F4W names group, '
                           'while SDH omits Sonya. Retain WWE three-person credit, following explicit named '
                           'group credit NM111 for Nia2023.',
            'sources': ['official', 'order', 'sdh'],
            'status': 'resolved'},
           {'table': 'eliminations',
            'record': 'zelina-vega',
            'field': 'eliminator_wrestler_id',
            'type': 'needs_human_judgement',
            'description': 'Nia eliminated Zelina before Nia physically entered. Official WWE credits her, '
                           'following before-entry Big Show2012 F241 and official-record Omos2021 precedent; '
                           'no additional fictional entry or elimination.',
            'sources': ['official', 'wiki'],
            'status': 'resolved'},
           {'table': 'entrants;events',
            'record': 'RR2025W',
            'field': 'ring_time;duration_total',
            'type': 'conflicting_sources',
            'description': 'WWE/independent Cageside: IYO SKY 1:06:45/1:06:43; Liv Morgan 1:07:00/1:06:59; '
                           'Lyra Valkyria 16:13/16:17; Chelsea Green 26:52/26:50; B-Fab 07:20/07:21; Ivy '
                           'Nile 16:29/16:30; Zoey Stark 16:58/16:55; Lash Legend 17:22/17:21; Shayna '
                           'Baszler 10:12/10:11; Bayley 46:59/46:58; Maxxine Dupri 01:20/01:18; Jordynne '
                           'Grace 22:41/22:40; Michin 16:59/16:57; Candice LeRae 16:32/16:31; Stephanie '
                           'Vaquer 19:02/18:59; Raquel Rodriguez 15:02/15:00; Charlotte Flair 15:04/15:03; '
                           'Giulia 10:08/10:07; Nikki Bella 03:04/05:06. Retain official individual times, '
                           'notably Nikki03:04 vs05:06. Match duration Cagematch70:20 vs Cageside70:21; use '
                           'tier4 Cagematch70:20.',
            'sources': ['official', 'timing', 'cm'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'lyra-valkyria;stephanie-vaquer',
            'field': 'debut_year_company',
            'type': 'conflicting_sources',
            'description': 'Lyra2015-05-02 established; English calls CCW Celtic Cross while Fandom Celtic '
                           'Championship. Preserve both spellings. Vaquer2009 established; Luchawiki '
                           'February versus German December/RALL, earliest English verified matches2010/MCL. '
                           'Store year/circuit, no unsupported exact first date/company.',
            'sources': ['lyra', 'lyraalt', 'vaquer', 'vaquerbio', 'vaqueralt'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'giulia',
            'field': 'real_name',
            'type': 'conflicting_sources',
            'description': 'English Eimi Gloria Matsudo versus German Hidemi Gloria Matsudo; store Eimi and '
                           'retain transliteration disagreement.',
            'sources': ['giulia', 'giuliaalt'],
            'status': 'open'},
           {'table': 'entrants',
            'record': 'naomi;bianca-belair',
            'field': 'title_won_date;days_into_reign_at_event',
            'type': 'needs_human_judgement',
            'description': 'WWE title history treats Bianca/Jade/Naomi as one reign beginning2024-08-31. '
                           'Naomi joined2024-12-20: her personal title-won date is Dec20 while Bianca '
                           'retains Aug31. Days reflect individual acquisition, not crediting Naomi months '
                           'before she joined.',
            'sources': ['tag', 'naomi'],
            'status': 'resolved'},
           {'table': 'entrants',
            'record': 'candice-lerae',
            'field': 'title_won_date',
            'type': 'conflicting_sources',
            'description': 'Official WWE win announcement dated2024-10-09 versus match taped2024-10-04 per '
                           'biography. Use actual taping date for title_won_date, same match-date convention '
                           'as Lash/Tiffany debuts; broadcast date preserved here.',
            'sources': ['speed', 'speedtap'],
            'status': 'resolved'},
           {'table': 'events',
            'record': 'RR2025W',
            'field': 'attendance_official',
            'type': 'conflicting_sources',
            'description': 'WWE release70,342 versus broadcast/reference70,347; retain official release as '
                           'in RR2025M.',
            'sources': ['attendance', 'wiki'],
            'status': 'open'},
           {'table': 'entrants',
            'record': 'RR2025W',
            'field': 'wrestler_id;surprise_entrant',
            'type': 'needs_human_judgement',
            'description': 'IYO reuses io-shirai and Michin mia-yim, following F429/2024 same-character '
                           'precedent. Surprise set: unadvertised NXT Roxanne,Lash,Jaida,Vaquer,Giulia; new '
                           'signing Grace; returns Bliss,Stratus,Bella. Advertised Charlotte return is not '
                           'marked surprise.',
            'sources': ['recap', 'wiki'],
            'status': 'resolved'}],
 'event_extra': {'attendance_official': '70342'},
 'moments': [{'category': 'record',
              'title': 'Charlotte becomes first two-time womens Rumble winner',
              'people': ['Charlotte Flair', 'Roxanne Perez'],
              'description': 'Flair followed2020 victory by last eliminating Perez.',
              'sources': ['official', 'wiki']},
             {'category': 'record',
              'title': 'Roxanne sets womens survival record',
              'people': ['Roxanne Perez'],
              'description': 'Official and independent timing agree at1:07:47.',
              'sources': ['official', 'timing']},
             {'category': 'record',
              'title': 'Nia Jax earns nine eliminations',
              'people': ['Nia Jax'],
              'description': 'WWE names nine victims including pre-entry Zelina elimination and five-woman '
                             'sweep; all credited individually.',
              'sources': ['official', 'recap']},
             {'category': 'storyline_moment',
              'title': 'Alexa Bliss returns after two-year absence',
              'people': ['Alexa Bliss'],
              'description': 'Bliss returned at entry21; Charlotte and Hall of Famers Stratus/Bella also '
                             'returned.',
              'sources': ['recap', 'wiki']}],
 'notes': 'Five-woman sweep chronological order disputed; F4W used. No footage-derived clock times invented.'}

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
