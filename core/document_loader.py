from pathlib import Path
from core.pdf_loader import PDFLoader

class DocumentLoader:

    def load_text(self, file_path: str) -> str:
        path = Path(file_path)

        if file_path.lower().endswith(".pdf"):
            loader = PDFLoader()
            return loader.load(file_path)

        if not path.exists():
            raise FileNotFoundError("File Does Not Exist")
        if path.suffix != '.txt':
            raise ValueError("Only txt files")

        text = path.read_text(encoding="utf-8")

        if not text.strip():
            raise ValueError("Document is empty")

        return self._normalize(text)




    def _normalize(self, text: str) -> str:
        # Basic normalization (more later)
        return " ".join(text.split())
