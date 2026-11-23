"""Material Symbols for Kobento's `$icon`, as the shards an editor expands calls with.

    python3 generator/icons.py <material-design-icons checkout> <out dir>

Reads the 24px symbols (`symbols/web/<name>/materialsymbols<style>/<name>[_fill1]_24px.svg`, the
paths Kobento draws) and writes `<out>/<style>[-filled]/<shard>.json`: a JSON object from each
name whose first character is <shard> to its SVG path. Every shard is written, empty or not, so the
set of paths is fixed and `ui-builder.json` can list it. The checkout is google/material-design-icons
at ICONS_COMMIT (Apache-2.0); `build-icons.sh` fetches exactly the files this reads.
"""
import json
import re
import sys
from pathlib import Path

ICONS_COMMIT = "10ecc14790612ca8fd164e3f4ffe9c16fc50d5b7"
STYLES = ("outlined", "rounded", "sharp")
SHARDS = "0123456789abcdefghijklmnopqrstuvwxyz"
PATH = re.compile(r' d="([^"]+)"')
NAME = re.compile(r"[a-z0-9_]+")


def shard_paths(prefix):
    """Every shard path, under [prefix], in a fixed order."""
    return [
        f"{prefix}{style}{'-filled' if filled else ''}/{shard}.json"
        for style in STYLES
        for filled in (False, True)
        for shard in SHARDS
    ]


def build(checkout, out):
    web = Path(checkout) / "symbols" / "web"
    shards = {path: {} for path in shard_paths("")}
    for folder in sorted(web.iterdir()):
        name = folder.name
        if not NAME.fullmatch(name):
            continue
        for style in STYLES:
            for filled in (False, True):
                svg = folder / f"materialsymbols{style}" / f"{name}_{'fill1_' if filled else ''}24px.svg"
                if not svg.is_file():
                    continue
                paths = PATH.findall(svg.read_text())
                if len(paths) != 1:
                    raise SystemExit(f"{svg}: expected one path, found {len(paths)}")
                key = f"{style}{'-filled' if filled else ''}/{name[0]}.json"
                shards[key][name] = paths[0]
    out = Path(out)
    for path, icons in shards.items():
        target = out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(dict(sorted(icons.items())), separators=(",", ":")) + "\n")
    return {path: len(icons) for path, icons in shards.items()}


if __name__ == "__main__":
    counts = build(sys.argv[1], sys.argv[2])
    print(f"{sum(counts.values())} symbols in {len(counts)} shards")
