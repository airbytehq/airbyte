---
name: source-mssql-e2e-tests
description: Stand up a local SQL Server 2022 backend, apply SQL fixtures, and sweep the Airbyte protocol commands (spec → check → discover → read) against airbyte/source-mssql:<tag> for ad-hoc end-to-end testing. Use when you need a deterministic, throwaway local environment for any source-mssql test or repro that is not CDC-specific.
---

# source-mssql-e2e-tests

Local end-to-end test harness for `source-mssql`. Stands up a SQL Server
2022 container named `source-mssql-db-backend`, lets you apply arbitrary
SQL fixtures, and runs Airbyte protocol commands against any
`airbyte/source-mssql:<tag>` image via
`airbyte-ops cloud connector regression-test`.

## When to use this skill

- Reproducing a non-CDC bug against `source-mssql` locally.
- Sweeping `spec` → `check` → `discover` → `read`, or running one of
  them, against any `airbyte/source-mssql:<tag>` for connector
  development.
- As the building block for the
  [`source-mssql-e2e-cdc-tests`](../source-mssql-e2e-cdc-tests/SKILL.md)
  skill, which adds CDC enable plus worked-example fixtures on top.

## Prerequisites

- Docker.
- [`uv`](https://docs.astral.sh/uv/). `uv tool install airbyte-internal-ops`
  puts `airbyte-ops` on `$PATH`; alternatively prefix every call with
  `uvx airbyte-internal-ops`.
- `jq`.
- A clone of `airbytehq/airbyte`.

You do not need GSM or Cloud admin credentials. Local-only mode (no
`--connection-id`) reads everything from local files.

## Layout

```
source-mssql-e2e-tests/
├── SKILL.md
├── scripts/
│   ├── start-backend.sh        # docker run mcr…/mssql/server:2022-latest as source-mssql-db-backend
│   ├── stop-backend.sh         # docker rm -f source-mssql-db-backend
│   ├── apply-sql.sh            # docker cp + docker exec sqlcmd -i
│   ├── render-config.sh        # jq the backend bridge IP into a config template
│   ├── make-catalog.sh         # configured catalog derived from a discover run's CATALOG message
│   ├── run-protocol-cmd.sh     # thin wrapper around `airbyte-ops … regression-test`
│   └── run.sh                  # one-shot: backend → fixtures → config → spec/check/discover → catalog → read → teardown
└── fixtures/
    ├── configs/
    │   └── base.template.json  # non-CDC config; host=mssql-db-backend placeholder
    └── sql/
        └── 00-init-base.sql    # CREATE DATABASE TestDb + dbo.sample table
```

The skill expects all script paths relative to the skill root.

## Conventions

- Container name: `source-mssql-db-backend`. Hard-coded in
  `scripts/start-backend.sh`, `stop-backend.sh`, `apply-sql.sh`, and
  `render-config.sh`. Override via `BACKEND_NAME=…` only for parallel
  test isolation; don't use customer connection names.
- Working directory for rendered configs and run output:
  `${REPRO_OUT:-/tmp/source-mssql-repro}`. A `run.sh` invocation writes
  everything under `$REPRO_OUT/<step-name>/`: the rendered `config.json`,
  the derived `configured_catalog.json`, and one subdirectory per
  protocol command (`spec/`, `check/`, `discover/`, `read/`) holding that
  command's `stdout.txt`, `stderr.txt`, `report.md`, and `report.html`.
  This is the same layout the ops repo's `connector-regression-test.yml`
  workflow uses under `/tmp/regression_test_artifacts`, so CI can upload
  it per command.
- Both containers (the SQL Server backend and the connector launched by
  `airbyte-ops`) share Docker's default `bridge` network. The connector
  resolves the backend by its bridge IP, which `render-config.sh`
  substitutes into the working config at runtime. Tracked upstream in
  [`airbytehq/airbyte-ops#765`](https://github.com/airbytehq/airbyte-ops/issues/765);
  once `--network` is supported the bridge-IP dance can collapse.
- SQL Server image is pinned to `mcr.microsoft.com/mssql/server:2022-latest`,
  not `latest`, for stable major-version behavior across CU patches.

## Usage

`scripts/run.sh` is the only supported entrypoint. It performs the whole
sequence — start the backend, apply the fixtures, render the config, run
`spec` → `check` → `discover`, derive the configured catalog from that
`discover`'s output, run `read`, tear down on exit:

```bash
cd airbyte-integrations/connectors/source-mssql

# Single version, full sweep.
poe e2e-local --test-version=5.0.0 \
  --fixture=.agents/skills/source-mssql-e2e-tests/fixtures/sql/00-init-base.sql

# Target vs. control comparison (prove-fix shape).
poe e2e-local --test-version=dev --control-version=5.0.0 \
  --fixture=.agents/skills/source-mssql-e2e-tests/fixtures/sql/00-init-base.sql

# One command only.
poe e2e-local --command=read --test-version=5.0.0
```

The sweep runs every command against the one backend and reports each
result rather than stopping at the first failure, then prints a summary
table and exits non-zero if any command failed — separating an
infrastructure failure (`ERROR`, no verdict was produced) from a failed
test verdict (`FAIL`), as the ops workflow's final-status step does. A
`read` whose `discover` failed earlier in the sweep is reported `SKIPPED`,
not `ERROR` — an invalid-config case is expected to fail `discover`, and
there is then no catalog for `read` to use. Under
CI the table is also appended to `$GITHUB_STEP_SUMMARY`. A run limited to
one command instead exits with the connector's own exit code, so a repro
can still assert on it.

Build the target image first when using `--test-version=dev`, or pass
`--build` to have `run.sh` run `:dockerBuildx` for you. Other options:
`--command=spec|check|discover|read` (default `all`), `--skip-read`,
`--step-name`, `--catalog` (skip discover-derived generation),
`--sync-mode=incremental`, `--cursor-field`, `--streams`,
`--config-template`, `--keep-backend`, and `--` to forward extra args to
`airbyte-ops`. Per-command timeouts match the workflow's (30/30/60/180
minutes) and are overridable with
`TIMEOUT_MINUTES_{SPEC,CHECK,DISCOVER,READ}`.

When `--control-version` is set, `run.sh` drops
`--skip-compare=True` and passes `--control-image`, so every command in
the sweep runs both images and diffs their protocol output with the
existing comparators (record counts, primary keys, per-record, schema).
Both runs must see identical backend state — a full-refresh sweep is
read-only, but for CDC that means recreating the backend and capture
instance between them, which the comparators cannot check for you.

## Asserting on output

Inline assertions in driver scripts. Suggested helpers:

- Exit code: check `$?` immediately after the call.
- AirbyteMessage shape: `jq -e 'select(.type == "RECORD")' $REPRO_OUT/<step>/read/stdout.txt`.
- Connector-side log shape: `grep -c '<expected substring>' $REPRO_OUT/<step>/read/stderr.txt`.
- Connection status: `jq -e 'select(.type == "CONNECTION_STATUS" and .connectionStatus.status == "SUCCEEDED")' $REPRO_OUT/<step>/check/stdout.txt`.

In comparison mode each command's directory holds `target/` and
`control/` subdirectories, and the raw output is under those.

Pass `-- --enable-debug-logs=True` to `run.sh` to set `LOG_LEVEL=DEBUG`
on the connector container. That surfaces the
Debezium "Adding table … to the list of capture schema tables" lines
that some assertions rely on.

## Common gotchas

- _No SQL Server Agent_ → CDC capture / cleanup jobs never run, and
  Debezium silently produces no records. `start-backend.sh` sets
  `MSSQL_AGENT_ENABLED=true` for this reason.
- _Race on first `sqlcmd`_ → SQL Server 2022 takes around 15 seconds to
  accept connections cold. `start-backend.sh` polls until `SELECT 1`
  succeeds before returning.
- _Configured-stream fields the validator rejects as null_ → the
  bulk-CDK schema validator requires `is_file_based`, `cursor_field`,
  `generation_id`, `minimum_generation_id`, `sync_id`,
  `destination_object_name`, and `include_files` on every
  `ConfiguredAirbyteStream`; omitting them fails with
  `Null value is not allowed. (code: 1021)`. This is not 4.3.x-only —
  verified on `4.4.12` and `5.0.0` too. `discover` does not emit
  `is_file_based`, so the catalog `run.sh` derives fills it in, and the
  catalog fixtures shipped with this and dependent skills populate all of
  them.
- _A failed `check` does not fail a single-version run_ → the CDK exits
  0 even when it emits `CONNECTION_STATUS` with `status: FAILED`, so the
  `check` step passes. Assert on the status message yourself (see
  [Asserting on output](#asserting-on-output)) rather than on the exit
  code when the repro hinges on `check`. Comparison mode does surface
  it, because it reads the report's verdict rather than the exit code.

## Tear-down

`run.sh` removes the backend container in an `EXIT` trap, so a run leaves
nothing behind unless you passed `--keep-backend`. After a
`--keep-backend` run, or to also discard the collected artifacts:

```bash
SKILL=airbyte-integrations/connectors/source-mssql/.agents/skills/source-mssql-e2e-tests
"$SKILL/scripts/stop-backend.sh"   # idempotent; docker rm -f no-ops when absent
rm -rf "${REPRO_OUT:-/tmp/source-mssql-repro}"
```
