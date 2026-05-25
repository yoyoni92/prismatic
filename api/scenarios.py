from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel


class ScenarioConfig(BaseModel):
    department_map: dict[str, str]
    sensitive_keywords: list[str]


def _load() -> dict[str, ScenarioConfig]:
    toml_path = Path(__file__).parent / "scenarios.toml"
    with open(toml_path, "rb") as f:
        raw = tomllib.load(f)
    return {k: ScenarioConfig(**v) for k, v in raw["scenarios"].items()}


SCENARIOS: dict[str, ScenarioConfig] = _load()
CATEGORIES: list[str] = list(SCENARIOS.keys())
