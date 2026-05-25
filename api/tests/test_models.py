from api.models import GeminiResult, EnrichResponse
import pytest

def test_gemini_result_valid():
    data = {
        "classification": "invoice",
        "sentiment": "neutral",
        "confidence_score": 0.85,
        "entities": {"people": [], "organizations": ["Acme"], "dates": [], "amounts": ["$1,200"]},
        "summary": "An invoice from Acme.",
        "action_items": ["Process payment"]
    }
    result = GeminiResult(**data)
    assert result.classification == "invoice"

def test_gemini_result_missing_field():
    with pytest.raises(Exception):
        GeminiResult(classification="invoice")  # missing required fields


def test_scenarios_load():
    from api.scenarios import SCENARIOS, CATEGORIES
    assert len(SCENARIOS) == 9
    assert "business" in SCENARIOS
    assert "medical" in SCENARIOS
    assert "other" in SCENARIOS
    assert SCENARIOS["business"].department_map["invoice"] == "Finance"
    assert "confidential" in SCENARIOS["business"].sensitive_keywords
    assert len(CATEGORIES) == 9
