import os
import re
import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://www.moj.gov.tw/2204/2645/136573/153839/153841/"
URL_TEMPLATE = "https://www.moj.gov.tw/2204/2645/136573/153839/153841/?Page={}&PageSize=60&type="
DOWNLOAD_DIR = "moj_pdfs"
OUTPUT_JSON = "moj_decisions.json"
MAX_PAGES = 8
MAX_WORKERS = 10

def parse_title(title):
    """
    Parses case number, person(s), and type from the title.
    Example: 115年度法義字第14號程○吉申請平復程○圖行政不法案件處分書
    """
    # Try to extract case number (e.g., 115年度法義字第14號)
    case_no_match = re.search(r"(\d+年度[^\d]+第\d+號)", title)
    case_no = case_no_match.group(1) if case_no_match else ""
    
    # Extract type (司法不法, 行政不法, etc.)
    type_match = re.search(r"(司法不法及行政不法|司法不法|行政不法)", title)
    case_type = type_match.group(1) if type_match else "未知"
    
    # Simple extraction of names (assuming they appear after the case number and before '申請' or '案件')
    # This is a bit tricky due to variations.
    names = []
    if case_no:
        name_part = title.replace(case_no, "").split("申請")[0].split("平復")[0].split("案件")[0].strip()
        # Look for patterns like X○X
        found_names = re.findall(r"([^\s\d]{1}○[^\s\d]{0,2})", name_part)
        if found_names:
            names = list(set(found_names))
        else:
            # Fallback if no circle notation
            pass
            
    return {
        "case_no": case_no,
        "names": names,
        "type": case_type,
        "raw_title": title
    }

def get_list_data():
    all_data = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    
    for page in range(1, MAX_PAGES + 1):
        print(f"Scraping page {page}...")
        url = URL_TEMPLATE.format(page)
        try:
            response = session.get(url, timeout=30)
            response.encoding = 'utf-8' # Explicitly set encoding
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = soup.select(".list ul li a")
            for item in items:
                title_text = item.get_text(strip=True)
                # Remove the number span if it exists
                num_span = item.select_one(".num")
                if num_span:
                    title_text = title_text.replace(num_span.get_text(strip=True), "").strip()
                
                href = item.get("href")
                full_pdf_url = urljoin(BASE_URL, href)
                
                parsed = parse_title(title_text)
                parsed["url"] = full_pdf_url
                all_data.append(parsed)
                
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            
    return all_data

def download_pdf(item):
    url = item["url"]
    # Clean filename: replace invalid chars
    filename = item["raw_title"].replace(" ", "_")
    if not filename.endswith(".pdf"):
        # Check if the URL has a filename we can use or just append .pdf
        if ".pdf" in url:
            # Extract real filename from URL if possible, but raw_title is better for identification
            filename += ".pdf"
        else:
            filename += ".pdf"
            
    # Remove characters that are illegal in Windows filenames
    filename = re.sub(r'[\/*?:"<>|]', "", filename)
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    if os.path.exists(filepath):
        # print(f"Skipping {filename} (already exists)")
        return
        
    try:
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        # print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        
    print("Starting list extraction...")
    results = get_list_data()
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Total items found: {len(results)}")
    print(f"Metadata saved to {OUTPUT_JSON}")
    
    print(f"Starting downloads with {MAX_WORKERS} workers...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(download_pdf, results)
    
    print("Done!")

if __name__ == "__main__":
    main()
