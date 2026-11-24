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
    # Components only Kobento's hosted `convert` expands (a `$gen` body): without these the palette
    # sends each one empty and `convert` refuses it, so it has no picture at all.
    "Callouts": {
        "aspect": 1.5,
        "parts": [{"label": "Screen", "x": 0.5, "y": 0.3}, {"label": "Button", "x": 0.5, "y": 0.8}],
    },
    "Chart3D": {"points": [[1, 2, 3], [2, 3, 1], [3, 1, 2], [2, 2, 2]]},
    "DashboardGrid": {
        "cards": [
            {"title": "Revenue", "content": {"type": "Text", "text": "$12k"}},
            {"title": "Users", "content": {"type": "Text", "text": "1,204"}},
        ],
    },
    "DataTable": {
        "columns": [{"title": "Name"}, {"title": "Qty"}],
        "rows": [["Apples", "3"], ["Pears", "5"], ["Plums", "8"]],
    },
    "FlowDiagram": {
        "nodes": [
            {"id": "a", "label": "Start"},
            {"id": "b", "label": "Review"},
            {"id": "c", "label": "Done"},
        ],
        "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "c"}],
    },
    "Fretboard": {"chord": "C"},
    "GraphDiagram": {
        "edges": [{"from": "A", "to": "B"}, {"from": "B", "to": "C"}, {"from": "A", "to": "C"}],
    },
    "Icon": {"name": "favorite"},
    "MapList": {"items": [{"title": "London", "place": "London"}, {"title": "Paris", "place": "Paris"}]},
    "MathPlot": {"fn": ["sin(x)"]},
    "PianoKeys": {"chord": "C"},
    "Sankey": {"sources": ["Solar", "Grid"], "uses": ["Home", "Car"], "flows": [3, 1, 2, 2]},
    "Scene3D": {"objects": [{"shape": "box"}]},
    "SplitFlap": {"text": "HELLO"},
    "GroupedBars": {
        "series": [{"name": "2024", "values": [3, 5, 4]}, {"name": "2025", "values": [4, 6, 5]}],
        "labels": ["Q1", "Q2", "Q3"],
    },
    "StackedBars": {
        "series": [{"name": "Rent", "values": [5, 5, 5]}, {"name": "Food", "values": [3, 4, 2]}],
        "labels": ["Jan", "Feb", "Mar"],
    },
    "TimelineTrack": {
        "items": [
            {"start": "09:00", "end": "10:30", "label": "Standup"},
            {"start": "11:00", "end": "12:00", "label": "Review"},
        ],
    },
}

# Series inside each item of a list param, published as `param[].field`: the exporter declares each
# item's list in `resources.floatArrays` and passes it by name (compose-ui-builder's
# `KobentoComponentJsonExporter`), as `series-bars` reads `series[i].values`.
ITEM_SERIES = {"GroupedBars": {"series[].values"}, "StackedBars": {"series[].values"}}

# `float` params a `$gen` generator reads as a float array, which [float_arrays] cannot see in a
# definition: the body hands the param to the generator whole, by name.
GEN_SERIES = {"Sankey": {"flows"}}

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
    """Fail on a starter or series naming a component or param the snapshot does not have."""
    item_params = {n: {e.split("[]")[0] for e in es} for n, es in ITEM_SERIES.items()}
    for name, params in list(STARTERS.items()) + list(GEN_SERIES.items()) + list(item_params.items()):
        if name not in components:
            raise SystemExit(f"starters.py: {name} is not a Kobento component")
        missing = set(params) - set(components[name])
        if missing:
            raise SystemExit(f"starters.py: {name} has no param {sorted(missing)}")
