> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-snowflake: Unique Connector Behaviors

## 1. Snowflake timestamps round up to microseconds

Snowflake timestamps can have nanosecond precision, but Airbyte timestamps support microseconds. The field converters round values up to the next microsecond when discarded nanoseconds are nonzero; the converted value is also used as an incremental cursor bound.

**Why this matters:** Rounding down a cursor can make it compare below a source row and omit that row from the next sync. Preserve round-up behavior for `TIMESTAMP_NTZ`, `TIMESTAMP_TZ`, and `TIMESTAMP_LTZ` when changing conversion or cursor handling.

## 2. Programmatic access-token authentication omits the JDBC username

For programmatic access-token credentials, the connector sets the JDBC `token` and `authenticator` properties without setting `user`; the token identifies the user for this authenticator. Username/password and key-pair authentication populate `user` separately.

**Why this matters:** Adding a username unconditionally can change or break the driver's token-authentication behavior. Keep the credential-specific JDBC properties separate.

## 3. Metadata error tolerance is limited to discovery

The metadata querier recognizes object-level errors `2003`, `2043`, `2037`, and `2057`, but its factory enables this tolerance only for the `discover` operation. `application.yml` separately classifies some of these errors; it does not configure `2057`.

**Why this matters:** Discovery can encounter objects whose metadata is unavailable, but the same tolerance is not applied to CHECK or READ. Do not broaden the allowlist or describe the classifier as covering codes it does not handle.

## 4. The SSH tunnel field is retained for compatibility

`SnowflakeSourceConfiguration` keeps an `sshTunnel` field for compatibility but documents that Snowflake does not need it; its default is `SshNoTunnelMethod`.

**Why this matters:** The field exists to fit the shared configuration shape, not as evidence of supported Snowflake tunneling. Do not rely on it when changing Snowflake connection setup.

## Reproducing bugs and testing

See [CONTRIBUTING.md](CONTRIBUTING.md#reproducing-bugs) for the remote-backend harness and troubleshooting details, and the
[source-snowflake-e2e-tests](.agents/skills/source-snowflake-e2e-tests/SKILL.md)
skill for the supported workflow.
