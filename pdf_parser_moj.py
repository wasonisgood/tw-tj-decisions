import json
import re
import os

INPUT_JSON = "moj_parsed_results.json"
OUTPUT_JSON = "moj_parsed_results.json"

class MOJPatcher:
    def get_line_level(self, line: str):
        line = line.strip()
        # 第一層級: 一、 (中文數字加頓號)
        m1 = re.match(r'^([一二三四五六七八九十百]+[、])\s*(.*)', line)
        if m1: return 1, m1.group(1), m1.group(2)

        # 第二層級: (一), （一） (括號中文數字)
        m2 = re.match(r'^([\(（][一二三四五六七八九十百]+[\)）])\s*(.*)', line)
        if m2: return 2, m2.group(1), m2.group(2)

        # 第三層級: 1., 1、, １., １、 (阿拉伯數字)
        m3 = re.match(r'^([\d０-９]+[.、])\s*(.*)', line)
        if m3: return 3, m3.group(1), m3.group(2)

        # 第四層級: (1), （1） (括號阿拉伯數字)
        m4 = re.match(r'^([\(（][\d０-９]+[\)）])\s*(.*)', line)
        if m4: return 4, m4.group(1), m4.group(2)

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
                # 若無標頭，視為上一層級的延伸內文
                stack[-1]["content"].append(line)
            else:
                new_node = {
                    "title": marker,
                    "level": level,
                    "content": [rest] if rest else [],
                    "children": []
                }
                # 判斷階層並回溯 stack
                while len(stack) > 1 and stack[-1]["level"] >= level:
                    stack.pop()
                
                stack[-1]["children"].append(new_node)
                stack.append(new_node)

        # 整理格式：將 content 清單合併回字串
        def clean_node(node):
            if isinstance(node["content"], list):
                node["content"] = "\n".join(node["content"])
            for child in node["children"]:
                clean_node(child)

        for item in root["children"]:
            clean_node(item)

        return root["children"]

    def patch(self):
        if not os.path.exists(INPUT_JSON):
            print(f"錯誤：找不到檔案 {INPUT_JSON}")
            return

        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"正在處理 {len(data)} 筆判決資料...")
        for item in data:
            if "sections" in item:
                # 結構化「事實」與「理由」
                item["structured_facts"] = self.structure_text(item["sections"].get("facts", ""))
                item["structured_reasons"] = self.structure_text(item["sections"].get("reasons", ""))

            # 補丁：如果結構化失敗但原本有文字，則放入一個預設節點
            if not item.get("structured_facts") and item.get("sections", {}).get("facts"):
                item["structured_facts"] = [{"title": "", "level": 0, "content": item["sections"]["facts"], "children": []}]
            if not item.get("structured_reasons") and item.get("sections", {}).get("reasons"):
                item["structured_reasons"] = [{"title": "", "level": 0, "content": item["sections"]["reasons"], "children": []}]

        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("處理完成！")

if __name__ == "__main__":
    MOJPatcher().patch()