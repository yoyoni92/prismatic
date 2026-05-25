from unittest.mock import MagicMock, patch

from api.sensitivity import classify_sensitivity
from api.models import GeminiResult, Entities


def make_result(amounts=None, people=None, summary=""):
    return GeminiResult(
        classification="report",
        sentiment="neutral",
        confidence_score=0.8,
        entities=Entities(amounts=amounts or [], people=people or []),
        summary=summary,
        action_items=[]
    )


def test_amounts_make_internal():
    resp = classify_sensitivity(make_result(amounts=["$50,000"]), scenario="business")
    assert resp.sensitivity in ("internal", "confidential")


def test_confidential_keyword_in_summary():
    resp = classify_sensitivity(
        make_result(summary="This is a confidential NDA document"), scenario="business"
    )
    assert resp.sensitivity == "confidential"


def test_plain_document_is_public():
    resp = classify_sensitivity(
        make_result(summary="General product overview"), scenario="product"
    )
    assert resp.sensitivity == "public"


def test_sunday_does_not_trigger_nda():
    resp = classify_sensitivity(
        make_result(summary="Operating hours: Sunday-Wednesday 10:00-21:00, Thursday 10:00-18:00"),
        scenario="business"
    )
    assert resp.sensitivity != "confidential"


def test_llm_verifier_downgrades_false_positive():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "public"

    with patch("api.verifier.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            resp = classify_sensitivity(
                make_result(summary="Confidential NDA between parties."), scenario="business"
            )
    # LLM said public → downgrade from confidential
    assert resp.sensitivity == "public"
    assert resp.llm_verified is True


def test_llm_verifier_fallback_on_failure():
    with patch("api.verifier.OpenAI") as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = Exception("timeout")
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            resp = classify_sensitivity(
                make_result(summary="Confidential NDA between parties."), scenario="business"
            )
    # OpenAI failed → fall back to rule-based confidential
    assert resp.sensitivity == "confidential"
    assert resp.llm_verified is False


def test_no_openai_key_skips_verification():
    import os
    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    with patch.dict("os.environ", env, clear=True):
        resp = classify_sensitivity(
            make_result(summary="Confidential NDA between parties."), scenario="business"
        )
    assert resp.sensitivity == "confidential"
    assert resp.llm_verified is False
