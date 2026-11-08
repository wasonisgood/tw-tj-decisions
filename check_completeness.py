import json
import os
from collections import Counter

JSON_FILE = "moj_parsed_results.json"
PDF_DIR = "moj_pdfs"

def check():
    if not os.path.exists(JSON_FILE):
        print("FileNotFound: " + JSON_FILE)
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("--- JSON Statistics ---")
    print("Total items in JSON: " + str(len(data)))

    # 1. Duplicates
    filenames = [item.get("filename") for item in data]
    case_nos = [item.get("case_no") for item in data if item.get("case_no")]

    file_counts = Counter(filenames)
    case_counts = Counter(case_nos)

    duplicates_file = {k: v for k, v in file_counts.items() if v > 1}
    duplicates_case = {k: v for k, v in case_counts.items() if v > 1}

    if duplicates_file:
        print("\n[WARN] Duplicate filenames found: " + str(len(duplicates_file)))
        for k, v in list(duplicates_file.items())[:5]:
            print(f"  - {k}: {v} times")
    else:
        print("\n[OK] No duplicate filenames.")

    if duplicates_case:
        print("\n[INFO] Duplicate case numbers found: " + str(len(duplicates_case)))
        for k, v in list(duplicates_case.items())[:5]:
            print(f"  - {k}: {v} times")
    else:
        print("[OK] No duplicate case numbers.")

    # 2. PDF check
    if not os.path.exists(PDF_DIR):
        print("\nDirNotFound: " + PDF_DIR)
        return

    pdf_files = {os.path.splitext(f)[0] for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")}
    json_filenames = set(filenames)

    missing_in_json = pdf_files - json_filenames
    extra_in_json = json_filenames - pdf_files

    print("\n--- File Comparison ---")
    print("PDF files in folder: " + str(len(pdf_files)))
    
    if not missing_in_json:
        print("[OK] All PDF files are present in JSON.")
    else:
        print("[ERROR] Missing in JSON: " + str(len(missing_in_json)))
        for f in list(missing_in_json)[:10]:
            print("  - " + f)

    if extra_in_json:
        print("[INFO] Extra in JSON (no PDF file): " + str(len(extra_in_json)))
        for f in list(extra_in_json)[:5]:
            print("  - " + f)

if __name__ == "__main__":
    check()