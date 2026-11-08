import os
import pdfplumber

PDF_DIR = "moj_pdfs"

def analyze_first_pdf():
    files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    if not files:
        print("No PDF files found.")
        return

    # Pick the first file
    target_file = files[0]
    file_path = os.path.join(PDF_DIR, target_file)
    print(f"Analyzing file: {target_file}")

    try:
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {i+1} ---")
                    text_content.append(text)
        
        full_text = "".join(text_content)
        print(full_text[:3000]) # Print first 3000 chars

    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    analyze_first_pdf()
