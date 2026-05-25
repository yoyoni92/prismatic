from __future__ import annotations

import datetime
import uuid

from api.models import EnrichResponse, GeminiResult
from api.scenarios import SCENARIOS
from api.utils import keyword_match


def enrich_document(data: GeminiResult, scenario: str = "business") -> EnrichResponse:
    config = SCENARIOS.get(scenario, SCENARIOS["business"])

    department = config.department_map.get(data.classification, "General")

    if data.confidence_score < 0.7:
        routing_tag = "needs-review"
    elif data.confidence_score >= 0.8:
        routing_tag = "auto-approved"
    else:
        routing_tag = "needs-review"

    all_text = " ".join([
        *data.entities.people,
        *data.entities.organizations,
        *data.entities.amounts,
        *data.action_items,
        data.summary,
    ]).lower()

    keyword_tags = [kw for kw in config.sensitive_keywords if keyword_match(all_text, kw)]

    entity_fields = [
        data.entities.people,
        data.entities.organizations,
        data.entities.dates,
        data.entities.amounts,
    ]
    filled = sum(1 for f in entity_fields if f)
    confidence_adjusted = min(1.0, data.confidence_score + (filled * 0.02))

    return EnrichResponse(
        document_id=str(uuid.uuid4()),
        department=department,
        routing_tag=routing_tag,
        processed_at=datetime.datetime.now(datetime.UTC).isoformat(),
        confidence_adjusted=round(confidence_adjusted, 3),
        keyword_tags=keyword_tags,
    )
