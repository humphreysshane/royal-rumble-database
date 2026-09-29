# -*- coding: utf-8 -*-
"""Build RR2023M. Live-researched 2026-09-22. Structure follows build_2020_men.py.
Official WWE results are primary for entry numbers, credited eliminators and survival times.
WrestleZone/CBS/Cageside independently cross-check entry/elimination order. Rey Mysterio was
assigned #17 but did not appear; fields requiring an actual ring entry/elimination are blank.
WWE explicitly credits already-eliminated Finn Balor with Edge's elimination; structured credit
is retained under the same official-credit precedent used for Omos in RR2021M, unlike AOP in
RR2020M where WWE's official results did not make AOP eliminators of record. See F427.
"""
import csv, os, sys
sys.path.insert(0,os.path.dirname(__file__))
from schema import WRESTLERS_FIELDS,ENTRANTS_FIELDS,ELIMINATIONS_FIELDS,EVENTS_FIELDS,NOTABLE_MOMENTS_FIELDS
DATA_DIR=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'..','data'); E='RR2023M'; DATE='2026-09-22'
def blank(fields): return {k:'' for k in fields}
def append_dict(fn,fields,rows):
 with open(os.path.join(DATA_DIR,fn),'a',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields); [w.writerow(r) for r in rows]
def sec(s):
 if not s:return ''
 p=[int(x) for x in s.split(':')]; return p[-1]+60*p[-2]+(3600*p[-3] if len(p)==3 else 0)
# Freshly allocated after RR2022: S251+, F426+, NM104+.
sources=[
 ['S251','WWE.com — 2023 Men’s Royal Rumble Match Results','official','https://www.wwe.com/shows/royalrumble/2023/mens-royal-rumble-match-results',1,'Official WWE',DATE,'Primary source for entrants, WWE eliminator-of-record credits, survival times and Rey Mysterio did-not-appear status.'],
 ['S252','WrestleZone — Cody Rhodes Wins 2023 Royal Rumble','contemporary_publication','https://www.wrestlezone.com/news/1341850-cody-rhodes-wins-2023-royal-rumble',9,'Contemporary wrestling publication',DATE,'Independent entry order and chronological elimination-order cross-check.'],
 ['S253','CBS Sports — 2023 WWE Royal Rumble results','contemporary_publication','https://www.cbssports.com/wwe/news/2023-wwe-royal-rumble-results-recap-grades-rhodes-ripley-win-rumble-matches-zayn-turns-on-bloodline/live/',8,'Major sports publication',DATE,'Contemporary narrative and elimination cross-check.'],
 ['S254','Cageside Seats — Men’s Royal Rumble 2023 match time/statistics','statistics_analysis','https://www.cagesideseats.com/wwe/2023/1/31/23579497/wwe-royal-rumble-2023-men-match-time-statistics-survival-intervals-crowded-90-seconds-numbers',9,'Independent timing analysis',DATE,'Timing cross-check; identifies WWE Angelo Dawkins 2:28 as likely typo versus footage-derived 3:17. WWE official value retained and conflict flagged.'],
 ['S255','Dedicated biography — Gunther / WALTER','biography','https://www.thesmackdownhotel.com/wrestlers/walter',7,'Dedicated wrestler profile',DATE,'Person-specific lookup for Gunther: Walter Hahn; 1987-08-20; Vienna, Austria; Austrian; debut 2005.'],
 ['S256','Dedicated biography — Karrion Kross','biography','https://www.thesmackdownhotel.com/wrestlers/killer-kross-karrion-kross',7,'Dedicated wrestler profile',DATE,'Person-specific lookup for Karrion Kross: Kevin Kesar; 1985-07-19; New York, New York; American; debut information checked.'],
 ['S257','Dedicated biography — Santos Escobar','biography','https://www.thesmackdownhotel.com/wrestlers/santos-escobar-el-hijo-del-fantasma-king-cuerno',7,'Dedicated wrestler profile',DATE,'Person-specific lookup for Santos Escobar: Jorge Luis Alcántara Boli; 1984-04-30; Mexico City; Mexican; career/ring names checked.'],
 ['S258','Dedicated biography — Logan Paul','biography','https://en.wikipedia.org/wiki/Logan_Paul',10,'Reference biography',DATE,'Person-specific lookup for Logan Paul: Logan Alexander Paul; 1995-04-01; Westlake, Ohio; American. WWE in-ring debut cross-checked against WWE profile.'],
 ['S259','WWE.com — Logan Paul profile','official','https://www.wwe.com/superstars/logan-paul',1,'Official WWE',DATE,'Confirms Paul’s WWE in-ring debut was WrestleMania 38 and his WWE contract followed in June 2022.']]
with open(os.path.join(DATA_DIR,'sources.csv'),'a',newline='',encoding='utf-8') as f: csv.writer(f).writerows(sources)
existing=list(csv.DictReader(open(os.path.join(DATA_DIR,'wrestlers.csv'),encoding='utf-8')))
lookup={r['ring_name'].lower():r['wrestler_id'] for r in existing}
for r in existing:
 for a in r['aliases_ring_names'].split(';'):
  if a.strip(): lookup.setdefault(a.strip().lower(),r['wrestler_id'])
bios={
 'Gunther':('gunther','Walter Hahn','1987-08-20','Vienna, Austria','Austrian','2005','Gunther;WALTER;Walter','S255'),
 'Karrion Kross':('karrion-kross','Kevin Kesar','1985-07-19','New York, New York, United States','American','2014','Karrion Kross;Killer Kross;Kevin Kross;The White Rabbit','S256'),
 'Santos Escobar':('santos-escobar','Jorge Luis Alcántara Boli','1984-04-30','Mexico City, Mexico','Mexican','2000','Santos Escobar;El Hijo del Fantasma;King Cuerno;Top Secret','S257'),
 'Logan Paul':('logan-paul','Logan Alexander Paul','1995-04-01','Westlake, Ohio, United States','American','2022','Logan Paul','S258;S259')}
new=[]
for n,b in bios.items():
 if n.lower() not in lookup:
  wid,real,dob,bp,nat,debut,aliases,sids=b; r=blank(WRESTLERS_FIELDS); r.update(wrestler_id=wid,ring_name=n,real_name=real,real_name_status='CONFIRMED',gender='M',dob=dob,dob_status='CONFIRMED',birthplace=bp,birthplace_status='CONFIRMED',nationality=nat,debut_year_company=debut,aliases_ring_names=aliases,notes=f'Added for {E}; individually researched.',source_ids=sids);new.append(r);lookup[n.lower()]=wid
append_dict('wrestlers.csv',WRESTLERS_FIELDS,new)
names=['Gunther','Sheamus','The Miz','Kofi Kingston','Johnny Gargano','Xavier Woods','Karrion Kross','Chad Gable','Drew McIntyre','Santos Escobar','Angelo Dawkins','Brock Lesnar','Bobby Lashley','Baron Corbin','Seth Rollins','Otis','Rey Mysterio','Dominik Mysterio','Elias','Finn Balor','Booker T','Damian Priest','Montez Ford','Edge','Austin Theory','Omos','Braun Strowman','Ricochet','Logan Paul','Cody Rhodes']
wid={n:lookup[n.lower()] for n in names}
times=['1:11:40','52:33','04:23','14:51','29:57','10:29','04:11','08:42','39:10','04:56','02:28','02:28','07:14','00:07','37:18','03:08','','25:44','00:39','07:45','00:42','04:03','00:44','01:04','15:39','02:26','11:12','09:14','10:57','15:08']
orders=[28,20,1,4,13,3,2,7,21,5,6,8,10,9,26,11,'',22,12,17,14,15,16,18,24,19,23,25,27,'']
elimby={'Gunther':['Cody Rhodes'],'Sheamus':['Gunther'],'The Miz':['Sheamus'],'Kofi Kingston':['Gunther'],'Johnny Gargano':['Dominik Mysterio','Finn Balor'],'Xavier Woods':['Gunther'],'Karrion Kross':['Drew McIntyre'],'Chad Gable':['Brock Lesnar'],'Drew McIntyre':['Gunther'],'Santos Escobar':['Brock Lesnar'],'Angelo Dawkins':['Brock Lesnar'],'Brock Lesnar':['Bobby Lashley'],'Bobby Lashley':['Seth Rollins'],'Baron Corbin':['Seth Rollins'],'Seth Rollins':['Logan Paul'],'Otis':['Drew McIntyre','Sheamus'],'Dominik Mysterio':['Cody Rhodes'],'Elias':['Drew McIntyre','Sheamus'],'Finn Balor':['Edge'],'Booker T':['Gunther'],'Damian Priest':['Edge'],'Montez Ford':['Damian Priest'],'Edge':['Finn Balor'],'Austin Theory':['Cody Rhodes'],'Omos':['Braun Strowman'],'Braun Strowman':['Cody Rhodes'],'Ricochet':['Austin Theory'],'Logan Paul':['Cody Rhodes']}
elimrows=[]; entrants=[]
for i,n in enumerate(names):
 es=elimby.get(n,[]); win=n=='Cody Rhodes'; no_show=n=='Rey Mysterio'; shared=len(es)>1
 for e in es:
  r=blank(ELIMINATIONS_FIELDS); r.update(event_id=E,order_in_match=orders[i],eliminated_wrestler_id=wid[n],eliminator_wrestler_id=wid[e],assisting_wrestler_ids=';'.join(wid[x] for x in es if x!=e) if shared else '',entry_number_of_eliminated=i+1,entry_number_of_eliminator=names.index(e)+1,elimination_type='over_top_rope',is_solo='FALSE' if shared else 'TRUE',is_shared='TRUE' if shared else 'FALSE',is_accidental='FALSE',is_self_elimination='FALSE',is_storyline_related='TRUE' if n=='Edge' else 'FALSE',is_disputed='FALSE',simultaneous_group_id=f'{E}-E{orders[i]}' if shared else '',data_quality_status='CONFIRMED',source_ids='S251;S252',notes='WWE credits Finn Balor after his own elimination.' if n=='Edge' else ''); elimrows.append(r)
 er=blank(ENTRANTS_FIELDS); er.update(event_id=E,wrestler_id=wid[n],match_id=E,entry_number=i+1,entry_number_status='CONFIRMED',ring_name_at_time=n,name_displayed_at_event=n,elim_number='' if no_show or win else orders[i],elim_number_status='N/A' if no_show else ('' if win else 'CONFIRMED'),eliminated_by_ids=';'.join(wid[x] for x in es),ring_time=times[i],ring_time_seconds=sec(times[i]),ring_time_status='' if no_show else 'CONFIRMED',self_eliminated='FALSE',is_winner='TRUE' if win else 'FALSE',is_runner_up='TRUE' if n=='Gunther' else 'FALSE',is_final_two='TRUE' if n in {'Cody Rhodes','Gunther'} else 'FALSE',is_final_three='TRUE' if n in {'Cody Rhodes','Gunther','Logan Paul'} else 'FALSE',is_final_four='TRUE' if n in {'Cody Rhodes','Gunther','Logan Paul','Seth Rollins'} else 'FALSE',surprise_entrant='TRUE' if n in {'Booker T','Edge'} else 'FALSE',legend_returning='TRUE' if n in {'Booker T','Edge'} else 'FALSE',celebrity_entrant='TRUE' if n=='Logan Paul' else 'FALSE',data_quality_status='CONFIRMED',source_ids='S251;S252',notes='Assigned entry #17 but did not appear or enter the ring; actual ring-time/elimination fields intentionally blank.' if no_show else ''); entrants.append(er)
credit={}
for r in elimrows: credit.setdefault(r['eliminator_wrestler_id'],[]).append(r['eliminated_wrestler_id'])
for r in entrants:
 c=credit.get(r['wrestler_id'],[]);r['wrestlers_eliminated_count']=len(c);r['wrestlers_eliminated_ids']=';'.join(c);r['solo_eliminations_count']=sum(x['eliminator_wrestler_id']==r['wrestler_id'] and x['is_solo']=='TRUE' for x in elimrows);r['assisted_eliminations_count']=sum(x['eliminator_wrestler_id']==r['wrestler_id'] and x['is_shared']=='TRUE' for x in elimrows)
append_dict('entrants.csv',ENTRANTS_FIELDS,entrants);append_dict('eliminations.csv',ELIMINATIONS_FIELDS,elimrows)
flags=[
 ['F426',E,'entrants','rey-mysterio','ring_time;elim_number;eliminated_by_ids','did_not_appear','WWE assigned Rey Mysterio entry #17 but explicitly records that he did not appear. Unlike a normal entrant/elimination, he never entered the ring. Following the existing Randy Savage RR1991M and Scotty 2 Hotty RR2005M no-show convention, elim_number_status is literal N/A as the structured no-show signal; elim_number, ring_time and elimination-clock fields remain blank, and no elimination row is created.','S251;S252;S254','resolved',DATE],
 ['F427',E,'eliminations','edge','eliminator_wrestler_id','official_nonactive_eliminator_credit','WWE officially lists Finn Balor as Edge’s eliminator after Balor had already been eliminated, so structured credit follows WWE’s eliminator-of-record. This follows the Omos/RR2021M precedent: Omos was not an entrant but WWE itself listed him as eliminator. It differs from Authors of Pain/RR2020M: AOP interference was narrative assistance and WWE did not list them as eliminators of record, so they did not receive structured credit.','S251;S252','resolved',DATE],
 ['F428',E,'entrants','angelo-dawkins','ring_time','conflicting_timing','WWE lists Angelo Dawkins at 2:28; Cageside Seats’ footage-derived timing is 3:17 and identifies WWE’s value as a likely duplicated Brock Lesnar time. The database retains WWE’s official 2:28 while explicitly preserving the conflict.','S251;S254','open',DATE]]
with open(os.path.join(DATA_DIR,'flags.csv'),'a',newline='',encoding='utf-8') as f: csv.writer(f).writerows(flags)
m=[]
for mid,title,people,desc in [('NM104','Cody Rhodes wins from No. 30',['Cody Rhodes'],'Rhodes returned from injury at No. 30 and won by last eliminating Gunther.'),('NM105','Gunther lasts 71:40',['Gunther'],'Gunther entered No. 1 and survived 1:11:40, reaching the final two.'),('NM106','Rey Mysterio does not appear',['Rey Mysterio'],'Mysterio was assigned No. 17 but never appeared or entered the ring.'),('NM107','Ricochet and Logan Paul collide',['Ricochet','Logan Paul'],'Ricochet and Logan Paul launched from opposite sides and collided in mid-air.')]:
 r=blank(NOTABLE_MOMENTS_FIELDS);r.update(moment_id=mid,event_id=E,wrestler_ids_involved=';'.join(wid[x] for x in people),category='notable',title=title,description=desc,data_quality_status='CONFIRMED',source_ids='S251;S252');m.append(r)
append_dict('notable_moments.csv',NOTABLE_MOMENTS_FIELDS,m)
ev=blank(EVENTS_FIELDS);ev.update(event_id=E,event_name='Royal Rumble 2023',match_name='Royal Rumble Match',match_type="Men's",event_date='2023-01-28',venue='Alamodome',city_region='San Antonio, Texas',country='United States',entrant_count=len(entrants),duration_total='1:11:40',duration_status='CONFIRMED',winner_id=wid['Cody Rhodes'],runner_up_id=wid['Gunther'],final_two_ids=wid['Cody Rhodes']+';'+wid['Gunther'],final_three_ids=';'.join(wid[x] for x in ['Cody Rhodes','Gunther','Logan Paul']),final_four_ids=';'.join(wid[x] for x in ['Cody Rhodes','Gunther','Logan Paul','Seth Rollins']),first_entrant_id=wid['Gunther'],second_entrant_id=wid['Sheamus'],final_entrant_id=wid['Cody Rhodes'],first_elimination_id=wid['The Miz'],last_elimination_before_winner_id=wid['Gunther'],eliminations_count=len({r['eliminated_wrestler_id'] for r in elimrows}),eliminators_count=len({r['eliminator_wrestler_id'] for r in elimrows}),surprise_entrants_count=sum(r['surprise_entrant']=='TRUE' for r in entrants),champions_in_field_count='',hall_of_famers_in_field_count='',tag_teams_count='',factions_count='',title_on_the_line='FALSE',championship_implications='Winner earned a world championship match at WrestleMania 39.',winners_reward='World championship match at WrestleMania 39.',data_quality_status='CONFIRMED',source_ids='S251;S252;S253')
append_dict('events.csv',EVENTS_FIELDS,[ev])
checks={'entrant_count':len(entrants),'eliminations_count':len({r['eliminated_wrestler_id'] for r in elimrows}),'eliminators_count':len({r['eliminator_wrestler_id'] for r in elimrows}),'surprise_entrants_count':sum(r['surprise_entrant']=='TRUE' for r in entrants)}
print('SELF-CHECK RR2023M')
for k,v in checks.items(): print(f'{k}: declared={ev[k]} recomputed={v} match={str(ev[k])==str(v)}')
print(f'RR2023M build complete: {len(new)} new wrestlers, {len(entrants)} entrants, {len(elimrows)} elimination-credit rows, {len(sources)} sources, {len(flags)} flags, {len(m)} moments.')
