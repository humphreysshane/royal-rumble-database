#!/usr/bin/env python3
"""Build RR2021M (2021 Men's Royal Rumble) into DATA_DIR.

Methodology: live-web research only for 2021 match facts. WWE's official match
results are the primary source; Cagematch and CBS Sports cross-check entry and
elimination order/credit. WWE official ring-time values are stored where a
one-second discrepancy exists with Cageside Seats' footage-timed values, and
those rows are marked CONFLICTING with F416. King Corbin reuses baron-corbin;
Riddle reuses matt-riddle. Damian Priest, Otis and Dominik Mysterio are the
only genuinely new entrants; Omos is also added as a non-entrant wrestler
because WWE officially credits him with eliminating Big E and Rey Mysterio.
No unsourced value is guessed; unknown fields are left blank/UNKNOWN.
"""
import csv, os, re, sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from schema import (WRESTLERS_FIELDS, EVENTS_FIELDS, ENTRANTS_FIELDS,
                    ELIMINATIONS_FIELDS, SOURCES_FIELDS, FLAGS_FIELDS,
                    NOTABLE_MOMENTS_FIELDS)

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR2021M"
BUILD_DATE = "2026-09-22"

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def mmss_to_seconds(s):
    p=[int(x) for x in s.split(':')]
    return p[0]*60+p[1] if len(p)==2 else p[0]*3600+p[1]*60+p[2]

sources = [
("S212","WWE.com — Edge won the 2021 Royal Rumble Match","official_wwe","https://www.wwe.com/shows/royalrumble/01-31-2021/mens-royal-rumble-match-results",1,"WWE / official sources",BUILD_DATE,"Primary source for entrants, official ring times, eliminator credits, winner and match narrative."),
("S213","Cagematch — WWE Royal Rumble 2021","event_database","https://www.cagematch.net/?id=1&nr=299033",4,"Cagematch",BUILD_DATE,"Cross-check for event metadata, entrant order, elimination sequence and match clock timestamps."),
("S214","CBS Sports — 2021 WWE Royal Rumble results","reputable_wrestling_press","https://new.cbssports.com/wwe/news/2021-wwe-royal-rumble-results-recap-grades-edge-bianca-belair-emerge-as-winners-on-strong-show/live/",7,"Wrestling Observer/reputable wrestling pubs",BUILD_DATE,"Independent cross-check for entrant order and elimination order."),
("S215","Cageside Seats — Men's Royal Rumble 2021 match time and statistics","contemporary_publication","https://www.cagesideseats.com/wwe/2021/2/7/22271314/wwe-royal-rumble-2021-mens-match-time-statistics-survival-intervals-crowded-90-seconds",9,"Contemporary wrestling publication",BUILD_DATE,"Footage-timed survival values using legal ring entry; several differ by one second from WWE official values, logged in F416."),
("S216","WWE.com — Full Royal Rumble 2021 results","official_wwe","https://www.wwe.com/shows/royalrumble/article/royal-rumble-results",1,"WWE / official sources",BUILD_DATE,"Cross-check for event results and championship matches on the card."),
("S217","WWE.com — Intercontinental Championship title history","official_wwe","https://www.wwe.com/titlehistory/intercontinental-championship",1,"WWE / official sources",BUILD_DATE,"Confirms Big E's Intercontinental Championship reign began 2020-12-25."),
("S218","WWE.com — United States Championship title history","official_wwe","https://www.wwe.com/titlehistory/united-states-championship",1,"WWE / official sources",BUILD_DATE,"Confirms Bobby Lashley's United States Championship reign began 2020-08-30."),
("S219","Wikipedia — Damian Priest","reference_site","https://en.wikipedia.org/wiki/Damian_Priest",10,"Wikipedia/reference sites",BUILD_DATE,"Single-source bio data for genuinely new database wrestler Damian Priest; therefore bio fields are PROBABLE."),
("S220","Wikipedia — Otis (wrestler)","reference_site","https://en.wikipedia.org/wiki/Otis_(wrestler)",10,"Wikipedia/reference sites",BUILD_DATE,"Single-source bio data for genuinely new database wrestler Otis; therefore bio fields are PROBABLE."),
("S221","Wikipedia — Dominik Mysterio","reference_site","https://en.wikipedia.org/wiki/Dominik_Mysterio",10,"Wikipedia/reference sites",BUILD_DATE,"Single-source bio data for genuinely new database wrestler Dominik Mysterio; therefore bio fields are PROBABLE."),
("S222","Wikipedia — Omos","reference_site","https://en.wikipedia.org/wiki/Omos",10,"Wikipedia/reference sites",BUILD_DATE,"Single-source bio data for non-entrant Omos, required because WWE officially credits him with two eliminations."),
("S223","Wikipedia — Royal Rumble (2021)","reference_site","https://en.wikipedia.org/wiki/Royal_Rumble_(2021)",10,"Wikipedia/reference sites",BUILD_DATE,"Cross-check for venue, date, St. Petersburg location and zero in-person attendance during the ThunderDome pandemic event."),
]
with open(os.path.join(DATA_DIR,'sources.csv'),'a',newline='',encoding='utf-8') as f: csv.writer(f).writerows(sources)

all_names=["Edge","Randy Orton","Sami Zayn","Mustafa Ali","Jeff Hardy","Dolph Ziggler","Shinsuke Nakamura","Carlito","Xavier Woods","Big E","John Morrison","Ricochet","Elias","Damian Priest","The Miz","Riddle","Daniel Bryan","Kane","King Corbin","Otis","Dominik Mysterio","Bobby Lashley","The Hurricane","Christian","AJ Styles","Rey Mysterio","Sheamus","Cesaro","Seth Rollins","Braun Strowman"]
assert len(all_names)==30
ENTRY_NUMBERS={n:i+1 for i,n in enumerate(all_names)}

survival={"Edge":"58:27","Randy Orton":"58:27","Sami Zayn":"13:04","Mustafa Ali":"13:18","Jeff Hardy":"3:25","Dolph Ziggler":"20:30","Shinsuke Nakamura":"22:01","Carlito":"8:26","Xavier Woods":"3:42","Big E":"29:45","John Morrison":"8:14","Ricochet":"11:37","Elias":"2:30","Damian Priest":"15:34","The Miz":"1:02","Riddle":"31:17","Daniel Bryan":"28:50","Kane":"1:51","King Corbin":"3:34","Otis":"0:53","Dominik Mysterio":"2:00","Bobby Lashley":"4:03","The Hurricane":"0:30","Christian":"18:12","AJ Styles":"10:27","Rey Mysterio":"3:47","Sheamus":"5:56","Cesaro":"4:10","Seth Rollins":"8:48","Braun Strowman":"7:24"}
assert set(survival)==set(all_names)
RING_TIME_CONFLICT={"Edge","Mustafa Ali","Shinsuke Nakamura","Xavier Woods","Big E","Elias","Damian Priest","Daniel Bryan","King Corbin","Otis","Dominik Mysterio","Christian","AJ Styles","Sheamus","Cesaro","Braun Strowman"}

ELIM_ORDER=["Jeff Hardy","Sami Zayn","Xavier Woods","Mustafa Ali","Carlito","Elias","The Miz","John Morrison","Dolph Ziggler","Ricochet","Kane","Shinsuke Nakamura","Otis","King Corbin","Dominik Mysterio","Damian Priest","The Hurricane","Bobby Lashley","Big E","Rey Mysterio","Cesaro","Sheamus","AJ Styles","Daniel Bryan","Riddle","Braun Strowman","Christian","Seth Rollins","Randy Orton"]
elim_number={n:i+1 for i,n in enumerate(ELIM_ORDER)}
assert len(ELIM_ORDER)==29
FINAL_TWO={"Edge","Randy Orton"}; FINAL_THREE={"Edge","Randy Orton","Seth Rollins"}; FINAL_FOUR={"Edge","Randy Orton","Seth Rollins","Christian"}

ELIMINATORS={
"Jeff Hardy":(["Dolph Ziggler"],False,""),"Sami Zayn":(["Big E"],False,"WWE and CBS credit Big E alone; Cagematch/411Mania also credit Xavier Woods. See F415."),"Xavier Woods":(["Mustafa Ali"],False,""),"Mustafa Ali":(["Big E"],False,""),"Carlito":(["Elias"],False,""),"Elias":(["Damian Priest"],False,""),"The Miz":(["Damian Priest"],False,"Eliminated at essentially the same moment as John Morrison; ordered Miz then Morrison following CBS/411Mania."),"John Morrison":(["Damian Priest"],False,"Eliminated at essentially the same moment as The Miz."),"Dolph Ziggler":(["Kane"],False,""),"Ricochet":(["Kane"],False,""),"Kane":(["Damian Priest"],False,""),"Shinsuke Nakamura":(["King Corbin"],False,""),"Otis":(["King Corbin"],False,""),"King Corbin":(["Dominik Mysterio"],False,""),"Dominik Mysterio":(["Bobby Lashley"],False,""),"Damian Priest":(["Bobby Lashley"],False,""),"The Hurricane":(["Big E","Bobby Lashley"],True,""),"Bobby Lashley":(["Big E","Christian","Daniel Bryan","Riddle"],True,""),"Big E":(["Omos"],False,"Omos was not an entrant; WWE officially credits him with this elimination."),"Rey Mysterio":(["Omos"],False,"Omos was not an entrant; WWE officially credits him with this elimination."),"Cesaro":(["Braun Strowman"],False,""),"Sheamus":(["Braun Strowman"],False,""),"AJ Styles":(["Braun Strowman"],False,""),"Daniel Bryan":(["Seth Rollins"],False,""),"Riddle":(["Seth Rollins"],False,""),"Braun Strowman":(["Edge","Christian"],True,"WWE official table and Cagematch credit Edge & Christian; CBS lists Edge alone and 411Mania lists Edge & Seth Rollins. See F415."),"Christian":(["Seth Rollins"],False,""),"Seth Rollins":(["Edge"],False,""),"Randy Orton":(["Edge"],False,"Final elimination; Orton had spent most of the match outside the ring after being injured in the opening angle but was never eliminated."),}
assert set(ELIMINATORS)==set(ELIM_ORDER)
DISPUTED_ELIM_CREDIT={"Sami Zayn","Braun Strowman"}

CHAMPS_AT_ENTRY={"Big E","Bobby Lashley"}
CHAMP_INFO={"Big E":("Intercontinental Championship","Intercontinental/United States","2020-12-25",37),"Bobby Lashley":("United States Championship","Intercontinental/United States","2020-08-30",154)}
SURPRISE_ENTRANTS={"Carlito","Damian Priest","Kane","Christian"}
LEGENDS={"Carlito","Kane","The Hurricane","Christian"}

new_wrestlers=[
("Damian Priest","Luis Martinez","PROBABLE","M","1982-09-26","PROBABLE","","New York City, U.S.","PROBABLE","American","2005","","Punishment Martinez; Damian Martinez","","Royal Rumble debut at #14; bio fields sourced from one reference source and therefore marked PROBABLE.","S219"),
("Otis","Nikola Michal Bogojević","PROBABLE","M","1991-12-21","PROBABLE","","Duluth, Minnesota, U.S.","PROBABLE","American","2015","","Otis Dozovic; Dozer; Niko Bogojevic; El Gran Gordo","","Royal Rumble debut at #20; bio fields sourced from one reference source and therefore marked PROBABLE.","S220"),
("Dominik Mysterio","Dominik Óscar Gutiérrez","PROBABLE","M","1997-04-05","PROBABLE","","San Diego, California, U.S.","PROBABLE","American","2020","","","","Royal Rumble debut at #21; son of Rey Mysterio, who also entered this match. Bio fields sourced from one reference source and therefore marked PROBABLE.","S221"),
("Omos","Tolulope Omogbehin","PROBABLE","M","1992-05-16","PROBABLE","","Lagos, Nigeria","PROBABLE","Nigerian","2019","","Jordan Omogbehin; The Nigerian Giant","","Not an entrant in RR2021M. Added because WWE officially credits Omos, AJ Styles' ringside associate, with eliminating Big E and Rey Mysterio.","S222"),
]
reused={"Edge":"edge","Randy Orton":"randy-orton","Sami Zayn":"sami-zayn","Mustafa Ali":"mustafa-ali","Jeff Hardy":"jeff-hardy","Dolph Ziggler":"dolph-ziggler","Shinsuke Nakamura":"shinsuke-nakamura","Carlito":"carlito","Xavier Woods":"xavier-woods","Big E":"big-e","John Morrison":"john-morrison","Ricochet":"ricochet","Elias":"elias","The Miz":"the-miz","Riddle":"matt-riddle","Daniel Bryan":"daniel-bryan","Kane":"kane","King Corbin":"baron-corbin","Bobby Lashley":"bobby-lashley","The Hurricane":"the-hurricane","Christian":"christian","AJ Styles":"aj-styles","Rey Mysterio":"rey-mysterio","Sheamus":"sheamus","Cesaro":"cesaro","Seth Rollins":"seth-rollins","Braun Strowman":"braun-strowman"}
wrestler_ids=dict(reused)
with open(os.path.join(DATA_DIR,'wrestlers.csv'),'a',newline='',encoding='utf-8') as f:
    w=csv.writer(f)
    for row in new_wrestlers:
        wid=slugify(row[0]); wrestler_ids[row[0]]=wid; w.writerow([wid]+list(row))
assert set(all_names).issubset(wrestler_ids)

NEW_ENTRANTS={"Damian Priest","Otis","Dominik Mysterio"}
entrant_rows=[]; elim_rows=[]
for name in all_names:
    wid=wrestler_ids[name]; winner=name=="Edge"; entry=ENTRY_NUMBERS[name]
    elim_by,is_shared,note=ELIMINATORS.get(name,([],False,""))
    champ_title,champ_level,champ_date,champ_days=CHAMP_INFO.get(name,("","","", ""))
    for eliminator in elim_by:
        ew=wrestler_ids[eliminator]
        elim_rows.append({"event_id":EVENT_ID,"order_in_match":elim_number[name],"eliminated_wrestler_id":wid,"eliminator_wrestler_id":ew,"assisting_wrestler_ids":";".join(wrestler_ids[e] for e in elim_by if e!=eliminator) if is_shared else "","entry_number_of_eliminated":entry,"entry_number_of_eliminator":ENTRY_NUMBERS.get(eliminator,""),"elimination_clock_time":"","elimination_clock_seconds":"","elimination_type":"over_top_rope","elimination_method":"","location_side":"","location_status":"UNKNOWN","is_solo":"FALSE" if is_shared else "TRUE","is_shared":"TRUE" if is_shared else "FALSE","is_accidental":"FALSE","is_self_elimination":"FALSE","is_storyline_related":"UNKNOWN","was_already_incapacitated":"UNKNOWN","is_disputed":"TRUE" if name in DISPUTED_ELIM_CREDIT else "FALSE","simultaneous_group_id":f"RR2021M-E{elim_number[name]}" if is_shared else "","data_quality_status":"CONFLICTING" if name in DISPUTED_ELIM_CREDIT else "CONFIRMED","source_ids":"S212;S213;S214","notes":note})
    dq="CONFLICTING" if name in (DISPUTED_ELIM_CREDIT|RING_TIME_CONFLICT) else "CONFIRMED"
    er={k:"" for k in ENTRANTS_FIELDS}
    er.update({"event_id":EVENT_ID,"wrestler_id":wid,"match_id":EVENT_ID,"entry_number":entry,"entry_number_status":"CONFIRMED","ring_name_at_time":name,"name_displayed_at_event":name,"is_first_rumble_appearance":"TRUE" if name in NEW_ENTRANTS else "","is_rumble_debut":"TRUE" if name in NEW_ENTRANTS else "FALSE","is_company_debut":"","is_returning_wrestler":"TRUE" if name in LEGENDS else "","age_status":"UNKNOWN","physical_status":"UNKNOWN","alignment_status":"UNKNOWN","current_champion_title":champ_title,"championship_level":champ_level,"title_won_date":champ_date,"days_into_reign_at_event":champ_days,"title_defended_same_card":"FALSE","title_lost_same_card":"FALSE","elim_number":"" if winner else elim_number[name],"elim_number_status":"N/A" if winner else "CONFIRMED","eliminated_by_ids":";".join(wrestler_ids[e] for e in elim_by),"ring_time":survival[name],"ring_time_seconds":mmss_to_seconds(survival[name]),"ring_time_status":"CONFLICTING" if name in RING_TIME_CONFLICT else "CONFIRMED","self_eliminated":"FALSE","is_winner":"TRUE" if winner else "FALSE","is_runner_up":"TRUE" if name=="Randy Orton" else "FALSE","is_final_two":"TRUE" if name in FINAL_TWO else "FALSE","is_final_three":"TRUE" if name in FINAL_THREE else "FALSE","is_final_four":"TRUE" if name in FINAL_FOUR else "FALSE","surprise_entrant":"TRUE" if name in SURPRISE_ENTRANTS else "FALSE","legend_returning":"TRUE" if name in LEGENDS else "FALSE","celebrity_entrant":"FALSE","non_full_time_wrestler":"TRUE" if name in LEGENDS else "FALSE","wrestled_earlier_on_card":"FALSE","was_hof_member_at_time":"TRUE" if name=="Edge" else "FALSE","data_quality_status":dq,"source_ids":"S212;S213;S214;S215","notes":note})
    entrant_rows.append(er)

credit={}
for r in elim_rows: credit.setdefault(r['eliminator_wrestler_id'],[]).append(r['eliminated_wrestler_id'])
for er in entrant_rows:
    c=credit.get(er['wrestler_id'],[])
    er['wrestlers_eliminated_count']=len(c) if c else 0
    er['wrestlers_eliminated_ids']=';'.join(c)
    er['solo_eliminations_count']=sum(1 for r in elim_rows if r['eliminator_wrestler_id']==er['wrestler_id'] and r['is_solo']=='TRUE')
    er['assisted_eliminations_count']=sum(1 for r in elim_rows if r['eliminator_wrestler_id']==er['wrestler_id'] and r['is_solo']=='FALSE')
with open(os.path.join(DATA_DIR,'entrants.csv'),'a',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=ENTRANTS_FIELDS); w.writerows(entrant_rows)
with open(os.path.join(DATA_DIR,'eliminations.csv'),'a',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=ELIMINATIONS_FIELDS); w.writerows(elim_rows)

flags=[
("F414",EVENT_ID,"wrestlers","damian-priest;otis;dominik-mysterio;omos","bio_fields","unverified","Four wrestler records were new to this database. Their bio fields currently rely on one reference source each, so sourced bio values are PROBABLE rather than CONFIRMED. Omos receives structured eliminator credit despite not being an entrant because WWE’s own official results table explicitly names him as the eliminator of Big E and Rey Mysterio. This differs from the Authors of Pain interference in RR2020M, where WWE did not list AOP as eliminators of record; narrative interference alone is not converted into structured eliminator credit.","S219;S220;S221;S222","open",BUILD_DATE),
("F415",EVENT_ID,"eliminations","sami-zayn;braun-strowman","eliminated_by_ids","conflicting_sources","Eliminator-credit disagreement. Sami Zayn: WWE/CBS credit Big E alone; Cagematch and 411Mania credit Big E & Xavier Woods. Stored WWE's higher-tier Big E-only credit. Braun Strowman: WWE/Cagematch credit Edge & Christian; CBS lists Edge alone; 411Mania lists Edge & Seth Rollins. Stored WWE/Cagematch Edge & Christian credit.","S212;S213;S214","open",BUILD_DATE),
("F416",EVENT_ID,"entrants","multiple","ring_time","conflicting_sources","WWE's official survival times and Cageside Seats' footage-timed legal-ring-entry values differ by one second for 16 entrants. Per source-tier rule, WWE values are stored; affected ring_time_status fields are CONFLICTING. Cageside explicitly uses legal ring entry, matching DEFINITIONS.md, so the discrepancy is preserved rather than silently discarded.","S212;S215","open",BUILD_DATE),
("F417",EVENT_ID,"entrants","all","elimination_clock_time","unverified","Cagematch publishes match-clock elimination timestamps, but this build leaves entrant/elimination clock fields blank because no second independent source using the same match-clock convention was found for all eliminations.","S213","open",BUILD_DATE),
]
with open(os.path.join(DATA_DIR,'flags.csv'),'a',newline='',encoding='utf-8') as f: csv.writer(f).writerows(flags)

nm_rows=[
{"moment_id":"NM88","event_id":EVENT_ID,"wrestler_ids_involved":"edge","category":"record","title":"Edge wins from the No. 1 entry","description":"Edge entered at No. 1 and won the 2021 Men's Royal Rumble, lasting WWE's official 58:27 and last eliminating Randy Orton.","data_quality_status":"CONFIRMED","source_ids":"S212;S213;S214","notes":""},
{"moment_id":"NM89","event_id":EVENT_ID,"wrestler_ids_involved":"edge;randy-orton","category":"record","title":"The first two entrants become the final two","description":"Edge and Randy Orton entered first and second and ultimately became the final two, after Orton spent much of the match outside the ring following the opening injury angle without being eliminated.","data_quality_status":"CONFIRMED","source_ids":"S212;S223","notes":""},
{"moment_id":"NM90","event_id":EVENT_ID,"wrestler_ids_involved":"christian;edge","category":"milestone_first","title":"Christian returns for his first true match since 2014","description":"Christian entered at No. 24 in a surprise return, reunited with Edge in the ring, reached the final four and lasted WWE's official 18:12.","data_quality_status":"CONFIRMED","source_ids":"S212;S213","notes":""},
{"moment_id":"NM91","event_id":EVENT_ID,"wrestler_ids_involved":"big-e;rey-mysterio;omos","category":"storyline_moment","title":"Non-entrant Omos eliminates Big E and Rey Mysterio","description":"Omos, who was at ringside with AJ Styles but was not an official entrant, was officially credited by WWE with eliminating Big E and Rey Mysterio.","data_quality_status":"CONFIRMED","source_ids":"S212;S213","notes":""},
]
with open(os.path.join(DATA_DIR,'notable_moments.csv'),'a',newline='',encoding='utf-8') as f: csv.DictWriter(f,fieldnames=NOTABLE_MOMENTS_FIELDS).writerows(nm_rows)

event_row={k:"" for k in EVENTS_FIELDS}
event_row.update({"event_id":EVENT_ID,"event_name":"Royal Rumble 2021","match_name":"Royal Rumble Match","match_type":"Men's","event_date":"2021-01-31","venue":"WWE ThunderDome at Tropicana Field","city_region":"St. Petersburg, Florida","country":"United States","attendance_official":0,"attendance_reported":0,"entrant_count":30,"duration_total":"58:27","duration_status":"CONFIRMED","winner_id":"edge","runner_up_id":"randy-orton","final_two_ids":"edge;randy-orton","final_three_ids":"edge;randy-orton;seth-rollins","final_four_ids":"edge;randy-orton;seth-rollins;christian","first_entrant_id":"edge","second_entrant_id":"randy-orton","final_entrant_id":"braun-strowman","first_elimination_id":"jeff-hardy","last_elimination_before_winner_id":"randy-orton","eliminations_count":29,"eliminators_count":len({r["eliminator_wrestler_id"] for r in elim_rows}),"surprise_entrants_count":len(SURPRISE_ENTRANTS),"champions_in_field_count":len(CHAMPS_AT_ENTRY),"hall_of_famers_in_field_count":1,"tag_teams_count":"","factions_count":"","commentary_team":"","ring_announcer":"","referees":"","special_rules":"Standard Royal Rumble rules. The event was held in the WWE ThunderDome without an in-person paying audience during the COVID-19 pandemic.","title_on_the_line":"FALSE","championship_implications":"The winner earned a world championship match at WrestleMania 37.","winners_reward":"A world championship match at WrestleMania 37.","historical_significance":"Edge won from the No. 1 entry, with No. 2 entrant Randy Orton finishing runner-up. Christian made a surprise return for his first true match since 2014. The event was staged without an in-person audience in the WWE ThunderDome at Tropicana Field.","notes":"Eliminator-credit conflicts are preserved in F415. One-second ring-time source disagreements are preserved in F416. Omos was not an entrant but is represented as a wrestler because WWE officially credits him with eliminating Big E and Rey Mysterio.","data_quality_status":"CONFLICTING","source_ids":"S212;S213;S214;S215;S216;S223"})
with open(os.path.join(DATA_DIR,'events.csv'),'a',newline='',encoding='utf-8') as f: csv.DictWriter(f,fieldnames=EVENTS_FIELDS).writerow(event_row)

print(f"2021 Men's build complete: 3 new entrant wrestlers + 1 non-entrant wrestler (Omos), {len(reused)} reused entrant IDs, {len(entrant_rows)} entrants, {len(elim_rows)} elimination-credit rows, {len(sources)} sources, {len(flags)} flags, {len(nm_rows)} notable moments.")
