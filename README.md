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
        │
        ▼
  ── EP4: Enrichment & Sensitivity ────────────────────────
        │
        ▼
  Code: diff_models.js       — compares Flash vs Pro, captures file metadata
        │                       and detected_scenario for downstream use
        ├──────────────────────────────────┐
        ▼                                  ▼
  HTTP → FastAPI /enrich            HTTP → FastAPI /sensitivity
  department, UUID, confidence      public / internal / confidential
                                    (OpenAI gpt-4o-mini verifies "confidential")
        └──────────────────────────────────┘
                           │
                           ▼
  Code: merge_results.js   — assembles final enriched record from all three nodes
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
├── api/                           # FastAPI enrichment microservice
│   ├── main.py                    # 4 endpoints: /health /categories /enrich /sensitivity
│   ├── models.py                  # Pydantic models
│   ├── scenarios.toml             # 9 domain configs (pure data)
│   ├── scenarios.py               # TOML loader with Pydantic validation
│   ├── enrichment.py              # Department routing, UUID, confidence adjustment
│   ├── sensitivity.py             # Sensitivity classification (rule-based + LLM verify)
│   ├── verifier.py                # OpenAI gpt-4o-mini verification layer
│   ├── utils.py                   # Shared helpers (word-boundary keyword matching)
│   ├── Dockerfile
│   └── tests/
│
├── n8n_code_blocks/
│   ├── parser/
│   │   └── parse_document.py      # Python Code node — paste into n8n
│   ├── gemini/
│   │   ├── detect_scenario.js     # Builds scenario classification request
│   │   ├── extract_scenario.js    # Parses detected_scenario from Gemini response
│   │   ├── build_prompt.js        # Builds domain-specific analysis request
│   │   ├── parse_response.js      # Validates and extracts gemini_flash output
│   │   └── diff_models.js         # Optional: compares Flash vs Pro output
│   └── fastapi-enrichment/
│       ├── merge_results.js       # Code node — assembles final record via $() references
│       └── http_nodes_config.md   # URL/body config for the 2 HTTP Request nodes
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
| `OPENAI_API_KEY` | OpenAI API key for sensitivity LLM verification (optional — falls back to rule-based if unset) |

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

### 5. Wire the enrichment in n8n

Add these nodes after **Final Result With Models Diff**, running Enrich and Sensitivity **in parallel**:

| Node | Type | Config |
|---|---|---|
| Final Result With Models Diff | Code | paste `diff_models.js` (updated — now also outputs file metadata and detected_scenario) |
| FastAPI - Enrich | HTTP Request | POST `http://api:8000/enrich`, body `{{ JSON.stringify({ scenario: $json.detected_scenario, data: $json.gemini_flash }) }}` |
| FastAPI - Sensitivity | HTTP Request | POST `http://api:8000/sensitivity`, body `{{ JSON.stringify({ scenario: $json.detected_scenario, data: $json.gemini_flash }) }}` |
| Merge Results | Code | paste `merge_results.js` |

Wire both HTTP nodes from **Final Result With Models Diff** (parallel branches), then wire both into **Merge Results**. The Code node uses `$()` references to pull from all three upstream nodes.

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

## FastAPI Enrichment API

A standalone Python microservice (`api/`) that enriches Gemini output with routing and sensitivity metadata. Runs as a Docker container alongside n8n.

### Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Health check |
| `/categories` | GET | List all 9 supported domain scenarios |
| `/enrich` | POST | Route document to department, assign UUID, adjust confidence |
| `/sensitivity` | POST | Classify document as public / internal / confidential |

### Request body (both POST endpoints)

```json
{
  "scenario": "business",
  "data": { "...gemini_flash fields..." }
}
```

### Sensitivity verification

The `/sensitivity` endpoint uses a two-layer approach:
1. **Rule-based** — keyword matching with word-boundary regex across scenario-specific and global sensitive keyword lists
2. **LLM verification** — when the rule-based result is `"confidential"`, OpenAI `gpt-4o-mini` independently verifies the classification. If OpenAI disagrees, the less restrictive level wins. Falls back silently to rule-based if no `OPENAI_API_KEY` is set or the call fails.

Response includes `"llm_verified": true/false` so you can track when LLM verification ran.

### Starting the API

```bash
docker compose -f n8n-setup/docker-compose.yml --env-file .env up -d api
```

The API starts automatically before n8n (enforced via `depends_on: condition: service_healthy`).
