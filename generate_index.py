import os
import json
import re

def build_index():
    decisions_dir = "parsed_results"
    index_file = "decisions_index.json"
    
    index_data = []
    if os.path.exists(decisions_dir):
        files = [f for f in os.listdir(decisions_dir) if f.lower().endswith(".json")]
        for filename in sorted(files):
            file_path = os.path.join(decisions_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 只保留 MetaData 和必要的 ID
                    item = {
                        "id": filename.replace(".", "_"),
                        "filename": filename,
                        "metadata": data.get("metadata", {})
                    }
                    index_data.append(item)
            except Exception as e:
                print(f"Skipping {filename}: {e}")
    
    # 排序
    def sort_key(item):
        case_no = item.get("metadata", {}).get("case_no", "") or ""
        match = re.search(r"第(\d+)號", case_no)
        num = int(match.group(1)) if match else 999999
        type_order = 0 if "促轉司字" in case_no else (1 if "復查" in case_no else 2)
        return (type_order, num)

    index_data.sort(key=sort_key)

    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {index_file} with {len(index_data)} entries.")

if __name__ == "__main__":
    build_index()
