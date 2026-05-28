"""
Document parser — n8n Python Code block.

In n8n's Code node (Python mode), paste this file and uncomment the
entry-point line at the very bottom:

    return process_items(items)

Input  : one or more n8n items, each carrying a binary property with the
         document bytes (PDF / DOCX / TXT / MD).
Output : same items enriched with a 'parsed' key containing:
           format       – "pdf" | "docx" | "txt"
           file_name    – original file name
           full_text    – all extracted text joined
           pages        – list of {page, text[, image_descriptions]}

Configuration (edit here or inject via n8n Set node upstream):
    BINARY_PROPERTY  name of the binary property on each item (default "data")
    USE_VISION       pass embedded images to Gemini Vision (default False)
    GEMINI_API_KEY   read from environment; override here if needed

Dependencies — must be installed in the Python environment n8n uses:
    pdfplumber           PDF parsing (pure Python)
    python-docx          DOCX parsing
    google-genai         Gemini Vision (only when USE_VISION = True)
"""

import base64
import os
import tempfile
from pathlib import Path

# ── configuration ─────────────────────────────────────────────────────────────

BINARY_PROPERTY = "data"
USE_VISION = False
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ── Gemini Vision ──────────────────────────────────────────────────────────────

def _describe_images(image_bytes_list, api_key):
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return ["[google-genai not installed; run: poetry add google-genai]"] * len(image_bytes_list)

    client = genai.Client(api_key=api_key)

    descriptions = []
    for img_bytes in image_bytes_list:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                "Describe the content of this image concisely.",
            ],
        )
        descriptions.append(response.text.strip())
    return descriptions


def _vision_result(image_bytes_list, api_key):
    if not image_bytes_list:
        return None
    if not api_key:
        return ["[GEMINI_API_KEY not set]"] * len(image_bytes_list)
    return _describe_images(image_bytes_list, api_key)


# ── parsers ───────────────────────────────────────────────────────────────────

def _parse_pdf(path, use_vision, api_key):
    import pdfplumber
    from pdfminer.layout import LTFigure, LTImage

    with pdfplumber.open(path) as pdf:
        pages = []
        text_parts = []

        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            page_data = {"page": i + 1, "text": text}

            if use_vision:
                img_bytes_list = []
                for item in page.layout:
                    if isinstance(item, LTFigure):
                        for sub in item:
                            if isinstance(sub, LTImage):
                                try:
                                    img_bytes_list.append(sub.stream.get_rawdata())
                                except Exception:
                                    pass
                descriptions = _vision_result(img_bytes_list, api_key)
                if descriptions is not None:
                    page_data["image_descriptions"] = descriptions

            pages.append(page_data)
            text_parts.append(text)

        return {
            "format": "pdf",
            "total_pages": len(pdf.pages),
            "full_text": "\n\n".join(text_parts),
            "pages": pages,
        }


def _parse_docx(path, use_vision, api_key):
    try:
        from docx import Document
    except ImportError:
        return {"error": "python-docx not installed; run: poetry add python-docx"}

    doc = Document(path)
    full_text = "\n".join(p.text for p in doc.paragraphs)

    result = {
        "format": "docx",
        "full_text": full_text,
        "pages": [{"page": 1, "text": full_text}],
    }

    if use_vision:
        img_bytes_list = []
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                try:
                    img_bytes_list.append(rel.target_part.blob)
                except Exception:
                    pass
        descriptions = _vision_result(img_bytes_list, api_key)
        if descriptions is not None:
            result["pages"][0]["image_descriptions"] = descriptions

    return result


def _parse_text(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return {
        "format": "txt",
        "full_text": text,
        "pages": [{"page": 1, "text": text}],
    }


# ── helpers ───────────────────────────────────────────────────────────────────

def _to_bytes(data):
    """Accept raw bytes, standard base64, or URL-safe base64 from n8n."""
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    s = data.strip()
    try:
        return base64.b64decode(s)
    except Exception:
        return base64.urlsafe_b64decode(s + "==")


# ── n8n item processor ────────────────────────────────────────────────────────

def process_items(items, binary_property=BINARY_PROPERTY, use_vision=USE_VISION, api_key=GEMINI_API_KEY):
    output = []

    for item in items:
        json_data = item.get("json", {})

        effective_api_key = (
            json_data.get("_geminiApiKey", "")
            or api_key
            or os.environ.get("GEMINI_API_KEY", "")
        )

        # filesystem-v2 mode: a JS Code node upstream extracted bytes into JSON
        raw = json_data.get("_fileBase64", "")
        file_name = json_data.get("_fileName", "document")

        # default (in-memory) mode: bytes are base64 in the binary property
        if not raw:
            binary = item.get("binary", {}).get(binary_property, {})
            raw = binary.get("data", "")
            file_name = binary.get("fileName", file_name)

        if not raw:
            output.append({"json": {**json_data, "error": "no binary data found"}})
            continue

        file_bytes = _to_bytes(raw)
        ext = Path(file_name).suffix.lower()

        # if no extension, derive from fileExtension field then mimeType
        if not ext:
            file_ext = json_data.get("fileExtension", "")
            mime = json_data.get("mimeType", "")
            if file_ext:
                ext = f".{file_ext.lower()}"
            elif "pdf" in mime:
                ext = ".pdf"
            elif "wordprocessing" in mime or "docx" in mime:
                ext = ".docx"
            elif "text" in mime:
                ext = ".txt"

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            if ext == ".pdf":
                parsed = _parse_pdf(tmp_path, use_vision, effective_api_key)
            elif ext == ".docx":
                parsed = _parse_docx(tmp_path, use_vision, effective_api_key)
            elif ext in (".txt", ".md"):
                parsed = _parse_text(tmp_path)
            else:
                parsed = {"error": f"unsupported file type: {ext}"}

            parsed["file_name"] = file_name

        except Exception as e:
            parsed = {"error": str(e), "file_name": file_name}
        finally:
            if tmp_path:
                os.unlink(tmp_path)

        output.append({"json": {**item.get("json", {}), "parsed": parsed}})

    return output


# ── n8n Code node entry point ─────────────────────────────────────────────────
# Uncomment the line below when pasting into n8n's Python Code node:
return process_items(_items)
