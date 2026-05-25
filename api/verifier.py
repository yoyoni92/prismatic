from __future__ import annotations

import os

from openai import OpenAI

_LEVELS = {"public": 0, "internal": 1, "confidential": 2}
_VALID = set(_LEVELS)


def llm_verify_sensitivity(text: str, rule_based: str) -> tuple[str, bool]:
    """
    Calls OpenAI to verify a sensitivity classification.
    Returns (final_sensitivity, was_verified).
    Falls back to rule_based silently on any failure.
    Only intended to be called when rule_based == "confidential".
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return rule_based, False

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=10,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a document sensitivity classifier. "
                        "Classify the sensitivity of the document as one of: "
                        "public, internal, confidential. "
                        "Respond with ONLY the sensitivity level, nothing else."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Document content:\n\n{text}",
                },
            ],
        )
        llm_result = response.choices[0].message.content.strip().lower()

        if llm_result not in _VALID:
            return rule_based, False

        # Take the less restrictive of the two
        final = llm_result if _LEVELS[llm_result] < _LEVELS[rule_based] else rule_based
        return final, True

    except Exception:
        return rule_based, False
