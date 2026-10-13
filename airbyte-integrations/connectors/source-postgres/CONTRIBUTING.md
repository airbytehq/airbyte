# Contributing to source-postgres

## Unique behaviors (summary)

### 1. Xmin incremental checks reject wraparound

Xmin checks reject databases with transaction-ID wraparound. See [AGENTS.md](AGENTS.md#1-xmin-incremental-checks-reject-wraparound).

### 2. CTID partition state tracks table filenodes

CTID state is tied to the table filenode and resets when a table rewrite changes it. See [AGENTS.md](AGENTS.md#2-ctid-partition-state-tracks-table-filenodes).

### 3. CDC replication slots advance during startup

Postgres validates and may advance the replication slot in the CDC startup hook, not at sync completion or checkpoint. See [AGENTS.md](AGENTS.md#3-cdc-replication-slots-advance-during-startup).

### 4. PostgreSQL-specific types have connector-defined encodings

Geometry, geography, intervals, and `money` use connector-specific conversion paths, including different `money` representations across encodings. See [AGENTS.md](AGENTS.md#4-postgresql-specific-types-have-connector-defined-encodings).

## Reproducing bugs

Use [source-postgres-e2e-tests](.agents/skills/source-postgres-e2e-tests/SKILL.md) for standard harness cases and [source-postgres-e2e-cdc-tests](.agents/skills/source-postgres-e2e-cdc-tests/SKILL.md) for CDC cases. The skills contain the supported invocations and setup details.
