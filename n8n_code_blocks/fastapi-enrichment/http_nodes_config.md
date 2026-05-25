# FastAPI HTTP Request Nodes — n8n Configuration

Both nodes sit after **Final Result With Models Diff** in the workflow.

> **Required on both HTTP nodes:** In each node's settings, enable
> **"Include Input Fields in Output"**. This passes all upstream fields
> (drive_file_id, detected_scenario, gemini_flash, etc.) through alongside
> the API response, so the Merge Results node can read everything from
> `$input` without any cross-node `$()` references.

---

## Node: FastAPI — Enrich

| Field               | Value |
|---------------------|-------|
| Method              | POST |
| URL                 | `http://api:8000/enrich` |
| Body Content Type   | JSON |
| Body                | `{{ JSON.stringify({ scenario: $json.detected_scenario, data: $json.gemini_flash }) }}` |

---

## Node: FastAPI — Sensitivity

| Field               | Value |
|---------------------|-------|
| Method              | POST |
| URL                 | `http://api:8000/sensitivity` |
| Body Content Type   | JSON |
| Body                | `{{ JSON.stringify({ scenario: $json.detected_scenario, data: $json.gemini_flash }) }}` |

---

## Wiring order

```
Final Result With Models Diff → FastAPI — Enrich → FastAPI — Sensitivity → Merge Results
```

`Merge Results` is a **Code** node — paste the contents of `merge_results.js`.
