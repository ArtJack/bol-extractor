import json
import sys
import time
from pathlib import Path
import pandas as pd
from extract_bol import extract_bol_data


def process_all_bols(bols_folder="bols", output_file="bol_summary.xlsx"):
    folder = Path(bols_folder)
    pdfs = sorted([p for p in folder.glob("*.pdf")])

    if not pdfs:
        print(f"No PDFs found in {bols_folder}/")
        return

    print(f"Found {len(pdfs)} BOLs to process\n")
    print("=" * 70)

    results = []
    failed = []

    for i, pdf_path in enumerate(pdfs, 1):
        print(f"\n[{i}/{len(pdfs)}] {pdf_path.name}")
        print("-" * 60)

        try:
            data = extract_bol_data(str(pdf_path))
            if data:
                extracted_bols = data if isinstance(data, list) else [data]
                extracted_bols = [bol for bol in extracted_bols if isinstance(bol, dict)]

                for bol in extracted_bols:
                    bol["source_file"] = pdf_path.name
                    results.append(bol)
                    print(f"  ✓ Extracted: BOL {bol.get('bol_number', '?')} | {bol.get('shipper_name', '?')} -> {bol.get('consignee_name', '?')}")

                if not extracted_bols:
                    failed.append(pdf_path.name)
                    print(f"  ✗ Failed to extract usable BOL records")
            else:
                failed.append(pdf_path.name)
                print(f"  ✗ Failed to extract")
        except Exception as e:
            failed.append(pdf_path.name)
            print(f"  ✗ Error: {e}")

        # Be nice to the API - small pause between calls
        time.sleep(1)

    print("\n" + "=" * 70)
    print(f"DONE: {len(results)} succeeded, {len(failed)} failed")

    if failed:
        print(f"\nFailed files:")
        for f in failed:
            print(f"  - {f}")

    if not results:
        print("\nNo data to save.")
        return

    # Save raw JSON backup
    with open("all_extractions.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nRaw JSON saved: all_extractions.json")

    # Build the Excel file
    df = pd.DataFrame(results)

    # Reorder columns for boss-readability
    column_order = [
        "source_file",
        "pickup_date",
        "delivery_date",
        "bol_number",
        "pro_number",
        "po_number",
        "load_number",
        "reference_number",
        "shipper_name",
        "shipper_location",
        "consignee_name",
        "consignee_location",
        "carrier",
        "commodity",
        "total_weight_lbs",
        "total_pieces",
        "freight_terms",
        "notes",
    ]
    # Only include columns that actually exist
    cols = [c for c in column_order if c in df.columns]
    df = df[cols]

    df.to_excel(output_file, index=False, sheet_name="BOLs")
    print(f"Excel saved: {output_file}")
    print(f"\nPreview:")
    print(df.head().to_string())


if __name__ == "__main__":
    process_all_bols()
