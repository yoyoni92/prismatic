from api.enrichment import enrich_document
from api.models import GeminiResult, Entities


def make_result(classification="invoice", confidence=0.85, amounts=None):
    return GeminiResult(
        classification=classification,
        sentiment="neutral",
        confidence_score=confidence,
        entities=Entities(amounts=amounts or ["$1,200"]),
        summary="Test",
        action_items=[]
    )


def test_invoice_routes_to_finance():
    resp = enrich_document(make_result("invoice"), scenario="business")
    assert resp.department == "Finance"


def test_low_confidence_needs_review():
    resp = enrich_document(make_result(confidence=0.5), scenario="business")
    assert resp.routing_tag == "needs-review"


def test_high_confidence_auto_approved():
    resp = enrich_document(make_result(confidence=0.9), scenario="business")
    assert resp.routing_tag == "auto-approved"


def test_document_id_is_uuid():
    import uuid
    resp = enrich_document(make_result(), scenario="business")
    uuid.UUID(resp.document_id)  # raises if invalid


def test_legal_scenario_contract():
    resp = enrich_document(make_result("contract"), scenario="legal")
    assert resp.department == "Legal"
