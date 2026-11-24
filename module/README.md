# Departmental test prep module

Standalone, Vercel-deployable (`outputDirectory: web`). Learner app `web/index.html`, admin dashboard `web/admin.html`.
Pipeline: `npm run extract` (pdftotext -> questions, repeat clustering) -> add rule-book answers in `data/answers.json`
-> `python3 -I tools/verify_quotes.py <book txt dir>` (every quote must appear verbatim in the book) -> `npm run build` -> `npm test`.
Status: 36 of 82 papers parsed (rest are scans awaiting OCR). Rule-book answers: pilot only.
calacutech.com integration: link its admin modules to `/admin` of this deployment (needs calacutech repo).

## Learning layer (tips)
Students see short plain-language tips, not raw exam questions. `data/facts.json`: one fact per card (`prompt`, `tip`, `topic`,
`requires`, `qid` = the past question it came from). The rule-book quote comes from that question's answer, so every tip is
traceable to an exact quote. Order = frequency in past papers, with `requires` pulled earlier. Raw questions stay for later quiz mode.
