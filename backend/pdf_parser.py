import pypdf
import re
import os

class PDFParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_clean_text(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"PDF file not found at {self.file_path}")
        
        reader = pypdf.PdfReader(self.file_path)
        pages_text = []
        
        for idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            # Clean up excessive linebreaks and unwanted non-printable chars
            txt_clean = re.sub(r'\s+', ' ', txt).strip()
            if len(txt_clean) > 20:  # ignore blank / header-only pages
                pages_text.append({
                    "page_number": idx + 1,
                    "text": txt_clean
                })
                
        full_text = " ".join([p["text"] for p in pages_text])
        return {
            "total_pages": len(reader.pages),
            "valid_pages": len(pages_text),
            "pages": pages_text,
            "full_text": full_text
        }

if __name__ == "__main__":
    parser = PDFParser("Document_Data_Reduit.pdf")
    res = parser.extract_clean_text()
    print(f"Extracted {res['valid_pages']}/{res['total_pages']} pages, total chars: {len(res['full_text'])}")
