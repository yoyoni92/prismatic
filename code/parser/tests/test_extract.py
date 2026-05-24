import json, subprocess, os

SAMPLES = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "docs", "samples", "test-files"
)

def test_pdf_extracts_text():
    result = subprocess.run(
        ["python3", "extract.py", os.path.join(SAMPLES, "sample_pdf.pdf")],
        capture_output=True, text=True,
        cwd=os.path.join(os.path.dirname(__file__), "..")
    )
    data = json.loads(result.stdout)
    assert "text" in data
    assert len(data["text"]) > 10
    assert "images" in data
    assert isinstance(data["images"], list)

def test_pdf_with_image_extracts_images():
    result = subprocess.run(
        ["python3", "extract.py", os.path.join(SAMPLES, "sample_pdf_with_image.pdf")],
        capture_output=True, text=True,
        cwd=os.path.join(os.path.dirname(__file__), "..")
    )
    data = json.loads(result.stdout)
    assert data["file_type"] == "pdf"
    assert isinstance(data["images"], list)

def test_docx_extracts_text():
    result = subprocess.run(
        ["python3", "extract.py", os.path.join(SAMPLES, "file-sample_100kB.docx")],
        capture_output=True, text=True,
        cwd=os.path.join(os.path.dirname(__file__), "..")
    )
    data = json.loads(result.stdout)
    assert data["file_type"] == "docx"
    assert len(data["text"]) > 10

def test_txt_extracts_text():
    result = subprocess.run(
        ["python3", "extract.py", os.path.join(SAMPLES, "sample_txt.txt")],
        capture_output=True, text=True,
        cwd=os.path.join(os.path.dirname(__file__), "..")
    )
    data = json.loads(result.stdout)
    assert data["file_type"] == "txt"
    assert len(data["text"]) > 0
