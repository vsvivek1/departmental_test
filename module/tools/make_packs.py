#!/usr/bin/env python3
"""data/lessons/<paper>.json (+ *.mcq.json) -> packs/<paper>.json in QuizKerala course-pack format (docs/course-plan.md).
Lessons without valid questions are dropped (reported). Usage: python3 -I tools/make_packs.py"""
import json,glob,pathlib,sys
NAMES={'paper1-ksr':'Departmental Test Paper I: Kerala Service Rules','paper2-kfc':'Departmental Test Paper II: Kerala Financial Code',
'paper3-kac':'Departmental Test Paper III: Account Code and Budget Manual','paper4-ktc':'Departmental Test Paper IV: Kerala Treasury Code',
'service-rules':'Departmental Test: Subordinate Service and CCA Rules','public-works':'Departmental Test: Public Works Accounts and Stores'}
def okq(q):
    o=q.get('options',[])
    return (0<len(q.get('q',''))<=1200 and 2<=len(o)<=6 and len(set(o))==len(o) and all(0<len(x)<=300 for x in o)
            and isinstance(q.get('answer'),int) and 0<=q['answer']<len(o) and 0<len(q.get('why',''))<=500)
tot=0
for f in sorted(glob.glob('data/lessons/*.json')):
    if f.endswith('.mcq.json'): continue
    paper=pathlib.Path(f).stem;lessons=json.load(open(f));mcq={}
    for m in glob.glob(f'data/lessons/{paper}.*.mcq.json'): mcq.update(json.load(open(m)))
    out=[];dropped=0
    for l in lessons:
        m=mcq.get(l['slug']);qs=[q for q in (m or {}).get('questions',[]) if okq(q)]
        if len(qs)<2: dropped+=1;continue
        pts=[x['tip'] for x in l['facts']][:30]
        rem=[r[:300] for r in (m.get('remember') or pts[:3])][:6] or pts[:3]
        src='; '.join(sorted({x['quote']['ref'] for x in l['facts']}))[:300]
        out.append({'slug':f"{paper.split('-')[0][:6]}-{l['slug'].split('-')[-1]}",'unit':l['unit'][:80],'title':l['title'][:200],'language':'en','source':src,
          'points':pts,'remember':rem,'questions':[{'q':q['q'],'options':q['options'],'answer':q['answer'],'why':q['why']} for q in qs[:30]]})
    days=[];run=[]
    for l in out:
        days.append({'kind':'lesson','lessons':[l['slug']]});run.append(l['slug'])
        if len(run)==6: days.append({'kind':'revision','lessons':run});run=[]
    if run: days.append({'kind':'revision','lessons':run})
    days+= [{'kind':'mock','mock':i} for i in range(1,min(4,max(1,len(out)//8))+1)]
    json.dump({'name':NAMES.get(paper,paper),'lessons':out,'days':days},open(f'packs/{paper}.json','w'),indent=1,ensure_ascii=False)
    print(paper,len(out),'lessons',len(days),'days; dropped',dropped);tot+=len(out)
print('total lessons',tot)
