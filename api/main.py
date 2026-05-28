from __future__ import annotations

import json
import os
import time

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.enrichment import enrich_document
from api.models import (
    CategoriesResponse,
    EnrichResponse,
    GeminiResult,
    HealthResponse,
    ProcessRequest,
    ResultsResponse,
    SheetRow,
    SensitivityResponse,
)
from api.scenarios import CATEGORIES
from api.sensitivity import classify_sensitivity

def _parse_source_zip(v: str) -> str:
    try:
        obj = json.loads(v)
        return obj.get("name", v)
    except (ValueError, TypeError, AttributeError):
        return v


def _try_float(v: str) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


_SHEET_CACHE: ResultsResponse | None = None
_SHEET_CACHE_TS: float = 0.0
_SHEET_CACHE_TTL = 60.0
_SHEET_RANGE = "Prismatic_Results!A2:P"

app = FastAPI(title="Prismatic Enrichment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/categories", response_model=CategoriesResponse)
def categories() -> CategoriesResponse:
    return CategoriesResponse(categories=CATEGORIES)


@app.get("/results", response_model=ResultsResponse)
async def results() -> ResultsResponse:
    global _SHEET_CACHE, _SHEET_CACHE_TS
    if _SHEET_CACHE and (time.monotonic() - _SHEET_CACHE_TS) < _SHEET_CACHE_TTL:
        return _SHEET_CACHE

    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "")
    api_key  = os.environ.get("GOOGLE_SHEETS_API_KEY", "")
    if not sheet_id or not api_key:
        raise HTTPException(status_code=503, detail="Google Sheets credentials not configured")

    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}"
        f"/values/{_SHEET_RANGE}?key={api_key}"
    )
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Sheets API error: {resp.text[:200]}")

    raw_rows = resp.json().get("values", [])
    rows = [
        SheetRow(
            document_id=r[0]  if len(r) > 0  else "",
            drive_file_id=r[1] if len(r) > 1  else "",
            model=r[2]         if len(r) > 2  else "",
            filename=r[3]       if len(r) > 3  else "",
            file_type=r[4]      if len(r) > 4  else "",
            source_zip=_parse_source_zip(r[5]) if len(r) > 5 and r[5] else "",
            processed_at=r[6]   if len(r) > 6  else "",
            classification=r[7] if len(r) > 7  else "",
            department=r[8]     if len(r) > 8  else "",
            sentiment=r[9]      if len(r) > 9  else "",
            confidence_score=_try_float(r[10]) if len(r) > 10 else 0.0,
            sensitivity=r[11]   if len(r) > 11 else "",
            routing_tag=r[12]   if len(r) > 12 else "",
            summary=r[13]       if len(r) > 13 else "",
            action_items=r[14]  if len(r) > 14 else "",
        )
        for r in raw_rows
    ]
    _SHEET_CACHE = ResultsResponse(rows=rows)
    _SHEET_CACHE_TS = time.monotonic()
    return _SHEET_CACHE


@app.post("/enrich", response_model=EnrichResponse)
def enrich(request: ProcessRequest) -> EnrichResponse:
    return enrich_document(request.data, scenario=request.scenario)


@app.post("/sensitivity", response_model=SensitivityResponse)
def sensitivity(request: ProcessRequest) -> SensitivityResponse:
    return classify_sensitivity(request.data, scenario=request.scenario)
