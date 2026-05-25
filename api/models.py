from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


ConfidenceScore = Annotated[float, Field(ge=0.0, le=1.0)]
Sensitivity = Annotated[str, Field(pattern=r"^(public|internal|confidential)$")]


class Entities(BaseModel):
    model_config = {"frozen": True}

    people: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    amounts: list[str] = Field(default_factory=list)


class GeminiResult(BaseModel):
    model_config = {"frozen": True}

    classification: str
    sentiment: str
    confidence_score: ConfidenceScore
    entities: Entities
    summary: str
    action_items: list[str] = Field(default_factory=list)


class EnrichResponse(BaseModel):
    model_config = {"frozen": True}

    document_id: str
    department: str
    routing_tag: str
    processed_at: str
    confidence_adjusted: ConfidenceScore
    keyword_tags: list[str] = Field(default_factory=list)


class SensitivityResponse(BaseModel):
    model_config = {"frozen": True}

    sensitivity: Sensitivity
    reason: str
    llm_verified: bool = False


class HealthResponse(BaseModel):
    model_config = {"frozen": True}

    status: str


class CategoriesResponse(BaseModel):
    model_config = {"frozen": True}

    categories: list[str] = Field(default_factory=list)


class ProcessRequest(BaseModel):
    scenario: str
    data: GeminiResult
