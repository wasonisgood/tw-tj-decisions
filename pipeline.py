import json
import os
from ey_crawler import EYCrawler
from pdf_parser import DecisionParser

def save_result(result, output_dir="results"):
    """
    將解析結果儲存為 JSON 檔案，模擬資料庫寫入
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = result['filename'].replace(".pdf", ".json")
    path = os.path.join(output_dir, filename)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  -> 解析結果已儲存: {path}")

def main():
    # 1. 初始化模組
    # 下載目錄
    download_dir = os.path.join(os.getcwd(), "downloads_ey_tjb")
    # 結果輸出目錄
    result_dir = os.path.join(os.getcwd(), "parsed_results")
    
    crawler = EYCrawler(download_dir=download_dir)
    parser = DecisionParser()

    print("=== 啟動自動化管線 (Pipeline) ===")
    print(f"下載目錄: {download_dir}")
    print(f"結果目錄: {result_dir}")
    print("--------------------------------")

    # 2. 執行管線 (Pipeline)
    # fetch_new_files 是 Generator，會一個接一個吐出檔案路徑
    # 這樣就達成「下載一個 -> 解析一個」的不閉塞流程
    try:
        count = 0
        # 設定 max_pages=1 僅供演示，實際使用可加大或移除參數
        for pdf_path in crawler.fetch_new_files(max_pages=5):
            count += 1
            print(f"\n[{count}] 收到檔案，開始處理: {os.path.basename(pdf_path)}")
            
            # 3. 呼叫解析器介面
            # 這裡回傳的是乾淨的 Dictionary 結構
            parsed_data = parser.parse(pdf_path)
            
            if "error" in parsed_data:
                print(f"  [X] 解析失敗: {parsed_data['error']}")
                continue
            
            # 4. 顯示或儲存結果
            meta = parsed_data['metadata']
            tables = parsed_data['tables']
            
            print(f"  -> 案號: {meta.get('case_no', 'N/A')}")
            print(f"  -> 聲請人: {meta.get('applicant', 'N/A')}")
            print(f"  -> 發現表格數: {len(tables)}")
            
            # 模擬資料庫寫入操作
            save_result(parsed_data, output_dir=result_dir)
            
    except KeyboardInterrupt:
        print("\n使用者中斷執行。")
    
    print("\n=== 管線執行完畢 ===")

if __name__ == "__main__":
    main()
