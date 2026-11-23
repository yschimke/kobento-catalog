#!/usr/bin/env bash
# Builds the Material Symbols shards Kobento's `$icon` draws from (generator/icons.py) into <out>,
# from google/material-design-icons (Apache-2.0) at icons.py's ICONS_COMMIT: a blobless, sparse
# fetch of the 24px symbols only, some 25,000 small files rather than the repository.
#
#   generator/build-icons.sh <out dir>      # writes <out>/<style>[-filled]/<shard>.json
set -euo pipefail
OUT="${1:?usage: build-icons.sh <out dir>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMIT="$(sed -n 's/^ICONS_COMMIT = "\([0-9a-f]\{40\}\)"$/\1/p' "$HERE/icons.py")"
[[ -n "$COMMIT" ]] || { echo "no ICONS_COMMIT in $HERE/icons.py" >&2; exit 1; }
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
git -C "$WORK" init -q symbols
git -C "$WORK/symbols" sparse-checkout set --no-cone \
  '/symbols/web/*/materialsymbols*/*_24px.svg' \
  '!/symbols/web/*/materialsymbols*/*_grad*' '!/symbols/web/*/materialsymbols*/*wght*'
git -C "$WORK/symbols" fetch -q --depth 1 --filter=blob:none \
  https://github.com/google/material-design-icons.git "$COMMIT"
git -C "$WORK/symbols" checkout -q FETCH_HEAD
python3 -I "$HERE/icons.py" "$WORK/symbols" "$OUT"
echo "built the Material Symbols shards from google/material-design-icons@$COMMIT"
