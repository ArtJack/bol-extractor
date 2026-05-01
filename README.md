# BOL Extractor

A work-in-progress Python tool for extracting structured data from Bill of Lading PDFs and turning the results into JSON or an Excel summary.

The project currently uses Anthropic Claude's document understanding API to read BOL PDFs and return a normalized shipment record with fields like BOL number, pickup and delivery dates, shipper, consignee, commodity, weight, carrier, freight terms, and notes.

## Status

This is an active, early-stage project. The extraction prompt, schema, and output formatting are still evolving as more BOL layouts are tested.

## Privacy

Real BOLs often contain private shipment, customer, carrier, and routing information. This public repository intentionally excludes:

- Source BOL PDFs
- `.env` files and API keys
- Generated JSON extraction results
- Generated Excel summaries
- Local debug logs and assistant settings

Put private documents in the local `bols/` folder when running the project. Do not commit real BOLs or extraction output.

## What It Does

- Reads a single BOL PDF and sends it to Claude for structured extraction
- Supports multi-BOL documents when the model returns an array
- Saves the most recent single-file extraction to `last_extraction.json`
- Processes a local folder of PDFs into `all_extractions.json`
- Exports a boss-friendly spreadsheet to `bol_summary.xlsx`

## Setup

This project is built for Python 3.12.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Anthropic API key to `.env`:

```bash
ANTHROPIC_API_KEY=your_key_here
```

## Usage

Create a local `bols/` folder and place private BOL PDFs there.

Extract one PDF:

```bash
python extract_bol.py "bols/example.pdf"
```

If no file is provided, `extract_bol.py` uses the first PDF it finds in `bols/`.

Process every PDF in `bols/`:

```bash
python process_all.py
```

The batch script writes:

- `all_extractions.json`
- `bol_summary.xlsx`

Both files are ignored by Git because they may contain private data.

## Extracted Fields

The current schema targets:

- BOL, PRO, PO, load, and reference numbers
- Pickup and delivery dates
- Shipper and consignee names and locations
- Commodity description
- Total weight and piece count
- Carrier
- Freight terms
- Notes and special instructions

## Roadmap

- Add sanitized sample fixtures
- Add automated tests for known BOL layouts
- Improve batch error reporting
- Add schema validation before writing output
- Add optional redaction tools for safe demos
