# Prismatic

An n8n-based document intelligence pipeline. Uploads from Google Drive are parsed, domain-classified, and analyzed by Gemini — producing structured JSON with summary, entities, sentiment, and action items.

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
        ├─ PDF  → pdfplumber  (text per page)
        ├─ DOCX → python-docx (paragraphs)
        └─ TXT  → plain read
                │
                └─ USE_VISION=True → Gemini Vision (gemini-2.5-flash-image)
                        (describes embedded images per page)
        │
        ▼
  Enriched output: { format, file_name, full_text, pages[] }
        │
        ▼
  ── EP3: AI Analysis ──────────────────────────────────────
        │
        ▼
  Code: detect_scenario.js   — builds classification prompt
        │
        ▼
  HTTP Request → Gemini Flash (classify)
        │
        ▼
  Code: extract_scenario.js  — outputs detected_scenario + scenario_reasoning
        │
        ▼
  Code: build_prompt.js      — builds domain-specific analysis prompt + requestBody
        │
        ▼
  HTTP Request → Gemini Flash (analyze)
        │
        ▼
  Code: parse_response.js    — validates + outputs gemini_flash
        │
        ▼
  Structured output: { summary, classification, sentiment, entities, action_items, confidence_score }
```

### Detected scenarios

The pipeline auto-detects one of 9 domain scenarios and applies a matching analysis persona:

| Scenario | Domain |
|---|---|
| `business` | Corporate communications, memos, operations |
| `cybersecurity` | Incident reports, threat intelligence, audits |
| `financial` | Financial statements, investment reports |
| `hr` | Employment contracts, performance reviews |
| `product` | Product specs, market positioning |
| `academic` | Research papers, studies |
| `legal` | Contracts, regulations, compliance |
| `medical` | Clinical notes, diagnoses, treatment plans |
| `other` | Does not fit any of the above |

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
│   ├── start-n8n.sh
│   ├── start-n8n.bat
│   └── README.md
│
├── n8n_code_blocks/
│   ├── parser/
│   │   └── parse_document.py      # Python Code node — paste into n8n
│   └── gemini/
│       ├── detect_scenario.js     # Builds scenario classification request
│       ├── extract_scenario.js    # Parses detected_scenario from Gemini response
│       ├── build_prompt.js        # Builds domain-specific analysis request
│       ├── parse_response.js      # Validates and extracts gemini_flash output
│       └── diff_models.js         # Optional: compares Flash vs Pro output
│
├── docs/
│   └── plans/
│       └── EP3-gemini.md          # EP3 implementation plan
│
├── tests/                         # pytest suite for parse_document.py
│   ├── conftest.py
│   └── test_parse_document.py
│
└── .env.example                   # Environment variable template
```

## Quick start

### 1. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
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

### 3. Wire the parser in n8n

1. Add a **Set** node before the Python Code node and set:
   - Field: `_geminiApiKey` → Value: `{{ $env.GEMINI_API_KEY }}` (expression mode)
   - Enable **Include Other Input Fields**

2. Paste `n8n_code_blocks/parser/parse_document.py` into a **Python Code** node.

3. **Optional:** set `USE_VISION = True` at the top of the script to have embedded images described by Gemini Vision.

### 4. Wire the AI analysis in n8n

Add these nodes after the parser, in order:

| Node | Type | Config |
|---|---|---|
| Detect Scenario | Code | paste `detect_scenario.js` |
| Gemini Flash (classify) | HTTP Request | POST `…/gemini-2.5-flash:generateContent?key={{ $env.GEMINI_API_KEY }}`, body `={{ $json.requestBody }}` |
| Extract Scenario | Code | paste `extract_scenario.js` |
| Build Prompt | Code | paste `build_prompt.js` |
| Gemini Flash (analyze) | HTTP Request | same URL as above, body `={{ $json.requestBody }}` |
| Parse Response | Code | paste `parse_response.js` |

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
