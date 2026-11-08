import pdfplumber
import os

def inspect_layout():
    # 挑選一個具代表性的檔案
    target_file = "moj_pdfs/112年度法義字第10號張○義申請平復司法不法案件處分書.pdf"
    
    if not os.path.exists(target_file):
        print(f"找不到檔案: {target_file}")
        return

    print(f"正在分析排版座標: {os.path.basename(target_file)}")
    
    with pdfplumber.open(target_file) as pdf:
        # 我們通常關注「理由」段落，通常在第 2-4 頁之間
        start_page = 1 
        end_page = min(4, len(pdf.pages))
        
        for i in range(start_page, end_page):
            page = pdf.pages[i]
            print(f"\n====== Page {i+1} (Width: {page.width:.2f}) ======")
            
            # 使用 extract_text_lines() 取得每一行的物理資訊
            lines = page.extract_text_lines()
            
            for line in lines:
                text = line['text'].strip()
                x0 = line['x0'] # 左邊界位置
                
                is_potential_header = False
                if any(text.startswith(c) for c in ['一、', '二、', '三、', '四、', '五、', '六、']):
                    is_potential_header = True
                elif any(text.startswith(c) for c in ['(一)', '(二)', '(三)', '(四)', '(五)', '（一）', '（二）']):
                    is_potential_header = True
                elif any(text.startswith(c) for c in ['1.', '2.', '3.', '4.', '1、', '2、']):
                    is_potential_header = True
                
                prefix = "[HEADER?]" if is_potential_header else "[TEXT   ]"
                print(f"X={x0:6.2f} | {prefix} {text[:40]}...")

if __name__ == "__main__":
    inspect_layout()