"""Sea-level scenarios shared by the Python pipeline and the Unity / web apps.

Fill `data/scenarios.json` with values from the NASA IPCC AR6 Sea Level
Projection Tool for the tide gauge or grid point nearest your site.
The example file only holds illustrative numbers.
"""
from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class Scenario:
    name: str        # e.g. "SSP2-4.5"
    year: int        # e.g. 2100
    rise_m: float    # median sea-level rise vs baseline, metres
    low_m: float | None = None   # likely-range low (17th pct)
    high_m: float | None = None  # likely-range high (83rd pct)


def load_scenarios(path: str) -> tuple[float, list[Scenario]]:
    """Return (baseline_water_level_m, scenarios)."""
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    scen = [Scenario(**s) for s in cfg["scenarios"]]
    return float(cfg["baseline_water_level_m"]), scen


def water_level(baseline: float, s: Scenario, extra_m: float = 0.0) -> float:
    """Absolute water level: baseline (e.g. mean high water) + rise + optional surge."""
    return baseline + s.rise_m + extra_m
