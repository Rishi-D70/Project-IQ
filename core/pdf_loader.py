import pdfplumber

class PDFLoader:
    def load(self, file_path: str) ->str:
        full_text=[]

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start = 1):
                text = page.extract_text()
                if not text:
                    continue

                full_text.append(f"\n\n--- Page {page_num} ---\n")
                full_text.append(text)

            return "\n".join(full_text)