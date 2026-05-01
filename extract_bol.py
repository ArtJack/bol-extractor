import base64
import json
import sys
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = Anthropic(timeout=120.0)

EXTRACTION_PROMPT = """Extract data from this Bill of Lading (BOL). Return ONLY valid JSON matching the schema below — no markdown fences, no explanation.

# CRITICAL FIELDS

## bol_number
The document's primary identifier. Look for: BOL#, B/L No, PRO#, BL#, Shipment ID, Tracking#. Often in the top-right header. NOT the same as PO, customer, container, or trailer number. Format: 6-15 alphanumeric characters.

## Reference numbers (extract any that appear; null if absent)
- po_number: Purchase Order, labeled PO#, P.O., Customer PO
- pro_number: Carrier tracking, labeled PRO#, Tracking#
- load_number: Internal load identifier, labeled Load#, Trip#, Load ID
- reference_number: Any other secondary number — Ref#, Order#, Customer Ref

## Dates (MM/DD/YYYY format always)
- pickup_date: When goods left shipper. Labels: Ship Date, Pickup Date, Date Shipped
- delivery_date: When goods arrived. Labels: Delivery Date, Delivered, ETA, Receipt Date
- If only ONE date with no label, treat it as pickup_date.

## Locations
- shipper_location: city + 2-letter state combined as "City, ST" (e.g. "Hollister, CA")
- consignee_location: same format

## notes
Special instructions, handwritten remarks, or anything unusual. Examples: "Protect from freezing", "Call before delivery 555-1234", "Damaged on arrival", "Receiving hours T-F 8AM-4:30PM". Keep concise — under 200 characters. Combine multiple short notes with semicolons.

# RULES
- Use null for missing fields, never empty strings
- Numbers are digits only — strip "lbs", commas, units
- For multi-shipment documents, return a JSON array
- Return ONLY the JSON, nothing else

# SCHEMA
{
    "bol_number": "string",
    "pro_number": "string or null",
    "po_number": "string or null",
    "load_number": "string or null",
    "reference_number": "string or null",
    "pickup_date": "MM/DD/YYYY or null",
    "delivery_date": "MM/DD/YYYY or null",
    "shipper_name": "string or null",
    "shipper_location": "City, ST or null",
    "consignee_name": "string or null",
    "consignee_location": "City, ST or null",
    "commodity": "short description or null",
    "total_weight_lbs": "number or null",
    "total_pieces": "number or null",
    "carrier": "trucking company or null",
    "freight_terms": "prepaid | collect | third party | null",
    "notes": "string or null"
}

Now extract from the document."""


def extract_bol_data(pdf_path):
    print(f"Reading PDF: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

    print(f"Sending to Claude (this takes 10-30 seconds)...")

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        },
                    },
                    {"type": "text", "text": EXTRACTION_PROMPT},
                ],
            }
        ],
    )

    raw_text = response.content[0].text.strip()
    print(f"Tokens: in={response.usage.input_tokens}, out={response.usage.output_tokens}")

    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, list):
            print(f"  > Multi-BOL document detected: {len(parsed)} BOLs")
            return parsed
        return parsed
    except json.JSONDecodeError as e:
        # Try to salvage truncated JSON arrays
        if raw_text.startswith("["):
            print(f"  > JSON looks truncated, attempting salvage...")
            # Find the last complete object in the array
            last_complete = raw_text.rfind("},")
            if last_complete > 0:
                salvaged = raw_text[:last_complete + 1] + "]"
                try:
                    parsed = json.loads(salvaged)
                    print(f"  > Salvaged {len(parsed)} complete BOLs")
                    return parsed
                except json.JSONDecodeError:
                    pass
        print(f"ERROR parsing JSON: {e}")
        print(f"Raw response (first 500 chars):\n{raw_text[:500]}")
        return None


def process_single_bol(pdf_path):
    print(f"\n{'='*60}")
    print(f"Processing: {pdf_path}")
    print(f"{'='*60}")

    data = extract_bol_data(pdf_path)

    if data:
        print(f"\nEXTRACTION SUCCESSFUL")
        print(f"{'-'*40}")
        # Handle both single BOL (dict) and multi-BOL (list)
        bols = data if isinstance(data, list) else [data]
        for i, bol in enumerate(bols, 1):
            if len(bols) > 1:
                print(f"\n[BOL {i}/{len(bols)}]")
            for key, value in bol.items():
                if value is not None:
                    print(f"  {key:20s}: {value}")
        return data
    else:
        print(f"\nEXTRACTION FAILED")
        return None


if __name__ == "__main__":
    print("Script starting...")

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        bols_folder = Path("bols")
        pdfs = sorted([p for p in bols_folder.glob("*.pdf")])
        if not pdfs:
            print("ERROR: No PDF files found in bols/ folder")
            sys.exit(1)
        pdf_path = str(pdfs[0])
        print(f"Auto-selected: {pdf_path}")

    result = process_single_bol(pdf_path)

    if result:
        with open("last_extraction.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nJSON saved to: last_extraction.json")

    print("\nScript finished.")
