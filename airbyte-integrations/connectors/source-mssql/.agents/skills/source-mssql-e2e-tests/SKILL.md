---
name: source-mssql-e2e-tests
description: Stand up a local SQL Server 2022 backend, apply SQL fixtures, and run airbyte-ops protocol commands (spec / check / discover / read) against airbyte/source-mssql:<tag> for ad-hoc end-to-end testing. Use when you need a deterministic, throwaway local environment for any source-mssql test or repro that is not CDC-specific.
---

# source-mssql-e2e-tests

Local end-to-end test harness for `source-mssql`. Stands up a SQL Server
2022 container named `source-mssql-db-backend`, lets you apply arbitrary
SQL fixtures, and runs Airbyte protocol commands against any
`airbyte/source-mssql:<tag>` image via
`airbyte-ops cloud connector regression-test`.

## When to use this skill

- Reproducing a non-CDC bug against `source-mssql` locally.
- Running `spec` / `check` / `discover` / `read` against any
  `airbyte/source-mssql:<tag>` for connector development.
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
│   └── run.sh                  # one-shot: backend → fixtures → config → catalog → command → teardown
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
  `${REPRO_OUT:-/tmp/source-mssql-repro}`. Each `regression-test` run
  writes `stdout.txt` and `stderr.txt` under
  `$REPRO_OUT/<step-name>/`. Use a fresh subdirectory per step so
  artifacts don't get clobbered.
- Both containers (the SQL Server backend and the connector launched by
  `airbyte-ops`) share Docker's default `bridge` network. The connector
  resolves the backend by its bridge IP, which `render-config.sh`
  substitutes into the working config at runtime. Tracked upstream in
  [`airbytehq/airbyte-ops-mcp#765`](https://github.com/airbytehq/airbyte-ops-mcp/issues/765);
  once `--network` is supported the bridge-IP dance can collapse.
- SQL Server image is pinned to `mcr.microsoft.com/mssql/server:2022-latest`,
  not `latest`, for stable major-version behavior across CU patches.

## Usage

`scripts/run.sh` is the only supported entrypoint. It performs the whole
sequence — start backend, apply fixtures, render config, derive the
configured catalog from a `discover` run, run the protocol command, tear
down on exit — and exits with the connector's own exit code:

```bash
cd airbyte-integrations/connectors/source-mssql

# Single version.
poe e2e-local --command=read --test-version=5.0.0 \
  --fixture=.agents/skills/source-mssql-e2e-tests/fixtures/sql/00-init-base.sql

# Target vs. control comparison (prove-fix shape).
poe e2e-local --command=read --test-version=dev --control-version=5.0.0 \
  --fixture=.agents/skills/source-mssql-e2e-tests/fixtures/sql/00-init-base.sql
```

Build the target image first when using `--test-version=dev`, or pass
`--build` to have `run.sh` run `:airbyteDocker` for you. Other options:
`--step-name`, `--catalog` (skip discover-derived generation),
`--sync-mode=incremental`, `--cursor-field`, `--streams`,
`--config-template`, `--keep-backend`, and `--` to forward extra args to
`airbyte-ops`.

When `--control-version` is set, `run.sh` drops
`--skip-compare=True` and passes `--control-image`, so the CLI runs both
images and diffs their protocol output with the existing comparators
(record counts, primary keys, per-record, schema). Both runs must see
identical backend state — for CDC that means recreating the backend and
capture instance between them, which the comparators cannot check for
you.

The other scripts under `scripts/` are `run.sh`'s internals. Invoke them
directly only from the composing
[`source-mssql-e2e-cdc-tests`](../source-mssql-e2e-cdc-tests/SKILL.md)
skill, which needs to interleave CDC setup between the steps; for
everything else drive them through `run.sh` so there is a single
ordering of the sequence.

## Asserting on output

Inline assertions in driver scripts. Suggested helpers:

- Exit code: check `$?` immediately after the call.
- AirbyteMessage shape: `jq -e 'select(.type == "RECORD")' $REPRO_OUT/<step>/stdout.txt`.
- Connector-side log shape: `grep -c '<expected substring>' $REPRO_OUT/<step>/stderr.txt`.
- Connection status: `jq -e 'select(.type == "CONNECTION_STATUS" and .connectionStatus.status == "SUCCEEDED")' $REPRO_OUT/<step>/stdout.txt`.

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
  0 even when it emits `CONNECTION_STATUS` with `status: FAILED`, so
  `run.sh` returns 0. Assert on the status message yourself (see
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
