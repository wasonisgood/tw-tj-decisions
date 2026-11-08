import json
import re
import os

INPUT_JSON = "moj_parsed_results.json"
OUTPUT_JSON = "moj_parsed_results.json"

class MOJPatcher:
    def get_line_level(self, line: str):
        line = line.strip()
        if not line: return 0, "", ""
        
        # 標題特徵匹配 (放寬長度限制至 100 字，因為法務部有些標題很長)
        # Level 1: 一、 或 一.
        m1 = re.match(r'^([一二三四五六七八九十百]+[、\.])\s*(.*)', line)
        if m1 and len(line) < 100: return 1, m1.group(1), m1.group(2)
        
        # Level 2: (一), （一）
        m2 = re.match(r'^([\(（][一二三四五六七八九十百]+[\)）])\s*(.*)', line)
        if m2 and len(line) < 100: return 2, m2.group(1), m2.group(2)
            
        # Level 3: 1., 1、, １., １、
        m3 = re.match(r'^([\d０-９]+[.、])\s*(.*)', line)
        if m3 and len(line) < 100: return 3, m3.group(1), m3.group(2)
            
        # Level 4: (1), （1）
        m4 = re.match(r'^([\(（][\d０-９]+[\)）])\s*(.*)', line)
        if m4 and len(line) < 100: return 4, m4.group(1), m4.group(2)
            
        return 0, "", line

    def structure_text(self, text: str):
        if not text: return []
        lines = text.split('\n')
        root = {"title": "ROOT", "level": 0, "content": [], "children": []}
        stack = [root]
        
        for line in lines:
            line = line.strip()
            if not line: continue

            level, marker, rest = self.get_line_level(line)

            if level == 0:
                stack[-1]["content"].append(line)
            else:
                new_node = {
                    "title": marker,
                    "level": level,
                    "content": [rest] if rest else [],
                    "children": []
                }
                while len(stack) > 1 and stack[-1]["level"] >= level:
                    stack.pop()
                stack[-1]["children"].append(new_node)
                stack.append(new_node)

        def clean_node(node):
            if isinstance(node["content"], list):
                node["content"] = "\n".join(node["content"]).strip()
            for child in node["children"]:
                clean_node(child)
        
        for item in root["children"]:
            clean_node(item)
            
        return root["children"]

    def patch(self):
        if not os.path.exists(INPUT_JSON): 
            print(f"Error: {INPUT_JSON} not found")
            return
        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        patched_count = 0
        for item in data:
            facts_text = ""
            reasons_text = ""
            
            # 支援兩種結構
            if "sections" in item and isinstance(item["sections"], dict):
                facts_text = item["sections"].get("facts", "")
                reasons_text = item["sections"].get("reasons", "")
            
            if not facts_text: facts_text = item.get("facts", "")
            if not reasons_text: reasons_text = item.get("reasons", "")
                
            s_facts = self.structure_text(facts_text)
            s_reasons = self.structure_text(reasons_text)
            
            item["structured_facts"] = s_facts
            item["structured_reasons"] = s_reasons
            
            if s_facts or s_reasons:
                patched_count += 1
                
        print(f"Successfully patched {patched_count} items.")
            
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    MOJPatcher().patch()
