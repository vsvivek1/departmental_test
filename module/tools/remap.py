#!/usr/bin/env python3
"""Re-key data/answers*.json after extract.py re-clusters (ids are sequential, so they shift).
Each answer stores 'q' (its question text); we match it to the closest new card (Jaccard >= 0.6)."""
import json,glob,re
new=json.load(open('data/raw_questions.json'))['cards']; old={}
for f in glob.glob('data/answers*.json'):
    pass
tk=lambda q:set(re.findall(r'[a-z0-9]+',q.lower()))
sc=lambda a,b:len(tk(a)&tk(b))/max(1,len(tk(a)|tk(b)))
for f in glob.glob('data/answers*.json'):
    a=json.load(open(f));out={}
    for k,v in a.items():
        q=v.get('q')
        if not q: out[k]=v;continue
        b=max(new,key=lambda c:sc(q,c['question']))
        if sc(q,b['question'])<0.6: print('LOST',k,q[:60]);continue
        out[b['id']]=v
    json.dump(out,open(f,'w'),indent=1,ensure_ascii=False)
