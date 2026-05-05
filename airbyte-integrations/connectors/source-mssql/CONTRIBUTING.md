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
  [`airbyte-internal-ops`](https://github.com/airbytehq/airbyte-ops-mcp)
  CLI's `airbyte-ops cloud connector regression-test` command.
  `airbyte-ops` handles the connector lifecycle (image pull,
  `spec` / `check` / `discover` / `read`, catalog filtering,
  AirbyteMessage parsing, exit-code interpretation) and writes
  `stdout.txt` and `stderr.txt` per command into a known output
  directory, so this doc stays focused on per-bug input shape rather
  than on docker-CLI plumbing.

In single-version mode (`--skip-compare=True`),
`airbyte-ops cloud connector regression-test` simply runs one Airbyte
protocol command (`spec`, `check`, `discover`, or `read`) against one
connector image with the supplied config / catalog / state. The
"comparison" path of the same command — used by the `/ai-prove-fix`
slash command — is not relevant for repro work.

### Prerequisites

- Docker
- A clone of this repo
- [`uv`](https://docs.astral.sh/uv/) — for invoking `airbyte-ops` via
  `uvx airbyte-internal-ops ...`. To pre-install (recommended for
  repeated invocations) run `uv tool install airbyte-internal-ops`,
  after which `airbyte-ops --help` is on `$PATH`.

You do **not** need the platform, Sonar, Airbyte Cloud, or any GSM /
Cloud admin credentials. Local-only mode (no `--connection-id`) reads
config / catalog / state from local files and runs the connector image
directly.

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

`MSSQL_AGENT_ENABLED=true` is required: SQL Server CDC capture / cleanup
are Agent jobs, and Debezium's CDC reader will silently produce no
records if Agent is off.

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

### Step 3 — Run the connector against the harness

The connector half is invoked through `airbyte-ops cloud connector regression-test`.
Pin to whichever version you're investigating — `metadata.yaml` has the
current `dockerImageTag`. Pass the version via `--test-image` as a docker
image identifier (e.g. `airbyte/source-mssql:4.4.2`,
`airbyte/source-mssql:dev` for a locally-built image, or
`airbyte/source-mssql:latest`).

The connector config lives in
[`dev/cdc-repro/config.cdc.json`](dev/cdc-repro/config.cdc.json). It
points at `mssql-cdc` (the container name on `cdc-harness-net`) and
selects the CDC `replication_method`. Configured catalogs live in
[`dev/cdc-repro/catalogs/`](dev/cdc-repro/catalogs/) — the baseline one
is `users-cdc.json`, which configures `dbo.users` for `incremental` +
`append_dedup` with `_ab_cdc_lsn` as the cursor.

Set a stable output directory so you know where to find logs:

```bash
export REPRO_OUT=/tmp/source-mssql-repro
mkdir -p "$REPRO_OUT"
```

**Connector check:**

```bash
uvx airbyte-internal-ops airbyte-ops cloud connector regression-test \
  --skip-compare=True \
  --command=check \
  --test-image=airbyte/source-mssql:4.4.2 \
  --config-path=airbyte-integrations/connectors/source-mssql/dev/cdc-repro/config.cdc.json \
  --output-dir="$REPRO_OUT/check"
```

A successful baseline check exits 0 and writes a `CONNECTION_STATUS`
AirbyteMessage with `"status": "SUCCEEDED"` to `$REPRO_OUT/check/stdout.txt`.

**Connector read** — uses the configured catalog at
`dev/cdc-repro/catalogs/users-cdc.json`:

```bash
uvx airbyte-internal-ops airbyte-ops cloud connector regression-test \
  --skip-compare=True \
  --command=read \
  --test-image=airbyte/source-mssql:4.4.2 \
  --config-path=airbyte-integrations/connectors/source-mssql/dev/cdc-repro/config.cdc.json \
  --catalog-path=airbyte-integrations/connectors/source-mssql/dev/cdc-repro/catalogs/users-cdc.json \
  --output-dir="$REPRO_OUT/read-baseline" \
  --enable-debug-logs=True
```

A successful baseline read of `dbo.users` exits 0 and emits three
`RECORD` AirbyteMessages on `stdout.txt`, each with `_ab_cdc_lsn`
populated. Debezium engine start-up, snapshot progress, and the
"Adding table … to the list of capture schema tables" lines (used by
the repro-12094 assertion below) land in `$REPRO_OUT/read-baseline/stderr.txt`.
`--enable-debug-logs=True` sets `LOG_LEVEL=DEBUG` on the connector
container, which surfaces the relevant Debezium TRACE-ish lines.

### Step 4 — Add a per-bug fixture

For a new bug, drop a SQL fixture in [`dev/cdc-repro/`](dev/cdc-repro/)
that extends the database to the **smallest** state that triggers the
symptom, apply it via `docker exec ... sqlcmd -i`, then re-run
`regression-test --command=read` against the affected stream. Two worked
examples live in that directory.

#### `repro-12162-spaces-in-name.sql`

For [`airbytehq/oncall#12162`](https://github.com/airbytehq/oncall/issues/12162).
Creates `dbo.[Order Items]` (note the space), enables CDC on it, and
re-runs `read` against the new stream using
`dev/cdc-repro/catalogs/order-items-cdc.json`:

```bash
docker cp \
  airbyte-integrations/connectors/source-mssql/dev/cdc-repro/repro-12162-spaces-in-name.sql \
  mssql-cdc:/tmp/repro-12162.sql
docker exec mssql-cdc /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "Test_password_1" -C -i /tmp/repro-12162.sql

uvx airbyte-internal-ops airbyte-ops cloud connector regression-test \
  --skip-compare=True \
  --command=read \
  --test-image=airbyte/source-mssql:4.4.2 \
  --config-path=airbyte-integrations/connectors/source-mssql/dev/cdc-repro/config.cdc.json \
  --catalog-path=airbyte-integrations/connectors/source-mssql/dev/cdc-repro/catalogs/order-items-cdc.json \
  --output-dir="$REPRO_OUT/read-12162"
```

Expected outcome: the read exits non-zero and `$REPRO_OUT/read-12162/stderr.txt`
contains:

```
io.debezium.DebeziumException: Connector configuration is not valid.
The 'message.key.columns' value is invalid:
dbo.Order Items:id has an invalid format (expecting '^\s*([^\s:]+):([^:\s]+)\s*$')
```

The bug is in
`MsSqlServerDebeziumOperations.buildMessageKeyColumns()` — it joins
`schema.table:pkcol` strings without filtering or escaping identifiers
that contain whitespace or `:`, and Debezium rejects them at engine
startup. The fix is to pre-filter such streams (Debezium falls back to
the table's native PK from system tables).

This worked example also demonstrates that whitespace in stream names
and namespace identifiers passes through `--catalog-path` cleanly — the
catalog file is JSON, so no shell-quoting or picocli arg-splitting
gymnastics are needed.

#### `repro-12094-schema-history.sql`

For [`airbytehq/oncall#12094`](https://github.com/airbytehq/oncall/issues/12094).
Creates 30 "noise" tables in `dbo` and does **not** enable CDC on them.
Re-run the Step 3 baseline `read` against `users` (using
`catalogs/users-cdc.json`) into a fresh output directory; the read
itself succeeds — the symptom is in the log shape:

```bash
docker cp \
  airbyte-integrations/connectors/source-mssql/dev/cdc-repro/repro-12094-schema-history.sql \
  mssql-cdc:/tmp/repro-12094.sql
docker exec mssql-cdc /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "Test_password_1" -C -i /tmp/repro-12094.sql

uvx airbyte-internal-ops airbyte-ops cloud connector regression-test \
  --skip-compare=True \
  --command=read \
  --test-image=airbyte/source-mssql:4.4.2 \
  --config-path=airbyte-integrations/connectors/source-mssql/dev/cdc-repro/config.cdc.json \
  --catalog-path=airbyte-integrations/connectors/source-mssql/dev/cdc-repro/catalogs/users-cdc.json \
  --output-dir="$REPRO_OUT/read-12094" \
  --enable-debug-logs=True

grep -c 'Adding table CdcTest\..* to the list of capture schema tables' \
  "$REPRO_OUT/read-12094/stderr.txt"
# expect: ~32 (30 noise + dbo.users + dbo.[Order Items] from repro-12162)
```

That is, Debezium loads schema for every table in the database, even
though the configured catalog has one stream. The bug is in the shared
CDK Debezium properties — `withSchemaHistory()` sets
`schema.history.internal.store.only.captured.databases.ddl=true` but
not `…captured.tables.ddl=true`. The same harness reproduces equivalent
behavior on `source-mysql` and `source-postgres` because the property
lives in the bulk-CDK `extract-cdc` toolkit.

### Step 5 — Tear down

```bash
docker rm -f mssql-cdc
docker network rm cdc-harness-net
rm -rf "$REPRO_OUT"
unset REPRO_OUT
```

### Notes

- `config.cdc.json` uses `"ssl_method": {"ssl_method": "unencrypted"}` —
  fine for a local throwaway container, never for a real source.
- `mssql-cdc` is the network-internal hostname used in `config.cdc.json`,
  resolvable when both the SQL Server container and the connector
  container share `cdc-harness-net`. `airbyte-ops cloud connector
  regression-test` runs the connector image with Docker socket access,
  so the network attachment happens automatically as long as the host
  can reach `cdc-harness-net`.
- Each `regression-test` invocation writes `stdout.txt` and `stderr.txt`
  into the supplied `--output-dir`, plus a small JSON summary. Use a
  fresh `--output-dir` per repro step so logs don't get clobbered.
- For comparison-style work (target image vs. control image), drop
  `--skip-compare=True` and supply both `--test-image` and
  `--control-image`. That's not normally needed for the per-bug repros
  documented above; if you do reach for it, the CLI's `--help` covers
  the additional flags.
