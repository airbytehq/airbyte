---
name: source-mssql-e2e-cdc-tests
description: Reproduce CDC bugs against source-mssql by enabling CDC on the local SQL Server backend, applying per-bug SQL fixtures, and running the connector via airbyte-ops. Composes on top of source-mssql-e2e-tests. Worked examples for airbytehq/oncall#11451, #12094, and #12162 ship with the skill.
---

# source-mssql-e2e-cdc-tests

Local CDC bug-reproduction harness for `source-mssql`. Builds on
[`source-mssql-e2e-tests`](../source-mssql-e2e-tests/SKILL.md): the
generic skill stands up the SQL Server backend and runs the connector;
this skill adds CDC enable, CDC-aware config / catalog templates, and
per-bug `.sh` driver scripts that apply a SQL fixture, run a protocol
command, and assert on the output.

## When to use this skill

- Reproducing a CDC-mode bug against `source-mssql` locally.
- Verifying a fix by re-running an existing worked example after
  pointing the driver script at a `--test-image=airbyte/source-mssql:dev`.
- Authoring a new repro fixture for a customer-reported CDC bug.
  Drop a SQL fixture and a `repro-<issue-number>.sh` driver into this
  skill; the driver does its own assertions inline.

## Prerequisites

Same as the generic skill:

- Docker, `uv`, `jq`, a clone of `airbytehq/airbyte`.
- The backend container `source-mssql-db-backend` started by
  `../source-mssql-e2e-tests/scripts/start-backend.sh`.

You do not need GSM or Cloud admin credentials.

## Layout

```
source-mssql-e2e-cdc-tests/
├── SKILL.md
├── scripts/
│   ├── repro-11451.sh                # airbytehq/oncall#11451 — LSN-range regression in 4.3.4+
│   ├── repro-12094.sh                # airbytehq/oncall#12094 — schema-history bloat
│   ├── repro-12162.sh                # airbytehq/oncall#12162 — whitespace in stream name
│   ├── canary-resume.sh               # snapshot-then-changes state replay canary
│   └── (state extraction lives in ../source-mssql-e2e-tests/scripts/)
└── fixtures/
    ├── configs/
    │   └── cdc.template.json
    ├── catalogs/
    │   ├── users-cdc.json
    │   └── order-items-cdc.json
    └── sql/
        ├── 00-init-cdc.sql
        ├── canary-resume-seed.sql
        ├── canary-resume-mutate.sql
        ├── repro-11451-lsn-cleanup.sql
        ├── repro-12094-schema-history.sql
        └── repro-12162-spaces-in-name.sql
```

## Conventions

- The `repro-*.sh` drivers assume the generic skill's backend is already
  running and apply CDC fixtures on top of it. `canary-resume.sh` instead
  goes through the generic `run.sh`, which owns the backend lifecycle
  itself. Re-applying any fixture is safe (every step is idempotent).
- Configured catalogs populate the bulk-CDK-required fields
  (`is_file_based`, `generation_id`, `minimum_generation_id`,
  `sync_id`, `destination_object_name`, `include_files`) so the same
  fixtures drive repros across `source-mssql:4.3.x` and `4.4.x`.
- `repro-*.sh` drivers default `VERSION=4.4.2` (`repro-11451.sh` pins its
  own baseline / target pair) and `canary-resume.sh` defaults
  `VERSION=5.0.0`. Override with
  `VERSION=4.3.4 ./scripts/repro-12162.sh` to test against an earlier
  version, or `VERSION=dev` after a local
  `./gradlew :airbyte-integrations:connectors:source-mssql:airbyteDocker`
  to test a fix.
- Assertions are inline in driver scripts: `grep -c '<substring>'` on
  `stderr.txt`, `jq -e` on `stdout.txt`, exit-non-zero on miss.
- The repro-11451 driver captures and uses Airbyte STATE messages. The
  generic skill's `extract-state.py` helper is `uv`-PEP-723 standalone;
  run with `../source-mssql-e2e-tests/scripts/extract-state.py
<stdout.txt>` or pipe stdin.

## Usage

Every driver script here is a standalone entrypoint that does its own
assertions and exits non-zero on failure. Two shapes ship: the canary
drives the generic skill's `run.sh` and needs no setup, while the
`repro-*.sh` drivers call the protocol wrapper directly and expect a
running backend.

```bash
cd airbyte-integrations/connectors/source-mssql
CDC=.agents/skills/source-mssql-e2e-cdc-tests
GENERIC=.agents/skills/source-mssql-e2e-tests

# Replay canary. Recreates the backend, then leaves it up.
"$CDC/scripts/canary-resume.sh"

# Per-bug repros. The backend goes up once per session; each driver
# applies 00-init-cdc.sql plus its own fixture on top.
"$GENERIC/scripts/start-backend.sh"
"$CDC/scripts/repro-12162.sh"
"$CDC/scripts/repro-12094.sh"
"$CDC/scripts/repro-11451.sh"

# (After a fix) verify by retargeting `dev` or a fixed version.
VERSION=dev "$CDC/scripts/repro-12162.sh"
```

The canary is also reachable straight from the generic entrypoint, which
is the shape to copy when varying flags — CDC needs nothing beyond a CDC
init fixture, a CDC config template, and a CDC catalog:

```bash
poe e2e-local --command=read --replay --test-version=5.0.0 \
  --step-name=canary-resume \
  --fixture=$CDC/fixtures/sql/00-init-cdc.sql \
  --fixture=$CDC/fixtures/sql/canary-resume-seed.sql \
  --mutate=$CDC/fixtures/sql/canary-resume-mutate.sql \
  --config-template=$CDC/fixtures/configs/cdc.template.json \
  --catalog=$CDC/fixtures/catalogs/resume-canary-cdc.json \
  --keep-backend
```

Artifacts land under `${REPRO_OUT:-/tmp/source-mssql-repro}/<step-name>/`
with the layout the generic skill documents.

A `repro-*.sh` driver is responsible for:

1. Calling
   `$GENERIC/scripts/apply-sql.sh fixtures/sql/<00-init-cdc.sql + per-bug.sql>`.
2. Calling `$GENERIC/scripts/render-config.sh` to produce a working
   config under `$REPRO_OUT/working/`.
3. Calling `$GENERIC/scripts/run-protocol-cmd.sh <command> <step-name>
<version>` with the right `--config-path` /
   `--catalog-path` / `--state-path` / `--enable-debug-logs=True`.
4. Asserting on `$REPRO_OUT/<step-name>/stdout.txt` or `stderr.txt`.
   Exit `0` on PASS, non-zero with a `FAIL:` message on FAIL.

## Tear-down

Both shapes leave the backend running, so tear down explicitly:

```bash
"$GENERIC/scripts/stop-backend.sh"   # idempotent
rm -rf "${REPRO_OUT:-/tmp/source-mssql-repro}"
```

## Worked examples

### airbytehq/oncall#12162 — whitespace in stream name

`scripts/repro-12162.sh`. Creates `dbo.[Order Items]` (note the space),
enables CDC on it, and runs `read` against it. Expected outcome: the
read exits non-zero and `stderr.txt` contains
`io.debezium.DebeziumException: Connector configuration is not valid.
The 'message.key.columns' value is invalid: dbo.Order Items:id has an
invalid format`.

Root cause: `MsSqlServerDebeziumOperations.buildMessageKeyColumns()`
joins `schema.table:pkcol` strings without filtering or escaping
identifiers that contain whitespace or `:`, and Debezium rejects them
at engine startup. Fix: pre-filter such streams (Debezium falls back
to the table's native PK from system tables).

### airbytehq/oncall#12094 — schema-history bloat

`scripts/repro-12094.sh`. Creates 30 noise tables in `dbo` (CDC not
enabled on them), runs the baseline `read` against `dbo.users`, and
greps `stderr.txt` for "Adding table CdcTest.dbo.\* to the list of
capture schema tables" lines. Expected outcome: at least 30 such
lines, even though the configured catalog has a single stream.

Root cause: `withSchemaHistory()` in the bulk-CDK Debezium properties
sets `schema.history.internal.store.only.captured.databases.ddl=true`
but not `…captured.tables.ddl=true`. Same harness reproduces equivalent
behavior on `source-mysql` and `source-postgres` because the property
lives in the bulk-CDK `extract-cdc` toolkit.

### airbytehq/oncall#11451 — LSN-range regression in 4.3.4+

`scripts/repro-11451.sh`. Captures a baseline state from a clean read,
generates noise commits, scans CDC, then runs
`sys.sp_cdc_cleanup_change_table` with a `low_water_mark` past the
saved LSN. Re-runs `read` against `4.3.4` (the first version with the
new per-instance LSN-range check) passing the stale state file.
Expected outcome: the read exits non-zero with "Saved offset no longer
present on the server, please reset the connection. Saved LSN '…' is
no longer available in SQL Server transaction logs."

Root cause: pre-`4.3.4` the LSN-range query computed `min` via
`sys.fn_cdc_get_min_lsn('')`, which always returns
`0x00000000000000000000`. `4.3.4` swapped to
`MIN(sys.fn_cdc_get_min_lsn(capture_instance)) FROM cdc.change_tables`,
which returns the actual per-instance min — a value that can advance
past a saved offset on geo-replicas with aggressive cleanup. The
saved-offset-rejection guard then fires even though the data is
still present. Investigation lives at
[`airbytehq/oncall#11451`](https://github.com/airbytehq/oncall/issues/11451).

### Snapshot-then-changes CDC canary

`scripts/canary-resume.sh` proves the generic harness's replay protocol:
it reads the seeded `resume_canary` table, saves the first STATE, applies
one update, one delete, and one insert, then reads again from that state.
The driver asserts that the second read contains exactly those three
record IDs and that the Debezium global `commit_lsn` advances between the
two saved states.

## Authoring a new repro

1. Drop a SQL fixture in `fixtures/sql/repro-<issue-number>-<slug>.sql`.
2. (Optional) Drop a CDC-aware catalog in `fixtures/catalogs/`.
3. Drop a driver script in `scripts/repro-<issue-number>.sh` modeled on
   the existing ones. Inline assertions; `set -euo pipefail`; default
   `VERSION=4.4.2` with a `${VERSION:-…}` override.
4. Verify locally:
   ```bash
   "$GENERIC/scripts/start-backend.sh"
   "$SKILL/scripts/repro-<issue-number>.sh"
   "$GENERIC/scripts/stop-backend.sh"
   ```
5. Note the worked example in this `SKILL.md`'s "Worked examples"
   section with: customer-symptom one-liner, expected
   exit-code / stderr substring, root-cause one-liner.
