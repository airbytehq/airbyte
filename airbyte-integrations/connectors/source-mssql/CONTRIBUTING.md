# Contributing to `source-mssql`

This file is connector-specific. For general Airbyte contribution guidance,
see the repo-root [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) and the
[connector contribution guide](https://docs.airbyte.com/connector-development/).

`source-mssql` is a Kotlin / bulk-CDK connector. Standard local commands:

```bash
./gradlew :airbyte-integrations:connectors:source-mssql:test
./gradlew :airbyte-integrations:connectors:source-mssql:assemble
./gradlew :airbyte-integrations:connectors:source-mssql:airbyteDocker
```

Test fixtures use `org.testcontainers:mssqlserver` — see
`src/test/kotlin/io/airbyte/integrations/source/mssql/MsSqlServerContainerFactory.kt`.

---

## Reproducing bugs locally

Most reported bugs against `source-mssql` are CDC-mode bugs, but the same
local-harness pattern is useful for non-CDC bugs too. Two co-located agent
skills under [`.agents/skills/`](.agents/skills/) own the actual harness:

- [`source-mssql-e2e-tests`](.agents/skills/source-mssql-e2e-tests/SKILL.md) —
  the generic harness. Stands up a SQL Server 2022 container
  (`source-mssql-db-backend`), applies SQL fixtures via `sqlcmd`, and runs
  one Airbyte protocol command (`spec` / `check` / `discover` / `read`)
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
"$SKILL/scripts/stop-backend.sh"
```

To investigate a new bug, write the smallest SQL fixture that produces
the reported symptom (drop into
[`source-mssql-e2e-cdc-tests/fixtures/sql/`](.agents/skills/source-mssql-e2e-cdc-tests/fixtures/sql/)),
add a driver script alongside (`repro-<oncall-id>.sh`), and assert on the
relevant `stdout.txt` / `stderr.txt` / exit-code shape. Each driver
script wraps the generic skill's `run-protocol-cmd.sh`, so the connector
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
  and the connector resolves the source by IP. The `render-config.sh`
  script in the generic skill handles this: it inspects the backend's
  bridge IP and substitutes it into the config template before each
  invocation.
- **Connector run on `4.3.x` rejects the catalog with `Validation error(s)`.**
  Bulk-CDK on `4.3.x` requires `is_file_based`, `generation_id`,
  `minimum_generation_id`, `sync_id`, `destination_object_name`, and
  `include_files` to be present on every configured stream.
  `4.4.x` made these nullable. The catalog fixtures shipped with the
  CDC skill populate all of them so the same fixtures drive repros on
  both major versions.
- **Debezium engine starts but produces no records.** SQL Server CDC
  capture / cleanup are SQL Server Agent jobs. The backend container
  must be started with `MSSQL_AGENT_ENABLED=true` (the generic skill's
  `start-backend.sh` sets this). Without Agent, Debezium silently sees
  an empty change table.
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
image). For per-bug repro driver scripts that's not normally needed —
they all pass `--skip-compare=True` via the generic skill's
`run-protocol-cmd.sh`. To reach for the comparison path manually, drop
`--skip-compare=True` and supply both `--test-image` and
`--control-image`; the CLI's `--help` covers the additional flags.
