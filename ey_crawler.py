import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re
from typing import Generator, Tuple

class EYCrawler:
    """
    行政院轉型正義決策書爬蟲
    功能：遍歷目標網站，下載 PDF，並以 Generator 形式即時回傳下載完成的檔案路徑。
    """
    
    BASE_URL = "https://www.ey.gov.tw/tjb/AAF17F8B016C031A"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def __init__(self, download_dir: str = "downloads_ey_tjb", page_size: int = 100):
        self.download_dir = download_dir
        self.page_size = page_size
        
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def _sanitize_filename(self, filename: str) -> str:
        """移除檔名中的非法字元"""
        return re.sub(r'[\\/*?:\"<>|]', "", filename).strip()

    def _download_file(self, url: str, filename: str) -> str:
        """
        下載檔案
        Returns: 
            str: 本地檔案絕對路徑
        """
        local_path = os.path.join(self.download_dir, filename)
        headers = {'User-Agent': self.USER_AGENT}
        
        # 1. 取得遠端檔案資訊
        try:
            with requests.get(url, headers=headers, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                accept_ranges = r.headers.get('accept-ranges', 'none')
        except Exception as e:
            print(f"[錯誤] 無法取得檔案資訊: {filename} - {e}")
            return None

        # 2. 檢查本地檔案 (去重/續傳檢查)
        downloaded_size = 0
        if os.path.exists(local_path):
            downloaded_size = os.path.getsize(local_path)
            
            if downloaded_size == total_size and total_size > 0:
                # 檔案已完整
                return local_path
            elif downloaded_size > total_size:
                # 異常，重新下載
                downloaded_size = 0
            # else: 需要續傳

        # 3. 處理續傳 Headers
        resume_header = headers.copy()
        mode = 'wb'
        
        if downloaded_size > 0 and accept_ranges == 'bytes':
            resume_header['Range'] = f'bytes={downloaded_size}-'
            mode = 'ab'
        else:
            downloaded_size = 0 

        # 4. 執行下載
        try:
            with requests.get(url, headers=resume_header, stream=True) as r:
                r.raise_for_status()
                
                if r.status_code == 200: # 伺服器不支援續傳，重頭來
                    mode = 'wb'
                    downloaded_size = 0
                
                with open(local_path, mode) as f:
                    # 只有真正下載時才顯示進度，避免洗版
                    if mode == 'wb' or (mode == 'ab' and downloaded_size < total_size):
                        print(f"[下載中] {filename} ...")
                        
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return local_path
            
        except Exception as e:
            print(f"[失敗] 下載中斷: {filename} - {e}")
            return None

    def fetch_new_files(self, max_pages: int = 10) -> Generator[str, None, None]:
        """
        核心生成器方法：爬取並即時 Yield 下載好的檔案路徑。
        
        Args:
            max_pages: 最大爬取頁數，防止無限迴圈
            
        Yields:
            str: 下載完成的檔案路徑 (絕對路徑)
        """
        page = 1
        has_next_page = True
        
        print(f"啟動爬蟲: {self.BASE_URL}")
        
        while has_next_page and page <= max_pages:
            target_url = f"{self.BASE_URL}?page={page}&PS={self.page_size}"
            # print(f"正在分析第 {page} 頁...")
            
            try:
                response = requests.get(target_url, headers={'User-Agent': self.USER_AGENT})
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                item_list = soup.find_all("li", class_="new_img")
                
                if not item_list:
                    has_next_page = False
                    break
                    
                for item in item_list:
                    link_tag = item.find("a", class_="words_a")
                    if not link_tag:
                        continue
                    
                    # 處理標題
                    title_div = link_tag.find("div", class_="title2")
                    if title_div:
                        for tag in title_div.find_all("i"):
                            tag.decompose()
                        raw_title = title_div.get_text(strip=True)
                    else:
                        raw_title = link_tag.get("title", "unknown_file")

                    if not raw_title.lower().endswith('.pdf'):
                        raw_title += ".pdf"
                        
                    filename = self._sanitize_filename(raw_title)
                    href = link_tag.get("href")
                    
                    if href:
                        full_url = urljoin(self.BASE_URL, href)
                        # 執行下載 (若存在則跳過)
                        file_path = self._download_file(full_url, filename)
                        
                        if file_path:
                            # 關鍵改動：下載完一個，立刻交出去
                            yield os.path.abspath(file_path)
            
                if len(item_list) < self.page_size:
                    has_next_page = False
                else:
                    page += 1
                    time.sleep(1) # 禮貌性延遲

            except Exception as e:
                print(f"[錯誤] 第 {page} 頁異常: {e}")
                break

if __name__ == "__main__":
    # 測試用
    crawler = EYCrawler()
    for path in crawler.fetch_new_files(max_pages=1):
        print(f"收到檔案: {path}")
