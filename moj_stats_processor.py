import os
import re
import json

# Configuration
PDF_DIR = "moj_pdfs"
MAPPING_JSON = "moj_decisions.json"
OUTPUT_STATS_JSON = "moj_stats.json"

def parse_filename(filename):
    """
    Parses case number, names, and type from a filename.
    Handles various formats seen in the directory.
    """
    # Clean up extension
    clean_name = filename.replace(".pdf", "")
    
    # 1. Extract Case Number (e.g., 112年度法義字第15號)
    case_no_match = re.search(r"(\d+年度[^\d]+第\d+號)", clean_name)
    case_no = case_no_match.group(1) if case_no_match else "未知編號"
    
    # 2. Extract Type
    case_type = "未知"
    if "司法不法及行政不法" in clean_name:
        case_type = "司法不法及行政不法"
    elif "司法不法" in clean_name:
        case_type = "司法不法"
    elif "行政不法" in clean_name:
        case_type = "行政不法"
        
    # 3. Extract Names
    # This is heuristic: usually between the case number and '申請' or '平復' or '案件'
    # Or sometimes it's just 'Name_Type'
    names = []
    
    # Remove case number to focus on the rest
    name_source = clean_name
    if case_no != "未知編號":
        name_source = name_source.replace(case_no, "")
        
    # Look for the circle pattern X○X
    found_circles = re.findall(r"([^\s\d]{1}○[^\s\d]{0,2})", name_source)
    if found_circles:
        names = list(set(found_circles))
    
    # If no circle pattern, try to find names before '申請'
    if not names:
        # Match Chinese characters that might be names (2-4 characters)
        # This is very rough and might need adjustment
        name_part = name_source.split("申請")[0].split("平復")[0].strip()
        # Heuristic: if it's short, it might be the name
        if 2 <= len(name_part) <= 10:
             # Try to split by common delimiters if multiple names
             potential_names = re.split(r"、|_", name_part)
             names = [n.strip() for n in potential_names if n.strip()]

    return {
        "filename": filename,
        "case_no": case_no,
        "names": names,
        "type": case_type
    }

def main():
    if not os.path.exists(PDF_DIR):
        print(f"Directory {PDF_DIR} not found.")
        return

    # Load original mapping if it exists to preserve URLs
    url_mapping = {}
    if os.path.exists(MAPPING_JSON):
        try:
            with open(MAPPING_JSON, "r", encoding="utf-8") as f:
                mapping_data = json.load(f)
                # Map by case number or title
                for item in mapping_data:
                    if item.get("case_no"):
                        url_mapping[item["case_no"]] = item.get("url")
                    # Also map by title in case case_no is missing
                    if item.get("raw_title"):
                        url_mapping[item["raw_title"]] = item.get("url")
        except Exception as e:
            print(f"Warning: Could not load {MAPPING_JSON} correctly: {e}")

    stats = []
    files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    
    print(f"Processing {len(files)} files in {PDF_DIR}...")
    
    type_counts = {"司法不法": 0, "行政不法": 0, "司法不法及行政不法": 0, "未知": 0}
    
    for f in files:
        parsed = parse_filename(f)
        
        # Try to retrieve URL from mapping
        # First try case number
        parsed["url"] = url_mapping.get(parsed["case_no"])
        
        # If not found, try fuzzy match with filename in url_mapping keys
        if not parsed["url"]:
            for key in url_mapping:
                if key in f or f.replace(".pdf", "") in key:
                    parsed["url"] = url_mapping[key]
                    break
        
        stats.append(parsed)
        type_counts[parsed["type"]] = type_counts.get(parsed["type"], 0) + 1

    # Save results
    with open(OUTPUT_STATS_JSON, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
        
    print("
--- Statistics ---")
    print(f"Total Files: {len(stats)}")
    for t, count in type_counts.items():
        print(f"{t}: {count}")
    print(f"
Detailed stats saved to {OUTPUT_STATS_JSON}")

if __name__ == "__main__":
    main()
