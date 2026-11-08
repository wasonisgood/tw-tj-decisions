import os
import json
import re

def normalize_name(name):
    """移除姓名中的空白與特殊字元，方便比對"""
    if not name: return ""
    return re.sub(r'[\s　]', '', name)

def get_decision_result(main_text):
    """
    根據主文判斷結果：
    - 駁回 (rejected)
    - 不受理 (dismissed)
    - 部分駁回 (partial)
    - 撤銷/通過 (approved)
    """
    if not main_text:
        return "approved"
    
    text = main_text.replace(" ", "").replace("\n", "").replace("\r", "")
    
    # 不受理判定
    dismiss_keywords = ["不受理", "不予受理", "不予處理"]
    if any(kw in text for kw in dismiss_keywords):
        return "dismissed"

    # 強化駁回判定關鍵字
    reject_keywords = ["申請駁回", "聲請駁回", "駁回申請", "駁回聲請", "應予駁回"]
    has_reject = any(kw in text for kw in reject_keywords)
    
    # 撤銷判定
    has_revoke = any(kw in text for kw in ["撤銷", "視為撤銷", "不法", "確認", "平復"])
    
    if has_reject:
        if has_revoke:
            return "partial"
        else:
            return "rejected"
            
    return "approved"

def parse_case_info(case_no):
    if not case_no:
        return (9999, 999999)
    year_match = re.search(r"(\d+)年度", case_no)
    year = int(year_match.group(1)) if year_match else 9999
    num_match = re.search(r"第(\d+)號", case_no)
    num = int(num_match.group(1)) if num_match else 999999
    return (year, num)

def get_type_priority(item):
    """
    依據內容、案號或檔名判斷類別
    返回 (排序權重, 類別文字)
    """
    case_no = item.get("case_no", "")
    filename = item.get("filename", "")
    type_str = item.get("type", "")
    source = item.get("source", "")

    # 1. 複查案件 (優先級最高，排在最後)
    if "複查" in case_no or "複查" in filename:
        return 10, "複"

    # 2. 調查報告 (檢查檔名)
    if "調查報告" in filename or "調查報告" in case_no:
        return 3, "調"

    # 3. 司法/行政識別
    if source == "tjc" and "促轉司" in case_no:
        return 0, "司"
        
    if "司法不法" in type_str and "行政不法" in type_str:
        return 2, "兼"
    if "司法不法" in type_str:
        return 0, "司"
    if "行政不法" in type_str:
        return 1, "行"
    
    return 9, "他"

def build_data_js():
    moj_file = "moj_parsed_results.json"
    tjc_dir = "parsed_results"
    revocations_file = "all_revocations.json"
    output_file = "decision_data.js"
    
    decisions_data = []
    
    # 1a. 法務部資料
    if os.path.exists(moj_file):
        try:
            with open(moj_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            for item in raw_data:
                item["id"] = "moj_" + item.get("filename", "unknown")
                item["source"] = "moj"
                item["result_status"] = get_decision_result(item.get("main_text", ""))
                year, num = parse_case_info(item.get("case_no", ""))
                item["_sort_year"] = year
                item["_sort_num"] = num
                prio, char = get_type_priority(item)
                item["_sort_type_prio"] = prio
                item["_type_char"] = char
                decisions_data.append(item)
        except Exception as e:
            print(f"Error reading MOJ: {e}")

    # 1b. 促轉會資料
    if os.path.exists(tjc_dir):
        for filename in os.listdir(tjc_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(tjc_dir, filename), "r", encoding="utf-8") as f:
                        item = json.load(f)
                    if not item: continue
                    
                    meta = item.get("metadata", {}) or {}
                    content = item.get("content", {}) or {}
                    
                    new_item = {
                        "id": "tjc_" + filename,
                        "source": "tjc",
                        "case_no": meta.get("case_no", ""),
                        "subject": meta.get("subject", ""),
                        "date": meta.get("date", ""),
                        "type": meta.get("type", ""),
                        "main_text": content.get("main_text", ""),
                        "facts": content.get("facts", ""),
                        "reasons": content.get("reasoning", ""),
                        "structured_reasons": item.get("structured_reasoning", []),
                        "filename": filename
                    }
                    new_item["result_status"] = get_decision_result(new_item["main_text"])
                    year, num = parse_case_info(new_item["case_no"])
                    new_item["_sort_year"] = year
                    new_item["_sort_num"] = num
                    prio, char = get_type_priority(new_item)
                    new_item["_sort_type_prio"] = prio
                    new_item["_type_char"] = char
                    decisions_data.append(new_item)
                except Exception as e:
                    print(f"Error reading TJC {filename}: {e}")

    # 排序邏輯
    def final_sort_key(x):
        # 1. 駁回、不受理或複查最末尾 (is_end = 1)
        # 2. 來源 (TJC 優先)
        # 3. 類型 (司 > 行 > 兼 > 調)
        # 4. 年份
        # 5. 案號
        is_end = 1 if (x["result_status"] in ["rejected", "dismissed"] or x["_type_char"] == "複") else 0
        source_prio = 0 if x["source"] == "tjc" else 1
        return (is_end, source_prio, x["_sort_type_prio"], x["_sort_year"], x["_sort_num"])

    decisions_data.sort(key=final_sort_key)

    # 2. 撤銷名冊
    revocations_data = []
    if os.path.exists(revocations_file):
        try:
            with open(revocations_file, "r", encoding="utf-8") as f:
                revocations_data = json.load(f)
        except: pass

    # 3. 連結
    decision_map = {}
    for d in decisions_data:
        subj = normalize_name(d.get("subject", ""))
        if subj:
            if subj not in decision_map: decision_map[subj] = []
            decision_map[subj].append(d["id"])

    for r in revocations_data:
        if r.get("category") == 2:
            r_name = normalize_name(r.get("name", ""))
            if r_name in decision_map:
                r["linked_decision_id"] = decision_map[r_name][0]

    # 4. 輸出
    final_payload = {"decisions": decisions_data, "revocations": revocations_data}
    js_content = f"window.DATA_STORE = {json.dumps(final_payload, ensure_ascii=False)};"
    with open(output_file, "w", encoding="utf-8") as out:
        out.write(js_content)
    print(f"Successfully processed {len(decisions_data)} decisions.")

if __name__ == "__main__":
    build_data_js()
