import os
import pdfplumber
import json
import re

# 嘗試從 extract_tables 匯入工具函數，如果失敗則自行定義
try:
    from extract_tables import normalize_header, split_values
except ImportError:
    def normalize_header(header):
        mapping = {
            "序號": "id",
            "姓名": "name",
            "裁判機關": "court",
            "原裁判機關": "court",
            "裁判法院": "court",
            "原裁判法院": "court",
            "審判機關": "court",
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
        if not text: return []
        text = re.sub(r'[／/]\s*[,，]?\s*', ';', text)
        parts = re.split(r"[、，,；;\n]+", text)
        return [p.strip() for p in parts if p.strip()]

def parse_special_pdf():
    target_file = "list/1075300110B(只有第一種).pdf"
    output_file = "all_revocations.json"
    
    if not os.path.exists(target_file):
        print(f"找不到檔案: {target_file}")
        return

    # 讀取現有的 json
    all_results = []
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                all_results = json.load(f)
            print(f"已讀取現有資料: {len(all_results)} 筆")
        except Exception as e:
            print(f"讀取 {output_file} 失敗: {e}")
            all_results = []

    new_results = []
    filename = os.path.basename(target_file)
    
    print(f"開始專門解析: {filename}")
    
    try:
        with pdfplumber.open(target_file) as pdf:
            current_cat = 1 # 已知為第一種
            header_names = []
            
            for i, page in enumerate(pdf.pages):
                # 依照使用者需求：第一頁有文字但不需要文字
                # 我們直接提取表格即可，不呼叫 page.extract_text()
                
                tables = page.extract_tables()
                if not tables:
                    continue
                
                for tbl in tables:
                    if not tbl: continue
                    
                    # 檢查這一桌是否包含標題列
                    first_row = [str(c) if c else "" for c in tbl[0]]
                    combined_row = "".join(first_row)
                    
                    if "姓名" in combined_row or "序號" in combined_row:
                        header_names = normalize_header(first_row)
                        data_rows = tbl[1:]
                    else:
                        if not header_names:
                            # 如果還沒抓到 header，且這一列看起來像 data 但沒 header，先跳過
                            continue
                        data_rows = tbl

                    for row in data_rows:
                        # 過濾全空列
                        if not any(row): continue
                        
                        entry = {
                            "source": filename,
                            "category": current_cat
                        }
                        
                        # 填充資料
                        for j, cell in enumerate(row):
                            if j < len(header_names):
                                field = header_names[j]
                                val = str(cell).strip() if cell else ""
                                
                                if field in ["crime", "sentence", "case_id", "court"]:
                                    entry[field] = split_values(val)
                                else:
                                    entry[field] = val
                        
                        # 姓名是必要的
                        if entry.get("name") and entry["name"] != "姓名":
                            new_results.append(entry)
                            
    except Exception as e:
        print(f"解析過程中發生錯誤: {e}")
        return

    # 合併並存檔
    all_results.extend(new_results)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"解析完成！新增 {len(new_results)} 筆資料，總計 {len(all_results)} 筆。")

if __name__ == "__main__":
    parse_special_pdf()
