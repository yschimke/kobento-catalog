"""What a chart arrives holding when an editor inserts it, and what its palette picture shows.

Kobento's chart components take their data as float arrays (a `float` param the definition reads
with `arrayLength`, `arrayGet` and friends), which an editor otherwise starts empty: an empty
chart. These are this repository's own sample values, not Kobento's documentation or examples:
round, generic numbers sized to each definition's reading of them (Candlestick's four series share
a length, Heatmap's values fill `rows` x `cols`).

`generate` checks every component and param named here against the snapshot, so a refresh that
renames one fails rather than publishing a seed nobody reads.
"""

import json
import re

SERIES = [3, 5, 4, 7, 6, 8]

# Kobento component name -> param -> its value, as plain JSON.
STARTERS = {
    "AllocationBar": {
        "values": [50, 30, 20],
        "items": [{"label": "Stocks"}, {"label": "Bonds"}, {"label": "Cash"}],
    },
    "ActivityRings": {
        "rings": [
            {"label": "Move", "value": 420, "target": 600},
            {"label": "Exercise", "value": 24, "target": 30},
            {"label": "Stand", "value": 9, "target": 12},
        ],
    },
    "BarChart": {"values": SERIES},
    "Candlestick": {
        "open": [10, 12, 11, 14, 13, 15],
        "close": [12, 11, 14, 13, 15, 17],
        "high": [13, 13, 15, 15, 16, 18],
        "low": [9, 10, 10, 12, 12, 14],
    },
    "DonutChart": {"values": [45, 30, 25]},
    "Heatmap": {
        "rows": 3,
        "cols": 7,
        "values": [2, 4, 3, 6, 5, 1, 0, 3, 5, 7, 4, 6, 2, 1, 1, 2, 4, 5, 7, 3, 2],
    },
    "Legend": {"values": [45, 30, 25], "labels": ["First", "Second", "Third"]},
    "LineChart": {"values": SERIES},
    "MeterBreakdown": {
        "value": 14,
        "target": 20,
        "unit": "kWh",
        "parts": [
            {"label": "Heating", "value": 12},
            {"label": "Lights", "value": 5},
            {"label": "Other", "value": 3},
        ],
    },
    "PriceChart": {"values": [102.4, 104.1, 103.2, 106.8, 105.5, 108.3]},
    "RadarChart": {
        "values": [7, 5, 8, 6, 4],
        "labels": ["Speed", "Range", "Power", "Comfort", "Price"],
    },
    "RankedList": {"names": ["First", "Second", "Third"], "values": [92, 74, 58]},
    "ScatterPlot": {"x": [1, 2, 3, 4, 5, 6], "y": [2, 4, 3, 6, 5, 7]},
    "SleepStages": {"stages": [0, 2, 3, 3, 2, 1, 2, 3, 2, 1, 0]},
    "Sparkline": {"values": SERIES},
    "TrendSparkline": {"values": SERIES},
}

ARRAY_READS = ("arrayLength", "arrayGet", "arrayMax", "arrayMin", "arraySum")


def float_arrays(definition: dict) -> set:
    """The `float` params [definition]'s locals and body read as an array, not a number."""
    text = json.dumps({k: v for k, v in definition.items() if k != "params"})
    arrays = set()
    for param, spec in (definition.get("params") or {}).items():
        if spec.get("type") != "float":
            continue
        ref = re.escape("@" + param)
        if re.search(r"(?:%s)\(\s*%s\b" % ("|".join(ARRAY_READS), ref), text):
            arrays.add(param)
    return arrays


def encode(value):
    """[value] as a design's property literal: compose-ui-builder's document encoding."""
    if isinstance(value, bool):
        return {"type": "bool", "value": value}
    if isinstance(value, (int, float)):
        return {"type": "float", "value": value}
    if isinstance(value, str):
        return {"type": "string", "value": value}
    if isinstance(value, list):
        return {"type": "list", "values": [encode(item) for item in value]}
    if isinstance(value, dict):
        return {"type": "object", "fields": {k: encode(v) for k, v in value.items()}}
    raise ValueError(f"no literal for {value!r}")


def check(components: dict) -> None:
    """Fail on a starter naming a component or param the snapshot does not have."""
    for name, params in STARTERS.items():
        if name not in components:
            raise SystemExit(f"starters.py: {name} is not a Kobento component")
        missing = set(params) - set(components[name])
        if missing:
            raise SystemExit(f"starters.py: {name} has no param {sorted(missing)}")
