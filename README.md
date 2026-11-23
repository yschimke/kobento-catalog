# kobento-catalog

A [Compose UI Builder](https://github.com/yschimke/compose-ui-builder) catalog of
[Kobento](https://mcp.kobento.dev/)'s Remote Compose components: 117 library components (cards,
controls, charts, clocks, maps, 3D) served to the builder as data, so a design can be assembled
from them and exported as Kobento component JSON or a `.rc` document.

Kobento is an independent implementation of Remote Compose (not affiliated with Google), open
source under Apache 2.0. Its component library lives on its own server, so this repository keeps a
**snapshot of the components' interfaces** (names, parameters, types, defaults, slots) taken from
Kobento's MCP `find` tool, and generates the catalog from it. Beside it are the components'
**definitions** and the **default theme**, so an editor can expand a component call itself and draw
it without asking Kobento.

| File | |
| --- | --- |
| [`catalog/components.snapshot.json`](catalog/components.snapshot.json) | the interface snapshot |
| [`catalog/ui-builder.json`](catalog/ui-builder.json) | the published catalog, generated |
| [`catalog/kobento/definitions.json`](catalog/kobento/definitions.json) | each component's definition: params, slots, locals, body |
| [`catalog/kobento/theme.json`](catalog/kobento/theme.json) | the default theme the definitions read: numbers, colours, mono modes |
| [`catalog/kobento/json2rc.mjs`](catalog/kobento/json2rc.mjs) | Kobento's JSON → `.rc` converter as a browser module, built by `generator/build-json2rc.sh` |
| `kobento/icons/<style>[-filled]/<letter>.json` (published only) | The Material Symbols Kobento's `$icon` draws, as SVG paths by name, built by `generator/build-icons.sh` |
| [`catalog/designs/`](catalog/designs) | seed documents a new design starts from, hand-written; `kobento-screen` is the default |
| [`generator/snapshot.py`](generator/snapshot.py) | `fetch` (needs a token), `generate`, `check` |

## Refreshing

Create a free account at <https://mcp.kobento.dev/> and a token on its account page, then:

```sh
KOBENTO_TOKEN=rc_... python3 generator/snapshot.py fetch
```

`refresh.yml` does this weekly with the `KOBENTO_TOKEN` repository secret and opens a pull request
when the interface changed.

## Publishing

Every push to `main` force-pushes the catalog to `design-artifacts/kobento` on
`yschimke/kobento-catalog-out` (needs the `ARTIFACTS_TOKEN` secret), where a UI Builder host reads
it like the other published catalogs. The seed documents go to `ui-builder/designs/` beside it, at
the paths `statusSemantics.templates` lists.

A seed is a design document pinned to `kobento`, whose `id` and `template` are its file name.
`generate` lists every file in `catalog/designs/` (the default first), and `check` refuses one that
names a component the catalog does not serve. Without a seed, a host falls back to its own blank
screen, whose root this catalog does not hold.

## Design

[`UI_BUILDER_KOBENTO.md`](https://github.com/yschimke/compose-ui-builder/blob/main/docs/design/UI_BUILDER_KOBENTO.md)
in compose-ui-builder: why the snapshot keeps only interface facts, why every component is a
builtin, the export routes, device presets and looks, and the landing order.

Apache 2.0. Kobento is Apache 2.0 too; `catalog/kobento/` is derived from it, with its
attribution in [`catalog/kobento/NOTICE`](catalog/kobento/NOTICE).
