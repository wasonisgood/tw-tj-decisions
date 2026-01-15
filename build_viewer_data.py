import os
import json

def build_data_js():
    source_dir = "parsed_results"
    output_file = "decision_data.js"
    
    if not os.path.exists(source_dir):
        print(f"Error: {source_dir} not found.")
        return

    all_data = []
    
    files = [f for f in os.listdir(source_dir) if f.lower().endswith(".json")]
    print(f"Processing {len(files)} files...")

    for filename in sorted(files):
        file_path = os.path.join(source_dir, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure filename is in the data object for the list view
                data["filename"] = filename
                # Add a simple ID for easier DOM manipulation
                data["id"] = filename.replace(".", "_")
                all_data.append(data)
        except Exception as e:
            print(f"Skipping {filename}: {e}")

    # Sort by case number if possible, otherwise filename
    # Simple heuristic to extract number from "促轉司字第X號"
    def sort_key(item):
        import re
        case_no = item.get("metadata", {}).get("case_no", "") or ""
        match = re.search(r"第(\d+)號", case_no)
        if match:
            return int(match.group(1))
        return 999999

    all_data.sort(key=sort_key)

    # Write to a JS file that assigns a global variable
    js_content = f"window.DECISIONS_DATA = {json.dumps(all_data, ensure_ascii=False)};"
    
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(js_content)
        
    print(f"Successfully wrote {len(all_data)} records to {output_file}")

if __name__ == "__main__":
    build_data_js()
