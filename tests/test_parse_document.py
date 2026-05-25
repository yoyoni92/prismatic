"""Tests for n8n_code_blocks/parser/parse_document.py."""

import base64
from pathlib import Path
from unittest.mock import patch

import parse_document as pd
from conftest import DOCX, PDF, PDF_WITH_IMAGE, TXT


# ── helpers ───────────────────────────────────────────────────────────────────

def make_n8n_item(file_path: Path, binary_property: str = "data") -> dict:
    """Build a minimal n8n item dict carrying a binary file payload."""
    data = base64.b64encode(file_path.read_bytes()).decode()
    return {
        "json": {},
        "binary": {
            binary_property: {
                "data": data,
                "fileName": file_path.name,
                "mimeType": "application/octet-stream",
            }
        },
    }


# ── PDF — plain (no embedded images) ─────────────────────────────────────────

class TestParsePdf:
    def test_output_shape(self):
        result = pd._parse_pdf(str(PDF), use_vision=False, api_key="")
        assert result["format"] == "pdf"
        assert result["total_pages"] == 1
        assert "full_text" in result
        assert result["pages"][0]["page"] == 1

    def test_text_content(self):
        result = pd._parse_pdf(str(PDF), use_vision=False, api_key="")
        assert "Sample PDF" in result["full_text"]
        assert "Lorem ipsum" in result["full_text"]

    def test_full_text_matches_pages_concatenation(self):
        result = pd._parse_pdf(str(PDF), use_vision=False, api_key="")
        expected = "\n\n".join(p["text"] for p in result["pages"])
        assert result["full_text"] == expected

    def test_no_image_descriptions_without_vision(self):
        result = pd._parse_pdf(str(PDF), use_vision=False, api_key="")
        assert "image_descriptions" not in result["pages"][0]


# ── PDF — with embedded image ─────────────────────────────────────────────────

class TestParsePdfWithImage:
    def test_total_pages(self):
        result = pd._parse_pdf(str(PDF_WITH_IMAGE), use_vision=False, api_key="")
        assert result["total_pages"] == 2

    def test_no_image_descriptions_without_vision_flag(self):
        result = pd._parse_pdf(str(PDF_WITH_IMAGE), use_vision=False, api_key="")
        for page in result["pages"]:
            assert "image_descriptions" not in page

    def test_image_detected_vision_no_key(self):
        result = pd._parse_pdf(str(PDF_WITH_IMAGE), use_vision=True, api_key="")
        assert result["pages"][0]["image_descriptions"] == ["[GEMINI_API_KEY not set]"]

    def test_page_without_image_has_no_descriptions(self):
        result = pd._parse_pdf(str(PDF_WITH_IMAGE), use_vision=True, api_key="")
        assert "image_descriptions" not in result["pages"][1]

    def test_vision_calls_describe_images(self):
        with patch("parse_document._describe_images", return_value=["a test chart"]) as mock:
            result = pd._parse_pdf(str(PDF_WITH_IMAGE), use_vision=True, api_key="fake-key")
        mock.assert_called_once()
        assert result["pages"][0]["image_descriptions"] == ["a test chart"]


# ── DOCX ──────────────────────────────────────────────────────────────────────

class TestParseDocx:
    def test_output_shape(self):
        result = pd._parse_docx(str(DOCX), use_vision=False, api_key="")
        assert result["format"] == "docx"
        assert result["pages"][0]["page"] == 1

    def test_text_content(self):
        result = pd._parse_docx(str(DOCX), use_vision=False, api_key="")
        assert "Lorem ipsum" in result["full_text"]

    def test_no_image_descriptions_without_vision(self):
        result = pd._parse_docx(str(DOCX), use_vision=False, api_key="")
        assert "image_descriptions" not in result["pages"][0]

    def test_image_detected_vision_no_key(self):
        result = pd._parse_docx(str(DOCX), use_vision=True, api_key="")
        assert result["pages"][0]["image_descriptions"] == ["[GEMINI_API_KEY not set]"]

    def test_vision_calls_describe_images(self):
        with patch("parse_document._describe_images", return_value=["a diagram"]) as mock:
            result = pd._parse_docx(str(DOCX), use_vision=True, api_key="fake-key")
        mock.assert_called_once()
        assert result["pages"][0]["image_descriptions"] == ["a diagram"]


# ── Plain text ────────────────────────────────────────────────────────────────

class TestParseText:
    def test_output_shape(self):
        result = pd._parse_text(str(TXT))
        assert result["format"] == "txt"
        assert result["pages"][0]["page"] == 1

    def test_text_content(self):
        result = pd._parse_text(str(TXT))
        assert "Madrid" in result["full_text"]

    def test_full_text_equals_raw_file(self):
        result = pd._parse_text(str(TXT))
        assert result["full_text"] == TXT.read_text(encoding="utf-8")


# ── process_items — n8n Code block entry point ────────────────────────────────

class TestProcessItems:
    def test_pdf_item(self):
        items = [make_n8n_item(PDF)]
        result = pd.process_items(items)
        assert len(result) == 1
        parsed = result[0]["json"]["parsed"]
        assert parsed["format"] == "pdf"
        assert "Sample PDF" in parsed["full_text"]
        assert parsed["file_name"] == PDF.name

    def test_pdf_with_image_item(self):
        items = [make_n8n_item(PDF_WITH_IMAGE)]
        result = pd.process_items(items)
        parsed = result[0]["json"]["parsed"]
        assert parsed["total_pages"] == 2

    def test_docx_item(self):
        items = [make_n8n_item(DOCX)]
        result = pd.process_items(items)
        parsed = result[0]["json"]["parsed"]
        assert parsed["format"] == "docx"
        assert "Lorem ipsum" in parsed["full_text"]

    def test_txt_item(self):
        items = [make_n8n_item(TXT)]
        result = pd.process_items(items)
        parsed = result[0]["json"]["parsed"]
        assert parsed["format"] == "txt"
        assert "Madrid" in parsed["full_text"]

    def test_preserves_existing_json_fields(self):
        item = make_n8n_item(PDF)
        item["json"]["source"] = "google_drive"
        result = pd.process_items([item])
        assert result[0]["json"]["source"] == "google_drive"
        assert "parsed" in result[0]["json"]

    def test_missing_binary_returns_error(self):
        items = [{"json": {}, "binary": {}}]
        result = pd.process_items(items)
        assert "error" in result[0]["json"]

    def test_unsupported_extension(self):
        item = make_n8n_item(PDF)
        item["binary"]["data"]["fileName"] = "archive.zip"
        result = pd.process_items([item])
        assert "error" in result[0]["json"]["parsed"]

    def test_multiple_items(self):
        items = [make_n8n_item(PDF), make_n8n_item(DOCX), make_n8n_item(TXT)]
        result = pd.process_items(items)
        assert len(result) == 3
        formats = [r["json"]["parsed"]["format"] for r in result]
        assert formats == ["pdf", "docx", "txt"]
