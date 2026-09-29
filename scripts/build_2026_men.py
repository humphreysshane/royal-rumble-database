# -*- coding: utf-8 -*-
"""Build RR2026M. Researched 2026-09-22.
Uses the section order and row-construction pattern of build_2020_men.py;
self-elimination handling follows build_2020_women.py. Flags explain all
identity/credit precedents and source discrepancies. Single-source times and
biography fields remain PROBABLE. Unknown/not-applicable fields are blank
except the documented no-show sentinel. Global IDs are allocated afresh.
Run against a copy first, rebuild derived tables, validate, then apply the
identical script to live data. Refuses to append an already-present event.
"""
SPEC = {'event_id': 'RR2026M',
 'division': 'M',
 'date': '2026-01-31',
 'venue': 'Riyadh Season Stadium at King Abdullah Financial District',
 'city': 'Riyadh',
 'country': 'Saudi Arabia',
 'duration': '58:21',
 'duration_status': 'CONFLICTING',
 'winner': 'Roman Reigns',
 'reward': 'World championship match at WrestleMania42.',
 'sources': [['official',
              'WWE2026 official statistics and results',
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
              'Cagematch2026 event timing and results',
              'reference_site',
              'https://www.cagematch.net/?id=1&nr=434667',
              4,
              'Cagematch',
              ''],
             ['ars',
              'All Rumble Stats2026 independent timing',
              'reference_site',
              'https://allrumblestats.com/events/wwe/royal-rumble/royal-rumble-2026-men/',
              12,
              'Other statistical/history sites',
              ''],
             ['oba',
              'Oba Femi biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Oba_Femi',
              10,
              'Wikipedia/reference sites',
              ''],
             ['obacollege',
              'Isaac Odugbesan official Alabama athletics biography',
              'official',
              'https://rolltide.com/sports/xctrack/roster/isaac-odugbesan/7577',
              1,
              'WWE / official sources',
              ''],
             ['solo',
              'Solo Sikoa biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Solo_Sikoa',
              10,
              'Wikipedia/reference sites',
              ''],
             ['solocm',
              'Solo Sikoa Cagematch biography',
              'reference_site',
              'https://www.cagematch.net/?id=2&nr=22525',
              4,
              'Cagematch',
              ''],
             ['soloalt',
              'Solo Sikoa biography and debut chronology',
              'reference_site',
              'https://www.onlineworldofwrestling.com/profile/sefa-fatu/',
              12,
              'Other statistical/history sites',
              ''],
             ['jevon',
              'JeVon Evans biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Je%27Von_Evans',
              10,
              'Wikipedia/reference sites',
              ''],
             ['jevondebut',
              'JeVon Evans FSPW debut chronology',
              'reference_site',
              'https://www.onlineworldofwrestling.com/profile/jay-malachi/',
              12,
              'Other statistical/history sites',
              ''],
             ['iguana',
              'Mr Iguana individual Luchawiki biography',
              'reference_site',
              'https://www.luchawiki.org/index.php?title=Mr._Iguana',
              10,
              'Wikipedia/reference sites',
              ''],
             ['iguanadebut',
              'Mr Iguana individual career history',
              'reference_site',
              'https://www.gerweck.net/2025/06/16/mr-iguana/',
              12,
              'Other statistical/history sites',
              ''],
             ['trick',
              'Trick Williams biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Trick_Williams',
              10,
              'Wikipedia/reference sites',
              ''],
             ['trickcm',
              'Trick Williams Cagematch birthday',
              'reference_site',
              'https://www.cagematch.net/?id=2&nr=24301',
              4,
              'Cagematch',
              ''],
             ['trickiwd',
              'Trick Williams alternate IWD birthday',
              'reference_site',
              'https://www.profightdb.com/wrestlers/trick-williams-19048.html',
              5,
              'ProFightDB / Internet Wrestling Database',
              ''],
             ['hobbs',
              'Powerhouse Hobbs biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Powerhouse_Hobbs',
              10,
              'Wikipedia/reference sites',
              ''],
             ['hobbsdob',
              'Royce Keys birthday and APW debut chronology',
              'reference_site',
              'https://www.onlineworldofwrestling.com/profile/will-hobbs/',
              12,
              'Other statistical/history sites',
              ''],
             ['ilja',
              'Ilja Dragunov biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Ilja_Dragunov',
              10,
              'Wikipedia/reference sites',
              ''],
             ['iljadebut',
              'Ilja Dragunov GWF debut account',
              'reference_site',
              'https://de.wikipedia.org/wiki/Ilja_Dragunov',
              10,
              'Wikipedia/reference sites',
              ''],
             ['parka',
              'La Parka III individual biography',
              'reference_site',
              'https://www.luchawiki.org/index.php/La_Parka_III',
              10,
              'Wikipedia/reference sites',
              ''],
             ['parkaalt',
              'La Parka III identity confirmation',
              'reference_site',
              'https://prowrestling.fandom.com/wiki/La_Parka_III',
              10,
              'Wikipedia/reference sites',
              ''],
             ['dragon',
              'Dragon Lee individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Dragon_Lee_(wrestler)',
              10,
              'Wikipedia/reference sites',
              ''],
             ['dragonbio',
              'Dragon Lee II debut and personal data',
              'reference_site',
              'https://www.luchawiki.org/index.php/Dragon_Lee_II',
              10,
              'Wikipedia/reference sites',
              ''],
             ['dragonname',
              'Dragon Lee real name in public trademark record',
              'reference_site',
              'https://trademarks.justia.com/982/42/dragon-98242146.html',
              10,
              'Wikipedia/reference sites',
              ''],
             ['fenix',
              'Rey Fenix biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Rey_F%C3%A9nix',
              10,
              'Wikipedia/reference sites',
              ''],
             ['fenixbio',
              'Rey Fenix personal data profile',
              'reference_site',
              'https://www.thesmackdownhotel.com/wrestlers/rey-fenix',
              12,
              'Other statistical/history sites',
              ''],
             ['kaiser',
              'Marcel Barthel individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Ludwig_Kaiser',
              10,
              'Wikipedia/reference sites',
              ''],
             ['kaiserdebut',
              'Marcel Barthel NFC debut chronology',
              'reference_site',
              'https://www.onlineworldofwrestling.com/profile/marcel-barthel/',
              12,
              'Other statistical/history sites',
              ''],
             ['gable',
              'Charles Betts individual biography',
              'reference_site',
              'https://en.wikipedia.org/wiki/Chad_Gable',
              10,
              'Wikipedia/reference sites',
              ''],
             ['gabledebut',
              'Charles Betts MPW debut chronology',
              'reference_site',
              'https://www.onlineworldofwrestling.com/profile/chad-gable/',
              12,
              'Other statistical/history sites',
              ''],
             ['cardona',
              'WWE Matt Cardona continuity biography',
              'official',
              'https://www.wwe.com/superstars/matt-cardona',
              1,
              'WWE / official sources',
              ''],
             ['tag',
              'World Tag Team title history',
              'official',
              'https://www.wwe.com/titlehistory/raw-tag-team-championship',
              1,
              'WWE / official sources',
              ''],
             ['solotitle',
              'Solo hands his championship to Talla January30',
              'official',
              'https://www.wwe.com/videos/solo-sikoa-hands-the-wwe-tag-team-title-to-talla-tonga-smackdown-highlights-jan-30-2026',
              1,
              'WWE / official sources',
              ''],
             ['solotitlealt',
              'Alternative ongoing Solo championship recognition',
              'reference_site',
              'https://en.wikipedia.org/wiki/List_of_WWE_Tag_Team_Champions',
              10,
              'Wikipedia/reference sites',
              ''],
             ['obavacant',
              'Oba vacates NXT championship January6',
              'official',
              'https://www.wwe.com/shows/wwenxt/2026-01-06',
              1,
              'WWE / official sources',
              ''],
             ['attendance',
              'Reported25000 ticket distribution',
              'reference_site',
              'https://www.pwmania.com/backstage-explanation-for-empty-seats-at-royal-rumble-2026',
              7,
              'Reputable wrestling publications',
              ''],
             ['aaa',
              'AAA January31 title challengers report',
              'reference_site',
              'https://www.tvazteca.com/aztecadeportes/aaa-luchas-alarido-cartelera-31-enero-ac-notas/',
              7,
              'Reputable wrestling publications',
              ''],
             ['pentasi',
              'Alternate Penta birthplace and debut biography',
              'reference_site',
              'https://www.si.com/fannation/wrestling/wwe/5-things-to-know-about-penta-el-zero-miedo-ahead-of-his-rumored-wwe-debut',
              7,
              'Reputable wrestling publications',
              '']],
 'match_sources': ['official', 'order', 'wiki', 'cm'],
 'event_sources': ['official', 'cm', 'wiki', 'attendance'],
 'rows': [['Oba Femi', 18, '39:04', ['Brock Lesnar']],
          ['Bron Breakker', 1, '00:10', ['Oba Femi']],
          ['Solo Sikoa', 3, '03:51', ['Oba Femi']],
          ['Rey Mysterio', 4, '02:43', ['Oba Femi']],
          ['Rusev', 2, '00:32', ['Oba Femi']],
          ['Matt Cardona', 5, '00:55', ['Oba Femi']],
          ['Damian Priest', 10, '11:06', ['Royce Keys']],
          ["Je'Von Evans", 22, '40:58', ['Randy Orton']],
          ['Mr. Iguana', 6, '02:05', ['Trick Williams']],
          ['Trick Williams', 9, '06:19', ['Cody Rhodes']],
          ['Cody Rhodes', 24, '36:50', ['Drew McIntyre']],
          ['El Grande Americano', 7, '02:45', ['Original El Grande Americano']],
          ['Original El Grande Americano', 8, '01:21', ['Trick Williams']],
          ['Royce Keys', 11, '09:55', ['Bronson Reed']],
          ['Austin Theory', 14, '10:08', ['LA Knight']],
          ['Bronson Reed', 15, '09:02', ['LA Knight']],
          ['Ilja Dragunov', 16, '11:00', ['Brock Lesnar']],
          ['La Parka', 12, '04:26', ['Austin Theory']],
          ['Dragon Lee', 13, '03:01', ['Bronson Reed']],
          ['Logan Paul', 27, '25:07', ['Roman Reigns']],
          ['LA Knight', 21, '14:25', ['Cody Rhodes']],
          ['Brock Lesnar', 19, '05:32', ['Cody Rhodes', 'LA Knight']],
          ['The Miz', 20, '07:05', ['Roman Reigns']],
          ['Rey Fenix', 17, '00:28', ['Brock Lesnar']],
          ['Jey Uso', 26, '13:08', ['Roman Reigns']],
          ['Roman Reigns', None, '15:48', []],
          ['Jacob Fatu', 25, '09:01', ['Roman Reigns']],
          ['Penta', 23, '06:01', ['Gunther']],
          ['Randy Orton', 28, '07:40', ['Gunther']],
          ['Gunther', 29, '07:51', ['Roman Reigns']]],
 'bios': {'Oba Femi': {'wrestler_id': 'oba-femi',
                       'real_name': 'Isaac Odugbesan',
                       'dob': '2001-05-21',
                       'birthplace': 'Lagos, Nigeria',
                       'nationality': 'Nigerian',
                       'debut_year_company': '2022-11-11, WWE NXT',
                       'sources': ['oba', 'obacollege'],
                       'notes': 'Person-specific biography research completed 2026-09-22.',
                       'dob_status': 'CONFLICTING'},
          'Solo Sikoa': {'wrestler_id': 'solo-sikoa',
                         'real_name': 'Joseph Yokozuna Fatu',
                         'dob': '1993-03-17',
                         'birthplace': 'Sacramento, California, United States',
                         'nationality': 'American',
                         'debut_year_company': '2018-04-29, KnokX Pro',
                         'sources': ['solo', 'solocm', 'soloalt'],
                         'notes': 'Person-specific biography research completed 2026-09-22.',
                         'dob_status': 'CONFLICTING',
                         'aliases_ring_names': 'Sefa Fatu'},
          "Je'Von Evans": {'wrestler_id': 'jevon-evans',
                           'real_name': 'Malachi Jeffers',
                           'dob': '2004-04-29',
                           'birthplace': 'Greensboro, North Carolina, United States',
                           'nationality': 'American',
                           'debut_year_company': '2018-01-26, Fire Star Pro Wrestling',
                           'sources': ['jevon', 'jevondebut'],
                           'notes': 'Person-specific biography research completed 2026-09-22.',
                           'aliases_ring_names': 'Jay Malachi;Kid Blacka Merica'},
          'Mr. Iguana': {'wrestler_id': 'mr-iguana',
                         'real_name': 'Santiago Ibarra Calderón',
                         'dob': '1988-07-20',
                         'birthplace': 'Culiacán, Sinaloa, Mexico',
                         'nationality': 'Mexican',
                         'debut_year_company': '2009-07-24; Culiacan independent circuit (first promotion '
                                               'not established)',
                         'sources': ['iguana', 'iguanadebut'],
                         'notes': 'Person-specific biography research completed 2026-09-22.'},
          'Trick Williams': {'wrestler_id': 'trick-williams',
                             'real_name': 'Matrick Mondre Belton',
                             'dob': '1994-05-26',
                             'birthplace': 'Columbia, South Carolina, United States',
                             'nationality': 'American',
                             'debut_year_company': '2020-01-31, Combat Zone Wrestling (first recorded match; '
                                                   'training began2018)',
                             'sources': ['trick', 'trickcm', 'trickiwd'],
                             'notes': 'Person-specific biography research completed 2026-09-22.',
                             'dob_status': 'CONFLICTING',
                             'aliases_ring_names': 'Sweet Daddy Trick'},
          'Royce Keys': {'wrestler_id': 'powerhouse-hobbs',
                         'real_name': 'William Hobson',
                         'dob': '1991-01-23',
                         'birthplace': 'East Palo Alto, California, United States',
                         'nationality': 'American',
                         'debut_year_company': '2009-07-18, All Pro Wrestling',
                         'sources': ['hobbs', 'hobbsdob'],
                         'notes': 'Person-specific biography research completed 2026-09-22.',
                         'aliases_ring_names': 'Powerhouse Hobbs;Will Hobbs;Will Rood;Will.I.IS'},
          'Ilja Dragunov': {'wrestler_id': 'ilja-dragunov',
                            'real_name': 'Ilja Rukober',
                            'dob': '1993-10-10',
                            'birthplace': 'Moscow, Russia',
                            'nationality': 'Russian-German',
                            'debut_year_company': '2012-04-21, German Wrestling Federation',
                            'sources': ['ilja', 'iljadebut'],
                            'notes': 'Person-specific biography research completed 2026-09-22.'},
          'La Parka': {'wrestler_id': 'la-parka-iii',
                       'real_name': '',
                       'dob': '1999-06-14',
                       'birthplace': 'Mexico City, Mexico',
                       'nationality': 'Mexican',
                       'debut_year_company': '2013-09-16; Mexican independent circuit (first promotion not '
                                             'established)',
                       'sources': ['parka', 'parkaalt'],
                       'notes': 'Person-specific biography research completed 2026-09-22.',
                       'aliases_ring_names': 'Brazo de Oro Jr. II;La Parka III'},
          'Dragon Lee': {'wrestler_id': 'dragon-lee',
                         'real_name': 'Emmanuel Muñoz González',
                         'dob': '1995-05-15',
                         'birthplace': 'Tala, Jalisco, Mexico',
                         'nationality': 'Mexican',
                         'debut_year_company': '2014-01-01, Consejo Mundial de Lucha Libre',
                         'sources': ['dragon', 'dragonbio', 'dragonname'],
                         'notes': 'Person-specific biography research completed 2026-09-22.',
                         'aliases_ring_names': 'Dragon Lee II;Ryu Lee;Drago'},
          'Rey Fenix': {'wrestler_id': 'rey-fenix',
                        'real_name': '',
                        'dob': '1990-12-30',
                        'birthplace': 'Mexico City, Mexico',
                        'nationality': 'Mexican',
                        'debut_year_company': '2007; Mexican independent circuit (first promotion not '
                                              'established)',
                        'sources': ['fenix', 'fenixbio'],
                        'notes': 'Person-specific biography research completed 2026-09-22.',
                        'aliases_ring_names': 'Fenix;Fénix;Rey Fénix;Mascara Oriental;The King;King Phoenix'},
          'El Grande Americano': {'wrestler_id': 'el-grande-americano-ii',
                                  'real_name': 'Marcel Barthel',
                                  'dob': '1990-07-08',
                                  'birthplace': 'Pinneberg, Schleswig-Holstein, Germany',
                                  'nationality': 'German',
                                  'debut_year_company': '2008-03-01, Nordisch Fight Club',
                                  'sources': ['kaiser', 'kaiserdebut'],
                                  'notes': 'Person-specific biography research completed 2026-09-22.',
                                  'character_split': True,
                                  'aliases_ring_names': 'El Grande Americano II'},
          'Original El Grande Americano': {'wrestler_id': 'el-grande-americano-i',
                                           'real_name': 'Charles Edward Betts',
                                           'dob': '1986-03-08',
                                           'birthplace': 'Saint Michael, Minnesota, United States',
                                           'nationality': 'American',
                                           'debut_year_company': '2003, Midwest Pro Wrestling (earliest '
                                                                 'located card2003-10-26; reported '
                                                                 'debut2003-09-08)',
                                           'sources': ['gable', 'gabledebut'],
                                           'notes': 'Person-specific biography research completed '
                                                    '2026-09-22.',
                                           'character_split': True,
                                           'aliases_ring_names': 'The Original El Grande Americano;El Grande '
                                                                 'Americano I'}},
 'reused': {'Bron Breakker': 'bron-breakker',
            'Rey Mysterio': 'rey-mysterio',
            'Rusev': 'rusev',
            'Matt Cardona': 'zack-ryder',
            'Damian Priest': 'damian-priest',
            'Cody Rhodes': 'cody-rhodes',
            'Austin Theory': 'austin-theory',
            'Bronson Reed': 'bronson-reed',
            'Logan Paul': 'logan-paul',
            'LA Knight': 'la-knight',
            'Brock Lesnar': 'brock-lesnar',
            'The Miz': 'the-miz',
            'Jey Uso': 'jey-uso',
            'Roman Reigns': 'roman-reigns',
            'Jacob Fatu': 'jacob-fatu',
            'Penta': 'penta',
            'Randy Orton': 'randy-orton',
            'Gunther': 'gunther'},
 'external_eliminators': {'Drew McIntyre': 'drew-mcintyre'},
 'disputed_credit': ['Cody Rhodes', 'Royce Keys', 'Dragon Lee', 'La Parka', "Je'Von Evans"],
 'time_status': {'Oba Femi': 'CONFLICTING',
                 'Bron Breakker': 'CONFLICTING',
                 'Solo Sikoa': 'CONFLICTING',
                 'Rey Mysterio': 'CONFLICTING',
                 'Rusev': 'CONFLICTING',
                 'Matt Cardona': 'CONFIRMED',
                 'Damian Priest': 'CONFLICTING',
                 "Je'Von Evans": 'CONFLICTING',
                 'Mr. Iguana': 'CONFLICTING',
                 'Trick Williams': 'CONFIRMED',
                 'Cody Rhodes': 'CONFLICTING',
                 'El Grande Americano': 'CONFIRMED',
                 'Original El Grande Americano': 'CONFLICTING',
                 'Royce Keys': 'CONFLICTING',
                 'Austin Theory': 'CONFLICTING',
                 'Bronson Reed': 'CONFLICTING',
                 'Ilja Dragunov': 'CONFLICTING',
                 'La Parka': 'CONFLICTING',
                 'Dragon Lee': 'CONFLICTING',
                 'Logan Paul': 'CONFLICTING',
                 'LA Knight': 'CONFLICTING',
                 'Brock Lesnar': 'CONFLICTING',
                 'The Miz': 'CONFIRMED',
                 'Rey Fenix': 'CONFLICTING',
                 'Jey Uso': 'CONFLICTING',
                 'Roman Reigns': 'CONFLICTING',
                 'Jacob Fatu': 'CONFLICTING',
                 'Penta': 'CONFIRMED',
                 'Randy Orton': 'CONFLICTING',
                 'Gunther': 'CONFLICTING'},
 'champions': {'Jey Uso': ['World Tag Team Championship', 'Tag Team', '2025-12-29', 'jimmy-uso']},
 'champions_complete': True,
 'champion_sources': ['tag', 'solotitle', 'solotitlealt', 'obavacant', 'aaa'],
 'surprises': ['Mr. Iguana', 'Original El Grande Americano', 'Royce Keys', 'La Parka', 'LA Knight'],
 'non_full_time': ['Brock Lesnar', 'Roman Reigns'],
 'legends': ['Rey Mysterio'],
 'company_debuts': ['Royce Keys'],
 'flags': [{'table': 'eliminations',
            'record': 'cody-rhodes',
            'field': 'eliminator_wrestler_id',
            'type': 'official_nonactive_eliminator_credit',
            'description': 'WWE credits Drew McIntyre, a nonentrant; WZ instead credits Jacob Fatu with Drew '
                           'assistance. Retain Drew, following The Miz RR2011M F262 and Omos RR2021M F414. '
                           'No entrant row/entry number for Drew. Unlike AOP2020 F397, WWE explicitly names '
                           'him as eliminator.',
            'sources': ['official', 'order', 'cm'],
            'status': 'resolved'},
           {'table': 'eliminations',
            'record': 'powerhouse-hobbs;dragon-lee;la-parka-iii;jevon-evans',
            'field': 'eliminator_wrestler_id',
            'type': 'conflicting_sources',
            'description': 'WWE credits Royce and Dragon Lee to Bronson alone; WZ credits all three Vision '
                           'members to both and Cagematch credits all three only for Royce. AllRumbleStats '
                           'credits Theory+Reed for La Parka versus official Theory. WZ credits Gunther for '
                           'Evans versus official Orton. Retain official named credits, applying F397 '
                           'distinction between assistance and eliminator-of-record.',
            'sources': ['official', 'order', 'cm', 'ars'],
            'status': 'open'},
           {'table': 'events;entrants',
            'record': 'RR2026M',
            'field': 'duration_total;ring_time',
            'type': 'conflicting_sources',
            'description': 'Cagematch58:21 versus Wikipedia56:10 and independent AllRumbleStats58:16; retain '
                           'tier4 Cagematch duration. WWE/AllRumbleStats individual times: Oba Femi '
                           '39:04/38:57; Bron Breakker 00:10/00:11; Solo Sikoa 03:51/04:01; Rey Mysterio '
                           "02:43/02:53; Rusev 00:32/00:34; Damian Priest 11:06/13:01; Je'Von Evans "
                           '40:58/40:54; Mr. Iguana 02:05/02:12; Cody Rhodes 36:50/36:42; Original El Grande '
                           'Americano 01:21/01:20; Royce Keys 09:55/09:56; Austin Theory 10:08/10:09; '
                           'Bronson Reed 09:02/09:04; Ilja Dragunov 11:00/10:58; La Parka 04:26/04:23; '
                           'Dragon Lee 03:01/03:07; Logan Paul 25:07/25:06; LA Knight 14:25/14:24; Brock '
                           'Lesnar 05:32/04:51; Rey Fenix 00:28/00:30; Jey Uso 13:08/13:10; Roman Reigns '
                           '15:48/15:52; Jacob Fatu 09:01/09:19; Randy Orton 07:40/07:41; Gunther '
                           '07:51/07:50. Independent clock sometimes begins at pre-entry attack, contrary to '
                           'project ring-time definition; retain official values with disagreements visible.',
            'sources': ['official', 'cm', 'wiki', 'ars'],
            'status': 'open'},
           {'table': 'entrants',
            'record': 'bron-breakker',
            'field': 'elim_number;ring_time',
            'type': 'needs_human_judgement',
            'description': 'Bron was attacked before entering, but entered and was eliminated by Oba. Retain '
                           'entry2, elimination1 and official10sec. Unlike documented Tozawa2025 no-show or '
                           'Rey2023, there was actual participation; no N/A sentinel.',
            'sources': ['official', 'ars'],
            'status': 'resolved'},
           {'table': 'wrestlers',
            'record': 'el-grande-americano-i;el-grande-americano-ii',
            'field': 'wrestler_id',
            'type': 'needs_human_judgement',
            'description': 'Both underlying people were individually matched: Charles Betts=chad-gable and '
                           'Marcel Barthel=ludwig-kaiser. Create separate masked performer identities under '
                           'full-character reinvention rule, following husky-harris/bray-wyatt F354. '
                           'Separate I/II IDs also prevent conflating two different people sharing a mask. '
                           'Both received fresh individual biography research. AllRumbleStats instead '
                           'aggregates them under unmasked identities; this database follows its '
                           'split-character convention.',
            'sources': ['official', 'gable', 'kaiser', 'ars'],
            'status': 'resolved'},
           {'table': 'entrants',
            'record': 'zack-ryder;rusev',
            'field': 'wrestler_id',
            'type': 'needs_human_judgement',
            'description': 'Matt Cardona reuses zack-ryder: WWE explicitly carries Ryder biography and Rough '
                           'Ryder/Broski Boot into current Cardona profile, supporting continuity rather '
                           'than full masked-character reinvention. Rusev reuses rusev (earlier Alexander '
                           'Rusev). F400 minor-moniker precedent; event billing preserved.',
            'sources': ['cardona', 'official'],
            'status': 'resolved'},
           {'table': 'wrestlers',
            'record': 'la-parka-iii;rey-fenix;mr-iguana',
            'field': 'real_name;debut_year_company',
            'type': 'unverified',
            'description': 'Person-specific searches established La Parka III is former Brazo de Oro Jr. II, '
                           'born1999, not L.A. Park or deceased La Parka II or Karis la Momia Jr. His and '
                           'Fenix real names remain unpublished in consulted profiles and are blank. First '
                           'promotion for La Parka/Fenix/Iguana was not established; sourced debut date/year '
                           'retained with circuit, no guessed company.',
            'sources': ['parka', 'parkaalt', 'fenix', 'fenixbio', 'iguana', 'iguanadebut'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'oba-femi',
            'field': 'dob',
            'type': 'conflicting_sources',
            'description': 'Official Alabama athletics biography says2001-05-21; English Wikipedia '
                           'says1998-04-22. Store primary official2001-05-21 with CONFLICTING status; this '
                           'is unresolved, not a verified exact birthday.',
            'sources': ['obacollege', 'oba'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'solo-sikoa;trick-williams',
            'field': 'dob',
            'type': 'conflicting_sources',
            'description': 'Solo: Cagematch1993-03-17 versus OWW1993-03-18; retain tier4 March17. Trick: '
                           'Cagematch1994-05-26 versus IWD1994-05-16; retain tier4 May26.',
            'sources': ['solocm', 'soloalt', 'trickcm', 'trickiwd'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'el-grande-americano-i',
            'field': 'debut_year_company',
            'type': 'conflicting_sources',
            'description': 'Chad biography/OWW report2003-09-08 but first located MPW card is2003-10-26. '
                           'Store year2003 and MPW with both dates annotated; do not imply September card '
                           'was independently found.',
            'sources': ['gable', 'gabledebut'],
            'status': 'open'},
           {'table': 'events',
            'record': 'RR2026M',
            'field': 'attendance_official;attendance_reported',
            'type': 'conflicting_sources',
            'description': 'No direct official attendance release located. Cagematch estimates22500; '
                           'reporting cites WWE sources saying25000 tickets. Leave official blank, '
                           'reported22500 from higher-tier Cagematch; estimate and alternative preserved.',
            'sources': ['cm', 'attendance', 'wiki'],
            'status': 'open'},
           {'table': 'entrants;events',
            'record': 'solo-sikoa;RR2026M',
            'field': 'current_champion_title;champions_in_field_count',
            'type': 'conflicting_sources',
            'description': 'WWE Jan30 video documents Solo handing his title to Talla; contemporary '
                           'interpretation is relinquishment, while retrospective title list retains '
                           'Solo/Tama as recognized champions. Apply higher-tier official transfer account '
                           'and leave Solo title blank at Rumble; count Jey as confirmed reigning champion. '
                           'Oba vacated Jan6; Dragon Lee lost Dec29; Iguana was a challenger for AAA mixed '
                           'title. Title membership uncertainty remains explicit.',
            'sources': ['solotitle', 'solotitlealt', 'tag', 'obavacant', 'aaa'],
            'status': 'open'},
           {'table': 'wrestlers',
            'record': 'penta',
            'field': 'birthplace;debut_year_company',
            'type': 'conflicting_sources',
            'description': 'Additional SI biography reports Xalapa and2004 debut, differing from '
                           'Ecatepec/2007 in the previously built Penta profile. Preserve alternative here; '
                           'existing2007 entry reflects his reported interview chronology. No silent rewrite '
                           'of the prior event biography.',
            'sources': ['pentasi'],
            'status': 'open'},
           {'table': 'entrants',
            'record': 'RR2026M',
            'field': 'surprise_entrant',
            'type': 'needs_human_judgement',
            'description': 'Unadvertised company debut Royce Keys, AAA guests Iguana/La Parka, and returning '
                           'Original Americano/LA Knight are marked surprises. Advertised Oba/Lesnar/Reigns '
                           'are not. Royce company debut is sourced explicitly in official recap.',
            'sources': ['official', 'wiki'],
            'status': 'resolved'}],
 'event_extra': {'attendance_reported': '22500'},
 'entrant_notes': {'Cody Rhodes': 'Eliminated by nonentrant Drew McIntyre; no entry number for external '
                                  'eliminator.',
                   'Bron Breakker': 'Attacked before entry, then entered and was eliminated; not a no-show.',
                   'El Grande Americano': 'Marcel Barthel masked incarnation, distinct from Original El '
                                          'Grande Americano (Charles Betts).',
                   'Original El Grande Americano': 'Charles Betts masked incarnation.',
                   'Solo Sikoa': 'Champion status disputed following Jan30 belt handover; see event flag.'},
 'moments': [{'category': 'milestone_first',
              'title': 'Royce Keys makes WWE debut',
              'people': ['Royce Keys'],
              'description': 'Former Powerhouse Hobbs entered at14 under his new ring name.',
              'sources': ['official', 'wiki']},
             {'category': 'storyline_moment',
              'title': 'Both El Grande Americanos collide',
              'people': ['El Grande Americano', 'Original El Grande Americano'],
              'description': 'Returning original masked wrestler eliminated the second incarnation.',
              'sources': ['official', 'wiki']},
             {'category': 'injury_or_incident',
              'title': 'Masked attack precedes Breakker elimination',
              'people': ['Bron Breakker', 'Oba Femi'],
              'description': 'An unidentified masked attacker assaulted Breakker before he entered; Femi '
                             'then eliminated him first. No attacker identity guessed.',
              'sources': ['official', 'wiki']},
             {'category': 'controversy',
              'title': 'Nonentrant McIntyre eliminates Rhodes',
              'people': ['Drew McIntyre', 'Cody Rhodes'],
              'description': 'WWE explicitly assigns the outside-interference elimination to McIntyre.',
              'sources': ['official', 'cm']},
             {'category': 'milestone_first',
              'title': 'Reigns wins his second Royal Rumble',
              'people': ['Roman Reigns', 'Gunther'],
              'description': 'Reigns last eliminated Gunther, adding to his2015 victory.',
              'sources': ['official', 'wiki']}],
 'notes': 'Attendance is an estimate, title membership and timing disputes retained. Twelve new character '
          'IDs include two researched masked personas; ten first-time underlying people. No footage-derived '
          'entrance or elimination-clock times invented.'}

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
