# 行政院轉型正義決定書資料庫 (Taiwan Transitional Justice Decisions Database)

這是一個開源專案，旨在自動化爬取、解析與視覺化行政院轉型正義業務的相關決定書。透過此工具，使用者可以輕鬆瀏覽、搜尋與分析平復司法不法之刑事審判案件。

## 功能特色 (Features)

*   **自動爬蟲 (`ey_crawler.py`)**: 自動從行政院轉型正義業務網站遍歷並下載最新的決定書 PDF。
*   **智慧解析 (`pdf_parser.py`)**: 使用 `pdfplumber` 精確提取 PDF 中的文字與表格，並利用正則表達式將內容結構化（自動區分主文、事實、理由）。
*   **資料管線 (`pipeline.py`)**: 串連下載與解析流程，將非結構化的 PDF 文件轉換為易於處理的 JSON 資料格式。
*   **互動閱讀器 (`index.html`)**: 提供搜尋、分類統計、關鍵字標記（如：叛亂、刑求、死刑）的靜態網頁介面，無需架設後端伺服器。

## 專案結構 (Project Structure)

*   `ey_crawler.py`: 爬蟲模組，負責檔案下載與去重。
*   `pdf_parser.py`: 解析模組，負責將 PDF 轉換為結構化資料。
*   `pipeline.py`: **主要執行檔**，整合爬蟲與解析器，自動化處理所有文件。
*   `build_viewer_data.py`: 資料建置腳本，將 `parsed_results/` 中的 JSON 彙整為前端所需的 `decision_data.js`。
*   `index.html`: 前端視覺化介面，包含決定書閱讀與統計圖表。
*   `parsed_results/`: 存放解析後的個別 JSON 檔案 (由 pipeline 生成)。
*   `downloads_ey_tjb/`: 存放原始 PDF 檔案 (由 pipeline 下載)。
*   `all_revocations.json`: 撤銷公告名冊的原始資料。

## 快速開始 (Quick Start)

### 1. 安裝環境與套件
本專案使用 Python 3 開發。請先安裝必要的相依套件：

```bash
pip install requests beautifulsoup4 pdfplumber
```

### 2. 執行爬取與解析
執行管線腳本以自動下載並解析最新的決定書：

```bash
python pipeline.py
```
> 程式會自動在 `downloads_ey_tjb` 資料夾下載 PDF，並將解析結果存入 `parsed_results` 資料夾。

### 3. 建置前端資料
解析完成後，執行以下指令將資料彙整給網頁使用：

```bash
python build_viewer_data.py
```
> 此步驟會生成 `decision_data.js` 檔案。

### 4. 開啟閱讀器
直接使用瀏覽器開啟專案目錄下的 `index.html` 即可開始瀏覽與檢索。

---

## 技術細節
- **前端架構**: 純 HTML/CSS/JS，無須後端資料庫，資料載入自本地 `decision_data.js`。
- **解析邏輯**: 針對決定書的法律文書格式（主文、理由、證據）進行了特定的文本清洗與段落合併演算法，以優化閱讀體驗。