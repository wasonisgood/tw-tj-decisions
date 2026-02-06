import os
import json
import re

def normalize_name(name):
    """移除姓名中的空白與特殊字元，方便比對"""
    if not name: return ""
    return re.sub(r'[\s　]', '', name)

def build_data_js():
    decisions_dir = "parsed_results"
    revocations_file = "all_revocations.json"
    output_file = "decision_data.js"
    
    # 1. 讀取決定書資料 (Decisions)
    decisions_data = []
    if os.path.exists(decisions_dir):
        files = [f for f in os.listdir(decisions_dir) if f.lower().endswith(".json")]
        print(f"Processing {len(files)} decision files...")

        for filename in sorted(files):
            file_path = os.path.join(decisions_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["filename"] = filename
                    data["id"] = filename.replace(".", "_")
                    decisions_data.append(data)
            except Exception as e:
                print(f"Skipping {filename}: {e}")
    
    # 排序決定書
    def sort_key(item):
        case_no = item.get("metadata", {}).get("case_no", "") or ""
        match = re.search(r"第(\d+)號", case_no)
        num = int(match.group(1)) if match else 999999
        # 司字優先 (0), 復查次之 (1)
        type_order = 0 if "促轉司字" in case_no else (1 if "復查" in case_no else 2)
        return (type_order, num)

    decisions_data.sort(key=sort_key)

    # 2. 讀取撤銷名冊資料 (Revocations)
    revocations_data = []
    if os.path.exists(revocations_file):
        try:
            with open(revocations_file, "r", encoding="utf-8") as f:
                revocations_data = json.load(f)
            print(f"Loaded {len(revocations_data)} revocation records.")
        except Exception as e:
            print(f"Error loading revocations: {e}")

    # 3. 建立連結 (Linking)
    # 目標：在 revocations_data 中加入 `decision_id`，如果它屬於第二類且找得到決定書
    # 建立索引：(姓名, 案號) -> Decision ID
    decision_map = {}
    for d in decisions_data:
        meta = d.get("metadata", {})
        # 主要 Key: 姓名 (Subject)
        subject = normalize_name(meta.get("subject", ""))
        case_no = meta.get("case_no", "")
        
        if subject:
            if subject not in decision_map:
                decision_map[subject] = []
            decision_map[subject].append({
                "id": d["id"],
                "case_no": case_no
            })

    # 嘗試配對
    link_count = 0
    for r in revocations_data:
        # 只針對第二類 (Category 2) 嘗試連結
        if r.get("category") == 2:
            r_name = normalize_name(r.get("name", ""))
            
            if r_name in decision_map:
                candidates = decision_map[r_name]
                # 簡單策略：如果只有一個候選人，直接連
                # 如果有多個，理想上要比對案號，但名冊案號格式可能與決定書不同
                # 這裡先取第一個匹配的，未來可優化
                if candidates:
                    r["linked_decision_id"] = candidates[0]["id"]
                    link_count += 1

    print(f"Linked {link_count} revocation records to decisions.")

    # 4. 輸出 JS
    final_payload = {
        "decisions": decisions_data,
        "revocations": revocations_data
    }
    
    js_content = f"window.DATA_STORE = {json.dumps(final_payload, ensure_ascii=False)};"
    
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(js_content)
        
    print(f"Successfully wrote data to {output_file}")

if __name__ == "__main__":
    build_data_js()