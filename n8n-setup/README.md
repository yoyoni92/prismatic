# n8n Setup

Self-hosted n8n with Python support, using the external runners architecture.

## How it works

n8n's default Docker image is a hardened Alpine image with no package manager — you cannot install Python packages into it directly. Instead, n8n supports an **external runners** model where code execution is offloaded to a separate container.

```
┌─────────────────────┐        WebSocket        ┌──────────────────────┐
│   n8n (port 5678)   │ ◄────── port 5679 ──────► │  runners container   │
│                     │                           │                      │
│  Workflow engine    │                           │  Python runner       │
│  UI & API           │                           │  JS runner           │
└─────────────────────┘                           │  pdfplumber          │
                                                  │  python-docx         │
                                                  │  google-genai        │
                                                  └──────────────────────┘
```

The `n8nio/runners` base image ships with Python 3.13 and `uv` pre-configured, with a venv already set up at `/opt/runners/task-runner-python/.venv/`. Python packages are installed into that venv at build time.

## Folder structure

```
n8n-setup/
├── config/
│   └── n8n-task-runners.json   # Runner process config (mounted into runners container)
├── runners/
│   ├── Dockerfile              # Builds from n8nio/runners, installs Python packages
│   └── requirements.txt        # Python dependencies
├── docker-compose.yml
├── start-n8n.sh                # Linux/macOS shortcut
├── start-n8n.bat               # Windows shortcut
└── README.md
```

### `config/n8n-task-runners.json`

This file is mounted over `/etc/n8n-task-runners.json` inside the runners container. It configures how the launcher starts the Python and JS runner processes, including which environment variables each runner is allowed to read. `GEMINI_API_KEY` is added to the Python runner's `allowed-env` so Python code nodes can access it.

### `runners/requirements.txt`

Add any Python packages you need available in n8n Python code nodes here.

## Setup

1. Copy `.env.example` (in the project root) to `.env` and fill in the values:

   ```
   GEMINI_API_KEY=your-key-here
   N8N_RUNNERS_AUTH_TOKEN=any-long-random-secret
   ```

   The auth token secures the WebSocket connection between n8n and the runners container. Generate one with:
   ```
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. Build and start:

   ```bash
   docker compose --env-file ../.env up -d n8n runners
   ```

   Or use the provided shortcuts:
   - Linux/macOS: `bash start-n8n.sh`
   - Windows: double-click `start-n8n.bat`

3. Open n8n at [http://localhost:5678](http://localhost:5678) (default credentials: `admin` / `changeme`).

## Adding Python packages

Edit `runners/requirements.txt`, then rebuild the runners image:

```bash
docker compose --env-file ../.env build runners
docker compose --env-file ../.env up -d runners
```

## Key environment variables

| Variable | Service | Purpose |
|---|---|---|
| `N8N_RUNNERS_MODE` | n8n | Must be `external` to use the runners container |
| `N8N_RUNNERS_BROKER_LISTEN_ADDRESS` | n8n | Set to `0.0.0.0` so runners can connect over Docker network |
| `N8N_RUNNERS_AUTH_TOKEN` | both | Shared secret for the WebSocket handshake |
| `N8N_RUNNERS_TASK_BROKER_URI` | runners | Points to `http://n8n:5679` |
| `GEMINI_API_KEY` | both | Passed to n8n for workflow credentials, and to runners for Python code nodes |
