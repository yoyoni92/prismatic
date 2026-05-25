from __future__ import annotations

import re


def keyword_match(text: str, keyword: str) -> bool:
    return bool(re.search(r"\b" + re.escape(keyword) + r"\b", text))
