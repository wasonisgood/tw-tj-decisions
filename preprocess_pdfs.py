import os
from pypdf import PdfReader, PdfWriter

def process_pdfs():
    source_dir = "list"
    output_dir = "processed_list"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    files = sorted([f for f in os.listdir(source_dir) if f.lower().endswith('.pdf')])
    
    print(f"找到 {len(files)} 個 PDF 檔案於 '{source_dir}'。")
    print(f"輸出目錄: '{output_dir}'")
    print("-" * 30)

    for filename in files:
        src_path = os.path.join(source_dir, filename)
        dst_path = os.path.join(output_dir, filename)
        
        # 邏輯 0: 排除「都不要處理」
        if "都不要處理" in filename:
            print(f"[跳過] {filename} (標註為不處理)")
            continue

        try:
            reader = PdfReader(src_path)
            writer = PdfWriter()
            
            # 一律移除第一頁 (從 index 1 開始)
            if len(reader.pages) <= 1:
                print(f"[警告] {filename} 只有一頁，移除首頁後將無內容，跳過處理。")
                continue
                
            print(f"[處理] {filename}")
            do_rotate = "不需" not in filename
            
            if do_rotate:
                print(f"  -> 執行: 移除首頁 + 旋轉頁面")
            else:
                print(f"  -> 執行: 僅移除首頁")

            for i in range(1, len(reader.pages)):
                page = reader.pages[i]
                if do_rotate:
                    # 3次逆時針 = 270度逆時針 = 90度順時針
                    page.rotate(90)
                writer.add_page(page)
            
            with open(dst_path, "wb") as f_out:
                writer.write(f_out)
                
        except Exception as e:
            print(f"  -> [錯誤] 處理 {filename} 時發生異常: {e}")

    print("-" * 30)
    print("處理完成。")

if __name__ == "__main__":
    process_pdfs()