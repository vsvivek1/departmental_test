#!/usr/bin/env python3
"""raw_questions.json (+ optional data/answers.json {id: {answer, source}}) -> web/data.json"""
import json,re,pathlib
raw=json.load(open('data/raw_questions.json'))
ans=json.load(open('data/answers.json')) if pathlib.Path('data/answers.json').exists() else {}
def exam(t):
    m=re.search(r"(Division\s*[‘'“\"]?\s*[A-E]\d?[’'”\"]?\s*\((?:Higher|Lower)[^)]*\)|PAPER\s*-\s*[IVX0-9]+[^|]{0,40}|FIRST GRADE[^|]{0,50}|HEAD SURVEYOR[^|]{0,40})",t,re.I)
    return re.sub(r'\s+',' ',m.group(1)).strip() if m else 'Other departmental tests'
pe={p['file']:exam(p['title']) for p in raw['papers']}
cards=[]
for c in raw['cards']:
    c=dict(c); a=ans.get(c['id'])
    if a: c['answer']=a['answer']; c['answer_source']=a.get('source'); c['quotes']=a.get('quotes',[])
    c['exams']=sorted({pe[f] for f in c['papers']}); c.pop('papers'); cards.append(c)
exams=sorted({e for c in cards for e in c['exams']})
json.dump({'exams':exams,'cards':cards,'needs_ocr':len(raw['needs_ocr'])},open('web/data.json','w'),ensure_ascii=False)
print(len(cards),'cards',len(exams),'exams:',exams)
