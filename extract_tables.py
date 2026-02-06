import os
import pdfplumber
import json
import re

def normalize_header(header):
    """標準化欄位名稱，將相似的欄位統一"""
    mapping = {
        "序號": "id",
        "姓名": "name",
        "裁判機關": "court",
        "原裁判機關": "court",
        "裁判法院": "court",
        "原裁判法院": "court",
        "審判機關": "court", # 新增
        "機關": "court",
        "裁判字號": "case_id",
        "原裁判字號": "case_id",
        "裁判案由": "crime",
        "原裁判案由": "crime",
        "罪名": "crime",
        "判決": "sentence",
        "刑期": "sentence",
        "原裁判刑度": "sentence",
        "補償內容": "compensation",
        "撤銷之內容": "revocation_content",
        "備註": "note"
    }
    cleaned = []
    for h in header:
        if not h:
            cleaned.append("")
            continue
        h_clean = h.replace("\n", "").strip()
        found = False
        for key, val in mapping.items():
            if key in h_clean:
                cleaned.append(val)
                found = True
                break
        if not found:
            cleaned.append(h_clean)
    return cleaned

def split_values(text):
    """
    分割多值欄位
    處理特殊組合： '／' 後方可能帶有空格或逗號
    """
    if not text: return []
    
    # 1. 統一將各種斜線組合（及其前後空格）替換為標點符號
    # 處理 '／ ' 或 '／,' 或 '/'
    text = re.sub(r'[／/]\s*[,，]?\s*', ';', text)
    
    # 2. 使用正則分割
    parts = re.split(r"[、，,；;\n]+", text)
    
    return [p.strip() for p in parts if p.strip()]

def run_extraction():
    src_dir = "processed_list"
    output_file = "all_revocations.json"
    all_results = []

    files = sorted([f for f in os.listdir(src_dir) if f.lower().endswith('.pdf')])
    print(f"開始處理 {len(files)} 個檔案...")

    for filename in files:
        path = os.path.join(src_dir, filename)
        file_default_cat = 2 if "只有第二種" in filename else None
        
        try:
            with pdfplumber.open(path) as pdf:
                current_cat = file_default_cat
                header_names = []
                
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    
                    if not file_default_cat:
                        if "公告名冊（一）" in text:
                            current_cat = 1
                        elif "公告名冊（二）" in text or "公告名冊(二)" in text:
                            current_cat = 2
                    
                    tables = page.extract_tables()
                    for tbl in tables:
                        if not tbl: continue
                        
                        raw_header = [str(c) if c else "" for c in tbl[0]]
                        if "姓名" in "".join(raw_header) or "序號" in "".join(raw_header):
                            header_names = normalize_header(raw_header)
                            data_rows = tbl[1:]
                        else:
                            if not header_names: continue
                            data_rows = tbl

                        for row in data_rows:
                            if not any(row): continue 
                            
                            entry = {
                                "source": filename,
                                "category": current_cat or 1
                            }
                            
                            for i, cell in enumerate(row):
                                if i < len(header_names):
                                    field = header_names[i]
                                    val = str(cell).strip() if cell else ""
                                    
                                    # 現在連裁判機關 (court) 也進行分割處理
                                    if field in ["crime", "sentence", "case_id", "court"]:
                                        entry[field] = split_values(val)
                                    else:
                                        entry[field] = val
                            
                            all_results.append(entry)
                            
        except Exception as e:
            print(f"  [錯誤] {filename}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"處理完成！共提取 {len(all_results)} 筆資料。")

if __name__ == "__main__":
    run_extraction()
