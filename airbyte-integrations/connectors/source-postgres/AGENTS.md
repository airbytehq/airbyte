> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-postgres: Unique Connector Behaviors

## 1. Xmin incremental checks reject wraparound

When Xmin is the configured incremental mode, `PostgresSourceMetadataQuerier.extraChecks()` checks for database transaction-ID wraparound and raises a `ConfigErrorException` if it detects one. The connector's check operation invokes these extra checks; this is not a guard applied to every incremental mode.

**Why this matters:** The connector reports that wraparound makes Xmin inefficient and can lead to higher credit consumption, and recommends switching to CDC or a cursor-based mode. Preserve this guard and its guidance so users can move away from a degraded Xmin configuration.

## 2. CTID partition state tracks table filenodes

CTID-based reads persist the table filenode with the CTID position. If a table's filenode changes (for example, after `VACUUM FULL`), the partition factory resets the affected stream so it starts over; a filenode change while a partition is active is treated as a transient failure.

**Why this matters:** CTIDs are physical row locations and are not stable across a table rewrite. Resuming an old CTID against a new filenode can skip rows, so the state and filenode checks must remain coupled.

## 3. CDC replication slots advance during startup

The CDC partition creator invokes the Postgres startup hook before creating its reader. That hook validates the saved offset and, unless Debezium is configured to commit LSNs itself, advances the replication slot to the earlier of `lsn_proc` and `lsn_commit`. This is a startup action, not an end-of-sync or checkpoint hook. Slot metadata is queried in a version-tolerant way because fields such as `confirmed_flush_lsn`, `wal_status`, and `invalidation_reason` were introduced in different PostgreSQL releases.

**Why this matters:** Slot advancement controls which WAL PostgreSQL must retain. Do not move this behavior to a checkpoint or assume it runs there; changing the advancement point can either retain unnecessary WAL or discard history needed to resume from the saved offset.

## 4. PostgreSQL-specific types have connector-defined encodings

The custom converter keeps built-in geometric types separate from PostGIS `GEOMETRY` and `GEOGRAPHY`, and converts those values through text. CDC intervals are also emitted as strings. For `money`, the JDBC schema is numeric, but the legacy JSON encoding is textual while Protobuf encoding normalizes the value to scale 2.

**Why this matters:** These encodings differ by type and, for `money`, by output encoding. Changing converters or schemas without preserving those distinctions can change field types or lose precision for existing destinations.

## Reproducing bugs and testing

Use the [PostgreSQL E2E skills](CONTRIBUTING.md#reproducing-bugs) for the connector's standard and CDC harnesses:
[source-postgres-e2e-tests](.agents/skills/source-postgres-e2e-tests/SKILL.md) and
[source-postgres-e2e-cdc-tests](.agents/skills/source-postgres-e2e-cdc-tests/SKILL.md).
