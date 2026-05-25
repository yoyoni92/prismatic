# Prismatic

An n8n-based document processing pipeline that extracts text (and optionally image descriptions via Gemini Vision) from uploaded files — PDF, DOCX, TXT, and Markdown.

## How it works

```
Google Drive (new file trigger)
        │
        ▼
  Set node — injects _geminiApiKey from $env.GEMINI_API_KEY
        │
        ▼
  Google Drive Download
        │
        ▼
  Python Code node: parse_document.py
        │
        ├─ PDF  → pdfplumber  (text per page)
        ├─ DOCX → python-docx (paragraphs)
        └─ TXT  → plain read
                │
                └─ USE_VISION=True → Gemini Vision (gemini-2.5-flash-image)
                        (describes embedded images per page)
        │
        ▼
  Enriched output: { format, file_name, full_text, pages[] }
```

The Python code runs inside a dedicated **runners container** (not the main n8n container), which is how n8n supports Python on its hardened Alpine base image. See [`n8n-setup/README.md`](n8n-setup/README.md) for the full architecture.

## Project structure

```
prismatic/
├── n8n-setup/              # Docker setup for n8n + Python runners
│   ├── config/
│   │   └── n8n-task-runners.json
│   ├── runners/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── docker-compose.yml
│   ├── start-n8n.bat
│   └── README.md
│
├── n8n_code_blocks/
│   └── parser/
│       ├── parse_document.py   # Python Code node — paste into n8n
│       └── extract_binary.js   # JS helper for filesystem-v2 binary mode
│
├── docs/
│   └── samples/
│       └── test-files/         # Sample PDF, DOCX, TXT for testing
│
├── tests/                      # pytest suite for parse_document.py
│   ├── conftest.py
│   └── test_parse_document.py
│
└── .env.example                # Environment variable template
```

## Quick start

### 1. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (required for Vision mode) |
| `N8N_RUNNERS_AUTH_TOKEN` | Random secret shared between n8n and the runners container |
| `N8N_BASIC_AUTH_PASSWORD` | n8n UI login password |

Generate a secure token:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Start n8n

```bash
docker compose -f n8n-setup/docker-compose.yml --env-file .env up -d n8n runners
```

On Linux/macOS: `bash n8n-setup/start-n8n.sh`
On Windows: double-click `n8n-setup/start-n8n.bat`

n8n will be available at [http://localhost:5678](http://localhost:5678).

### 3. Use the parser in n8n

1. Add a **Set** node before the Python Code node and set:
   - Field: `_geminiApiKey` → Value: `{{ $env.GEMINI_API_KEY }}` (expression mode)
   - Enable **Include Other Input Fields**

2. Open `n8n_code_blocks/parser/parse_document.py`, paste its contents into an n8n **Python Code** node. The last line is already active:

```python
return process_items(_items)
```

3. **Optional:** set `USE_VISION = True` at the top of the script to have embedded images described by Gemini Vision.

> **Note:** n8n uses `default` binary data mode (`N8N_DEFAULT_BINARY_DATA_MODE=default`), so binary files are passed as base64 directly to the Python node — no extra extraction step needed.

## Running tests

```bash
poetry run pytest
```

Tests cover: PDF parsing, DOCX parsing, plain text, Vision fallback behaviour, `process_items` edge cases (missing binary, unsupported extension, multiple items, field preservation).

## Python dependencies

| Package | Purpose |
|---|---|
| `pdfplumber` | PDF text extraction |
| `python-docx` | DOCX text and image extraction |
| `google-genai` | Gemini Vision for image descriptions |

Dependencies are declared in both `pyproject.toml` (for local dev/tests) and `n8n-setup/runners/requirements.txt` (for the Docker runners container).
