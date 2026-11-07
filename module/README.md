# Departmental test prep module

Standalone, Vercel-deployable (`outputDirectory: web`). Learner app `web/index.html`, admin dashboard `web/admin.html`.
Pipeline: `npm run extract` (pdftotext -> questions, repeat clustering) -> add rule-book answers in `data/answers.json`
-> `python3 -I tools/verify_quotes.py <book txt dir>` (every quote must appear verbatim in the book) -> `npm run build` -> `npm test`.
Status: 36 of 82 papers parsed (rest are scans awaiting OCR). Rule-book answers: pilot only.
calacutech.com integration: link its admin modules to `/admin` of this deployment (needs calacutech repo).
