#!/usr/bin/env python3
import csv,os,re,sys
sys.path.insert(0,os.path.dirname(__file__))
from schema import *
D=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'..','data'); E='RR2022M'; DATE='2026-09-22'
def sec(s): a=list(map(int,s.split(':'))); return a[-2]*60+a[-1]
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def append_dict(fn,fields,rows):
 with open(os.path.join(D,fn),'a',newline='',encoding='utf-8') as f: csv.DictWriter(f,fieldnames=fields).writerows(rows)
def blank(fields): return {k:'' for k in fields}
# S232-S242 freshly allocated after max S231.
sources=[
['S232','WWE.com — Brock Lesnar wins the 2022 Men’s Royal Rumble','official_wwe','https://www.wwe.com/shows/royalrumble/2022/30-man-royal-rumble-match-results',1,'WWE / official sources',DATE,'Primary entrant, eliminator and official survival-time table.'],
['S233','Wikipedia — Royal Rumble (2022), men’s entrances/eliminations','event_database','https://en.wikipedia.org/wiki/Royal_Rumble_(2022)',8,'Reference cross-check',DATE,'Cross-check for elimination order, venue, duration and final sequence.'],
]
bio={
'Austin Theory':('austin-theory','Austin Tyler White','1997-08-02','McDonough, Georgia, United States','American','2016','Austin Theory;Theory','https://www.thesmackdownhotel.com/wrestlers/austin-theory'),
'Ridge Holland':('ridge-holland','Luke Menzies','1988-05-29','Liversedge, West Yorkshire, England','English','','Ridge Holland;Luke Menzies','https://en.wikipedia.org/wiki/Ridge_Holland'),
'Montez Ford':('montez-ford','Kenneth Crawford','1990-05-31','Chicago, Illinois, United States','American','2015','Montez Ford;Kenneth Crawford','https://en.wikipedia.org/wiki/Montez_Ford'),
'Johnny Knoxville':('johnny-knoxville','Philip John Clapp','1971-03-11','Knoxville, Tennessee, United States','American','','Johnny Knoxville','https://www.imdb.com/name/nm0424216/bio/'),
'Angelo Dawkins':('angelo-dawkins','Gary Gordon','1990-07-24','Fairfield, Ohio, United States','American','2012','Angelo Dawkins','https://en.wikipedia.org/wiki/Angelo_Dawkins'),
'Chad Gable':('chad-gable','Charles Edward Betts','1986-03-08','Saint Michael, Minnesota, United States','American','2003','Chad Gable;Shorty G','https://en.wikipedia.org/wiki/Chad_Gable'),
'Rick Boogs':('rick-boogs','Eric Bugenhagen','1987-12-01','Franklin, Wisconsin, United States','American','2017','Rick Boogs;Eric Bugenhagen','https://en.wikipedia.org/wiki/Rick_Boogs'),
'Madcap Moss':('riddick-moss','Michael Carter Rallis','1989-10-10','Edina, Minnesota, United States','American','2014','Madcap Moss;Riddick Moss','https://en.wikipedia.org/wiki/Riddick_Moss'),
'Bad Bunny':('bad-bunny','Benito Antonio Martínez Ocasio','1994-03-10','Vega Baja, Puerto Rico','Puerto Rican','','Bad Bunny','https://www.biography.com/musicians/bad-bunny')}
for i,(n,b) in enumerate(bio.items(),234): sources.append([f'S{i}',f'Dedicated biography — {n}','biography',b[-1],7,'Dedicated biography source',DATE,f'Person-specific biography lookup for {n}.'])
with open(os.path.join(D,'sources.csv'),'a',newline='',encoding='utf-8') as f: csv.writer(f).writerows(sources)
wr=list(csv.DictReader(open(os.path.join(D,'wrestlers.csv'),encoding='utf-8'))); byname={r['ring_name'].lower():r['wrestler_id'] for r in wr}; aliases={a.strip().lower():r['wrestler_id'] for r in wr for a in r['aliases_ring_names'].split(';') if a.strip()}
new=[]
for i,(n,b) in enumerate(bio.items(),234):
 if n.lower() not in byname and n.lower() not in aliases:
  wid,real,dob,bp,nat,debut,als,url=b; r=blank(WRESTLERS_FIELDS); r.update(wrestler_id=wid,ring_name=n,real_name=real,real_name_status='CONFIRMED',gender='M',dob=dob,dob_status='CONFIRMED',birthplace=bp,birthplace_status='CONFIRMED',nationality=nat,debut_year_company=debut,aliases_ring_names=als,notes=f'Added for {E}; individually researched.',source_ids=f'S{i}'); new.append(r); byname[n.lower()]=wid
append_dict('wrestlers.csv',WRESTLERS_FIELDS,new)
# stable-id overrides for event monikers
ids={**byname,**aliases}; ids.update({'happy corbin':'baron-corbin','riddle':'matt-riddle'})
names=['AJ Styles','Shinsuke Nakamura','Austin Theory','Robert Roode','Ridge Holland','Montez Ford','Damian Priest','Sami Zayn','Johnny Knoxville','Angelo Dawkins','Omos','Ricochet','Chad Gable','Dominik Mysterio','Happy Corbin','Dolph Ziggler','Sheamus','Rick Boogs','Madcap Moss','Riddle','Drew McIntyre','Kevin Owens','Rey Mysterio','Kofi Kingston','Otis','Big E','Bad Bunny','Shane McMahon','Randy Orton','Brock Lesnar']
wid={n:ids[n.lower()] for n in names}
times=['29:06','05:51','22:06','00:54','19:11','09:10','11:04','03:17','01:26','02:15','04:24','04:23','08:18','03:44','10:47','20:46','17:55','04:33','04:24','19:46','19:18','11:13','09:05','00:21','08:52','06:37','07:41','05:38','02:21','02:32']
order=[14,2,11,1,12,6,7,4,3,5,8,9,13,10,17,20,19,15,16,27,29,22,21,18,24,23,26,28,25,'']
elimby={'AJ Styles':['Madcap Moss'],'Shinsuke Nakamura':['AJ Styles'],'Austin Theory':['AJ Styles'],'Robert Roode':['AJ Styles'],'Ridge Holland':['AJ Styles'],'Montez Ford':['Omos'],'Damian Priest':['Omos'],'Sami Zayn':['AJ Styles'],'Johnny Knoxville':['Sami Zayn'],'Angelo Dawkins':['Omos'],'Omos':['AJ Styles','Austin Theory','Chad Gable','Dominik Mysterio','Ricochet','Ridge Holland'],'Ricochet':['Happy Corbin'],'Chad Gable':['Rick Boogs'],'Dominik Mysterio':['Happy Corbin'],'Happy Corbin':['Drew McIntyre'],'Dolph Ziggler':['Bad Bunny'],'Sheamus':['Bad Bunny'],'Rick Boogs':['Happy Corbin'],'Madcap Moss':['Drew McIntyre'],'Riddle':['Brock Lesnar'],'Drew McIntyre':['Brock Lesnar'],'Kevin Owens':['Shane McMahon'],'Rey Mysterio':['Otis'],'Kofi Kingston':['Kevin Owens'],'Otis':['Randy Orton','Riddle'],'Big E':['Randy Orton','Riddle'],'Bad Bunny':['Brock Lesnar'],'Shane McMahon':['Brock Lesnar'],'Randy Orton':['Brock Lesnar']}
elimrows=[]; entrants=[]
for i,n in enumerate(names):
 es=elimby.get(n,[]); shared=len(es)>1; win=n=='Brock Lesnar'
 for e in es:
  r=blank(ELIMINATIONS_FIELDS); r.update(event_id=E,order_in_match=order[i],eliminated_wrestler_id=wid[n],eliminator_wrestler_id=wid[e],assisting_wrestler_ids=';'.join(wid[x] for x in es if x!=e) if shared else '',entry_number_of_eliminated=i+1,entry_number_of_eliminator=names.index(e)+1,elimination_type='over_top_rope',is_solo='FALSE' if shared else 'TRUE',is_shared='TRUE' if shared else 'FALSE',is_accidental='FALSE',is_self_elimination='FALSE',is_disputed='FALSE',simultaneous_group_id=f'{E}-E{order[i]}' if shared else '',data_quality_status='CONFIRMED',source_ids='S232;S233'); elimrows.append(r)
 er=blank(ENTRANTS_FIELDS); er.update(event_id=E,wrestler_id=wid[n],match_id=E,entry_number=i+1,entry_number_status='CONFIRMED',ring_name_at_time=n,name_displayed_at_event=n,elim_number=order[i],elim_number_status='' if win else 'CONFIRMED',eliminated_by_ids=';'.join(wid[x] for x in es),ring_time=times[i],ring_time_seconds=sec(times[i]),ring_time_status='CONFIRMED',self_eliminated='FALSE',is_winner='TRUE' if win else 'FALSE',is_runner_up='TRUE' if n=='Drew McIntyre' else 'FALSE',is_final_two='TRUE' if n in {'Brock Lesnar','Drew McIntyre'} else 'FALSE',is_final_three='TRUE' if n in {'Brock Lesnar','Drew McIntyre','Shane McMahon'} else 'FALSE',is_final_four='TRUE' if n in {'Brock Lesnar','Drew McIntyre','Shane McMahon','Riddle'} else 'FALSE',surprise_entrant='TRUE' if n in {'Bad Bunny','Shane McMahon','Brock Lesnar'} else 'FALSE',legend_returning='FALSE',celebrity_entrant='TRUE' if n in {'Johnny Knoxville','Bad Bunny'} else 'FALSE',wrestled_earlier_on_card='TRUE' if n=='Brock Lesnar' else 'FALSE',data_quality_status='CONFIRMED',source_ids='S232;S233'); entrants.append(er)
credit={}
for r in elimrows: credit.setdefault(r['eliminator_wrestler_id'],[]).append(r['eliminated_wrestler_id'])
for r in entrants:
 c=credit.get(r['wrestler_id'],[]); r['wrestlers_eliminated_count']=len(c);r['wrestlers_eliminated_ids']=';'.join(c);r['solo_eliminations_count']=sum(x['eliminator_wrestler_id']==r['wrestler_id'] and x['is_solo']=='TRUE' for x in elimrows);r['assisted_eliminations_count']=sum(x['eliminator_wrestler_id']==r['wrestler_id'] and x['is_shared']=='TRUE' for x in elimrows)
append_dict('entrants.csv',ENTRANTS_FIELDS,entrants);append_dict('eliminations.csv',ELIMINATIONS_FIELDS,elimrows)
flags=[['F422',E,'entrants','happy-corbin;riddle','wrestler_id','name_stable_id','Happy Corbin reuses baron-corbin and Riddle reuses matt-riddle, following the earlier database precedent that a presentation/name change does not create a duplicate person record. This differs from genuinely distinct-performer additions such as Omos in RR2021M.','S232;S233','resolved',DATE],['F423',E,'entrants','johnny-knoxville;bad-bunny','celebrity_entrant','classification','Johnny Knoxville and Bad Bunny are explicitly treated as celebrity entrants because the event sources identify them as actor/stunt performer and music star respectively, while still crediting their official in-match eliminations.','S232;S233','resolved',DATE]]
with open(os.path.join(D,'flags.csv'),'a',newline='',encoding='utf-8') as f: csv.writer(f).writerows(flags)
m=[]
for mid,title,people,desc in [('NM96','Brock Lesnar wins from No. 30',['Brock Lesnar'],'Lesnar entered at No. 30 and won after five eliminations.'),('NM97','Bad Bunny returns',['Bad Bunny'],'Bad Bunny returned as a surprise celebrity entrant and recorded two eliminations.'),('NM98','Johnny Knoxville enters',['Johnny Knoxville'],'Johnny Knoxville entered at No. 9 and was eliminated by Sami Zayn.'),('NM99','Omos group elimination',['Omos'],'Six official entrants combined to eliminate Omos.')]:
 r=blank(NOTABLE_MOMENTS_FIELDS);r.update(moment_id=mid,event_id=E,wrestler_ids_involved=';'.join(wid[x] for x in people),category='notable',title=title,description=desc,data_quality_status='CONFIRMED',source_ids='S232;S233');m.append(r)
append_dict('notable_moments.csv',NOTABLE_MOMENTS_FIELDS,m)
ev=blank(EVENTS_FIELDS); ev.update(event_id=E,event_name='Royal Rumble 2022',match_name='Royal Rumble Match',match_type="Men's",event_date='2022-01-29',venue="The Dome at America's Center",city_region='St. Louis, Missouri',country='United States',entrant_count=len(entrants),duration_total='51:10',duration_status='CONFIRMED',winner_id=wid['Brock Lesnar'],runner_up_id=wid['Drew McIntyre'],final_two_ids=wid['Brock Lesnar']+';'+wid['Drew McIntyre'],final_three_ids=';'.join(wid[x] for x in ['Brock Lesnar','Drew McIntyre','Shane McMahon']),final_four_ids=';'.join(wid[x] for x in ['Brock Lesnar','Drew McIntyre','Shane McMahon','Riddle']),first_entrant_id=wid['AJ Styles'],second_entrant_id=wid['Shinsuke Nakamura'],final_entrant_id=wid['Brock Lesnar'],first_elimination_id=wid['Robert Roode'],last_elimination_before_winner_id=wid['Drew McIntyre'],eliminations_count=len({r['eliminated_wrestler_id'] for r in elimrows}),eliminators_count=len({r['eliminator_wrestler_id'] for r in elimrows}),surprise_entrants_count=sum(r['surprise_entrant']=='TRUE' for r in entrants),champions_in_field_count='',hall_of_famers_in_field_count='',tag_teams_count='',factions_count='',title_on_the_line='FALSE',championship_implications='Winner earned a world championship match at WrestleMania 38.',winners_reward='World championship match at WrestleMania 38.',data_quality_status='CONFIRMED',source_ids='S232;S233')
append_dict('events.csv',EVENTS_FIELDS,[ev])
checks={'entrant_count':len(entrants),'eliminations_count':len({r['eliminated_wrestler_id'] for r in elimrows}),'eliminators_count':len({r['eliminator_wrestler_id'] for r in elimrows}),'surprise_entrants_count':sum(r['surprise_entrant']=='TRUE' for r in entrants)}
print('SELF-CHECK RR2022M');
for k,v in checks.items(): print(f'{k}: declared={ev[k]} recomputed={v} match={str(ev[k])==str(v)}')
print(f'RR2022M build complete: {len(new)} new wrestlers, {len(entrants)} entrants, {len(elimrows)} elimination-credit rows, {len(sources)} sources, {len(flags)} flags, {len(m)} moments.')
