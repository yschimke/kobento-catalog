# AGENTS.md

A [Compose UI Builder](https://github.com/yschimke/compose-ui-builder) catalog of
[Kobento](https://mcp.kobento.dev/)'s Remote Compose components, published as data
(`ui-builder.json`) the way `m3-catalog`, `wear-m3-catalog` and `remote-m3-catalog` publish theirs.
The design is compose-ui-builder's
[`docs/design/UI_BUILDER_KOBENTO.md`](https://github.com/yschimke/compose-ui-builder/blob/main/docs/design/UI_BUILDER_KOBENTO.md).

## Rules

- **Git history attributes work only to the human committer.** No `Co-authored-by:` trailer naming
  an agent, and no agent author/committer identity (an `@anthropic.com` / `@openai.com` email or an
  agent name). Session links and "Generated with" footers are fine. The PR title and body are
  scanned too. Install the hooks once per clone: `scripts/install-git-hooks.sh`. CI's
  `Reject agent attribution` enforces it.
- **Branch names are `agent/...`** for agent work. Commit subjects and PR titles use Conventional
  Commits (`Conventional Commit title` checks the PR title; PRs are squash-merged with the title).
- **`catalog/ui-builder.json` is generated.** Change `generator/snapshot.py` (or the snapshot) and
  run `python3 generator/snapshot.py generate`; CI's `check` fails on a hand edit.
- **Commit interface facts only.** The snapshot keeps component names, param types, defaults, enum
  values and slots. Kobento's prose (summaries, docs, pitfalls) is served from a private repository
  under no stated licence, and is never committed here.
- **Never commit a Kobento token.** `fetch` reads `KOBENTO_TOKEN` from the environment; in CI it is
  a repository secret, and in a cloud session the proxy injects it.
- **The exporter is not here.** Lowering a design to Kobento JSON or `.rc` is compose-ui-builder's
  (`KobentoComponentJsonExporter`). This repository owns the catalog and its refresh.
- Merge only when explicitly asked.

## Layout

```
generator/snapshot.py          fetch | generate | check (stdlib Python, 3.9+)
catalog/components.snapshot.json   Kobento's component interfaces, from its MCP `find`
catalog/ui-builder.json        the published catalog: every component a builtin (no Kotlin call site)
.github/workflows/ci.yml       `check`, the required check: catalog matches the generator, JSON parses
.github/workflows/publish.yml  main -> yschimke/kobento-catalog-out@design-artifacts/kobento (ARTIFACTS_TOKEN)
.github/workflows/refresh.yml  weekly fetch with KOBENTO_TOKEN; a PR when the interface changed
```

## Checks

```sh
python3 generator/snapshot.py check
scripts/test-agent-attribution.sh
KOBENTO_TOKEN=... python3 generator/snapshot.py fetch   # refresh by hand
```

The merge policy (required checks, squash-only, the `Protect Main` ruleset) is applied from
[yschimke/renovate-config `repo-policy/`](https://github.com/yschimke/renovate-config/tree/main/repo-policy).
