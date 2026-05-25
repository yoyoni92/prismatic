import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

SAMPLE_REQUEST = {
    "scenario": "business",
    "data": {
        "classification": "invoice",
        "sentiment": "neutral",
        "confidence_score": 0.9,
        "entities": {
            "people": [],
            "organizations": ["Acme"],
            "dates": [],
            "amounts": ["$1,200"]
        },
        "summary": "Invoice from Acme.",
        "action_items": ["Pay invoice"]
    }
}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_categories():
    resp = client.get("/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert "categories" in data
    assert len(data["categories"]) == 9
    assert "business" in data["categories"]
    assert "other" in data["categories"]


def test_enrich_invoice_business():
    resp = client.post("/enrich", json=SAMPLE_REQUEST)
    assert resp.status_code == 200
    data = resp.json()
    assert data["department"] == "Finance"
    assert data["routing_tag"] == "auto-approved"
    assert "document_id" in data


def test_sensitivity_confidential():
    confidential_data = {**SAMPLE_REQUEST["data"], "summary": "Confidential NDA between parties."}
    resp = client.post("/sensitivity", json={"scenario": "business", "data": confidential_data})
    assert resp.status_code == 200
    data = resp.json()
    assert data["sensitivity"] == "confidential"
    assert "llm_verified" in data


def test_enrich_unknown_scenario_falls_back():
    resp = client.post("/enrich", json={**SAMPLE_REQUEST, "scenario": "unknown"})
    assert resp.status_code == 200
    assert resp.json()["department"] == "Finance"
