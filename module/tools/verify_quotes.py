#!/usr/bin/env python3
"""Fail if any quote in data/answers.json is not an exact (whitespace-normalised) substring of its rule book.
Usage: python3 -I tools/verify_quotes.py <dir with pdftotext .txt of the books>"""
import json,re,sys,pathlib
norm=lambda s:re.sub(r'\s+',' ',s).replace('“','"').replace('”','"').replace('’',"'").strip()
d=pathlib.Path(sys.argv[1]);ans=json.load(open('data/answers.json'));bad=0
for cid,a in ans.items():
    for q in a.get('quotes',[]):
        t=norm((d/(q['book']+'.txt')).read_text())
        ok=norm(q['text']) in t
        print(('OK  ' if ok else 'FAIL'),cid,q['ref']);bad+=not ok
sys.exit(1 if bad else 0)
