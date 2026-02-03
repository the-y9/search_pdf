import os
from PyPDF2 import PdfReader

def find_pdfs_containing_text(folder_path: str, search_str: str):
    matching_pdfs = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)

            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text and search_str.lower in text:
                        matching_pdfs.append(pdf_path)
                        break  # stop reading this PDF once found
            except Exception as e:
                print(f"Could not read {pdf_path}: {e}")

    return matching_pdfs

if __name__ == '__main__':
    folder = r"data"
    query = "GREAT"
    results = find_pdfs_containing_text(folder, query)
    for pdf in results:
        print(pdf)
