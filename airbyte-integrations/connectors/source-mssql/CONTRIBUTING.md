# Contributing to `source-mssql`

This file is connector-specific. For general Airbyte contribution guidance,
see the repo-root [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) and the
[connector contribution guide](https://docs.airbyte.com/connector-development/).

`source-mssql` is a Kotlin / bulk-CDK connector. Standard local commands:

```bash
./gradlew :airbyte-integrations:connectors:source-mssql:test
./gradlew :airbyte-integrations:connectors:source-mssql:assemble
./gradlew :airbyte-integrations:connectors:source-mssql:airbyteDocker
```

Test fixtures use `org.testcontainers:mssqlserver` — see
`src/test/kotlin/io/airbyte/integrations/source/mssql/MsSqlServerContainerFactory.kt`.

---

## Reproducing CDC issues locally

Most reported bugs against `source-mssql` are CDC-mode bugs. Before you
investigate one, build a deterministic, throwaway local repro. **Never
reproduce against a customer connection**, and never repro against an
Airbyte Cloud instance.

The pattern below has been used to reproduce
[`airbytehq/oncall#12162`](https://github.com/airbytehq/oncall/issues/12162)
and
[`airbytehq/oncall#12094`](https://github.com/airbytehq/oncall/issues/12094).
Worked examples for both bugs live in [`dev/cdc-repro/`](dev/cdc-repro/).

The harness has two halves:

- A **SQL Server container** with CDC enabled, run by hand using `docker`
  + `sqlcmd`. This is the source-side environment that the connector
  connects *to* — it is intentionally hand-rolled because the bug-relevant
  state (CDC enable flags, schema history, table-name shapes) is what
  varies per repro.
- The **published `source-mssql` connector image**, driven by the
  [`airbyte-coral-mcp-powered-by-pyairbyte`](https://github.com/airbytehq/PyAirbyte)
  MCP server. PyAirbyte handles the connector lifecycle (image pull,
  `check`/`discover`/`read`, catalog shaping, AirbyteMessage parsing,
  exit-code interpretation) so this doc stays focused on per-bug input
  shape rather than on docker-CLI plumbing.

### Prerequisites

- Docker
- A clone of this repo
- An MCP-capable agent (Devin, Claude Code, or any MCP client) connected
  to the `airbyte-coral-mcp-powered-by-pyairbyte` server. The MCP tool
  invocations below are shown in JSON-args form; adapt to your agent's
  surface as needed.

You do **not** need the platform, Sonar, or Airbyte Cloud.

### Step 1 — Start SQL Server with CDC capability

```bash
docker network create cdc-harness-net 2>/dev/null || true

docker run -d --rm \
  --name mssql-cdc \
  --network cdc-harness-net \
  -e ACCEPT_EULA=Y \
  -e MSSQL_SA_PASSWORD=Test_password_1 \
  -e MSSQL_AGENT_ENABLED=true \
  -e MSSQL_PID=Developer \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2022-latest

# Wait until SQL Server is accepting connections (about 15s on cold start).
until docker exec mssql-cdc /opt/mssql-tools18/bin/sqlcmd \
        -S localhost -U sa -P "Test_password_1" -C -Q "SELECT 1" \
        >/dev/null 2>&1; do sleep 2; done
```

`MSSQL_AGENT_ENABLED=true` is required: SQL Server CDC capture/cleanup are
Agent jobs, and Debezium's CDC reader will silently produce no records if
Agent is off.

### Step 2 — Bootstrap a CDC database

```bash
# from the repo root
docker cp \
  airbyte-integrations/connectors/source-mssql/dev/cdc-repro/00-init.sql \
  mssql-cdc:/tmp/00-init.sql

docker exec mssql-cdc /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "Test_password_1" -C -i /tmp/00-init.sql
```

The script creates a `CdcTest` database, calls `sys.sp_cdc_enable_db`,
creates a `dbo.users` table, calls `sys.sp_cdc_enable_table` on it, and
inserts three rows. Re-running is safe (idempotent guards on every step).

### Step 3 — Run the connector against the harness via coral-mcp

The connector half is invoked through coral-mcp's local MCP tools. Pin to
whichever version you're investigating — `metadata.yaml` has the current
`dockerImageTag`. Pass the version via the `connector_name` argument as a
docker image identifier (e.g. `airbyte/source-mssql:4.4.2`,
`airbyte/source-mssql:dev` for a locally-built image, or
`airbyte/source-mssql` for the latest).

The connector config lives in
[`dev/cdc-repro/config.cdc.json`](dev/cdc-repro/config.cdc.json). It points
at `mssql-cdc` (the container name on `cdc-harness-net`) and selects the
CDC `replication_method`. Both the MCP server and the connector image must
be on `cdc-harness-net` to resolve that hostname.

**Connector check** — `validate_connector_config`:

```jsonc
// Tool: airbyte-coral-mcp-powered-by-pyairbyte / validate_connector_config
{
  "connector_name": "airbyte/source-mssql:4.4.2",
  "config_file": "airbyte-integrations/connectors/source-mssql/dev/cdc-repro/config.cdc.json"
}
```

A successful baseline check returns `(true, "Configuration for ... is valid!")`.

**Connector read** — `read_source_stream_records`. PyAirbyte uses
incremental sync mode by default, which is exactly what CDC requires; the
cursor field comes from the connector's discovered catalog
(`_ab_cdc_lsn`). Capture the connector logs to a known path using
`log_file_path` so per-bug assertions on log shape (see Step 4) can grep
them.

```jsonc
// Tool: airbyte-coral-mcp-powered-by-pyairbyte / read_source_stream_records
{
  "source_connector_name": "airbyte/source-mssql:4.4.2",
  "config_file": "airbyte-integrations/connectors/source-mssql/dev/cdc-repro/config.cdc.json",
  "stream_name": "users",
  "log_file_path": "/tmp/source-mssql-repro/read.log"
}
```

A successful baseline read of `dbo.users` returns three records, each with
`_ab_cdc_lsn` populated. The log file at the specified `log_file_path`
captures the connector's full stderr stream — including Debezium engine
start-up and snapshot progress lines — for inspection.

### Step 4 — Add a per-bug fixture

For a new bug, drop a SQL fixture in [`dev/cdc-repro/`](dev/cdc-repro/)
that extends the database to the **smallest** state that triggers the
symptom, apply it via `docker exec ... sqlcmd -i`, then re-run Step 3's
`read_source_stream_records` against the affected stream. Two worked
examples live in that directory.

#### `repro-12162-spaces-in-name.sql`

For [`airbytehq/oncall#12162`](https://github.com/airbytehq/oncall/issues/12162).
Creates `dbo.[Order Items]` (note the space), enables CDC on it, and
re-runs `read` against the new stream:

```bash
docker cp \
  airbyte-integrations/connectors/source-mssql/dev/cdc-repro/repro-12162-spaces-in-name.sql \
  mssql-cdc:/tmp/repro-12162.sql
docker exec mssql-cdc /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "Test_password_1" -C -i /tmp/repro-12162.sql
```

```jsonc
// Tool: airbyte-coral-mcp-powered-by-pyairbyte / read_source_stream_records
{
  "source_connector_name": "airbyte/source-mssql:4.4.2",
  "config_file": "airbyte-integrations/connectors/source-mssql/dev/cdc-repro/config.cdc.json",
  "stream_name": "Order Items",
  "log_file_path": "/tmp/source-mssql-repro/read-12162.log"
}
```

Expected outcome: the read returns an error string (instead of records)
containing:

```
io.debezium.DebeziumException: Connector configuration is not valid.
The 'message.key.columns' value is invalid:
dbo.Order Items:id has an invalid format (expecting '^\s*([^\s:]+):([^:\s]+)\s*$')
```

The bug is in
`MsSqlServerDebeziumOperations.buildMessageKeyColumns()` — it joins
`schema.table:pkcol` strings without filtering or escaping identifiers
that contain whitespace or `:`, and Debezium rejects them at engine
startup. The fix is to pre-filter such streams (Debezium falls back to the
table's native PK from system tables).

This worked example also demonstrates that `connector_name` and
`stream_name` are passed through MCP as opaque strings — whitespace in the
SQL Server stream name doesn't need any catalog-side escaping or shell
quoting on the caller side.

#### `repro-12094-schema-history.sql`

For [`airbytehq/oncall#12094`](https://github.com/airbytehq/oncall/issues/12094).
Creates 30 "noise" tables in `dbo` and does **not** enable CDC on them.
Re-run the Step 3 baseline `read` against `users`. The read itself
succeeds — the symptom is in the log shape:

```bash
grep -c 'Adding table CdcTest\..* to the list of capture schema tables' \
  /tmp/source-mssql-repro/read.log
# expect: ~32 (30 noise + dbo.users + dbo.[Order Items] from repro-12162)
```

That is, Debezium loads schema for every table in the database, even
though the configured catalog has one stream. The bug is in the shared
CDK Debezium properties — `withSchemaHistory()` sets
`schema.history.internal.store.only.captured.databases.ddl=true` but not
`...captured.tables.ddl=true`. The same harness reproduces equivalent
behavior on `source-mysql` and `source-postgres` because the property
lives in the bulk-CDK `extract-cdc` toolkit.

### Step 5 — Tear down

```bash
docker rm -f mssql-cdc
docker network rm cdc-harness-net
rm -rf /tmp/source-mssql-repro
```

### Notes

- `config.cdc.json` uses `"ssl_method": {"ssl_method": "unencrypted"}` —
  fine for a local throwaway container, never for a real source.
- `mssql-cdc` is the network-internal hostname used in `config.cdc.json`.
  The MCP server hosting `airbyte-coral-mcp-powered-by-pyairbyte` and the
  connector image it launches must both be reachable on
  `cdc-harness-net`. Most setups run the MCP server on the host with
  Docker socket access, in which case PyAirbyte's docker executor handles
  the network attachment automatically; if your MCP server runs in a
  container of its own, attach it to `cdc-harness-net` explicitly.
