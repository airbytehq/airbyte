---
name: source-mysql-e2e-tests
description: Stand up a local MySQL 8.0 backend, apply SQL fixtures, and sweep the Airbyte protocol commands (spec → check → discover → read) against airbyte/source-mysql:<tag> for ad-hoc end-to-end testing. Use when you need a deterministic, throwaway local environment for any source-mysql test or prove-fix comparison.
---

# source-mysql-e2e-tests

Local end-to-end test harness for `source-mysql`. The engine-independent
orchestration lives in
[`airbyte-integrations/db-harness-lib/`](../../../../../db-harness-lib/);
this skill keeps the MySQL backend lifecycle scripts, fixtures, and config
templates. It stands up a MySQL 8.0 container named
`source-mysql-db-backend`, lets you apply arbitrary SQL fixtures, and runs
Airbyte protocol commands against any `airbyte/source-mysql:<tag>` image via
`airbyte-ops cloud connector regression-test`.

## When to use this skill

- Reproducing a `source-mysql` bug locally.
- Sweeping `spec` → `check` → `discover` → `read`, or running one of
  them, against any `airbyte/source-mysql:<tag>` for connector
  development.
- Proving a fix by comparing a target image with a control image.

## Prerequisites

- Docker.
- [`uv`](https://docs.astral.sh/uv/). `uv tool install
airbyte-internal-ops` puts `airbyte-ops` on `$PATH`; alternatively prefix
  every call with `uvx airbyte-internal-ops`.
- `jq`.
- A clone of `airbytehq/airbyte`.

You do not need GSM or Cloud admin credentials. Local-only mode (no
`--connection-id`) reads everything from local files.

## Layout

```
source-mysql-e2e-tests/
├── SKILL.md
├── scripts/
│   ├── start-backend.sh        # docker run mysql:8.0 with ROW binlog + GTIDs
│   ├── apply-sql.sh            # docker exec mysql on stdin
│   ├── reset-databases.sh      # drop and recreate non-system databases
│   └── run.sh                  # engine shim to db-harness-lib orchestration
└── fixtures/
    ├── configs/
    │   └── base.template.json  # STANDARD config; host placeholder
    └── sql/
        └── 00-init-base.sql    # sample table with three rows
```

The engine shim and lifecycle scripts remain in this skill's `scripts/`
directory; the shared orchestration and protocol helpers live in
[`airbyte-integrations/db-harness-lib/`](../../../../../db-harness-lib/).
The skill expects all script paths relative to the skill root.

## Conventions

- Container name: `source-mysql-db-backend`. Hard-coded in the lifecycle
  scripts. Override via `BACKEND_NAME=…` only for parallel test isolation;
  don't use customer connection names.
- Root password: `test_password`. Override with `BACKEND_PASSWORD` when
  running an isolated local backend.
- Initial database: `test_db`. Override with `BACKEND_DB` when using a
  different fixture database.
- Working directory for rendered configs and run output:
  `${REPRO_OUT:-/tmp/source-mysql-repro}`. A `run.sh` invocation writes
  everything under `$REPRO_OUT/<step-name>/`: the rendered `config.json`,
  the derived `configured_catalog.json`, and one subdirectory per protocol
  command (`spec/`, `check/`, `discover/`, `read/`) holding that command's
  `stdout.txt`, `stderr.txt`, `report.md`, and `report.html`.
- Both containers (the MySQL backend and the connector launched by
  `airbyte-ops`) share Docker's default `bridge` network. The connector
  resolves the backend by its bridge IP, which the shared
  [`render-config.sh`](../../../../../db-harness-lib/scripts/render-config.sh)
  substitutes into the working config at runtime. Tracked upstream in
  [`airbytehq/airbyte-ops-mcp#765`](https://github.com/airbytehq/airbyte-ops-mcp/issues/765).
- The backend image is pinned to `mysql:8.0`, not `latest`, for stable
  major-version behavior. Override with `BACKEND_IMAGE=…` for a
  version-specific reproduction.
- The backend starts with ROW-format binary logging, a full row image,
  and GTIDs. This leaves the container ready for a CDC driver without
  restarting it.

## Usage

`scripts/run.sh` is the only supported entrypoint. It performs the whole
sequence — start the backend, apply the fixtures, render the config, run
`spec` → `check` → `discover`, derive the configured catalog from that
`discover` output, run `read`, and tear down on exit:

```bash
cd airbyte-integrations/connectors/source-mysql

# Single version, full sweep.
poe e2e-local --test-version=3.53.3

# Target vs. control comparison, non-CDC.
poe e2e-local --test-version=dev --control-version=3.53.2

# One command only.
poe e2e-local --command=read --test-version=3.53.3
```

The sweep runs every command against the one backend and reports each
result rather than stopping at the first failure, then prints a summary
table and exits non-zero if any command failed. A `read` whose `discover`
failed earlier is reported `SKIPPED`, not `ERROR`. Under CI the table is
also appended to `$GITHUB_STEP_SUMMARY`. A run limited to one command
instead exits with the connector's own exit code.

Prefer a published target image for code on a pushed PR branch. Publish a
pre-release from the PR with the Airbyte Ops MCP tool
`publish_connector_to_airbyte_registry`, then pass the resulting
`<version>-preview.<7-char-sha>` tag as `--test-version`. See
[Getting a target image](../../../../../db-harness-lib/README.md#getting-a-target-image)
for details. Build the target image first when using `--test-version=dev`, or
pass `--build` to have `run.sh` run `:dockerBuildx` for code that is not on a
pushed PR branch. Other options:
`--command=spec|check|discover|read` (default `all`), `--skip-read`,
`--skip-fixtures`, `--step-name`, `--catalog`, `--state=PATH`,
`--sync-mode=incremental`, `--cursor-field`, `--streams`,
`--config-template`, `--fixture`, `--reset=none|fixture|backend`,
`--keep-backend`, and `--` to forward extra args to `airbyte-ops`.
Per-command timeouts match the workflow's (30/30/60/180 minutes) and are
overridable with `TIMEOUT_MINUTES_{SPEC,CHECK,DISCOVER,READ}`.

## Declarative expectations

Instead of driver scripts hand-rolling `grep -q '<substring>' || exit 1`
against command artifacts, `run.sh` accepts expectation flags that it
enforces before returning:

| Flag                                               | Effect                                                                                                       |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `--expect-test=pass\|fail`                         | Overall target verdict.                                                                                      |
| `--expect-control=pass\|fail`                      | Control verdict in comparison mode; requires `--control-version` and `--reset=fixture` or `--reset=backend`. |
| `--min-records=N`                                  | Target read must contain at least N `RECORD` messages.                                                       |
| `--min-states=N`                                   | Target read must contain at least N `STATE` messages.                                                        |
| `--expect-match=[<command>:]<channel>:<regex>[:N]` | Target command output must match the regex at least N times.                                                 |
| `--forbid-match=[<command>:]<channel>:<regex>`     | Target command output must not match the regex.                                                              |

Match assertions use the target-side artifacts for the named command and
default to `read` when no command prefix is supplied. The accepted
channels are `stdout`, `stderr`, and `any`; command names are `spec`,
`check`, `discover`, and `read`.

Any expectation failure exits non-zero and is included in the generated
summary. For example, a driver can replace a `grep` assertion with
`--expect-match=stderr:expected message`.

## Comparison modes with `--control-version`

- **`--reset=none` (default)** — `run.sh` invokes `airbyte-ops` with both
  `--test-image` and `--control-image`, so the images run sequentially
  against one backend and the built-in comparators emit a target-vs-control
  diff. This is appropriate for non-CDC full-refresh work.
- **`--reset=fixture`** — `run.sh` runs the control sweep first, drops every
  non-system database, reapplies the fixtures, and then runs the target
  sweep. Artifacts land under
  `$REPRO_OUT/<step-name>/{control,target}/<command>/`. Use this for CDC
  comparisons so the target does not read a warm capture instance.
- **`--reset=backend`** — like `--reset=fixture`, but recreates the MySQL
  container between sweeps. Use this only when matching binlog or GTID
  sequences matters.

`--reset` has no effect without `--control-version` and produces a warning.
The flag governs the reset between two image runs; there is no second run
in single-version mode.

## Common gotchas

- **CDC needs ROW binlogging.** `start-backend.sh` sets
  `--binlog-format=ROW`, `--binlog-row-image=FULL`, and a server ID.
  The connecting user must have replication privileges; the root user
  created by the fixture has them.
- **MySQL config shapes are specific.** `ssl_mode` uses `preferred`,
  `required`, `verify_ca`, or `verify_identity`; the base config uses
  `preferred` for the local plaintext backend. The
  `replication_method.method` value is `STANDARD` or `CDC`.
- **`tinyint(1)` mapping.** The connector maps `TINYINT(1)` to boolean by
  default. Set `treat_tinyint1_as_integer: true` in a config when
  reproducing a typing issue.
- **The connector resolves the backend by bridge IP.** The shared
  `render-config.sh` substitutes that IP into each rendered config because
  the local regression-test command does not currently accept `--network`.
- **`check` failures may exit zero.** The connector can emit a failed
  `CONNECTION_STATUS` while exiting zero. Assert on the status message when
  a reproduction depends on check-time behavior.
- **Do not use customer connections.** This harness is for local testing
  only and must never be used against customer connections or Airbyte Cloud.

## Teardown

The shared library's default `stop-backend.sh` is idempotent:

```bash
BACKEND_NAME=source-mysql-db-backend \
  airbyte-integrations/db-harness-lib/scripts/stop-backend.sh
rm -rf "$REPRO_OUT"
unset REPRO_OUT
```
