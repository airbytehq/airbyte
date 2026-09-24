---
name: source-mysql-e2e-cdc-tests
description: Reproduce MySQL binlog CDC behavior against a local MySQL backend with CDC-aware fixtures, catalogs, and smoke cases. Composes on source-mysql-e2e-tests and db-harness-lib.
---

# source-mysql-e2e-cdc-tests

Local CDC test harness for `source-mysql`. It builds on the
engine-independent orchestration in
[`airbyte-integrations/db-harness-lib/`](../../../../../db-harness-lib/) and
the generic MySQL skill
([`source-mysql-e2e-tests`](../source-mysql-e2e-tests/SKILL.md)). The generic
skill starts a MySQL 8.0 backend and runs the connector; this skill supplies
the binlog CDC config, CDC catalog, SQL fixtures, and case scripts.

MySQL CDC is binlog-based and server-wide. The generic backend already starts
MySQL with ROW binlogging, full row images, and GTIDs, so this skill does not
enable CDC per table or start a second backend.

## When to use this skill

- Reproducing a CDC-mode `source-mysql` bug locally.
- Verifying a fix with a published connector image or `VERSION=dev` after
  building the connector locally.
- Running the initial-load and incremental-replay smoke cases.
- Authoring a new MySQL CDC repro with an idempotent SQL fixture and a case
  script that invokes the generic skill's `scripts/run.sh`.

## Prerequisites

Same as the generic skill:

- Docker, `uv`, `jq`, and a clone of `airbytehq/airbyte`.
- The backend container `source-mysql-db-backend`, started by
  `../source-mysql-e2e-tests/scripts/start-backend.sh`.

You do not need GSM or Cloud admin credentials. Never run this harness against
a customer connection or Airbyte Cloud.

## Layout

```
source-mysql-e2e-cdc-tests/
├── SKILL.md
├── cases/
│   ├── initial-load.sh             # CDC initial-load smoke case
│   └── incremental-replay.sh       # read → mutate → read-with-state smoke case
└── fixtures/
    ├── configs/
    │   └── cdc.template.json       # CDC replication config
    ├── catalogs/
    │   └── users-cdc.json          # users stream with MySQL CDC metadata
    └── sql/
        ├── 00-init-cdc.sql         # dedicated cdc_test database and rows
        └── mutate-insert-users.sql # row inserted between replay phases
```

`extract-state.py` is implemented in
[`airbyte-integrations/db-harness-lib/scripts/extract-state.py`](../../../../../db-harness-lib/scripts/extract-state.py);
it extracts protocol-level STATE messages and is not engine-specific.

## Conventions

- Cases reuse the generic backend and pass `--keep-backend`. Start it once at
  the top of a session, run the cases, and tear it down when finished.
- The generic MySQL backend starts with `--log-bin`, `--binlog-format=ROW`,
  `--binlog-row-image=FULL`, `--gtid-mode=ON`, and
  `--enforce-gtid-consistency=ON`. Do not add per-table CDC enable steps or
  engine-specific backend startup to this skill.
- `00-init-cdc.sql` drops and recreates the dedicated `cdc_test` database on
  every application. Re-applying it wipes existing rows and any accumulated
  binlog-relative table state, which is why `cases/incremental-replay.sh`
  passes `--skip-fixtures` on its second phase.
- CDC catalogs include the bulk-CDK fields (`is_file_based`,
  `generation_id`, `minimum_generation_id`, `sync_id`,
  `destination_object_name`, and `include_files`) and use
  `["_ab_cdc_cursor"]` as the cursor field.
- Cases default to `VERSION=3.53.4`, the current published image used by this
  harness. Override it with `VERSION=dev` after building a local image.
- Assertions are declarative `run.sh` expectations. The runner enforces
  `--expect-test`, `--expect-match`, `--forbid-match`, `--min-records`, and
  `--min-states` before returning.
- Multi-phase cases extract the latest STATE message with the shared
  `extract-state.py` and pass it to the next invocation with `--state=PATH`.

## Usage

```bash
SKILL=airbyte-integrations/connectors/source-mysql/.agents/skills/source-mysql-e2e-cdc-tests
GENERIC=airbyte-integrations/connectors/source-mysql/.agents/skills/source-mysql-e2e-tests
LIB=airbyte-integrations/db-harness-lib
export REPRO_OUT=/tmp/source-mysql-repro

# Start the binlog-ready backend once.
"$GENERIC/scripts/start-backend.sh"

# Run either smoke case. Both pass --keep-backend.
"$SKILL/cases/initial-load.sh"
"$SKILL/cases/incremental-replay.sh"

# Use a locally built connector image after a code change.
VERSION=dev "$SKILL/cases/initial-load.sh"

# Tear down after the session.
BACKEND_NAME=source-mysql-db-backend \
  "$LIB/scripts/stop-backend.sh"
```

Prefer a published target image for code on a pushed PR branch. Publish a
pre-release with the Airbyte Ops MCP tool
`publish_connector_to_airbyte_registry`, then pass the resulting
`<version>-preview.<7-char-sha>` tag as `--test-version`. See
[Getting a target image](../../../../../db-harness-lib/README.md#getting-a-target-image)
for details. Use `--test-version=dev` only for code that is not on a pushed
PR branch.

Each case invokes the generic skill's engine shim, which delegates to
`airbyte-integrations/db-harness-lib/scripts/run.sh`. The runner applies the
fixture, renders the config, runs the requested connector command, stores
artifacts under `$REPRO_OUT/<step-name>/`, and enforces the case assertions.

## Worked examples

### Initial CDC load

`cases/initial-load.sh` applies `00-init-cdc.sql` and reads the configured
`users` stream with `cdc.template.json` and `users-cdc.json`. It asserts a
passing read with at least three records and one STATE message. This verifies
that the binlog-ready backend, CDC config, catalog metadata, and initial load
work together.

### Incremental replay

`cases/incremental-replay.sh` runs a baseline read, extracts its STATE message,
inserts `dave@example.com`, and replays from the saved state without
re-applying fixtures. It asserts a passing replay containing
`dave@example.com` and no `alice@example.com`, proving that the saved binlog
position resumes after the initial load.

These are smoke canaries, not per-bug reproductions. No MySQL CDC fixtures or
worked per-bug examples existed before this skill.

## Authoring a new repro

1. Add an idempotent SQL fixture under `fixtures/sql/`. Keep any CDC database
   setup dedicated to the fixture and do not add per-table CDC enable steps.
2. Add a CDC-aware catalog under `fixtures/catalogs/` when the case needs a
   stream shape not covered by `users-cdc.json`.
3. Add `cases/<name>.sh` with `set -euo pipefail`, a `${VERSION:-3.53.4}`
   default, and a call to the generic skill's `scripts/run.sh`. Pass
   `--config-template`, `--catalog`, `--fixture`, `--keep-backend`, and the
   relevant `--expect-*` flags.
4. For a multi-phase case, model the sequence on
   `cases/incremental-replay.sh`: baseline `read`, extract STATE from
   `$REPRO_OUT/<step>/read/stdout.txt`, mutate through the generic
   `apply-sql.sh`, then run with `--skip-fixtures --state=PATH`.
5. Verify the case against a published image or `VERSION=dev`, inspect its
   artifacts, and keep the backend lifecycle in the generic skill.

The generic `apply-sql.sh` uses the plain MySQL client on stdin, so fixtures
may contain multiple statements. The MySQL server's binlog and GTID settings
are established when the generic backend starts; no additional CDC setup is
needed in a case.
