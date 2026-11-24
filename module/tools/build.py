#!/usr/bin/env python3
"""raw_questions.json (+ optional data/answers.json {id: {answer, source}}) -> web/data.json"""
import json,re,pathlib
raw=json.load(open('data/raw_questions.json'))
ans={}
for f in sorted(pathlib.Path('data').glob('answers*.json')): ans.update(json.load(open(f)))
def exam(t):
    m=re.search(r"(Division\s*[‘'“\"]?\s*[A-E]\d?[’'”\"]?\s*\((?:Higher|Lower)[^)]*\)|PAPER\s*-\s*[IVX0-9]+[^|]{0,40}|FIRST GRADE[^|]{0,50}|HEAD SURVEYOR[^|]{0,40})",t,re.I)
    return re.sub(r'\s+',' ',m.group(1)).strip() if m else 'Other departmental tests'
pe={p['file']:exam(p['title']) for p in raw['papers']}
cards=[]
for c in raw['cards']:
    c=dict(c); a=ans.get(c['id'])
    if a: c['answer']=a['answer']; c['answer_source']=a.get('source'); c['quotes']=a.get('quotes',[])
    c['exams']=sorted({pe[f] for f in c['papers']}); c.pop('papers'); cards.append(c)
# Learning layer: one short plain-language tip per fact, linked to its quote and the past question it came from.
byq={c['id']:c for c in cards}
facts=[]
if pathlib.Path('data/facts.json').exists():
    for f in json.load(open('data/facts.json')):
        q=byq.get(f['qid'])
        if not q or not q.get('quotes'): print('skip',f['id'],'no linked answered question'); continue
        facts.append({'id':f['id'],'topic':f['topic'],'question':f['prompt'],'tip':f['tip'],'answer':f['tip'],
          'quotes':q['quotes'][:1],'requires':f['requires'],'freq':q['freq'],'sessions':q['sessions'],'exams':q['exams'],'source_question':q['id']})
exams=sorted({e for c in cards for e in c['exams']})
json.dump({'exams':exams,'cards':facts or cards,'questions':len(cards),'answered':sum(1 for c in cards if c['answer']),'needs_ocr':len(raw['needs_ocr'])},open('web/data.json','w'),ensure_ascii=False)
print(len(cards),'cards',len(exams),'exams:',exams)
