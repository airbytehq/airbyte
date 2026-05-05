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

### Prerequisites

- Docker
- A clone of this repo

You do **not** need the platform, Sonar, or Airbyte Cloud. The harness runs
the published connector image directly against a local SQL Server container.

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

### Step 3 — Run the connector against the harness

```bash
mkdir -p /tmp/source-mssql-repro/{secrets,catalogs,output}

cp airbyte-integrations/connectors/source-mssql/dev/cdc-repro/config.cdc.json \
   /tmp/source-mssql-repro/secrets/config.json

# Pin to whichever version you're investigating. metadata.yaml has the
# current dockerImageTag.
IMAGE=airbyte/source-mssql:4.4.2

# 1. spec / check
docker run --rm --network cdc-harness-net \
  -v /tmp/source-mssql-repro/secrets:/secrets \
  $IMAGE check --config /secrets/config.json

# 2. discover -> configured catalog. Build from the discovered catalog so
#    json_schema types match exactly (the bulk-CDK catalog validator is
#    strict about INTEGER vs NUMBER, etc.).
STREAM='users'
CATALOG_FILE='users.json'   # NEVER use a filename containing whitespace
                            # — see Step 4 / repro-12162 for why.
docker run --rm --network cdc-harness-net \
  -v /tmp/source-mssql-repro/secrets:/secrets \
  $IMAGE discover --config /secrets/config.json 2>/dev/null \
  | grep -E '^\{"type":"CATALOG"' \
  | STREAM="$STREAM" python3 -c "
import sys, json, os
catalog = json.loads(sys.stdin.read())['catalog']
configured = {'streams': []}
for s in catalog['streams']:
    if s['name'] != os.environ['STREAM']:
        continue
    configured['streams'].append({
        'stream': s,
        'sync_mode': 'incremental',
        'destination_sync_mode': 'append_dedup',
        'primary_key': s.get('source_defined_primary_key', []),
        'cursor_field': ['_ab_cdc_lsn'],
    })
print(json.dumps(configured, indent=2))
" > "/tmp/source-mssql-repro/catalogs/$CATALOG_FILE"

# 3. read in CDC mode
docker run --rm --network cdc-harness-net \
  -v /tmp/source-mssql-repro/secrets:/secrets \
  -v /tmp/source-mssql-repro/catalogs:/catalogs \
  $IMAGE read \
    --config /secrets/config.json \
    --catalog "/catalogs/$CATALOG_FILE" \
  > /tmp/source-mssql-repro/output/read.jsonl 2>&1

echo "exit=$?"
echo "RECORD: $(grep -c '^{\"type\":\"RECORD\"' /tmp/source-mssql-repro/output/read.jsonl)"
echo "ERROR : $(grep -c '\"type\":\"TRACE\".*\"type\":\"ERROR\"' /tmp/source-mssql-repro/output/read.jsonl)"

# Quoting matters: `STREAM` is the SQL stream name (which CAN contain
# whitespace, see repro-12162) and is passed to python3 via env-var so
# the python source is never reparsed by the shell. `CATALOG_FILE` is
# the on-disk filename, which MUST be whitespace-free so picocli inside
# the connector container parses `--catalog /catalogs/<file>` as a
# single argument.
```

A successful baseline sync of `dbo.users` emits three `RECORD` messages,
each with `_ab_cdc_lsn` populated, and exits 0.

### Step 4 — Add a per-bug fixture

For a new bug, drop a SQL fixture in [`dev/cdc-repro/`](dev/cdc-repro/) that
extends the database to the **smallest** state that triggers the symptom,
and re-run step 3 against the affected stream. Two worked examples live in
that directory:

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

# IMPORTANT: STREAM has a space, so CATALOG_FILE MUST NOT mirror it.
STREAM='Order Items'
CATALOG_FILE='order-items.json'

# Re-run the discover + python catalog-shaping block from Step 3 with
# these two variables, then `read` with --catalog "/catalogs/$CATALOG_FILE".
```

Expected outcome: exit 1, zero `RECORD`s, and the `read` log contains:

```
io.debezium.DebeziumException: Connector configuration is not valid.
The 'message.key.columns' value is invalid:
dbo.Order Items:id has an invalid format (expecting '^\s*([^\s:]+):([^:\s]+)\s*$')
```

The bug is in
`MsSqlServerDebeziumOperations.buildMessageKeyColumns()` — it joins
`schema.table:pkcol` strings without filtering or escaping identifiers
that contain whitespace or `:`, and Debezium rejects them at engine
startup. Confirms the connector should pre-filter such streams (Debezium
falls back to the table's native PK from system tables).

#### `repro-12094-schema-history.sql`

For [`airbytehq/oncall#12094`](https://github.com/airbytehq/oncall/issues/12094).
Creates 30 "noise" tables in `dbo` and does **not** enable CDC on them.
Re-run `read` with the same `STREAM='users'` catalog.

Expected outcome: exit 0, three `RECORD`s. But the `read` log contains:

```
Snapshot step 2 - Determining captured tables
Adding table CdcTest.dbo.users to the list of capture schema tables
Adding table CdcTest.dbo.noise_1 to the list of capture schema tables
... (29 more) ...
```

That is, Debezium loads schema for every table in the database, even
though the configured catalog has one stream. To verify deterministically:

```bash
grep -c 'Adding table CdcTest\..* to the list of capture schema tables' \
  /tmp/source-mssql-repro/output/read.jsonl
# expect: ~32 (30 noise + dbo.users + any other CDC-enabled tables)
```

The bug is in the shared CDK Debezium properties — `withSchemaHistory()`
sets `schema.history.internal.store.only.captured.databases.ddl=true` but
not `...captured.tables.ddl=true`. The same harness reproduces equivalent
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
  It only resolves from sibling containers on `cdc-harness-net`. Host-side
  tools (a local `sqlcmd`, your IDE) connect to `localhost:1433`.
- A previous `read` will have left state in Debezium's `FileOffsetBackingStore`
  inside the connector container; because we use `--rm`, that state is
  discarded between runs and every `read` is a fresh "first sync". To
  exercise checkpoint/resume behavior, mount a host-side directory at
  `/tmp/airbyte-debezium-state` so the offset file persists.
- For schema-change scenarios, run DDL directly via `sqlcmd` between two
  `read` invocations and inspect the second `read`'s output.
