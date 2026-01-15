import pdfplumber
import re
import os
from typing import Dict, List, Any, Optional

class DecisionParser:
    """
    促轉會決定書解析器
    功能：解析 PDF，提取 MetaData、主文、理由，並識別表格內容。
    """

    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """基礎清洗：去除頁碼、多餘空白"""
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        # 排除常見的頁尾雜訊
        page_number_pattern = re.compile(r'^\s*\d+\s*$|^\s*PAGE\s*\d+\s*$', re.IGNORECASE)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if page_number_pattern.match(line):
                continue
            cleaned_lines.append(line)
            
        return "\n".join(cleaned_lines)

    def merge_paragraphs(self, text: str) -> str:
        """
        將被截斷的句子合併。
        邏輯：若一行結尾不是句號，且下一行開頭沒有特定格式，通常屬於同一段。
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        merged_lines = []
        if not lines:
            return ""

        current_paragraph = lines[0]
        # 段落開頭特徵：一、 (一) 1. 主文 理由
        new_para_pattern = re.compile(r'^([一二三四五六七八九十]+、|\([一二三四五六七八九十]+\)|\d+[、\.]|\(\d+\)|主\s*文|理\s*由|據\s*上\s*論\s*結)')

        for i in range(1, len(lines)):
            line = lines[i]
            is_new_para = False
            
            if new_para_pattern.match(line):
                is_new_para = True
            elif current_paragraph.strip().endswith(('。', '：', ':')):
                is_new_para = True
            
            if is_new_para:
                merged_lines.append(current_paragraph)
                current_paragraph = line
            else:
                current_paragraph += line # 中文不加空格

        merged_lines.append(current_paragraph)
        return "\n".join(merged_lines)

    def extract_metadata(self, text: str) -> Dict[str, str]:
        """從文本中提取案號、聲請人與受裁判人"""
        metadata = {
            "case_no": None,
            "applicant": None,
            "subject": None, # 受裁判人 (當事人)
            "date": None 
        }
        
        # 1. 提取案號
        case_match = re.search(r'(促\s*轉\s*.*?\s*字\s*第\s*\d+\s*號)', text)
        if case_match:
            metadata["case_no"] = re.sub(r'\s+', '', case_match.group(1))
            
        # 2. 提取聲請人 (支援一般聲請人與復查申請人)
        # 優先找 "復查申請人" (Review Applicant)
        review_app_match = re.search(r'復查申請人[:：]\s*([^\n]+)', text)
        if review_app_match:
            raw_app = review_app_match.group(1).strip()
            cut_off_pattern = re.compile(r'(復查申請人因|有關|受|因|為|，|。)')
            split_app = cut_off_pattern.split(raw_app)
            metadata["applicant"] = split_app[0].strip()
        else:
            # 一般聲請人
            app_match = re.search(r'聲請人[:：]\s*([^\n]+)', text)
            if app_match:
                raw_app = app_match.group(1).strip()
                cut_off_pattern = re.compile(r'(有關|受|因|為|，|。)')
                split_app = cut_off_pattern.split(raw_app)
                metadata["applicant"] = split_app[0].strip()
            elif "依職權調查" in text:
                metadata["applicant"] = "依職權調查"

        # 3. 提取受裁判人 (Subject)
        main_text_match = re.search(r'(主\s*文[\s\S]*?)(?=理\s*由|事\s*實)', text)
        if main_text_match:
            main_content = re.sub(r'^主\s*文[:：]?\s*', '', main_text_match.group(1)).strip()
            subject_match = re.match(r'^([\u4e00-\u9fa5\w、]+)\s*受', main_content)
            if subject_match:
                metadata["subject"] = subject_match.group(1).strip()
        
        # 若是復查案件且沒抓到 subject，通常 applicant 就是 subject
        if not metadata["subject"] and metadata["applicant"] and "復查" in (metadata["case_no"] or ""):
             metadata["subject"] = metadata["applicant"]

        # 4. 提取日期
        # 擴大搜索範圍至最後 2000 字，並支援可能的雜訊
        footer_text = text[-2000:] if len(text) > 2000 else text
        date_match = re.search(r'中\s*華\s*民\s*國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日', footer_text)
        if date_match:
            year = date_match.group(1)
            month = date_match.group(2)
            day = date_match.group(3)
            metadata["date"] = f"中華民國{year}年{month}月{day}日"
            
        return metadata

    def extract_sections(self, text: str) -> Dict[str, str]:
        """將文本依據法律結構分類 (主文、事實、理由)，並排除結尾的署名與附表"""
        sections = {
            "main_text": "", # 主文
            "facts": "",     # 事實 (復查決定書常見)
            "reasoning": ""  # 理由
        }
        
        # 1. 抓取「主文」
        # Lookahead (?=事實|理由) 確保抓到 事實 或 理由 之前
        main_text_match = re.search(r'(主\s*文[\s\S]*?)(?=事\s*實|理\s*由)', text)
        if main_text_match:
            clean_content = re.sub(r'^主\s*文[:：]?\s*', '', main_text_match.group(1)).strip()
            sections["main_text"] = clean_content
            
        # 2. 抓取「事實」 (Optional)
        facts_match = re.search(r'(事\s*實[\s\S]*?)(?=理\s*由)', text)
        if facts_match:
            clean_content = re.sub(r'^事\s*實[:：]?\s*', '', facts_match.group(1)).strip()
            sections["facts"] = clean_content

        # 3. 抓取「理由」
        reason_match = re.search(r'(理\s*由[\s\S]*)', text)
        if reason_match:
            raw_reasoning = re.sub(r'^理\s*由[:：]?\s*', '', reason_match.group(1)).strip()
            
            cutoff_pattern = re.compile(r'(促進轉型正義委員會|中\s*華\s*民\s*國\s*\d+\s*年|附\s*表[:：])')
            
            match = cutoff_pattern.search(raw_reasoning)
            if match:
                clean_content = raw_reasoning[:match.start()].strip()
            else:
                clean_content = raw_reasoning

            sections["reasoning"] = clean_content

        return sections

    def get_line_level(self, line: str) -> int:
        """判斷單行文字的層級，回傳 1-4，若非標題則回傳 0 (Body)"""
        line = line.strip()
        # L1: 一、 二、 (中文數字 + 頓號)
        # 容許全形頓號與半形點
        if re.match(r'^[一二三四五六七八九十]+[、\.]', line):
            return 1
        
        # L2: (一) (二) - 支援全形/半形括號
        # 格式: (一) 或 （一）
        if re.match(r'^[\(（][一二三四五六七八九十]+[\)）]', line):
            return 2
            
        # L3: 1. 2. 或 1、 - 數字 + 點/頓號
        if re.match(r'^\d+[.、]', line):
            return 3
            
        # L4: (1) (2) - 支援全形/半形括號 + 數字
        if re.match(r'^[\(（]\d+[\)）]', line):
            return 4
            
        return 0 # Body text

    def build_hierarchy_tree(self, text: str) -> List[Dict[str, Any]]:
        """
        將文字解析為巢狀樹狀結構 (Tree Structure)。
        適合前端遞迴渲染 (Recursive Rendering)。
        
        Structure Node:
        {
            "text": "標題文字",
            "level": 1,
            "content": ["內文行1", "內文行2"],
            "children": [Node, Node...]
        }
        """
        if not text:
            return []

        lines = text.split('\n')
        
        # 虛擬根節點 (Level 0)，最後回傳 root['children']
        root = {"text": "ROOT", "level": 0, "content": [], "children": []}
        
        # Stack 用來追蹤當前的父節點路徑
        # stack[-1] 永遠是當前要插入內容的對象
        stack = [root] 

        for line in lines:
            line = line.strip()
            if not line:
                continue

            level = self.get_line_level(line)

            if level == 0:
                # 這是內文 (Body)，直接加入當前節點的 content
                # 為了避免將內文誤加到已經結束的子節點，需確保加入的是 stack 最上層
                current_node = stack[-1]
                current_node["content"].append(line)
            else:
                # 這是新標題 (Header)
                new_node = {
                    "text": line,
                    "level": level,
                    "content": [],
                    "children": []
                }

                # 調整 Stack 指標，找到正確的父節點
                # 邏輯：如果新節點層級 <= Stack 頂端節點層級，代表上一層結束了，要 Pop 出去
                # 例如：目前在 L2，現在來了個 L1，代表 L2 和它的父 L1 都結束了 (或是同級 L1)
                while stack[-1]["level"] >= level:
                    stack.pop()

                # 現在 stack[-1] 的 level 一定小於 new_node level
                parent = stack[-1]
                parent["children"].append(new_node)
                
                # 將新節點推入 Stack，成為下一個可能的父節點
                stack.append(new_node)

        return root["children"]

    def parse(self, pdf_path: str) -> Dict[str, Any]:
        """
        解析單一 PDF 的公開接口
        
        Returns:
            Dict: {
                "filename": str,
                "metadata": { "case_no": str, "applicant": str, "subject": str },
                "content": { "main_text": str, "reasoning": str, "full_text": str },
                "structured_reasoning": List[Dict], # 巢狀樹狀結構
                "tables": List[List[List[str]]]
            }
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")

        filename = os.path.basename(pdf_path)
        full_text_list = []
        all_tables = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # 1. 提取文字
                    text = page.extract_text()
                    if text:
                        cleaned = self.clean_text(text)
                        full_text_list.append(cleaned)
                    
                    # 2. 提取表格
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            cleaned_table = [
                                [cell.strip().replace('\n', '') if cell else "" for cell in row]
                                for row in table
                            ]
                            all_tables.append({
                                "page": i + 1,
                                "data": cleaned_table
                            })

        except Exception as e:
            return {"error": f"PDF parsing failed: {str(e)}", "filename": filename}

        raw_full_text = "\n".join(full_text_list)
        merged_text = self.merge_paragraphs(raw_full_text)
        
        meta = self.extract_metadata(merged_text)
        sections = self.extract_sections(merged_text)
        
        # 使用新的樹狀解析方法
        structured_reasoning = self.build_hierarchy_tree(sections.get("reasoning", ""))

        result = {
            "filename": filename,
            "metadata": meta,
            "content": {
                "full_text": merged_text,
                **sections
            },
            "structured_reasoning": structured_reasoning,
            "tables": all_tables
        }
        
        return result

# 測試用區塊 (當此檔案被直接執行時)
if __name__ == "__main__":
    import sys
    # 簡單測試
    parser = DecisionParser()
    # 假設 demo 目錄下有檔案
    demo_dir = "demo"
    if os.path.exists(demo_dir):
        for f in os.listdir(demo_dir):
            if f.endswith(".pdf"):
                print(f"Testing {f}...")
                res = parser.parse(os.path.join(demo_dir, f))
                print(f"Metadata: {res['metadata']}")
                print(f"Tables found: {len(res['tables'])}")
                print("-" * 20)
