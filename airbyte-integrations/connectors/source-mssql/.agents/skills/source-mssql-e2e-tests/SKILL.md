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
│   └── run-protocol-cmd.sh     # thin wrapper around `airbyte-ops … regression-test`
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

```bash
SKILL=airbyte-integrations/connectors/source-mssql/.agents/skills/source-mssql-e2e-tests
export REPRO_OUT=/tmp/source-mssql-repro

# 1. Start the backend (ACCEPT_EULA, MSSQL_AGENT_ENABLED=true).
"$SKILL/scripts/start-backend.sh"

# 2. Apply a SQL fixture.
"$SKILL/scripts/apply-sql.sh" "$SKILL/fixtures/sql/00-init-base.sql"

# 3. Render a working config from a template, substituting the backend IP.
"$SKILL/scripts/render-config.sh" \
  "$SKILL/fixtures/configs/base.template.json" \
  "$REPRO_OUT/working/base.json"

# 4. Run a protocol command. Output lands under $REPRO_OUT/check-baseline/.
"$SKILL/scripts/run-protocol-cmd.sh" check baseline 4.4.2 \
  --config-path="$REPRO_OUT/working/base.json"

# 5. Tear down.
"$SKILL/scripts/stop-backend.sh"
```

`run-protocol-cmd.sh <command> <step-name> <version> [extra-args…]`
maps to:

```
airbyte-ops cloud connector regression-test \
  --skip-compare=True \
  --command=<command> \
  --test-image=airbyte/source-mssql:<version> \
  --output-dir=$REPRO_OUT/<step-name> \
  <extra-args…>
```

## Asserting on output

Inline assertions in driver scripts. Suggested helpers:

- Exit code: check `$?` immediately after the call.
- AirbyteMessage shape: `jq -e 'select(.type == "RECORD")' $REPRO_OUT/<step>/stdout.txt`.
- Connector-side log shape: `grep -c '<expected substring>' $REPRO_OUT/<step>/stderr.txt`.
- Connection status: `jq -e 'select(.type == "CONNECTION_STATUS" and .connectionStatus.status == "SUCCEEDED")' $REPRO_OUT/<step>/stdout.txt`.

`run-protocol-cmd.sh` accepts `--enable-debug-logs=True` as an extra arg
to set `LOG_LEVEL=DEBUG` on the connector container. That surfaces the
Debezium "Adding table … to the list of capture schema tables" lines
that some assertions rely on.

## Common gotchas

- _No SQL Server Agent_ → CDC capture / cleanup jobs never run, and
  Debezium silently produces no records. `start-backend.sh` sets
  `MSSQL_AGENT_ENABLED=true` for this reason.
- _Race on first `sqlcmd`_ → SQL Server 2022 takes around 15 seconds to
  accept connections cold. `start-backend.sh` polls until `SELECT 1`
  succeeds before returning.
- _Catalog schema drift across major versions_ → the bulk-CDK schema
  validator on `source-mssql:4.3.x` requires `is_file_based`,
  `generation_id`, `minimum_generation_id`, `sync_id`,
  `destination_object_name`, and `include_files` on every
  `ConfiguredAirbyteStream`. On `4.4.x` they default. Catalog fixtures
  used by this and dependent skills populate them so the same fixtures
  work across both majors.

## Tear-down

`stop-backend.sh` is idempotent: `docker rm -f` is a no-op if the
container doesn't exist. To wipe everything:

```bash
"$SKILL/scripts/stop-backend.sh"
rm -rf "$REPRO_OUT"
unset REPRO_OUT
```
