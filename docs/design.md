# BOL Extractor — Design (SDD)

> How the system meets [requirements.md](requirements.md).

## 1. Architecture
```
 BOL PDF(s) ──▶ extract_bol.py ──▶ Claude document understanding ──▶ normalized record(s)
   (local bols/)        │                                                   │
                  process_all.py ──────────────────────────────────▶ all_extractions.json
                                                                      bol_summary.xlsx
```

## 2. Key design decisions
1. **Privacy by construction.** The repo is public but carries no data: `bols/`, `.env`, and every
   generated artifact are git-ignored. You cannot accidentally leak a customer BOL by cloning.
2. **One record shape, many layouts.** A single normalized schema is the contract; the LLM absorbs
   per-carrier format variation so downstream code stays simple.
3. **Single-file and batch share one extractor.** `process_all.py` reuses the same path as
   `extract_bol.py`, so behavior can't drift between the two entry points.
4. **Boss-friendly output.** JSON for machines, Excel for humans — the spreadsheet is the artifact
   a dispatcher actually wants.

## 3. Components
- `extract_bol.py` — single PDF → record(s), saved to `last_extraction.json`.
- `process_all.py` — folder → `all_extractions.json` + `bol_summary.xlsx`.
- Schema — the normalized shipment fields (see requirements.md FR-5).

## 4. Roadmap (engineering, not just features)
- Sanitized sample fixtures so the repo is runnable without private data.
- Automated tests against known BOL layouts.
- Schema validation before writing output.
- Optional redaction tools for safe public demos.
