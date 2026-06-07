# BOL Extractor — Requirements (SDD)

> Spec-driven development artifact: *what* and *why*. See [design.md](design.md).

## 1. Purpose
Turn messy **Bill of Lading (BOL) PDFs** into clean, structured shipment records (JSON + an
Excel summary) using an LLM's document-understanding, so logistics back-office work that's done
by hand can be automated.

## 2. Users
- Carriers / brokers / back-office staff who receive BOLs as PDFs and need structured data.

## 3. Functional requirements
- **FR-1** Read a single BOL PDF and return a normalized shipment record.
- **FR-2** Support multi-BOL documents (model returns an array).
- **FR-3** Batch-process a local folder of PDFs into one combined JSON.
- **FR-4** Export a human-friendly Excel summary.
- **FR-5** Target schema: BOL/PRO/PO/load/reference numbers, pickup & delivery dates, shipper &
  consignee (name + location), commodity, weight, piece count, carrier, freight terms, notes.

## 4. Non-functional requirements
- **NFR-1 Privacy first.** Real BOLs contain private shipment/customer/routing data. Source PDFs,
  API keys, and all generated output are **git-ignored** and never committed; the public repo
  ships code only.
- **NFR-2 Robust to layout variation.** Many carriers, many BOL templates — extraction must
  tolerate format differences.
- **NFR-3 Validatable.** Output schema should be checkable before write (roadmap).

## 5. Out of scope (current)
- A hosted web service / UI (CLI + folder workflow for now).

## 6. Status & acceptance criteria
- **Early-stage / active.** Schema + prompt still evolving as more layouts are tested.
- Single-file and batch extraction produce valid JSON + Excel. ✓
- Roadmap: sanitized sample fixtures, automated tests per layout, schema validation, redaction
  tools for safe demos.
