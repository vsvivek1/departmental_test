#!/usr/bin/env python3
"""Fail if any quote in data/answers.json is not an exact (whitespace-normalised) substring of its rule book.
Usage: python3 -I tools/verify_quotes.py <dir with pdftotext .txt of the books>"""
import json,re,sys,pathlib
norm=lambda s:re.sub(r'\s+',' ',s).replace('“','"').replace('”','"').replace('’',"'").strip()
d=pathlib.Path(sys.argv[1]);ans={};bad=0
for f in sorted(pathlib.Path('data').glob('answers*.json')): ans.update(json.load(open(f)))
for cid,a in ans.items():
    for q in a.get('quotes',[]):
        t=norm((d/(q['book']+'.txt')).read_text())
        ok=norm(q['text']) in t
        print(('OK  ' if ok else 'FAIL'),cid,q['ref']);bad+=not ok
for f in sorted(pathlib.Path('data').glob('facts_book_*.json')):
    for x in json.load(open(f)):
        q=x['quote'];t=norm((d/(q['book']+'.txt')).read_text());ok=norm(q['text']) in t
        print(('OK  ' if ok else 'FAIL'),x['id'],q['ref']);bad+=not ok
sys.exit(1 if bad else 0)
