import os
import json
from pdf_parser import DecisionParser

def print_tree(nodes, f, indent_level=0):
    """遞迴列印樹狀結構"""
    indent = "    " * indent_level
    for node in nodes:
        # 標題
        level_tag = f"[L{node['level']}]"
        short_title = node['text'][:60] + "..." if len(node['text']) > 60 else node['text']
        f.write(f"{indent}{level_tag} {short_title}\n")
        
        # 內文 (Body)
        for line in node['content']:
            short_line = line[:60] + "..." if len(line) > 60 else line
            f.write(f"{indent}    [Body] {short_line}\n")
            
        # 遞迴子節點
        if node['children']:
            print_tree(node['children'], f, indent_level + 1)

def test_demo_files():
    demo_dir = "demo"
    if not os.path.exists(demo_dir):
        print(f"錯誤: 找不到 {demo_dir} 資料夾")
        return

    parser = DecisionParser()
    
    with open("test_output.txt", "w", encoding="utf-8") as f:
        files = [f for f in os.listdir(demo_dir) if f.lower().endswith('.pdf')]
        f.write(f"找到 {len(files)} 個 PDF 檔案，開始測試...\n\n")

        for filename in files:
            filepath = os.path.join(demo_dir, filename)
            f.write("="*60 + "\n")
            f.write(f"檔案: {filename}\n")
            
            try:
                result = parser.parse(filepath)
                
                if "error" in result:
                    f.write(f"[失敗] {result['error']}\n")
                    continue

                meta = result['metadata']
                content = result['content']
                tables = result['tables']

                f.write(f"1. [Meta] 案號: {meta.get('case_no')}\n")
                f.write(f"2. [Meta] 聲請人: {meta.get('applicant')}\n")
                f.write(f"3. [Meta] 受裁判人: {meta.get('subject')}\n")
                
                main_text = content.get('main_text', '')
                f.write(f"4. [主文] (前 100 字): {main_text[:100]}...\n" if main_text else "4. [主文] 未抓取到\n")
                
                reasoning = content.get('reasoning', '')
                # f.write(f"5. [理由] (前 100 字): {reasoning[:100]}...\n" if reasoning else "5. [理由] 未抓取到\n")
                
                # 新增結構化展示區塊 (Tree View)
                struct_reason = result.get('structured_reasoning', [])
                if struct_reason:
                    f.write("\n   --- [理由結構化樹狀預覽] ---\n")
                    print_tree(struct_reason, f)
                else:
                    f.write("\n   --- [理由結構化為空] ---\n")

                
                f.write(f"\n6. [表格] 數量: {len(tables)}\n")
                if tables:
                    f.write(f"   -> 表格範例 (第一列): {tables[0]['data'][0] if tables[0]['data'] else '空表格'}\n")

            except Exception as e:
                f.write(f"[異常] {e}\n")
                
            f.write("\n")

    print("測試完成，結果已寫入 test_output.txt")

if __name__ == "__main__":
    test_demo_files()