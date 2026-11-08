import json

try:
    with open("moj_decisions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        print(json.dumps(data[0], ensure_ascii=False, indent=2))
except Exception as e:
    print(e)
