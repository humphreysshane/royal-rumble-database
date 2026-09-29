#!/usr/bin/env python3
"""Build RR2023W from live-web researched sources. Unknown fields stay blank."""
import csv, os, re, sys
sys.path.insert(0,os.path.dirname(__file__))
from schema import WRESTLERS_FIELDS,EVENTS_FIELDS,ENTRANTS_FIELDS,ELIMINATIONS_FIELDS,SOURCES_FIELDS,FLAGS_FIELDS,NOTABLE_MOMENTS_FIELDS
DATA_DIR=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'..','data')
E='RR2023W'; DATE='2026-09-22'
def blank(fields): return {k:'' for k in fields}
def sec(s):
 if not s:return ''
 a=list(map(int,s.split(':'))); return a[-1]+60*a[-2]+(3600*a[-3] if len(a)==3 else 0)
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def append_dict(fn,fields,rows):
 with open(os.path.join(DATA_DIR,fn),'a',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writerows(rows)
# Freshly recomputed after RR2023M: S260 / F429 / NM108.
sources=[
 {'source_id':'S260','source_name':'WWE.com — Rhea Ripley won the 2023 Women’s Royal Rumble Match','source_type':'official_wwe','url':'https://www.wwe.com/shows/royalrumble/2023/womens-royal-rumble-match-results','tier':'1','tier_name':'WWE / official sources','date_accessed':DATE,'notes':'Primary source: all 30 entrants, official survival times, eliminator credits and match narrative.'},
 {'source_id':'S261','source_name':'Royal Rumble (2023) — women’s entrances and eliminations','source_type':'event_database','url':'https://en.wikipedia.org/wiki/Royal_Rumble_(2023)#Women%27s_Royal_Rumble_match_entrances_and_eliminations','tier':'6','tier_name':'Reference/event table','date_accessed':DATE,'notes':'Cross-check for entry order, chronological elimination order, credits, duration and final placements.'},
]
bio_src=[
 ('S262','Emma / Tenille Dashwood — Pro Wrestlers Database','https://www.thesmackdownhotel.com/wrestlers/emma-tenille-dashwood'),
 ('S263','B-Fab — Pro Wrestlers Database','https://www.thesmackdownhotel.com/wrestlers/briana-brandy'),
 ('S264','Roxanne Perez — Pro Wrestlers Database','https://www.thesmackdownhotel.com/wrestlers/rok-c'),
 ('S265','Zoey Stark — Pro Wrestlers Database','https://www.thesmackdownhotel.com/wrestlers/zoey-stark-lacey-ryan'),
 ('S266','Piper Niven — Pro Wrestlers Database','https://www.thesmackdownhotel.com/wrestlers/piper-niven'),
 ('S267','Raquel Rodriguez — Pro Wrestlers Database','https://www.thesmackdownhotel.com/wrestlers/raquel-gonzalez'),
 ('S268','Mia Yim / Michin — Pro Wrestlers Database','https://www.thesmackdownhotel.com/wrestlers/mia-yim'),
 ('S269','Indi Hartwell — Pro Wrestlers Database','https://www.thesmackdownhotel.com/wrestlers/indi-hartwell'),
]
for sid,n,u in bio_src:sources.append({'source_id':sid,'source_name':n,'source_type':'wrestler_profile','url':u,'tier':'8','tier_name':'Dedicated wrestler profile','date_accessed':DATE,'notes':'Dedicated person-specific biography lookup for newly added wrestler.'})
append_dict('sources.csv',SOURCES_FIELDS,[{k:r.get(k,'') for k in SOURCES_FIELDS} for r in sources])
rows=list(csv.DictReader(open(os.path.join(DATA_DIR,'wrestlers.csv'),encoding='utf-8')))
lookup={}
for r in rows:
 for x in [r['ring_name']]+r.get('aliases_ring_names','').split(';'):
  if x.strip():lookup.setdefault(x.strip().lower(),r['wrestler_id'])
# Existing identity aliases established by prior records.
lookup.setdefault('iyo sky',lookup.get('io shirai',''))
lookup.setdefault('shotzi',lookup.get('shotzi blackheart',''))
lookup.setdefault('michin',lookup.get('mia yim',''))
bios={
 'Emma':('emma','Tenille Averil Dashwood','1989-03-01','Boronia, Victoria, Australia','Australian','2005','Emma;Tenille Dashwood;Emmalina;Tenille Tayla;Valentine','S262'),
 'B-Fab':('b-fab','Briana Brandy','1990-11-22','Canton, Ohio, United States','American','2019','B-Fab;Briana Brandy','S263'),
 'Roxanne Perez':('roxanne-perez','Carla Gonzalez','2001-11-05','Laredo, Texas, United States','American','2018','Roxanne Perez;Rok-C','S264'),
 'Zoey Stark':('zoey-stark','Theresa Serrano','1994-01-25','Salt Lake City, Utah, United States','American','','Zoey Stark;Lacey Ryan;Zoey Serrano;Serrano','S265'),
 'Piper Niven':('piper-niven','Kimberly Benson','1991-05-06','Ayrshire, Scotland','Scottish','2009','Piper Niven;Doudrop;Viper','S266'),
 'Raquel Rodriguez':('raquel-rodriguez','Victoria González','1991-01-12','La Feria, Texas, United States','American','2016','Raquel Rodriguez;Raquel González;Reina González;Victoria González','S267'),
 'Michin':('mia-yim','Stephanie Hym Bell','1989-04-16','Los Angeles, California, United States','American','2009','Michin;Mia Yim;RECKONING;Jade','S268'),
 'Indi Hartwell':('indi-hartwell','Samantha De Martin','1996-08-17','Melbourne, Australia','Australian','2016','Indi Hartwell;Samantha De Martin','S269'),
}
new=[]
for n,b in bios.items():
 if n.lower() not in lookup:
  wid,real,dob,bp,nat,debut,aliases,sids=b;r=blank(WRESTLERS_FIELDS);r.update(wrestler_id=wid,ring_name=n,real_name=real,real_name_status='CONFIRMED',gender='F',dob=dob,dob_status='CONFIRMED',birthplace=bp,birthplace_status='CONFIRMED',nationality=nat,debut_year_company=debut,aliases_ring_names=aliases,notes=f'Added for {E}; individually researched from a dedicated person-specific source.',source_ids=sids);new.append(r);lookup[n.lower()]=wid
append_dict('wrestlers.csv',WRESTLERS_FIELDS,new)
names=['Rhea Ripley','Liv Morgan','Dana Brooke','Emma','Shayna Baszler','Bayley','B-Fab','Roxanne Perez','Dakota Kai','IYO SKY','Natalya','Candice LeRae','Zoey Stark','Xia Li','Becky Lynch','Tegan Nox','Asuka','Piper Niven','Tamina','Chelsea Green','Zelina Vega','Raquel Rodriguez','Michin','Lacey Evans','Michelle McCool','Indi Hartwell','Sonya Deville','Shotzi','Nikki Cross','Nia Jax']
wid={n:lookup[n.lower()] for n in names}
times=['1:01:08','1:01:07','11:43','10:12','13:28','27:09','00:36','04:34','22:20','20:49','03:08','05:11','26:34','15:30','10:45','03:41','33:15','28:05','11:58','00:05','11:30','20:40','17:44','14:05','13:53','04:51','10:17','08:39','09:16','01:57']
orders=['',29,2,3,6,13,1,4,10,11,5,7,16,14,12,8,28,25,15,9,17,26,24,20,22,18,21,23,27,19]
elimby={
'Dana Brooke':['Bayley','Dakota Kai','IYO SKY'],'Emma':['Dakota Kai'],'Shayna Baszler':['Bayley','Dakota Kai','IYO SKY'],'Bayley':['Liv Morgan'],'B-Fab':['Rhea Ripley'],'Roxanne Perez':['Bayley','Dakota Kai','IYO SKY'],'Dakota Kai':['Becky Lynch'],'IYO SKY':['Becky Lynch'],'Natalya':['Bayley','Dakota Kai','IYO SKY'],'Candice LeRae':['IYO SKY'],'Zoey Stark':['Sonya Deville'],'Xia Li':['Zelina Vega'],'Becky Lynch':['Bayley'],'Tegan Nox':['Asuka'],'Asuka':['Rhea Ripley'],'Piper Niven':['Raquel Rodriguez'],'Tamina':['Michelle McCool'],'Chelsea Green':['Rhea Ripley'],'Zelina Vega':['Lacey Evans'],'Raquel Rodriguez':['Rhea Ripley'],'Michin':['Piper Niven'],'Lacey Evans':['Raquel Rodriguez'],'Michelle McCool':['Rhea Ripley'],'Indi Hartwell':['Sonya Deville'],'Sonya Deville':['Asuka'],'Shotzi':['Michin'],'Nikki Cross':['Liv Morgan'],'Nia Jax':['Asuka','Lacey Evans','Liv Morgan','Michelle McCool','Michin','Nikki Cross','Piper Niven','Raquel Rodriguez','Rhea Ripley','Sonya Deville','Shotzi'],'Liv Morgan':['Rhea Ripley']}
elimrows=[];entrants=[]
for i,n in enumerate(names):
 es=elimby.get(n,[]);win=n=='Rhea Ripley';shared=len(es)>1
 for e in es:
  r=blank(ELIMINATIONS_FIELDS);r.update(event_id=E,order_in_match=orders[i],eliminated_wrestler_id=wid[n],eliminator_wrestler_id=wid[e],assisting_wrestler_ids=';'.join(wid[x] for x in es if x!=e) if shared else '',entry_number_of_eliminated=i+1,entry_number_of_eliminator=names.index(e)+1,elimination_type='over_top_rope',is_solo='FALSE' if shared else 'TRUE',is_shared='TRUE' if shared else 'FALSE',is_accidental='FALSE',is_self_elimination='FALSE',is_disputed='FALSE',simultaneous_group_id=f'{E}-E{orders[i]}' if shared else '',data_quality_status='CONFIRMED',source_ids='S260;S261',notes='');elimrows.append(r)
 er=blank(ENTRANTS_FIELDS);er.update(event_id=E,wrestler_id=wid[n],match_id=E,entry_number=i+1,entry_number_status='CONFIRMED',ring_name_at_time=n,name_displayed_at_event=n,elim_number='' if win else orders[i],elim_number_status='' if win else 'CONFIRMED',eliminated_by_ids=';'.join(wid[x] for x in es),ring_time=times[i],ring_time_seconds=sec(times[i]),ring_time_status='CONFIRMED',self_eliminated='FALSE',is_winner='TRUE' if win else 'FALSE',is_runner_up='TRUE' if n=='Liv Morgan' else 'FALSE',is_final_two='TRUE' if n in {'Rhea Ripley','Liv Morgan'} else 'FALSE',is_final_three='TRUE' if n in {'Rhea Ripley','Liv Morgan','Asuka'} else 'FALSE',is_final_four='TRUE' if n in {'Rhea Ripley','Liv Morgan','Asuka','Nikki Cross'} else 'FALSE',surprise_entrant='TRUE' if n in {'Roxanne Perez','Michelle McCool','Indi Hartwell','Nia Jax'} else 'FALSE',legend_returning='TRUE' if n in {'Michelle McCool','Nia Jax'} else 'FALSE',celebrity_entrant='FALSE',data_quality_status='CONFIRMED',source_ids='S260;S261',notes='WWE page displays a stray minus sign before 0:10:12; independent event table and narrative support 10:12. See F430.' if n=='Emma' else '');entrants.append(er)
credit={}
for r in elimrows:credit.setdefault(r['eliminator_wrestler_id'],[]).append(r['eliminated_wrestler_id'])
for r in entrants:
 c=credit.get(r['wrestler_id'],[]);r['wrestlers_eliminated_count']=len(c);r['wrestlers_eliminated_ids']=';'.join(c);r['solo_eliminations_count']=sum(x['eliminator_wrestler_id']==r['wrestler_id'] and x['is_solo']=='TRUE' for x in elimrows);r['assisted_eliminations_count']=sum(x['eliminator_wrestler_id']==r['wrestler_id'] and x['is_shared']=='TRUE' for x in elimrows)
append_dict('entrants.csv',ENTRANTS_FIELDS,entrants);append_dict('eliminations.csv',ELIMINATIONS_FIELDS,elimrows)
flags=[
 ['F429',E,'wrestlers;entrants','io-shirai;shotzi-blackheart','wrestler_id','identity_alias_reuse','The event names IYO SKY and Shotzi are later/current ring names of existing database people io-shirai and shotzi-blackheart. Following the same-person alias precedent used for Riddle/matt-riddle and King Corbin/baron-corbin, the existing wrestler_ids are reused rather than creating duplicate people.','S260;S261;S268','resolved',DATE],
 ['F430',E,'entrants','emma','ring_time','source_typo','WWE’s official results table renders Emma’s time as -0:10:12, an impossible negative survival time. The independent event table records 10:12 and WWE’s narrative places her normal entry/elimination sequence. Store 10:12; this is a source-display typo correction, not an unknown value.','S260;S261','resolved',DATE]
]
with open(os.path.join(DATA_DIR,'flags.csv'),'a',newline='',encoding='utf-8') as f:csv.writer(f).writerows(flags)
m=[]
for mid,title,people,desc in [
 ('NM108','Rhea Ripley wins from No. 1',['Rhea Ripley'],'Ripley became the first woman to win the Royal Rumble from the No. 1 position.'),
 ('NM109','Ripley and Morgan go wire-to-wire',['Rhea Ripley','Liv Morgan'],'The No. 1 and No. 2 entrants became the final two after each lasting more than 61 minutes.'),
 ('NM110','Chelsea Green eliminated in five seconds',['Chelsea Green','Rhea Ripley'],'Returning Chelsea Green was eliminated by Ripley after five seconds.'),
 ('NM111','Eleven women eliminate Nia Jax',['Nia Jax','Asuka','Lacey Evans','Liv Morgan','Michelle McCool','Michin','Nikki Cross','Piper Niven','Raquel Rodriguez','Rhea Ripley','Sonya Deville','Shotzi'],"WWE's official RR2023W results explicitly state that the other 11 Superstars eliminated Nia Jax, and its Eliminated By table names Asuka, Lacey Evans, Liv Morgan, Michelle McCool, Michin, Nikki Cross, Piper Niven, Raquel Rodriguez, Rhea Ripley, Sonya Deville, and Shotzi. All 11 therefore receive structured assisted-elimination credit.")]:
 r=blank(NOTABLE_MOMENTS_FIELDS);r.update(moment_id=mid,event_id=E,wrestler_ids_involved=';'.join(wid[x] for x in people),category='notable',title=title,description=desc,data_quality_status='CONFIRMED',source_ids='S260;S261');m.append(r)
append_dict('notable_moments.csv',NOTABLE_MOMENTS_FIELDS,m)
ev=blank(EVENTS_FIELDS);ev.update(event_id=E,event_name='Royal Rumble 2023',match_name='Royal Rumble Match',match_type="Women's",event_date='2023-01-28',venue='Alamodome',city_region='San Antonio, Texas',country='United States',entrant_count=len(entrants),duration_total='1:01:08',duration_status='CONFIRMED',winner_id=wid['Rhea Ripley'],runner_up_id=wid['Liv Morgan'],final_two_ids=wid['Rhea Ripley']+';'+wid['Liv Morgan'],final_three_ids=';'.join(wid[x] for x in ['Rhea Ripley','Liv Morgan','Asuka']),final_four_ids=';'.join(wid[x] for x in ['Rhea Ripley','Liv Morgan','Asuka','Nikki Cross']),first_entrant_id=wid['Rhea Ripley'],second_entrant_id=wid['Liv Morgan'],final_entrant_id=wid['Nia Jax'],first_elimination_id=wid['B-Fab'],last_elimination_before_winner_id=wid['Liv Morgan'],eliminations_count=len({r['eliminated_wrestler_id'] for r in elimrows}),eliminators_count=len({r['eliminator_wrestler_id'] for r in elimrows}),surprise_entrants_count=sum(r['surprise_entrant']=='TRUE' for r in entrants),champions_in_field_count='',hall_of_famers_in_field_count='',tag_teams_count='',factions_count='',title_on_the_line='FALSE',championship_implications='Winner earned a women’s world championship match at WrestleMania 39.',winners_reward='Women’s world championship match at WrestleMania 39.',data_quality_status='CONFIRMED',source_ids='S260;S261')
append_dict('events.csv',EVENTS_FIELDS,[ev])
checks={'entrant_count':len(entrants),'eliminations_count':len({r['eliminated_wrestler_id'] for r in elimrows}),'eliminators_count':len({r['eliminator_wrestler_id'] for r in elimrows}),'surprise_entrants_count':sum(r['surprise_entrant']=='TRUE' for r in entrants)}
print('SELF-CHECK RR2023W')
for k,v in checks.items():print(f'{k}: declared={ev[k]} recomputed={v} match={str(ev[k])==str(v)}')
print(f'RR2023W build complete: {len(new)} new wrestlers, {len(entrants)} entrants, {len(elimrows)} elimination-credit rows, {len(sources)} sources, {len(flags)} flags, {len(m)} moments.')
