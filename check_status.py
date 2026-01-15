import os
import re

def check_status():
    download_dir = "downloads_ey_tjb"
    parsed_dir = "parsed_results"
    
    if not os.path.exists(download_dir) or not os.path.exists(parsed_dir):
        print("Directory missing.")
        return

    pdfs = sorted([f for f in os.listdir(download_dir) if f.lower().endswith(".pdf")])
    jsons = [f for f in os.listdir(parsed_dir) if f.lower().endswith(".json")]
    
    # 1. Check for unparsed PDFs
    unparsed_files = []
    for pdf in pdfs:
        json_name = pdf.rsplit('.', 1)[0] + ".json"
        if json_name not in jsons:
            unparsed_files.append(pdf)
            
    print(f"Total PDFs: {len(pdfs)}")
    print(f"Total JSONs: {len(jsons)}")
    print(f"Unparsed PDFs ({len(unparsed_files)}):")
    for f in unparsed_files:
        print(f"  - {f}")
        
    # 2. Check for sequence gaps in "促轉司字第X號"
    # Pattern: 促轉司字第(\d+)號
    ids = []
    for pdf in pdfs:
        match = re.search(r"促轉司字第(\d+)號", pdf)
        if match:
            ids.append(int(match.group(1)))
            
    if ids:
        ids.sort()
        missing_ids = []
        min_id = ids[0]
        max_id = ids[-1]
        
        # Check gaps between min and max
        for i in range(min_id, max_id + 1):
            if i not in ids:
                missing_ids.append(i)
                
        print(f"\nSequence range: {min_id} to {max_id}")
        if missing_ids:
            print(f"Missing numbers in sequence ({len(missing_ids)}): {missing_ids}")
        else:
            print("No gaps in sequence.")
            
        # Check if 1 is the start
        if min_id > 1:
            print(f"Note: Sequence starts at {min_id}, potentially missing 1-{min_id-1}")

    # 3. Check for "復查決定書" sequence if applicable
    # Pattern: 促轉復查字第(\d+)號
    review_ids = []
    for pdf in pdfs:
        match = re.search(r"促轉復查字第(\d+)號", pdf)
        if match:
            review_ids.append(int(match.group(1)))
            
    if review_ids:
        review_ids.sort()
        missing_reviews = []
        min_rev = review_ids[0]
        max_rev = review_ids[-1]
        
        for i in range(min_rev, max_rev + 1):
            if i not in review_ids:
                missing_reviews.append(i)
                
        print(f"\nReview Sequence range: {min_rev} to {max_rev}")
        if missing_reviews:
            print(f"Missing review numbers ({len(missing_reviews)}): {missing_reviews}")
        else:
            print("No gaps in review sequence.")

if __name__ == "__main__":
    check_status()
