> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to `source-mssql`

This file is connector-specific. For general Airbyte contribution guidance,
see the repo-root [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) and the
[connector contribution guide](https://docs.airbyte.com/connector-development/).

`source-mssql` is a Kotlin / bulk-CDK connector. Standard local commands:

```bash
./gradlew :airbyte-integrations:connectors:source-mssql:test
./gradlew :airbyte-integrations:connectors:source-mssql:assemble
./gradlew :airbyte-integrations:connectors:source-mssql:dockerBuildx
```

Test fixtures use `org.testcontainers:mssqlserver` — see
`src/test/kotlin/io/airbyte/integrations/source/mssql/MsSqlServerContainerFactory.kt`.

---

## Reproducing bugs locally

Most reported bugs against `source-mssql` are CDC-mode bugs, but the same
local-harness pattern is useful for non-CDC bugs too. The
engine-independent orchestration now lives in
[`airbyte-integrations/db-harness-lib/`](../../db-harness-lib/), while the
co-located agent skills under [`.agents/skills/`](.agents/skills/) keep the
MSSQL backend lifecycle, fixtures, and config templates:

- [`source-mssql-e2e-tests`](.agents/skills/source-mssql-e2e-tests/SKILL.md) —
  the generic harness. Stands up a SQL Server 2022 container
  (`source-mssql-db-backend`), applies SQL fixtures via `sqlcmd`, and
  sweeps the Airbyte protocol commands (`spec` → `check` → `discover` →
  `read`, or just one of them)
  against `airbyte/source-mssql:<tag>` using the
  [`airbyte-internal-ops`](https://github.com/airbytehq/airbyte-ops-mcp)
  CLI's `airbyte-ops cloud connector regression-test --skip-compare=True`.
  Use this skill for any non-CDC bug or as a building block.
- [`source-mssql-e2e-cdc-tests`](.agents/skills/source-mssql-e2e-cdc-tests/SKILL.md) —
  layers on top: enables CDC, ships CDC-aware config / catalog templates,
  and contains per-bug fixtures and driver scripts. Three worked examples
  ship today, each with inline pass / fail assertions:
  - `repro-12162.sh` — [`airbytehq/oncall#12162`](https://github.com/airbytehq/oncall/issues/12162)
    (whitespace in stream name → Debezium rejects `message.key.columns`).
  - `repro-12094.sh` — [`airbytehq/oncall#12094`](https://github.com/airbytehq/oncall/issues/12094)
    (Debezium loads schema history for every database table, not just the
    configured catalog).
  - `repro-11451.sh` — [`airbytehq/oncall#11451`](https://github.com/airbytehq/oncall/issues/11451)
    (saved CDC offset rejected after `min_lsn` advances past it).

**Never** repro against a customer connection or against an Airbyte Cloud
instance.

### Getting a target image

Follow the shared
[Getting a target image](../../db-harness-lib/README.md#getting-a-target-image)
guidance. Build locally with
`./gradlew :airbyte-integrations:connectors:source-mssql:dockerBuildx` only
for code that is not on a pushed PR branch.

### Quickstart

```bash
SKILL=airbyte-integrations/connectors/source-mssql/.agents/skills/source-mssql-e2e-tests
CDC_SKILL=airbyte-integrations/connectors/source-mssql/.agents/skills/source-mssql-e2e-cdc-tests

# Backend
"$SKILL/scripts/start-backend.sh"

# Init the CDC database
"$SKILL/scripts/apply-sql.sh" "$CDC_SKILL/fixtures/sql/00-init-cdc.sql"

# Reproduce a specific bug (each script is idempotent and exits non-zero
# on assertion failure)
"$CDC_SKILL/scripts/repro-12162.sh"
"$CDC_SKILL/scripts/repro-12094.sh"
"$CDC_SKILL/scripts/repro-11451.sh"

# Cleanup
BACKEND_NAME=source-mssql-db-backend \
  airbyte-integrations/db-harness-lib/scripts/stop-backend.sh
```

To investigate a new bug, write the smallest SQL fixture that produces
the reported symptom (drop into
[`source-mssql-e2e-cdc-tests/fixtures/sql/`](.agents/skills/source-mssql-e2e-cdc-tests/fixtures/sql/)),
add a driver script alongside (`repro-<oncall-id>.sh`), and assert on the
relevant `stdout.txt` / `stderr.txt` / exit-code shape. Each driver
script invokes the engine shim, which delegates orchestration to
`airbyte-integrations/db-harness-lib/scripts/run.sh`, so the connector
lifecycle (image pull, AirbyteMessage parsing, exit-code surfacing) is
already handled.

### Prerequisites

- Docker
- A clone of this repo
- [`uv`](https://docs.astral.sh/uv/) — for invoking `airbyte-ops` via
  `uvx airbyte-internal-ops ...`. To pre-install (recommended for
  repeated invocations) run `uv tool install airbyte-internal-ops`,
  after which `airbyte-ops --help` is on `$PATH`.

You do **not** need the platform, Sonar, Airbyte Cloud, or any GSM /
Cloud admin credentials. Local-only mode (no `--connection-id`) reads
config / catalog / state from local files and runs the connector image
directly.

## Troubleshooting

- **Connector cannot reach `source-mssql-db-backend`.**
  `airbyte-ops cloud connector regression-test` does not currently expose
  `--network` (tracked in
  [`airbytehq/airbyte-ops-mcp#765`](https://github.com/airbytehq/airbyte-ops-mcp/issues/765)).
  Until it does, both containers share Docker's default `bridge` network
  and the connector resolves the source by IP. The shared library's
  [`render-config.sh`](../../db-harness-lib/scripts/render-config.sh)
  handles this: it inspects the backend's bridge IP and substitutes it
  into the config template before each invocation.
- **A connector run rejects the catalog with `Validation error(s)`.**
  Bulk-CDK requires `is_file_based`, `cursor_field`, `generation_id`,
  `minimum_generation_id`, `sync_id`, `destination_object_name`, and
  `include_files` on every configured stream, and rejects them as null
  with `code: 1021`. This is not limited to `4.3.x` — `4.4.12` and
  `5.0.0` reject them too. `discover` never emits `is_file_based`, so the
  shared library's
  [`make-catalog.sh`](../../db-harness-lib/scripts/make-catalog.sh) fills
  it in; the catalog fixtures shipped with the CDC skill populate all of
  them.
- **A `check` that fails still exits 0 in single-version mode.** The CDK
  emits `CONNECTION_STATUS` with `status: FAILED` and exits 0, so the
  harness cannot surface it as a non-zero exit. Assert on the status
  message when a repro hinges on `check`. Comparison mode reads the
  report's verdict instead, so it does fail.
- **Debezium engine starts but produces no records.** SQL Server CDC
  capture / cleanup are SQL Server Agent jobs. The backend container
  must be started with `MSSQL_AGENT_ENABLED=true` (the generic skill's
  `start-backend.sh` sets this). Without Agent, Debezium silently sees
  an empty change table.
- **A CDC read returns records but no `_ab_cdc_cursor` values.** The
  configured `cursor_field` of a CDC stream must be
  `["_ab_cdc_cursor"]`, the stream's source-defined cursor. Bulk-CDK
  resolves a configured cursor against the stream's data columns and the
  CDK's global cursor only, so any other name — `_ab_cdc_lsn` included,
  even though it is in the stream schema — resolves to null. On CDK
  versions predating [#75636](https://github.com/airbytehq/airbyte/pull/75636)
  (which is every `source-mssql` image up to and including `4.3.5`) an
  unresolved cursor downgrades the stream to full refresh, and the run
  looks green while never exercising CDC.
- **`prettier` reformats your committed JSON catalog.** The Format Check
  CI job runs `prettier`, which collapses short JSON arrays onto one
  line. Run `pnpm prettier --write airbyte-integrations/connectors/source-mssql/.agents`
  before pushing.
- **The matrix detector requires a `dockerImageTag` bump.** Files inside
  `airbyte-integrations/connectors/source-mssql/` are treated as
  connector changes by CI, including `.agents/skills/` and
  `CONTRIBUTING.md`. Bump `metadata.yaml`'s `dockerImageTag` and append
  a row to the changelog when you touch any of them.
- **`config.cdc.json` uses `ssl_method: unencrypted`.** Fine for a local
  throwaway container, never for a real source.

## Comparison-mode regression testing

The same `airbyte-ops cloud connector regression-test` command is used
by `/ai-prove-fix` for comparison-style work (target image vs. control
image). Per-bug repro driver scripts don't normally need it and stay on
the single-version path, which passes `--skip-compare=True`.

For a prove-fix comparison, use the generic skill's one-shot entrypoint
with a control version:

```bash
cd airbyte-integrations/connectors/source-mssql

# Non-CDC (default). Both images run against one backend and airbyte-ops
# emits the built-in target-vs-control diff.
poe e2e-local --test-version=dev --control-version=5.0.0 \
  --fixture=.agents/skills/source-mssql-e2e-tests/fixtures/sql/00-init-base.sql

# CDC. Two single-version sweeps with a fixture reset between them, so
# the target does not read against the control's warm capture instance.
poe e2e-local --test-version=dev --control-version=5.0.0 --reset=fixture \
  --fixture=.agents/skills/source-mssql-e2e-cdc-tests/fixtures/sql/00-init-cdc.sql \
  --fixture=.agents/skills/source-mssql-e2e-cdc-tests/fixtures/sql/<per-bug>.sql
```

Both runs must observe equivalent backend state. Under
`--reset=none` (the default) the two images share the backend, which is
safe for a full-refresh read but not for CDC — a shared capture instance
and an advanced log position make the diff look clean while being
meaningless. `--reset=fixture` drops every non-system database and
re-applies the fixtures between the two runs (fast; the log-LSN clock
still ticks server-wide); `--reset=backend` also recreates the backend
container (~15s extra, resets the LSN clock). Pick `--reset=fixture` for
CDC unless the reproduction depends on matching LSN sequences. See
[`SKILL.md`](.agents/skills/source-mssql-e2e-tests/SKILL.md#comparison-modes-with---control-version)
for the full breakdown.
