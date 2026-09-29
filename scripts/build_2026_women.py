# -*- coding: utf-8 -*-
"""Build RR2026W. Researched 2026-09-22.
Uses the section order and row-construction pattern of build_2020_men.py;
self-elimination handling follows build_2020_women.py. Flags explain all
identity/credit precedents and source discrepancies. Single-source times and
biography fields remain PROBABLE. Unknown/not-applicable fields are blank
except the documented no-show sentinel. Global IDs are allocated afresh.
Run against a copy first, rebuild derived tables, validate, then apply the
identical script to live data. Refuses to append an already-present event.
"""
SPEC = {'event_id': 'RR2026W',
 'division': 'W',
 'date': '2026-01-31',
 'venue': 'Riyadh Season Stadium at King Abdullah Financial District',
 'city': 'Riyadh',
 'country': 'Saudi Arabia',
 'duration': '1:06:51',
 'duration_status': 'CONFLICTING',
 'winner': 'Liv Morgan',
 'reward': 'World championship match at WrestleMania42.',
 'sources': [['official',
              'WWE2026 official match statistics and recap',
              'official',
              'https://www.wwe.com/shows/royalrumble/royal-rumble-2026',
              1,
              'WWE / official sources',
              ''],
             ['order',
              'WrestleZone2026 chronological eliminations',
              'reference_site',
              'https://www.wrestlezone.com/news/1609516-wwe-royal-rumble-2026-order-of-entry-and-elimination',
              7,
              'Reputable wrestling publications',
              ''],
             ['wiki',
              'Royal Rumble2026 reference table',
              'reference_site',
              'https://en.wikipedia.org/wiki/Royal_Rumble_(2026)',
              10,
              'Wikipedia/reference sites',
              ''],
             ['cm',
              'Cagematch2026 event results and timing',
              'reference_site',
              'https://www.cagematch.net/?id=1&nr=434667',
              4,
              'Cagematch',
              ''],
             ['ars',
              'All Rumble Stats2026 women independent timing',
              'reference_site',
              'https://allrumblestats.com/events/wwe/royal-rumble/royal-rumble-2026-women/',
              12,
              'Other statistical/history sites',
              ''],
             ['kiana',
              'Kiana James individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Kiana_James',
              10,
              'Wikipedia/reference sites',
              ''],
             ['kianacm',
              'Kiana James Cagematch biography',
              'reference_site',
              'https://www.cagematch.net/?id=2&nr=25036',
              4,
              'Cagematch',
              ''],
             ['kianabio',
              'Kiana real name and nationality',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/kayla-inlay',
              12,
              'Other statistical/history sites',
              ''],
             ['kianaalt',
              'Kiana alternate published real name',
              'reference_site',
              'https://de.wikipedia.org/wiki/Kiana_James',
              10,
              'Wikipedia/reference sites',
              ''],
             ['lola',
              'Lola Vice individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Lola_Vice',
              10,
              'Wikipedia/reference sites',
              ''],
             ['loladebut',
              'Lola Vice biography differentiating debut matches',
              'reference_site',
              'https://gerweck.net/2022/11/15/valerie-loureda/',
              12,
              'Other statistical/history sites',
              ''],
             ['sol',
              'Sol Ruca individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Sol_Ruca',
              10,
              'Wikipedia/reference sites',
              ''],
             ['soldebut',
              'Sol Ruca individual biography and NXT live debut',
              'reference_site',
              'https://gerweck.net/2023/03/06/sol-ruca/',
              12,
              'Other statistical/history sites',
              ''],
             ['jacy',
              'Jacy Jayne individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Jacy_Jayne',
              10,
              'Wikipedia/reference sites',
              ''],
             ['jacycm',
              'Jacy Jayne Cagematch personal data',
              'reference_site',
              'https://www.cagematch.net/?id=2&nr=21368',
              4,
              'Cagematch',
              ''],
             ['jacyalt',
              'Jacy Jayne alternate biography',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/jacy-jayne',
              12,
              'Other statistical/history sites',
              ''],
             ['jacyofficial',
              'WWE recruits biography identifying Taylor Grado',
              'official',
              'https://www.wwe.com/shows/wwenxt/article/largest-class-in-history-reports-wwe-performance-center',
              1,
              'WWE / official sources',
              ''],
             ['kelani',
              'Kelani Jordan individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Kelani_Jordan',
              10,
              'Wikipedia/reference sites',
              ''],
             ['kelanibio',
              'Kelani Jordan OWW biography',
              'reference_site',
              'https://www.onlineworldofwrestling.com/profile/kelani-jordan/',
              12,
              'Other statistical/history sites',
              ''],
             ['kelanialt',
              'Kelani alternate debut account',
              'reference_site',
              'https://gerweck.net/2023/05/18/kelani-jordan/',
              12,
              'Other statistical/history sites',
              ''],
             ['kelanidob',
              'Kelani alternate Spanish birthday',
              'reference_site',
              'https://es.wikipedia.org/wiki/Kelani_Jordan',
              10,
              'Wikipedia/reference sites',
              ''],
             ['kelaniname',
              'Kelani full real name',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/kelani-jordan',
              12,
              'Other statistical/history sites',
              ''],
             ['rawtitles',
              'Becky and Rhea/IYO title wins Jan5',
              'official',
              'https://www.wwe.com/shows/raw/2026-01-05',
              1,
              'WWE / official sources',
              ''],
             ['giuliatitle',
              'Giulia title win Jan2',
              'official',
              'https://www.wwe.com/shows/smackdown/2026-01-02',
              1,
              'WWE / official sources',
              ''],
             ['nxttitle',
              'NXT Womens title history',
              'official',
              'https://www.wwe.com/titlehistory/nxt-womens-championship',
              1,
              'WWE / official sources',
              ''],
             ['speed',
              'Womens Speed title history',
              'official',
              'https://www.wwe.com/classics/titlehistory/wwe-womens-speed-championship',
              1,
              'WWE / official sources',
              ''],
             ['aaatitle',
              'Chelsea Green and Ethan Page win AAA mixed title',
              'reference_site',
              'https://www.tpww.net/2025/11/aaa-chelsea-green-ethan-page-wins-aaa-mixed-tag-team-titles-at-aaa-dia-de-muertos-2025-show-ethan-page-vs-el-hijo-de-dr-wagner-jr-for-aaa-latin-american-title-set-for-aaa-guerra-de-titanes-2025/',
              7,
              'Reputable wrestling publications',
              ''],
             ['aaacurrent',
              'AAA January31 title challengers report',
              'reference_site',
              'https://www.tvazteca.com/aztecadeportes/aaa-luchas-alarido-cartelera-31-enero-ac-notas/',
              7,
              'Reputable wrestling publications',
              ''],
             ['nattie',
              'Natalya introduced as Nattie at Royal Rumble',
              'reference_site',
              'https://www.fightful.com/wrestling/natalya-introduced-as-nattie-in-2026-wwe-womens-royal-rumble-match-debuts-new-theme-song/',
              7,
              'Reputable wrestling publications',
              ''],
             ['attendance',
              'Reported25000 ticket distribution',
              'reference_site',
              'https://www.pwmania.com/backstage-explanation-for-empty-seats-at-royal-rumble-2026',
              7,
              'Reputable wrestling publications',
              '']],
 'match_sources': ['official', 'order', 'wiki', 'cm'],
 'event_sources': ['official', 'cm', 'wiki', 'attendance'],
 'rows': [['Charlotte Flair', 23, '59:49', ['Lash Legend']],
          ['Alexa Bliss', 5, '13:29', ['Charlotte Flair']],
          ['Kiana James', 9, '27:30', ['Raquel Rodriguez']],
          ['Nia Jax', 4, '09:29', ['Charlotte Flair']],
          ['Ivy Nile', 3, '06:24', ['Jordynne Grace']],
          ['Lola Vice', 1, '04:32', ['Jordynne Grace']],
          ['Candice LeRae', 2, '02:13', ['Jordynne Grace']],
          ['Jordynne Grace', 8, '14:47', ['Lash Legend']],
          ['Becky Lynch', 7, '07:35', ['Nattie']],
          ['Sol Ruca', 28, '50:47', ['Tiffany Stratton']],
          ['Roxanne Perez', 12, '22:12', ['Rhea Ripley']],
          ['Maxxine Dupri', 6, '02:47', ['Becky Lynch']],
          ['Nattie', 13, '23:01', ['Liv Morgan']],
          ['Liv Morgan', None, '43:50', []],
          ['Lash Legend', 25, '38:46', ['Rhea Ripley']],
          ['Zelina', 10, '10:54', ['Giulia']],
          ['Raquel Rodriguez', 27, '35:29', ['Liv Morgan']],
          ['Chelsea Green', 11, '08:35', ['Rhea Ripley']],
          ['Giulia', 14, '15:15', ['Lyra Valkyria']],
          ['IYO SKY', 24, '27:31', ['Lash Legend']],
          ['Asuka', 15, '14:36', ['Kairi Sane']],
          ['Rhea Ripley', 26, '25:40', ['Raquel Rodriguez']],
          ['Bayley', 18, '16:22', ['Nikki Bella']],
          ['Jacy Jayne', 20, '16:11', ['Sol Ruca']],
          ['Nikki Bella', 21, '14:02', ['Lash Legend']],
          ['Lyra Valkyria', 17, '10:44', ['Brie Bella']],
          ['Kelani Jordan', 19, '09:22', ['Jacy Jayne']],
          ['Kairi Sane', 16, '01:36', ['IYO SKY']],
          ['Brie Bella', 22, '06:50', ['Lash Legend']],
          ['Tiffany Stratton', 29, '12:48', ['Liv Morgan']]],
 'bios': {'Kiana James': {'wrestler_id': 'kiana-james',
                          'real_name': 'Kayla Klingensmith',
                          'dob': '1997-05-23',
                          'birthplace': 'Sioux City, Iowa, United States',
                          'nationality': 'American',
                          'debut_year_company': '2021-09-11, All Elite Wrestling (Dark taping; aired '
                                                'September21)',
                          'sources': ['kiana', 'kianacm', 'kianabio', 'kianaalt'],
                          'notes': 'Person-specific biography research completed 2026-09-22.',
                          'aliases_ring_names': 'Kayla Inlay;Xtina Kay',
                          'real_name_status': 'CONFLICTING',
                          'dob_status': 'CONFIRMED',
                          'birthplace_status': 'CONFIRMED'},
          'Lola Vice': {'wrestler_id': 'lola-vice',
                        'real_name': 'Valerie Loureda',
                        'dob': '1998-07-19',
                        'birthplace': 'Miami, Florida, United States',
                        'nationality': 'Cuban-American',
                        'debut_year_company': '2022-10-28, WWE NXT (battle royal; first regular match '
                                              'November12)',
                        'sources': ['lola', 'loladebut'],
                        'notes': 'Person-specific biography research completed 2026-09-22.',
                        'aliases_ring_names': 'Valerie Loureda',
                        'real_name_status': 'CONFIRMED',
                        'dob_status': 'CONFIRMED',
                        'birthplace_status': 'CONFIRMED'},
          'Sol Ruca': {'wrestler_id': 'sol-ruca',
                       'real_name': 'Calyx Harmony Hampton',
                       'dob': '1999-08-26',
                       'birthplace': 'Ontario, California, United States',
                       'nationality': 'American',
                       'debut_year_company': '2022-06-24, WWE NXT',
                       'sources': ['sol', 'soldebut'],
                       'notes': 'Person-specific biography research completed 2026-09-22.',
                       'real_name_status': 'CONFIRMED',
                       'dob_status': 'CONFIRMED',
                       'birthplace_status': 'CONFIRMED'},
          'Jacy Jayne': {'wrestler_id': 'jacy-jayne',
                         'real_name': 'Taylor Grado',
                         'dob': '1996-06-02',
                         'birthplace': 'Clearwater Beach, Florida, United States',
                         'nationality': 'American',
                         'debut_year_company': '2016-06-25; first promotion not established (ACW2018 debut '
                                               'separately reported)',
                         'sources': ['jacy', 'jacycm', 'jacyalt', 'jacyofficial'],
                         'notes': 'Person-specific biography research completed 2026-09-22.',
                         'aliases_ring_names': 'Avery Taylor',
                         'real_name_status': 'CONFIRMED',
                         'dob_status': 'CONFLICTING',
                         'birthplace_status': 'CONFLICTING'},
          'Kelani Jordan': {'wrestler_id': 'kelani-jordan',
                            'real_name': 'Lea Simone Mitchell',
                            'dob': '1998-10-22',
                            'birthplace': 'Boynton Beach, Florida, United States',
                            'nationality': 'American',
                            'debut_year_company': '2022-10-28, WWE NXT (battle royal; televised match debut '
                                                  'May2023)',
                            'sources': ['kelani', 'kelanibio', 'kelanialt', 'kelanidob', 'kelaniname'],
                            'notes': 'Person-specific biography research completed 2026-09-22.',
                            'aliases_ring_names': 'Lea Mitchell',
                            'dob_status': 'CONFLICTING',
                            'birthplace_status': 'CONFIRMED'}},
 'reused': {'Charlotte Flair': 'charlotte-flair',
            'Alexa Bliss': 'alexa-bliss',
            'Nia Jax': 'nia-jax',
            'Ivy Nile': 'ivy-nile',
            'Candice LeRae': 'candice-lerae',
            'Jordynne Grace': 'jordynne-grace',
            'Becky Lynch': 'becky-lynch',
            'Roxanne Perez': 'roxanne-perez',
            'Maxxine Dupri': 'maxxine-dupri',
            'Nattie': 'natalya',
            'Liv Morgan': 'liv-morgan',
            'Lash Legend': 'lash-legend',
            'Zelina': 'zelina-vega',
            'Raquel Rodriguez': 'raquel-rodriguez',
            'Chelsea Green': 'chelsea-green',
            'Giulia': 'giulia',
            'IYO SKY': 'io-shirai',
            'Asuka': 'asuka',
            'Rhea Ripley': 'rhea-ripley',
            'Bayley': 'bayley',
            'Nikki Bella': 'nikki-bella',
            'Lyra Valkyria': 'lyra-valkyria',
            'Kairi Sane': 'kairi-sane',
            'Brie Bella': 'brie-bella',
            'Tiffany Stratton': 'tiffany-stratton'},
 'disputed_credit': ['Bayley', 'Lyra Valkyria', 'Kiana James', 'Sol Ruca'],
 'time_status': {'Charlotte Flair': 'CONFLICTING',
                 'Alexa Bliss': 'CONFIRMED',
                 'Kiana James': 'CONFLICTING',
                 'Nia Jax': 'CONFLICTING',
                 'Ivy Nile': 'CONFLICTING',
                 'Lola Vice': 'CONFLICTING',
                 'Candice LeRae': 'CONFIRMED',
                 'Jordynne Grace': 'CONFIRMED',
                 'Becky Lynch': 'CONFLICTING',
                 'Sol Ruca': 'CONFLICTING',
                 'Roxanne Perez': 'CONFLICTING',
                 'Maxxine Dupri': 'CONFLICTING',
                 'Nattie': 'CONFLICTING',
                 'Liv Morgan': 'CONFLICTING',
                 'Lash Legend': 'CONFLICTING',
                 'Zelina': 'CONFLICTING',
                 'Raquel Rodriguez': 'CONFIRMED',
                 'Chelsea Green': 'CONFLICTING',
                 'Giulia': 'CONFLICTING',
                 'IYO SKY': 'CONFIRMED',
                 'Asuka': 'CONFLICTING',
                 'Rhea Ripley': 'CONFIRMED',
                 'Bayley': 'CONFLICTING',
                 'Jacy Jayne': 'CONFIRMED',
                 'Nikki Bella': 'CONFIRMED',
                 'Lyra Valkyria': 'CONFIRMED',
                 'Kelani Jordan': 'CONFLICTING',
                 'Kairi Sane': 'CONFLICTING',
                 'Brie Bella': 'CONFLICTING',
                 'Tiffany Stratton': 'CONFLICTING'},
 'champions': {'Becky Lynch': ["Women's Intercontinental Championship",
                               'Intercontinental/United States',
                               '2026-01-05'],
               'Giulia': ["Women's United States Championship",
                          'Intercontinental/United States',
                          '2026-01-02'],
               'Rhea Ripley': ["WWE Women's Tag Team Championship", 'Tag Team', '2026-01-05', 'io-shirai'],
               'IYO SKY': ["WWE Women's Tag Team Championship", 'Tag Team', '2026-01-05', 'rhea-ripley'],
               'Jacy Jayne': ["NXT Women's Championship", 'NXT', '2025-11-18'],
               'Chelsea Green': ['AAA World Mixed Tag Team Championship',
                                 'Other',
                                 '2025-11-02',
                                 'Ethan Page']},
 'champions_complete': True,
 'champion_sources': ['rawtitles', 'giuliatitle', 'nxttitle', 'aaatitle', 'aaacurrent'],
 'surprises': ['Lola Vice', 'Sol Ruca', 'Jacy Jayne', 'Kelani Jordan', 'Brie Bella', 'Tiffany Stratton'],
 'legends': ['Brie Bella', 'Nikki Bella'],
 'non_full_time': ['Brie Bella', 'Nikki Bella'],
 'flags': [{'table': 'eliminations',
            'record': 'bayley;lyra-valkyria;kiana-james;sol-ruca',
            'field': 'eliminator_wrestler_id',
            'type': 'conflicting_sources',
            'description': 'WWE statistics credit Bayley solely to Nikki and Lyra solely to Brie; '
                           'WZ/Cagematch describe shared Bella credit. WWE narrative describes all Judgment '
                           'Day assisting with Kiana, but table credits Raquel only. WZ credits Sol to Liv '
                           'versus WWE table/recap Tiffany. Retain specific official table credits, applying '
                           'F397 assistance versus eliminator-of-record precedent.',
            'sources': ['official', 'order', 'cm', 'ars'],
            'status': 'open'},
           {'table': 'entrants;eliminations',
            'record': 'alba-fyre',
            'field': 'wrestler_id;order_in_match',
            'type': 'needs_human_judgement',
            'description': 'Alba accompanied Chelsea and was thrown out by Rhea but was not an official '
                           'entrant. As with R-Truth intrusion RR2024W, no fictional entrant or elimination '
                           'row is created; unlike Drew RR2026M, she is not named as an official eliminator '
                           'either.',
            'sources': ['official'],
            'status': 'resolved'},
           {'table': 'entrants',
            'record': 'natalya;zelina-vega;io-shirai',
            'field': 'wrestler_id;ring_name_at_time',
            'type': 'needs_human_judgement',
            'description': 'Nattie reuses natalya: same acknowledged Hart-family performer and continuing '
                           'Maxxine storyline, despite heel turn/new music. WWE explicitly counts Nattie '
                           'among all-nine-Rumble participants, supporting continuity. Zelina reuses '
                           'zelina-vega; IYO reuses io-shirai. Follow F400/F429 moniker precedent; preserve '
                           'billed names.',
            'sources': ['official', 'nattie'],
            'status': 'resolved'},
           {'table': 'entrants;events',
            'record': 'RR2026W',
            'field': 'ring_time;duration_total',
            'type': 'conflicting_sources',
            'description': 'WWE/AllRumbleStats times: Charlotte Flair 59:49/59:50; Kiana James 27:30/27:31; '
                           'Nia Jax 09:29/09:30; Ivy Nile 06:24/06:22; Lola Vice 04:32/04:30; Becky Lynch '
                           '07:35/07:37; Sol Ruca 50:47/50:50; Roxanne Perez 22:12/22:10; Maxxine Dupri '
                           '02:47/02:46; Nattie 23:01/23:02; Liv Morgan 43:50/43:52; Lash Legend '
                           '38:46/38:57; Zelina 10:54/11:55; Chelsea Green 08:35/08:36; Giulia 15:15/15:16; '
                           'Asuka 14:36/14:46; Bayley 16:22/16:30; Kelani Jordan 09:22/09:15; Kairi Sane '
                           '01:36/01:40; Brie Bella 06:50/06:52; Tiffany Stratton 12:48/12:55. Retain '
                           'official times; independent clock includes pre-entry attacks for some entrants. '
                           'Cagematch duration66:51 versus Wikipedia67:00 and AllRumbleStats66:50; store '
                           'tier4 Cagematch.',
            'sources': ['official', 'cm', 'wiki', 'ars'],
            'status': 'open'},
           {'table': 'eliminations',
            'record': 'lola-vice;candice-lerae;nia-jax;alexa-bliss',
            'field': 'order_in_match',
            'type': 'needs_video_review',
            'description': 'WWE describes Lola/Candice and Nia/Alexa as simultaneous pairs. Retain published '
                           'WZ chronological tie ordering1/2 and4/5; ordering within each pair is source '
                           'convention, not independently frame-verified. Both pairs receive one victim '
                           'record each, not additional shared eliminator credits.',
            'sources': ['official', 'order', 'cm'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'jacy-jayne',
            'field': 'dob;birthplace;debut_year_company',
            'type': 'conflicting_sources',
            'description': 'Cagematch1996-06-02 Clearwater Beach and2016-06-25 in-ring start; English '
                           'Wikipedia1995-06-02 New Jersey and2018-05-30 ACW debut; SDH1996-06-02 Tampa '
                           'and2016-07-16 career start. Store higher-tier Cagematch values. WWE recruitment '
                           'identifies Taylor Grado of Clearwater Beach. Dedicated first-company search did '
                           'not establish a2016 promotion; do not retroactively assign2018 ACW to2016.',
            'sources': ['jacycm', 'jacy', 'jacyalt', 'jacyofficial'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'kiana-james',
            'field': 'real_name',
            'type': 'conflicting_sources',
            'description': 'English/SDH Kayla Klingensmith nee Inlay versus German Kayla Klink. Store '
                           'current published Klingensmith with Inlay alias; preserve Klink alternative '
                           'rather than silently treating it as confirmed.',
            'sources': ['kiana', 'kianabio', 'kianaalt'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'kelani-jordan',
            'field': 'dob;real_name;debut_year_company',
            'type': 'conflicting_sources',
            'description': 'English/OWW birthday1998-10-22 versus Spanish1998-10-14. Use Oct22 supported by '
                           'multiple profiles, conflicting status. Full Lea Simone Mitchell is single-source '
                           'SDH (PROBABLE); other profiles shorten to Lea Mitchell. Debut2022-10-28 battle '
                           'royal versus Gerweck May9 2023 television taping; preserve distinction, not '
                           'a2023 professional start.',
            'sources': ['kelani', 'kelanibio', 'kelanialt', 'kelanidob', 'kelaniname'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'lola-vice;kiana-james',
            'field': 'debut_year_company',
            'type': 'needs_human_judgement',
            'description': 'Lola first participated in a2022-10-28 NXT battle royal before regular '
                           'six-person match Nov12; earliest participation retained. Kiana first match '
                           'taped2021-09-11, broadcastSep21; match date retained, same taping-date '
                           'convention as prior builds.',
            'sources': ['lola', 'loladebut', 'kiana', 'kianacm'],
            'status': 'resolved'},
           {'table': 'entrants',
            'record': 'chelsea-green',
            'field': 'current_champion_title;championship_partner',
            'type': 'unverified',
            'description': 'Chelsea still held AAA Mixed Tag title at Jan31 with Ethan Page after Nov2 win; '
                           'later Feb7 loss is outside event date. Partner stored as published name because '
                           'he has no wrestler_id in this Rumble database; no invented identity row solely '
                           'for a partner. Sol had vacated Speed Oct28 and is not a reigning champion.',
            'sources': ['aaatitle', 'aaacurrent', 'speed'],
            'status': 'resolved'},
           {'table': 'events',
            'record': 'RR2026W',
            'field': 'attendance_official;attendance_reported',
            'type': 'conflicting_sources',
            'description': 'Same event as RR2026M: Cagematch estimates22500 versus reports of25000 tickets '
                           'attributed to WWE sources. No direct official figure located; official blank, '
                           'reported22500 with estimate qualifier.',
            'sources': ['cm', 'attendance', 'wiki'],
            'status': 'open'},
           {'table': 'entrants',
            'record': 'RR2026W',
            'field': 'surprise_entrant',
            'type': 'needs_human_judgement',
            'description': 'NXT guests Lola,Sol,Jacy,Kelani and returns Brie/Tiffany form surprise set; '
                           'standard roster entrants not marked simply for first Rumble. Brie and Nikki are '
                           'non-full-time Hall-of-Fame returns; company debut not inferred from Rumble '
                           'debut.',
            'sources': ['official', 'wiki'],
            'status': 'resolved'}],
 'event_extra': {'attendance_reported': '22500'},
 'moments': [{'category': 'milestone_first',
              'title': 'Liv Morgan wins her first Royal Rumble',
              'people': ['Liv Morgan', 'Tiffany Stratton'],
              'description': 'Morgan last eliminated returning Stratton after two earlier runner-up '
                             'finishes.',
              'sources': ['official', 'wiki']},
             {'category': 'record',
              'title': 'Liv and Nattie continue all-event participation',
              'people': ['Liv Morgan', 'Nattie'],
              'description': 'WWE identifies them as the only women to participate in all nine womens Royal '
                             'Rumbles through2026.',
              'sources': ['official']},
             {'category': 'storyline_moment',
              'title': 'Bella Twins reunite in the Rumble',
              'people': ['Brie Bella', 'Nikki Bella'],
              'description': 'Brie returned at29 and reunited with Nikki; WWE assigns Lyra to Brie and '
                             'Bayley to Nikki.',
              'sources': ['official', 'wiki']},
             {'category': 'storyline_moment',
              'title': 'Alba Fyre intrudes without becoming an entrant',
              'people': ['alba-fyre', 'Rhea Ripley', 'Chelsea Green'],
              'description': 'Rhea threw out Chelsea companion Alba; this is a narrative incident, not a '
                             'thirtieth elimination.',
              'sources': ['official']},
             {'category': 'storyline_moment',
              'title': 'Lash Legend leads elimination count',
              'people': ['Lash Legend'],
              'description': 'Five official victims: Grace, Nikki, Brie, Charlotte and IYO.',
              'sources': ['official', 'ars']}],
 'notes': 'Published simultaneous pairs keep source tie ordering; no frame-perfect elimination order '
          'claimed. Attendance estimate and biography disagreements retained. Five new wrestlers '
          'individually researched; unknown entrance and elimination clock times remain blank.'}

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
for name,wid in SPEC.get('external_eliminators',{}).items():
    assert name not in wrestler_ids and wid in existing_ids
    wrestler_ids[name]=wid

# Entrant/elimination construction follows build_2020_men.py and the women's self-elimination convention.
entrant_rows=[]; elim_rows=[]
for name in all_names:
    wid=wrestler_ids[name]; entry=ENTRY_NUMBERS[name]; winner=name==WINNER; no_show=name in NO_SHOWS
    elim_by,is_shared,_=ELIMINATORS[name]; is_self=elim_by==[name]
    quality='CONFLICTING' if name in DISPUTED_ELIM_CREDIT else SPEC.get('credit_status','CONFIRMED')
    for eliminator in elim_by:
        elim_rows.append(blank('eliminations.csv',event_id=EVENT_ID,order_in_match=elim_number[name],eliminated_wrestler_id=wid,eliminator_wrestler_id=wrestler_ids[eliminator],assisting_wrestler_ids=';'.join(wrestler_ids[e] for e in elim_by if e!=eliminator) if is_shared else '',entry_number_of_eliminated=entry,entry_number_of_eliminator=ENTRY_NUMBERS.get(eliminator,''),elimination_type='self_elimination' if is_self else 'over_top_rope',is_solo=truth(not(is_shared or is_self)),is_shared=truth(is_shared),is_self_elimination=truth(is_self),is_disputed=truth(name in DISPUTED_ELIM_CREDIT),simultaneous_group_id=f'{EVENT_ID}-E{elim_number[name]}' if is_shared else '',data_quality_status=quality,source_ids=refs(SPEC['match_sources']),notes=SPEC.get('entrant_notes',{}).get(name,'')))
    er=blank('entrants.csv',event_id=EVENT_ID,wrestler_id=wid,match_id=EVENT_ID,entry_number=entry,entry_number_status=SPEC.get('entry_status','CONFIRMED'),ring_name_at_time=name,name_displayed_at_event=name,elim_number='' if winner or no_show else elim_number[name],elim_number_status='N/A' if no_show else ('' if winner else SPEC.get('order_status','CONFIRMED')),eliminated_by_ids=';'.join(wrestler_ids[e] for e in elim_by),ring_time=survival[name],ring_time_seconds=mmss_to_seconds(survival[name]),ring_time_status=SPEC.get('time_status',{}).get(name,SPEC.get('default_time_status','PROBABLE')) if survival[name] else '',self_eliminated=truth(is_self),is_winner=truth(winner),is_runner_up=truth(name==ELIM_ORDER[-1]),is_final_two=truth(name in FINAL_TWO),is_final_three=truth(name in FINAL_THREE),is_final_four=truth(name in FINAL_FOUR),surprise_entrant=truth(name in SURPRISE_ENTRANTS),legend_returning='TRUE' if name in LEGENDS else '',non_full_time_wrestler='TRUE' if name in NON_FULL_TIME else '',celebrity_entrant='TRUE' if name in SPEC.get('celebrities',[]) else '',data_quality_status=quality,source_ids=refs(SPEC['match_sources']),notes=SPEC.get('entrant_notes',{}).get(name,''))
    if name in SPEC.get('company_debuts',[]): er['is_company_debut']='TRUE'
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
entrant_ids={r['wrestler_id'] for r in en}
assert sum(int(r['wrestlers_eliminated_count']) for r in en)==sum(r['is_self_elimination']!='TRUE' and r['eliminator_wrestler_id'] in entrant_ids for r in el)
external=[r for r in el if r['eliminator_wrestler_id'] not in entrant_ids]
assert all(r['entry_number_of_eliminator']=='' for r in external)
if external: print(f'External non-entrant elimination credits verified: {len(external)}; no fictional entrant rows created.')
print(f'All {len(en)} entrant credit totals and populated time/reign derivations verified from persisted rows.')
print(f'{EVENT_ID} build complete: {len(new_wrestlers)} new wrestlers, {len(en)} entrants, {len(el)} elimination rows, {len(sources)} sources, {len(flags)} flags, {len(nm_rows)} moments.')
