import sys
import types
from pathlib import Path

PARSER_DIR = Path(__file__).parent.parent / "n8n_code_blocks" / "parser"
TEST_FILES = Path(__file__).parent.parent / "docs" / "samples" / "test-files"

PDF = TEST_FILES / "sample_pdf.pdf"
PDF_WITH_IMAGE = TEST_FILES / "sample_pdf_with_image.pdf"
DOCX = TEST_FILES / "file-sample_100kB.docx"
TXT = TEST_FILES / "sample_txt.txt"


def _load_parser():
    """Import parse_document.py by stripping the n8n top-level return."""
    src = (PARSER_DIR / "parse_document.py").read_text()
    src_clean = "\n".join(
        line for line in src.splitlines()
        if line.strip() != "return process_items(_items)"
    )
    mod = types.ModuleType("parse_document")
    mod.__file__ = str(PARSER_DIR / "parse_document.py")
    exec(compile(src_clean, str(PARSER_DIR / "parse_document.py"), "exec"), mod.__dict__)
    sys.modules["parse_document"] = mod


_load_parser()
