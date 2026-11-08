import requests
from bs4 import BeautifulSoup

URL = "https://www.moj.gov.tw/2204/2645/136573/153839/153841/?Page=1&PageSize=60&type="

def debug_request():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    
    print(f"Fetching {URL}...")
    response = session.get(URL, timeout=30)
    print(f"Apparent encoding: {response.apparent_encoding}")
    print(f"Encoding from header: {response.encoding}")
    
    # Force UTF-8 and check
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    item = soup.select_one(".list ul li a")
    if item:
        print(f"Full item HTML: {item}")
        text = item.get_text(strip=True)
        print(f"Full item text: {text}")
        num_span = item.select_one(".num")
        if num_span:
            print(f"Num span HTML: {num_span}")
            print(f"Num span text: {num_span.get_text(strip=True)}")
        
        # Current logic
        temp_text = text
        if num_span:
            temp_text = temp_text.replace(num_span.get_text(strip=True), "").strip()
        print(f"Current logic result: {temp_text}")
    else:
        print("No items found.")

if __name__ == "__main__":
    debug_request()
