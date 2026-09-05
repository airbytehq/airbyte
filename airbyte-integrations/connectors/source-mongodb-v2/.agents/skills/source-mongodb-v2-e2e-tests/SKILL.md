---
name: source-mongodb-v2-e2e-tests
description: Stand up a local MongoDB 7.0 single-node replica set, apply mongosh JavaScript fixtures, and sweep the Airbyte protocol commands (spec → check → discover → read) against airbyte/source-mongodb-v2:<tag> for ad-hoc end-to-end testing. Use when you need a deterministic, throwaway local environment for any non-CDC source-mongodb-v2 test or prove-fix comparison.
---

# source-mongodb-v2-e2e-tests

Local end-to-end test harness for `source-mongodb-v2`. The engine-independent
orchestration lives in
[`airbyte-integrations/db-harness-lib/`](../../../../../db-harness-lib/);
this skill keeps the MongoDB backend lifecycle scripts, fixtures, and config
templates. It stands up a MongoDB 7.0 container named
`source-mongodb-v2-db-backend` configured as a single-node replica set
(`rs0`), lets you apply arbitrary `mongosh` JavaScript fixtures, and runs
Airbyte protocol commands against any `airbyte/source-mongodb-v2:<tag>` image
via `airbyte-ops cloud connector regression-test`.

Scope: non-CDC (full-refresh / initial-snapshot) behavior. Change-stream
resume-token replay and CDC comparison flows are not covered by this skill.

## When to use this skill

- Reproducing a `source-mongodb-v2` bug locally without Atlas credentials.
- Sweeping `spec` → `check` → `discover` → `read`, or running one of them,
  against any `airbyte/source-mongodb-v2:<tag>` for connector development.
- Proving a fix by comparing a target image with a control image.

## Prerequisites

- Docker.
- [`uv`](https://docs.astral.sh/uv/). `uv tool install
airbyte-internal-ops` puts `airbyte-ops` on `$PATH`; alternatively prefix
  every call with `uvx airbyte-internal-ops`.
- `jq`.
- A clone of `airbytehq/airbyte`.

You do not need GSM, Atlas, or Cloud admin credentials. Local-only mode (no
`--connection-id`) reads everything from local files.

## Layout

```
source-mongodb-v2-e2e-tests/
├── SKILL.md
├── scripts/
│   ├── start-backend.sh        # docker run mongo:7.0 --replSet rs0; rs.initiate()
│   ├── apply-sql.sh            # docker exec mongosh with a .js fixture on stdin
│   ├── reset-databases.sh      # drop every non-system database
│   └── run.sh                  # engine shim to db-harness-lib orchestration
└── fixtures/
    ├── configs/
    │   └── base.template.json  # SELF_MANAGED_REPLICA_SET config; host placeholder
    └── js/
        └── 00-init-base.js     # test_db.sample with three documents
```

`apply-sql.sh` keeps the db-harness-lib engine entrypoint name, but MongoDB
fixtures are `mongosh` scripts, not SQL. Each fixture runs with `test_db`
(`BACKEND_DB`) as the current `db`; use `db.getSiblingDB(...)` for others.

## Conventions

- Container name: `source-mongodb-v2-db-backend`. Override via
  `BACKEND_NAME=…` only for parallel test isolation; don't use customer
  connection names.
- No authentication. The backend runs without `--auth`; the config's
  `database_config` omits `username`/`password`. Add them to a copied
  template if you need to reproduce an auth-specific issue.
- Replica set: `rs0` (`BACKEND_REPLSET`). The connector requires a replica
  set even for non-CDC reads. `start-backend.sh` registers the single member
  under the container's bridge IP so the connector container, which performs
  replica-set discovery from the seed list, can reach the advertised host.
  Do not change the member host to `localhost`: the connector would then
  fail to connect.
- Initial database: `test_db`. Override with `BACKEND_DB`; keep
  `database_config.databases` in the config template in sync.
- Working directory for rendered configs and run output:
  `${REPRO_OUT:-/tmp/source-mongodb-v2-repro}`, laid out as
  `$REPRO_OUT/<step-name>/{config.json,configured_catalog.json,<command>/}`.
- Both containers share Docker's default `bridge` network. The engine shim
  sets `CONFIG_HOST_JQ` so the shared
  [`render-config.sh`](../../../../../db-harness-lib/scripts/render-config.sh)
  rewrites `database_config.connection_string` to
  `mongodb://<bridge-ip>:27017/?replicaSet=rs0` at runtime.
- The backend image is pinned to `mongo:7.0`. Override with `BACKEND_IMAGE=…`
  for a version-specific reproduction.

## Usage

`scripts/run.sh` is the only supported entrypoint. It performs the whole
sequence — start the backend, apply the fixtures, render the config, run
`spec` → `check` → `discover`, derive the configured catalog from that
`discover` output, run `read`, and tear down on exit:

```bash
cd airbyte-integrations/connectors/source-mongodb-v2

# Single version, full sweep.
poe e2e-local --test-version=2.0.7

# Target vs. control comparison.
poe e2e-local --test-version=dev --control-version=2.0.6 --reset=fixture

# One command only.
poe e2e-local --command=read --test-version=2.0.7
```

The sweep runs every command against the one backend and reports each
result rather than stopping at the first failure, then prints a summary
table and exits non-zero if any command failed. Under CI the table is also
appended to `$GITHUB_STEP_SUMMARY`.

Prefer a published target image for code on a pushed PR branch (publish a
pre-release with the Airbyte Ops MCP tool
`publish_connector_to_airbyte_registry` and pass the resulting
`<version>-preview.<7-char-sha>` tag as `--test-version`). See
[Getting a target image](../../../../../db-harness-lib/README.md#getting-a-target-image).
All other `run.sh` options (`--command`, `--fixture`, `--config-template`,
`--reset`, `--expect-*`, `--min-records`, …) are documented in the
[db-harness-lib README](../../../../../db-harness-lib/README.md) and
`poe e2e-local --help`.

## Common gotchas

- **Schema enforcement.** The base template sets
  `database_config.schema_enforced: true`, so `discover` samples documents
  and emits typed fields. Set it to `false` in a copied template to
  reproduce schemaless (`data` blob) behavior.
- **`_id` types.** Fixtures use integer `_id`s for readability; use
  `ObjectId()` in a fixture when the bug depends on ObjectId serialization.
- **Discovery only sees non-empty collections.** A `db.createCollection()`
  without documents is still discovered, but with `schema_enforced: true`
  it will have no sampled fields beyond `_id`.
- **Reset drops databases, not the replica set.** `--reset=fixture` removes
  all non-system databases and reapplies fixtures; the oplog and resume
  tokens survive. Use `--reset=backend` when a run must start from a fresh
  oplog.
- **Do not use customer connections.** This harness is for local testing
  only and must never be used against customer connections, Atlas clusters
  holding customer data, or Airbyte Cloud.

## Teardown

The shared library's default `stop-backend.sh` is idempotent:

```bash
BACKEND_NAME=source-mongodb-v2-db-backend \
  airbyte-integrations/db-harness-lib/scripts/stop-backend.sh
rm -rf "$REPRO_OUT"
unset REPRO_OUT
```
