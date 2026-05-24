import sys
import json
import base64
from abc import ABC, abstractmethod
from pathlib import Path

import fitz
from docx import Document


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, filepath: str) -> dict:
        pass

    def _base_result(self, file_type: str) -> dict:
        return {"text": "", "images": [], "page_count": None, "file_type": file_type}


class PdfParser(DocumentParser):
    def parse(self, filepath: str) -> dict:
        result = self._base_result("pdf")
        doc = fitz.open(filepath)
        result["page_count"] = len(doc)
        texts = []
        for page in doc:
            texts.append(page.get_text())
            for img in page.get_images(full=True):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                result["images"].append(base64.b64encode(pix.tobytes()).decode())
        result["text"] = "".join(texts)
        return result


class DocxParser(DocumentParser):
    def parse(self, filepath: str) -> dict:
        result = self._base_result("docx")
        doc = Document(filepath)
        result["text"] = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return result


class TxtParser(DocumentParser):
    def parse(self, filepath: str) -> dict:
        result = self._base_result("txt")
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            result["text"] = f.read()
        return result


class ParserRouter:
    def __init__(self):
        self._parsers = {
            ".pdf": PdfParser(),
            ".docx": DocxParser(),
            ".doc": DocxParser(),
        }
        self._default = TxtParser()

    def parse(self, filepath: str) -> dict:
        ext = Path(filepath).suffix.lower()
        parser = self._parsers.get(ext, self._default)
        return parser.parse(filepath)


def main():
    filepath = sys.argv[1]
    try:
        result = ParserRouter().parse(filepath)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
