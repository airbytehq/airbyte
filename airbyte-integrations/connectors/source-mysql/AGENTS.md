> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-mysql: Unique Connector Behaviors

## 1. Saved CDC positions are validated against available binlog history

At CDC startup, the connector validates saved GTID or binlog state against the server's executed and purged GTID sets and the available binlog files. If the saved position is no longer usable, `invalid_cdc_cursor_position_behavior` determines whether the sync fails or resets; its default is `Fail sync`.

**Why this matters:** A reset may reread data, while continuing from a purged position cannot recover the missing change history. Preserve the configured fail-versus-reset behavior when changing offset validation.

## 2. Zero dates and times have distinct CDC conversions

The CDC converter turns zero `DATE` and `DATETIME` values into `null`, and those fields are made nullable. A zero `TIMESTAMP` instead becomes the Unix epoch, while midnight `TIME` remains a valid time value.

**Why this matters:** These MySQL zero values are not interchangeable. Collapsing the cases can change schemas or turn legitimate midnight values into nulls.

## 3. TINYINT(1) defaults to boolean in CDC

Unless `treat_tinyint1_as_integer` is enabled, the Debezium boolean converter maps `TINYINT(1)` values to booleans. Enabling the option disables that converter so CDC emits integers.

**Why this matters:** This setting changes the output type for existing columns. Keep the JDBC and CDC behavior aligned when changing how the option is applied.

## 4. TLS settings are translated for JDBC and Debezium

The configured SSL mode and certificate material are mapped into JDBC properties and separately into Debezium's `database.ssl.*` properties. The Debezium binlog client does not use the JDBC driver's SSL properties, so CDC depends on the second property set.

**Why this matters:** A JDBC-only TLS change can leave the binlog connection using different security settings. Preserve both mappings when changing TLS behavior.

## 5. Only specific binlog EOF errors are transient

`application.yml` classifies several specific binlog EOF message patterns as transient. This is a narrow set of recognized messages, not a catch-all rule for EOF or other connection failures.

**Why this matters:** Broadening the classification can make permanent failures retry indefinitely, while narrowing it can fail syncs for the known transient binlog cases.

## Reproducing bugs and testing

See [CONTRIBUTING.md](CONTRIBUTING.md#reproducing-bugs-locally) for the local harness and the
[source-mysql-e2e-tests](.agents/skills/source-mysql-e2e-tests/SKILL.md) and
[source-mysql-e2e-cdc-tests](.agents/skills/source-mysql-e2e-cdc-tests/SKILL.md) skills.
