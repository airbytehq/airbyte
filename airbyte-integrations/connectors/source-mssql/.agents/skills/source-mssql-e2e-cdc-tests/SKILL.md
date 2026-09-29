---
name: source-mssql-e2e-cdc-tests
description: Reproduce CDC bugs against source-mssql by enabling CDC on the local SQL Server backend, applying per-bug SQL fixtures, and running the connector via airbyte-ops. Composes on top of source-mssql-e2e-tests. Worked examples for airbytehq/oncall#11451, #12094, and #12162 ship with the skill.
---

# source-mssql-e2e-cdc-tests

Local CDC bug-reproduction harness for `source-mssql`. Builds on the
engine-independent orchestration in
[`airbyte-integrations/db-harness-lib/`](../../../../../db-harness-lib/) and
the MSSQL engine skill
([`source-mssql-e2e-tests`](../source-mssql-e2e-tests/SKILL.md)):
generic skill stands up the SQL Server backend and runs the connector;
this skill adds CDC enable, CDC-aware config / catalog templates, and
per-bug **case scripts** under `cases/` that call `run.sh` with the
appropriate fixtures and `--expect-*` assertions.

## When to use this skill

- Reproducing a CDC-mode bug against `source-mssql` locally.
- Verifying a fix by re-running an existing case with
  `VERSION=dev ./cases/<id>.sh` (after `:dockerBuildx`).
- Verifying that a fix which _loosens_ CDC offset validation still
  rejects genuinely invalid state — `cases/11451.sh` is the
  invalid-state case for LSN availability; see
  [Invalid-state case](#invalid-state-case-for-lsn-availability-fixes).
- Authoring a new repro for a customer-reported CDC bug. Drop a SQL
  fixture under `fixtures/sql/` and a `cases/<issue-number>.sh` script
  that invokes `run.sh` with the right fixtures and `--expect-*`
  assertions.

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
├── cases/
│   ├── 11451.sh                      # airbytehq/oncall#11451 — LSN-range regression in 4.3.4+ (multi-phase; invalid-state case)
│   ├── 12094.sh                      # airbytehq/oncall#12094 — schema-history bloat
│   └── 12162.sh                      # airbytehq/oncall#12162 — whitespace in stream name
└── fixtures/
    ├── configs/
    │   └── cdc.template.json
    ├── catalogs/
    │   ├── users-cdc.json
    │   └── order-items-cdc.json
    └── sql/
        ├── 00-init-cdc.sql
        ├── repro-11451-lsn-cleanup.sql
        ├── repro-12094-schema-history.sql
        └── repro-12162-spaces-in-name.sql
```

`extract-state.py` is implemented in
[`airbyte-integrations/db-harness-lib/scripts/extract-state.py`](../../../../../db-harness-lib/scripts/extract-state.py);
it walks Airbyte STATE messages, which is protocol-level and not
CDC-specific.

## Conventions

- Cases keep the backend up across invocations (`--keep-backend`).
  Start the backend once at the top of a session, run any subset of
  cases, tear down when done — see the Usage section below.
- Fixtures are re-applied at the start of each `run.sh` invocation, so
  they must be idempotent (`00-init-cdc.sql` uses `IF DB_ID(...) IS NULL`
  guards, per-bug fixtures use similar shape). Re-applying a fixture
  during a multi-phase case does not reset the CDC state that the
  previous phase established.
- Configured catalogs populate the bulk-CDK-required fields
  (`is_file_based`, `generation_id`, `minimum_generation_id`,
  `sync_id`, `destination_object_name`, `include_files`) so the same
  fixtures drive repros across `source-mssql:4.3.x` and `4.4.x`.
- Cases default `VERSION=4.4.2` (except `11451.sh` which splits into
  `BASELINE_VERSION`/`TARGET_VERSION`). Override with
  `VERSION=4.3.4 ./cases/12162.sh` to test against an earlier version,
  or `VERSION=dev` after a local
  `./gradlew :airbyte-integrations:connectors:source-mssql:dockerBuildx`
  to test a fix.
- **Assertions** are declarative via `run.sh`'s expectation flags:
  `--expect-test`, `--expect-match=[<command>:]<channel>:<regex>[:N]`,
  `--forbid-match`, `--min-records`, `--min-states`. The runner
  enforces them and exits non-zero on any failure. The `<command>:`
  prefix defaults to `read` when omitted; set it explicitly
  (`check:stderr:…`, `discover:stderr:…`) for check-time or
  discover-time signatures.
- Multi-phase cases (`11451.sh`, and any future read → mutate →
  read-with-state repros) capture Airbyte STATE messages between reads
  via the shared
  [`extract-state.py`](../../../../../db-harness-lib/scripts/extract-state.py)
  (`uv`-PEP-723 standalone; pass `<stdout.txt>` as its argument or pipe
  stdin) and feed the file back into the second read with
  `run.sh --state=PATH`.
  Use `--step-name=<bug>/<phase>` to give each phase its own artifact
  subtree.

## Usage

```bash
SKILL=airbyte-integrations/connectors/source-mssql/.agents/skills/source-mssql-e2e-cdc-tests
GENERIC=airbyte-integrations/connectors/source-mssql/.agents/skills/source-mssql-e2e-tests
LIB=airbyte-integrations/db-harness-lib
export REPRO_OUT=/tmp/source-mssql-repro

# 1. Bring up the backend (once per session). Cases pass --keep-backend,
#    so they don't tear it down between runs.
"$GENERIC/scripts/start-backend.sh"

# 2. Run any case. Each case's --expect-* flags gate its own exit code
#    (non-zero on any expectation failure), so bash's `set -e` will fail
#    the sequence on the first failing case if you chain them.
"$SKILL/cases/12162.sh"
"$SKILL/cases/12094.sh"
"$SKILL/cases/11451.sh"

# 3. (After fix) verify by retargeting `dev` or a fixed version.
VERSION=dev "$SKILL/cases/12162.sh"

# 4. Tear down.
BACKEND_NAME=source-mssql-db-backend "$LIB/scripts/stop-backend.sh"
rm -rf "$REPRO_OUT"
```

Each case is a shell script that composes `run.sh` invocations:

1. Applies its SQL fixtures (via `--fixture=…`; `run.sh` calls
   `apply-sql.sh` internally).
2. Renders the config against the running backend (via
   `--config-template=…`).
3. Runs the target protocol command with any `--catalog` / `--state`.
4. Gates its exit code on `--expect-*` flags — the runner enforces
   them and exits non-zero on any failure, so the case script has no
   inline assertion logic to maintain.

Multi-phase cases (`11451.sh`) call `run.sh` more than once, with
`extract-state.py` and `apply-sql.sh` between invocations. Each phase
uses `--step-name=<bug>/<phase>` to keep its artifacts separate under
`$REPRO_OUT/<bug>/<phase>/`.

## Worked examples

### airbytehq/oncall#12162 — whitespace in stream name

`cases/12162.sh`. Creates `dbo.[Order Items]` (note the space), enables
CDC on it, and runs `read` against it. Case asserts
`--expect-test=fail`, `--expect-match=stderr:io.debezium.DebeziumException`,
and `--expect-match=stderr:message.key.columns` — i.e. the read exits
non-zero and Debezium's `stderr.txt` contains its
`Connector configuration is not valid. The 'message.key.columns' value
is invalid` rejection.

Root cause: `MsSqlServerDebeziumOperations.buildMessageKeyColumns()`
joins `schema.table:pkcol` strings without filtering or escaping
identifiers that contain whitespace or `:`, and Debezium rejects them
at engine startup. Fix: pre-filter such streams (Debezium falls back
to the table's native PK from system tables).

### airbytehq/oncall#12094 — schema-history bloat

`cases/12094.sh`. Creates 30 noise tables in `dbo` (CDC not enabled on
them), runs the baseline `read` against `dbo.users`, and asserts
`--expect-match='stdout:Adding table CdcTest\..* to the list of capture schema tables:30'`
(the trailing `:30` is the count threshold; the fixture creates 30
noise tables). Adjust with `MIN_LOADED=<N>`. Expected outcome: at
least 30 "Adding table" lines even though the configured catalog has
a single stream.

Root cause: `withSchemaHistory()` in the bulk-CDK Debezium properties
sets `schema.history.internal.store.only.captured.databases.ddl=true`
but not `…captured.tables.ddl=true`. Same harness reproduces equivalent
behavior on `source-mysql` and `source-postgres` because the property
lives in the bulk-CDK `extract-cdc` toolkit.

### airbytehq/oncall#11451 — LSN-range regression in 4.3.4+

`cases/11451.sh`. Multi-phase:

1. Baseline `read` on clean CdcTest (`BASELINE_VERSION`, default `4.4.2`).
   Case asserts `--expect-test=pass --min-states=1` so a missing STATE
   fails the case immediately rather than later at replay.
2. `extract-state.py` on the baseline stdout, then
   `apply-sql.sh repro-11451-lsn-cleanup.sql` runs
   `sys.sp_cdc_cleanup_change_table`
   with a `low_water_mark` past the saved LSN — advancing
   `fn_cdc_get_min_lsn('dbo_users')` past the baseline offset.
3. Replay `read` on `TARGET_VERSION` (default `4.3.4`) with the stale
   state. Case asserts `--expect-test=fail`,
   `--expect-match=stderr:Saved offset no longer present`, and
   `--expect-match='stderr:is no longer available in SQL Server transaction logs'`.

Root cause: pre-`4.3.4` the LSN-range query computed `min` via
`sys.fn_cdc_get_min_lsn('')`, which always returns
`0x00000000000000000000`. `4.3.4` swapped to
`MIN(sys.fn_cdc_get_min_lsn(capture_instance)) FROM cdc.change_tables`,
which returns the actual per-instance min — a value that can advance
past a saved offset on geo-replicas with aggressive cleanup. The
saved-offset-rejection guard then fires even though the data is
still present. Investigation lives at
[`airbytehq/oncall#11451`](https://github.com/airbytehq/oncall/issues/11451).

#### Invalid-state case for LSN-availability fixes

This case's Phase 3 is a _genuinely_ expired saved offset: Phase 2
advances `fn_cdc_get_min_lsn` past the captured LSN, so rejecting the
replay is the correct behavior, not the bug. That makes it the
invalid-state counterpart to any repro built around a saved LSN that is
still valid — for example an unauthorized capture instance returning
`0x0` and poisoning
`MIN(sys.fn_cdc_get_min_lsn(capture_instance))`.

So when a change relaxes what the offset-availability check aggregates
or tolerates, run this case against the image built from that change:

```bash
TARGET_VERSION=dev "$SKILL/cases/11451.sh"
```

It must still fail with the same two `stderr` signatures the case
asserts on. A pass here means the guard stopped firing on state it is
supposed to reject, which turns an actionable "reset the connection"
error into a silently incomplete sync — the symptom-gone evidence from
the valid-LSN repro cannot distinguish that from a correct fix.

## Authoring a new repro

1. Drop a SQL fixture in `fixtures/sql/repro-<issue-number>-<slug>.sql`.
   Make it idempotent (`IF NOT EXISTS` guards for `CREATE`,
   `IF EXISTS` guards for `DROP`) — cases re-apply fixtures on every
   `run.sh` invocation.
2. (Optional) Drop a CDC-aware catalog in `fixtures/catalogs/`.
3. Drop a case script in `cases/<issue-number>.sh` modeled on the
   existing ones. `set -euo pipefail`; default `VERSION=4.4.2` with a
   `${VERSION:-…}` override; invoke `run.sh` with the right
   `--command`, `--fixture=`, `--config-template=`, `--catalog=`, and
   `--expect-*` flags. Pass `--keep-backend` so the shared-session
   Usage flow works. For check-time or discover-time signatures, use
   `--expect-match=check:stderr:…` / `--expect-match=discover:stderr:…`
   (the `<command>:` prefix defaults to `read` when omitted).
4. Verify locally:
   ```bash
   "$GENERIC/scripts/start-backend.sh"
   "$SKILL/cases/<issue-number>.sh"
   BACKEND_NAME=source-mssql-db-backend "$LIB/scripts/stop-backend.sh"
   ```
5. Note the worked example in this `SKILL.md`'s "Worked examples"
   section with: customer-symptom one-liner, `--expect-*` assertions
   the case gates on, root-cause one-liner.

### Multi-phase repros

When the reproduction is single-phase (one `run.sh` invocation is
enough to trigger the bug), follow the recipe above. Reach for a
multi-phase shape only when the bug needs an intermediate mutation
that depends on state from a first read — the canonical example is
read → extract STATE → mutate the server based on that STATE → replay
with the stale STATE. Model on [`cases/11451.sh`](cases/11451.sh) —
the three primitives it composes are:

- **`--step-name=<bug>/<phase>`** — per-phase artifact dirs under
  `$REPRO_OUT/<bug>/`. `cases/11451.sh` uses `11451/baseline` and
  `11451/stale`; a new case would use its own bug number and phase
  names.
- **`extract-state.py`** (implemented in `db-harness-lib`) — reads a phase's
  `read/stdout.txt` and emits a JSON array of AirbyteStateMessage
  objects, which is what `run.sh --state=PATH` expects.
- **`--skip-fixtures`** on the second/later `run.sh` invocation —
  opts out of the initial-fixture reapply so the intermediate state
  the previous phase established survives. Otherwise `run.sh`'s
  default fixture-application would re-run `00-init-cdc.sql`, which
  drops and recreates `CdcTest` and wipes the mutation. Rejects
  `--fixture=` in the same invocation (either apply fixtures or skip
  them).

The between-phase mutation itself is a plain `apply-sql.sh` call
against a fixture in `fixtures/sql/`. Nothing about the mutation is
special-cased in `run.sh` — the case script drives the sequencing.
