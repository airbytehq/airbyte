---
name: source-mysql-e2e-tests
description: Stand up a local MySQL backend, apply SQL fixtures, and run airbyte-ops protocol commands (spec / check / discover / read) against airbyte/source-mysql:<tag> for ad-hoc end-to-end testing and prove-fix comparisons. Use when you need a deterministic, throwaway local environment for any source-mysql test, repro, or target-vs-control fix validation.
---

# source-mysql-e2e-tests

Local end-to-end test harness for `source-mysql`. Stands up a MySQL
container named `source-mysql-db-backend`, lets you apply arbitrary SQL
fixtures, and runs Airbyte protocol commands against any
`airbyte/source-mysql:<tag>` image via
`airbyte-ops cloud connector regression-test` — in single-version mode
for repros, or comparison mode (target vs control) for `/ai-prove-fix`.

Modeled on
[`source-mssql-e2e-tests`](../../../source-mssql/.agents/skills/source-mssql-e2e-tests/SKILL.md);
the script contract is identical so driver scripts port across engines.

## When to use this skill

- Reproducing a `source-mysql` bug locally (type mapping, discovery,
  incremental cursor, `tinyint(1)` handling, null/edge-value handling,
  identifier quoting).
- Running `spec` / `check` / `discover` / `read` against any
  `airbyte/source-mysql:<tag>` for connector development.
- Proving a fix: comparing a PR image (`--test-image`) against a
  known-bad or latest control (`--control-image`) — see the
  `db_prove_fix` playbook in `airbytehq/ai-skills`.

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
source-mysql-e2e-tests/
├── SKILL.md
├── scripts/
│   ├── start-backend.sh        # docker run mysql:8.0 (binlog ROW + GTID) as source-mysql-db-backend
│   ├── stop-backend.sh         # docker rm -f source-mysql-db-backend
│   ├── apply-sql.sh            # docker exec mysql (stdin)
│   ├── render-config.sh        # jq the backend bridge IP into a config template
│   └── run-protocol-cmd.sh     # thin wrapper around `airbyte-ops … regression-test`
└── fixtures/
    ├── configs/
    │   └── base.template.json  # STANDARD (non-CDC) config; host placeholder
    └── sql/
        └── 00-init-base.sql    # sample table with three rows
```

The skill expects all script paths relative to the skill root.

## Conventions

- Container name: `source-mysql-db-backend`. Override via
  `BACKEND_NAME=…` only for parallel test isolation; don't use customer
  connection names.
- Working directory for rendered configs and run output:
  `${REPRO_OUT:-/tmp/source-mysql-repro}`. Each `regression-test` run
  writes artifacts under `$REPRO_OUT/<step-name>/`. Use a fresh
  subdirectory per step so artifacts don't get clobbered.
- Both containers (the MySQL backend and the connector launched by
  `airbyte-ops`) share Docker's default `bridge` network. The connector
  resolves the backend by its bridge IP, which `render-config.sh`
  substitutes into the working config at runtime. Tracked upstream in
  [`airbytehq/airbyte-ops-mcp#765`](https://github.com/airbytehq/airbyte-ops-mcp/issues/765);
  once `--network` is supported the bridge-IP dance can collapse.
- Image is pinned to `mysql:8.0` (override with `BACKEND_IMAGE=…` to
  reproduce a version-specific bug — e.g. `mysql:5.7`).
- The backend starts with `--binlog-format=ROW`, `--binlog-row-image=FULL`,
  and GTIDs on, so a CDC repro can read the binlog on the same container
  without a restart.

## Usage

```bash
SKILL=airbyte-integrations/connectors/source-mysql/.agents/skills/source-mysql-e2e-tests
export REPRO_OUT=/tmp/source-mysql-repro

# 1. Start the backend.
"$SKILL/scripts/start-backend.sh"

# 2. Apply a SQL fixture.
"$SKILL/scripts/apply-sql.sh" "$SKILL/fixtures/sql/00-init-base.sql"

# 3. Render a working config from a template, substituting the backend IP.
"$SKILL/scripts/render-config.sh" \
  "$SKILL/fixtures/configs/base.template.json" \
  "$REPRO_OUT/working/base.json"

# 4a. Single-version run. Output lands under $REPRO_OUT/check-baseline/.
"$SKILL/scripts/run-protocol-cmd.sh" check baseline 3.53.1 \
  --config-path="$REPRO_OUT/working/base.json"

# 4b. Prove-fix comparison: PR image (dev) vs known-bad control (3.53.0).
CONTROL_VERSION=3.53.0 "$SKILL/scripts/run-protocol-cmd.sh" read prove dev \
  --config-path="$REPRO_OUT/working/base.json" \
  --catalog-path="$REPRO_OUT/working/catalog.json"

# 5. Tear down.
"$SKILL/scripts/stop-backend.sh"
```

`run-protocol-cmd.sh <command> <step-name> <version> [extra-args…]`
maps to (single-version, default):

```
airbyte-ops cloud connector regression-test \
  --skip-compare=True \
  --command=<command> \
  --test-image=airbyte/source-mysql:<version> \
  --output-dir=$REPRO_OUT/<step-name> \
  <extra-args…>
```

Set `CONTROL_VERSION=<tag>` to switch to comparison mode: `--skip-compare`
is dropped and `--control-image=airbyte/source-mysql:$CONTROL_VERSION`
is added so airbyte-ops emits a side-by-side SPEC/CHECK/DISCOVER/READ
diff — the evidence engine the `db_prove_fix` playbook relies on.

## Asserting on output

Inline assertions in driver scripts. Suggested helpers:

- Exit code: check `$?` immediately after the call.
- AirbyteMessage shape: `jq -e 'select(.type == "RECORD")' $REPRO_OUT/<step>/stdout.txt`.
- Discovered types: inspect the `DISCOVER` catalog JSON for the field's `json_schema`.
- Connector-side log shape: `grep -c '<expected substring>' $REPRO_OUT/<step>/stderr.txt`.
- Connection status: `jq -e 'select(.type == "CONNECTION_STATUS" and .connectionStatus.status == "SUCCEEDED")' $REPRO_OUT/<step>/stdout.txt`.

`run-protocol-cmd.sh` accepts `--enable-debug-logs=True` as an extra arg
to set `LOG_LEVEL=DEBUG` on the connector container. That surfaces the
Debezium / bulk-CDK debug lines that some assertions rely on.

## Common gotchas

- _CDC needs ROW binlog_ → `start-backend.sh` sets `--binlog-format=ROW`
  and a `--server-id`. A CDC repro switches the config
  `replication_method` to `{"method": "CDC"}` and reads the binlog; the
  connecting user needs `REPLICATION SLAVE` / `REPLICATION CLIENT`
  (root has them). MySQL 8.0 has binlog on by default; the explicit
  flags make the format deterministic.
- _`ssl_mode` shape_ → MySQL uses `preferred / required / verify_ca /
  verify_identity` (the base config uses `preferred` so the local
  plaintext backend connects), not the Postgres `disable`/`require`
  strings or the mssql `unencrypted` shape.
- _`replication_method.method` is `STANDARD` / `CDC`_ (all caps), like
  mssql — not the Postgres `Standard`.
- _`tinyint(1)`_ → by default the connector maps `TINYINT(1)` to boolean;
  `treat_tinyint1_as_integer: true` in the config forces integer. Set it
  in a fixture config when reproducing a `tinyint` typing bug.

## Tear-down

`stop-backend.sh` is idempotent: `docker rm -f` is a no-op if the
container doesn't exist. To wipe everything:

```bash
"$SKILL/scripts/stop-backend.sh"
rm -rf "$REPRO_OUT"
unset REPRO_OUT
```
