> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-snowflake: Unique Connector Behaviors

## 1. Snowflake timestamps round up to microseconds

Snowflake timestamps can have nanosecond precision, but Airbyte timestamps support microseconds. The field converters round values up to the next microsecond when discarded nanoseconds are nonzero, except that the maximum `9999-12-31 23:59:59.999999999` sentinel is capped at `9999-12-31 23:59:59.999999` to avoid overflowing into year 10000. The converted value is also used as an incremental cursor bound.

**Why this matters:** Rounding down a cursor can make it compare below a source row and omit that row from the next sync, while rounding the maximum sentinel past year 9999 produces an invalid timestamp. Preserve round-up behavior and maximum-sentinel clamping for `TIMESTAMP_NTZ`, `TIMESTAMP_TZ`, and `TIMESTAMP_LTZ` when changing conversion or cursor handling.

## 2. Programmatic access-token authentication omits the JDBC username

For programmatic access-token credentials, the connector sets the JDBC `token` and `authenticator` properties without setting `user`; the token identifies the user for this authenticator. Username/password and key-pair authentication populate `user` separately.

**Why this matters:** Adding a username unconditionally can change or break the driver's token-authentication behavior. Keep the credential-specific JDBC properties separate.

## 3. Metadata error tolerance is limited to discovery

The metadata querier recognizes object-level errors `2003`, `2043`, `2037`, and `2057`, plus `904` in `discover`: a view with an invalid identifier is skipped as a whole, while a table falls back to per-column probes. `application.yml` classifies `904` as a configuration error when it propagates.

**Why this matters:** Discovery tolerates these object-level errors so one broken view or unauthorized object does not fail the full discover; CHECK and READ do not receive that tolerance. Keep the tolerance narrow and confined to discovery.

## 4. The SSH tunnel field is retained for compatibility

`SnowflakeSourceConfiguration` keeps an `sshTunnel` field for compatibility but documents that Snowflake does not need it; its default is `SshNoTunnelMethod`.

**Why this matters:** The field exists to fit the shared configuration shape, not as evidence of supported Snowflake tunneling. Do not rely on it when changing Snowflake connection setup.

## 5. TIME columns use a Snowflake-specific reader

`SnowflakeSourceOperations` maps `TIME` to `SnowflakeLocalTimeFieldType`. Its accessor reads with `ResultSet.getTimestamp()` and converts to `LocalTime`: the Snowflake JDBC driver rejects `getObject(..., LocalTime::class.java)`, while `getTime()` keeps only milliseconds. Nanoseconds are rounded up to microseconds; if rounding would cross midnight, the value is capped at `23:59:59.999999` rather than wrapping.

**Why this matters:** The default local-time reader would emit `NULL` for Snowflake `TIME` values, and `getTime()` loses fractional precision. Preserve the custom reader and end-of-day cap when changing `TIME` conversion.

## 6. CHECK validates the default warehouse, database, and schema

`SnowflakeSourceConfiguration` sets JDBC `validateDefaultParameters=true` by default, making the driver reject a missing or unauthorized warehouse, database, or schema at login; otherwise `SHOW` and `LIMIT 0` probes can pass CHECK without a usable warehouse. User-supplied `jdbcUrlParams` are applied afterwards and can override this setting. The resulting Snowflake JDBC errors match the connector's `application.yml` `error: config` rules, which the `JdbcExceptionClassifier` maps to `ConfigError` and CHECK surfaces as `CONFIG_ERROR`.

**Why this matters:** Without validation, CHECK can pass even though the first real query will fail. Preserve login-time validation and configuration-error classification for invalid or inaccessible defaults.

## 7. Metadata schema filters disable JDBC wildcard matching

`SnowflakeSourceConfiguration` sets `ENABLE_WILDCARDS_IN_SHOW_METADATA_COMMANDS=false` before applying user-supplied `jdbcUrlParams`. By default, this makes `_` and `%` in a schema filter literal; otherwise the JDBC driver treats them as `LIKE` wildcards, scans schemas across the database, and can match similarly named schemas such as `SCHEMA_A` and `SCHEMAXA`.

**Why this matters:** Re-enabling wildcard matching can turn a schema-scoped metadata query into a full-database scan and return duplicate or unrelated metadata. Keep schema filters exact.

## 8. NTZ cursor bounds are bound as TIMESTAMP_NTZ

`SnowflakeLocalDateTimeAccessor.set` binds cursor values with `PreparedStatement.setObject(..., SnowflakeType.EXTRA_TYPES_TIMESTAMP_NTZ)` instead of plain `setTimestamp`. The latter is interpreted using the session `TIMEZONE` and can shift a `TIMESTAMP_NTZ` cursor bound.

**Why this matters:** A shifted bound can make a warm incremental sync skip rows. Preserve explicit `TIMESTAMP_NTZ` binding when changing cursor accessors.

## Reproducing bugs and testing

See [CONTRIBUTING.md](CONTRIBUTING.md#reproducing-bugs) for the remote-backend harness and troubleshooting details, and the
[source-snowflake-e2e-tests](.agents/skills/source-snowflake-e2e-tests/SKILL.md)
skill for the supported workflow.
