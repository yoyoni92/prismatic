from __future__ import annotations

from api.models import GeminiResult, SensitivityResponse
from api.scenarios import SCENARIOS
from api.utils import keyword_match
from api.verifier import llm_verify_sensitivity

CONFIDENTIAL_KEYWORDS = [
    "confidential", "attorney-client", "privilege", "sealed",
    "nda", "non-disclosure", "proprietary", "trade secret",
    "patient", "phi", "hipaa", "salary", "termination",
]


def classify_sensitivity(data: GeminiResult, scenario: str = "business") -> SensitivityResponse:
    config = SCENARIOS.get(scenario, SCENARIOS["business"])

    all_text = " ".join([
        *data.entities.people,
        *data.entities.organizations,
        data.summary,
        *data.action_items,
    ]).lower()

    global_hit = any(keyword_match(all_text, kw) for kw in CONFIDENTIAL_KEYWORDS)
    scenario_hit = any(keyword_match(all_text, kw) for kw in config.sensitive_keywords)

    if global_hit or scenario_hit:
        final, verified = llm_verify_sensitivity(all_text, "confidential")
        reason = (
            "Sensitive keywords detected in document content"
            if final == "confidential"
            else "Rule-based flagged confidential but LLM verified as not confidential"
        )
        return SensitivityResponse(sensitivity=final, reason=reason, llm_verified=verified)

    if data.entities.amounts or len(data.entities.people) > 1:
        return SensitivityResponse(
            sensitivity="internal",
            reason="Document contains financial figures or multiple named individuals",
        )

    return SensitivityResponse(
        sensitivity="public",
        reason="No sensitive content detected",
    )
