#!/usr/bin/env python3
"""Extract questions from text-layer question-paper PDFs, cluster repeats, rank by frequency.
Usage: python3 -I tools/extract.py <pdf_dir> <out_json>
Scanned PDFs (no text layer) are listed in out_json['needs_ocr'] for a separate OCR/vision pass."""
import json, re, subprocess, sys, pathlib, collections

STOP = set("the of and to in a is are for or by on as at be with from that this which what any under shall may his her it its an if not state write short notes explain following give briefly".split())
MARK = re.compile(r'^\s*(?:\(?(?:[IVX]{1,5}|\d{1,2}|[a-z]|[ivx]{1,4})[\).]|\([a-z0-9ivx]+\))\s+')
NOISE = re.compile(r'^(?:\[?P\.?T\.?O\.?\]?|Marks|\[\d+\]|\d+)\s*$|Maximum|Duration|Time\s*:|With Books|Without Books|\[with|\[without', re.I)

def text_of(pdf):
    return subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,text=True).stdout

def title_of(txt):
    lines=[l.strip() for l in txt.splitlines() if l.strip()]
    return ' | '.join(lines[:6])[:200]

def questions(txt):
    out,cur=[],''
    started=False
    for raw in txt.splitlines():
        l=re.sub(r'\s{2,}.*?(\(\d.*\)|\d+)\s*$','',raw).strip()  # strip trailing marks column
        l=re.sub(r'\s{3,}',' ',l)
        if not l or NOISE.search(l): continue
        if MARK.match(l):
            started=True
            if len(cur)>25: out.append(cur)
            cur=MARK.sub('',l)
        elif started:
            cur=(cur+' '+l).strip()
    if len(cur)>25: out.append(cur)
    return [q for q in out if len(q.split())>=5 and not re.search(r'DEPARTMENTAL|EXAMINATION|TEST\s*[—-]|Division\s*[‘\'"“]',q)]

def toks(q): return {w for w in re.findall(r'[a-z0-9]+',q.lower()) if w not in STOP and len(w)>2}
def jac(a,b): return len(a&b)/max(1,len(a|b))

def main(d,out):
    papers=[];needs=[]
    for pdf in sorted(pathlib.Path(d).glob('*.pdf')):
        t=text_of(pdf)
        qs=questions(t) if len(re.findall(r'[A-Za-z]{4,}',t))>120 else []
        if not qs: needs.append(pdf.name); continue
        papers.append({'file':pdf.name,'session':pdf.name[:7],'title':title_of(t),'questions':qs})
    clusters=[]  # each: {rep, toks, items:[(file,session,text)]}
    for p in papers:
        for q in p['questions']:
            tk=toks(q)
            best=max(clusters,key=lambda c:jac(tk,c['toks']),default=None)
            if best and jac(tk,best['toks'])>=0.5: best['items'].append((p['file'],p['session'],q)); best['toks']|=tk
            else: clusters.append({'toks':set(tk),'items':[(p['file'],p['session'],q)]})
    cards=[]
    for i,c in enumerate(sorted(clusters,key=lambda c:-len({s for _,s,_ in c['items']}))):
        sess=sorted({s for _,s,_ in c['items']})
        cards.append({'id':f'q{i:04d}','question':max((t for _,_,t in c['items']),key=len),
          'freq':len(c['items']),'sessions':sess,'papers':sorted({f for f,_,_ in c['items']}),
          'answer':None,'answer_source':None})
    json.dump({'papers':[{k:v for k,v in p.items() if k!='questions'}|{'n':len(p['questions'])} for p in papers],
               'needs_ocr':needs,'cards':cards},open(out,'w'),indent=1,ensure_ascii=False)
    print(len(papers),'papers parsed;',len(needs),'need OCR;',len(cards),'unique questions;',sum(c['freq']>1 for c in cards),'repeated')
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
