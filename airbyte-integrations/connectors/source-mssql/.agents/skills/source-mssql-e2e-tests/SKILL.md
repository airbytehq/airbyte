---
name: source-mssql-e2e-tests
description: Stand up a local SQL Server 2022 backend, apply SQL fixtures, and sweep the Airbyte protocol commands (spec → check → discover → read) against airbyte/source-mssql:<tag> for ad-hoc end-to-end testing. Use when you need a deterministic, throwaway local environment for any source-mssql test or repro that is not CDC-specific.
---

# source-mssql-e2e-tests

Local end-to-end test harness for `source-mssql`. The engine-independent
orchestration lives in
[`airbyte-integrations/db-harness-lib/`](../../../../db-harness-lib/);
this skill keeps the MSSQL backend lifecycle scripts, fixtures, and config
templates. It stands up a SQL Server
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
│   ├── apply-sql.sh            # docker cp + docker exec sqlcmd -i
│   ├── reset-databases.sh      # docker exec sqlcmd → drop every non-system database (used by run.sh --reset=fixture)
│   └── run.sh                  # engine shim to db-harness-lib orchestration
└── fixtures/
    ├── configs/
    │   └── base.template.json  # non-CDC config; host=mssql-db-backend placeholder
    └── sql/
        ├── .gitignore          # `.tmp/` — subtree for uncommitted per-bug scratch fixtures
        └── 00-init-base.sql    # CREATE DATABASE TestDb + dbo.sample table
```

The engine shim and backend lifecycle scripts remain in this skill's
`scripts/` directory; the shared orchestration, default teardown, and
protocol helpers live in
[`airbyte-integrations/db-harness-lib/`](../../../../../db-harness-lib/).
The skill expects all script paths relative to the skill root.

## Conventions

- Container name: `source-mssql-db-backend`. Hard-coded in
  `scripts/start-backend.sh` and `apply-sql.sh`. The shared
  `db-harness-lib/scripts/stop-backend.sh` removes this container by
  `BACKEND_NAME`; the engine shim supplies the default. Override via
  `BACKEND_NAME=…` only for parallel test isolation; don't use customer
  connection names.
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
  resolves the backend by its bridge IP, which the shared
  [`render-config.sh`](../../../../../db-harness-lib/scripts/render-config.sh)
  substitutes into the working config at runtime. Tracked upstream in
  [`airbytehq/airbyte-ops-mcp#765`](https://github.com/airbytehq/airbyte-ops-mcp/issues/765);
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

# Target vs. control comparison, non-CDC (airbyte-ops's built-in comparator).
poe e2e-local --test-version=dev --control-version=5.0.0 \
  --fixture=.agents/skills/source-mssql-e2e-tests/fixtures/sql/00-init-base.sql

# Target vs. control comparison, CDC (per-image reset between the two runs).
poe e2e-local --test-version=dev --control-version=5.0.0 --reset=fixture \
  --fixture=.agents/skills/source-mssql-e2e-cdc-tests/fixtures/sql/00-init-cdc.sql \
  --fixture=.agents/skills/source-mssql-e2e-cdc-tests/fixtures/sql/<per-bug>.sql

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

Prefer a published tag over `--test-version=dev`: for code on a pushed PR
branch, publish a pre-release and pass its `<version>-preview.<sha>` tag,
which skips the Gradle build and gives reviewers a tag they can re-run
against — see
[Getting a target image](../../../AGENTS.md#getting-a-target-image). When
you do use `--test-version=dev`, build the target image first, or pass
`--build` to have `run.sh` run `:dockerBuildx` for you. Other options:
`--command=spec|check|discover|read` (default `all`), `--skip-read`,
`--skip-fixtures` (run against whatever state the backend already has;
for the second/later `run.sh` invocation of a multi-phase driver, when
re-applying the initial fixture would wipe intermediate state),
`--step-name`, `--catalog` (skip discover-derived generation),
`--state=PATH` (pass a saved STATE file to the read as `--state-path`;
for use by multi-phase drivers), `--sync-mode=incremental`,
`--cursor-field`, `--streams`, `--config-template`,
`--reset=none|fixture|backend`, `--keep-backend`, and `--` to forward
extra args to `airbyte-ops`. Per-command timeouts match the workflow's
(30/30/60/180 minutes) and are overridable with
`TIMEOUT_MINUTES_{SPEC,CHECK,DISCOVER,READ}`.

### Declarative expectations

Instead of driver scripts hand-rolling `grep -q '<substring>' || exit 1`
against each command's artifacts, `run.sh` accepts a small set of
expectation flags that it enforces itself before returning:

| Flag                                               | Effect                                                                                                                                                                                                                             |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--expect-test=pass\|fail`                         | Overall target verdict. `pass` = every executed command's status was `pass`; `fail` = one or more failed.                                                                                                                          |
| `--expect-control=pass\|fail`                      | Same for the control sweep (comparison-mode runs only; requires `--control-version`).                                                                                                                                              |
| `--min-records=N`                                  | Target read's `stdout.txt` must contain ≥N `RECORD` messages.                                                                                                                                                                      |
| `--min-states=N`                                   | Target read's `stdout.txt` must contain ≥N `STATE` messages.                                                                                                                                                                       |
| `--expect-match=[<command>:]<channel>:<regex>[:N]` | Target's `<command>` step's `<channel>` (`stdout` \| `stderr` \| `any`) must match `<regex>` at least N times (default 1). `<command>` (`spec` \| `check` \| `discover` \| `read`) is optional and defaults to `read`. Repeatable. |
| `--forbid-match=[<command>:]<channel>:<regex>`     | Same shape but must match zero times. Repeatable.                                                                                                                                                                                  |

All match assertions run against the **target-side** artifacts of the
named command (or `read` if no `<command>` prefix). Under
`--control-version + --reset=none` those live at
`$ARTIFACTS_DIR/<command>/target/` (created by airbyte-ops's comparison
mode); under `--reset=fixture|backend` at
`$ARTIFACTS_DIR/target/<command>/`; under single-version at
`$ARTIFACTS_DIR/<command>/`. `run.sh` picks the right path automatically.

The match-spec grammar disambiguates the leading `<command>:` from the
`<channel>:` on the first colon-separated field (command names and
channel names don't overlap), and strips a trailing `:N` only when the
last field is a positive integer. So a regex containing `:` still
parses: `--expect-match=stderr:io.debezium.DebeziumException` reads as
command `read` (default), channel `stderr`, regex
`io.debezium.DebeziumException`, count 1. `--expect-match=check:stderr:should be positive`
reads as command `check`, channel `stderr`, regex `should be positive`,
count 1.

`--min-records` and `--min-states` are read-step only — they count
RECORD / STATE envelopes, which are read-specific — and have no
`<command>:` prefix.

Any expectation failure exits non-zero regardless of the command-level
verdicts and appends an `**Expectation failures:**` section to the
summary. Migrating an existing driver script's `grep -q '<X>' || exit 1`
block is straightforward — drop the block and add
`--expect-match=stderr:X` to the shared `run.sh` invocation.

### Multi-phase drivers

`run.sh` runs one sweep. A driver script composes multi-phase flows
(read → mutate → read-with-state) by calling `run.sh` more than once
with `--step-name` for each invocation and `--state=` to feed the
second read the state extracted from the first. `extract-state.py`
lives in
[`airbyte-integrations/db-harness-lib/scripts/extract-state.py`](../../../../../db-harness-lib/scripts/extract-state.py)
because it walks Airbyte STATE messages, which is a protocol-level
operation and not CDC-specific.

The CDC skill's [`cases/11451.sh`](../source-mssql-e2e-cdc-tests/cases/11451.sh)
is a worked example: it invokes the engine shim's `run.sh` around an
intermediate `apply-sql.sh` mutation and the shared
`db-harness-lib/scripts/extract-state.py` step, and asserts on the
connector's stderr. New multi-phase drivers can follow the same shape
but call `run.sh --state=PATH` directly instead of smuggling
`--state-path` through trailing args.

### Comparison modes with `--control-version`

- **`--reset=none` (default)** — `run.sh` invokes `airbyte-ops` once per
  protocol command with both `--test-image` and `--control-image`, so
  the two images run sequentially against a single backend and
  `airbyte-ops`'s built-in comparators emit the target-vs-control diff
  (record counts, primary keys, per-record, schema). Right for non-CDC
  full-refresh work: the diff is meaningful and the shared-backend
  assumption is safe because a full-refresh read does not mutate the
  upstream. This is the current behavior for any caller that doesn't
  set `--reset`.
- **`--reset=fixture`** — `run.sh` runs the whole sweep against the
  control image first, drops every non-system database, re-applies the
  fixtures, then runs the sweep against the target image. Two
  single-version `airbyte-ops` calls, no built-in comparator; artifacts
  land under `$REPRO_OUT/<step-name>/{control,target}/<command>/`.
  Right for **CDC comparisons**, where reusing the backend leaves the
  target reading against a warm capture instance and an advanced log
  position — the built-in diff can look clean while being meaningless.
  The SQL Server log-LSN clock is server-wide and keeps ticking across
  the reset, so per-record LSN columns and STATE offsets still differ
  between runs; gate the verdict on record-level shape rather than on
  those values.
- **`--reset=backend`** — same as `--reset=fixture` but also recreates
  the backend container between the two sweeps, resetting the LSN clock
  at ~15s of extra startup cost. Use only when the reproduction depends
  on matching LSN sequences across runs.

`--reset` has no effect without `--control-version` and produces a
warning; the flag governs the reset between two image runs, and there
is no second run in single-version mode.

## Asserting on output

Inline assertions in driver scripts. Suggested helpers:

- Exit code: check `$?` immediately after the call.
- AirbyteMessage shape: `jq -e 'select(.type == "RECORD")' $REPRO_OUT/<step>/read/stdout.txt`.
- Connector-side log shape: `grep -c '<expected substring>' $REPRO_OUT/<step>/read/stderr.txt`.
- Connection status: `jq -e 'select(.type == "CONNECTION_STATUS" and .connectionStatus.status == "SUCCEEDED")' $REPRO_OUT/<step>/check/stdout.txt`.

In comparison mode with `--reset=none` each command's directory holds
`target/` and `control/` subdirectories (created by `airbyte-ops`).
With `--reset=fixture|backend` the split lives one level up:
`$REPRO_OUT/<step-name>/{control,target}/<command>/`.

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
LIB=airbyte-integrations/db-harness-lib
BACKEND_NAME=source-mssql-db-backend "$LIB/scripts/stop-backend.sh"   # idempotent; docker rm -f no-ops when absent
rm -rf "${REPRO_OUT:-/tmp/source-mssql-repro}"
```
