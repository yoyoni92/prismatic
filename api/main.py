from __future__ import annotations

from fastapi import FastAPI

from api.enrichment import enrich_document
from api.models import (
    CategoriesResponse,
    EnrichResponse,
    GeminiResult,
    HealthResponse,
    ProcessRequest,
    SensitivityResponse,
)
from api.scenarios import CATEGORIES
from api.sensitivity import classify_sensitivity

app = FastAPI(title="Prismatic Enrichment API", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/categories", response_model=CategoriesResponse)
def categories() -> CategoriesResponse:
    return CategoriesResponse(categories=CATEGORIES)


@app.post("/enrich", response_model=EnrichResponse)
def enrich(request: ProcessRequest) -> EnrichResponse:
    return enrich_document(request.data, scenario=request.scenario)


@app.post("/sensitivity", response_model=SensitivityResponse)
def sensitivity(request: ProcessRequest) -> SensitivityResponse:
    return classify_sensitivity(request.data, scenario=request.scenario)
