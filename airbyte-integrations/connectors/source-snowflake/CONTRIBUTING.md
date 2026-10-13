# Contributing to source-snowflake

## Unique behaviors (summary)

### 1. Snowflake timestamps round up to microseconds

Timestamp values with sub-microsecond precision are rounded up for Airbyte output and cursor bounds. See [AGENTS.md](AGENTS.md#1-snowflake-timestamps-round-up-to-microseconds).

### 2. Programmatic access-token authentication omits the JDBC username

Programmatic access-token authentication sets the token and authenticator without a JDBC username. See [AGENTS.md](AGENTS.md#2-programmatic-access-token-authentication-omits-the-jdbc-username).

### 3. Metadata error tolerance is limited to discovery

Selected object-level metadata errors are tolerated only during discovery, not CHECK or READ. See [AGENTS.md](AGENTS.md#3-metadata-error-tolerance-is-limited-to-discovery).

### 4. The SSH tunnel field is retained for compatibility

Snowflake retains the shared SSH tunnel field for compatibility, but does not use it for Snowflake connections. See [AGENTS.md](AGENTS.md#4-the-ssh-tunnel-field-is-retained-for-compatibility).

`source-snowflake` is a Kotlin / bulk-CDK connector. Standard local commands:

```bash
./gradlew :airbyte-integrations:connectors:source-snowflake:test
./gradlew :airbyte-integrations:connectors:source-snowflake:assemble
./gradlew :airbyte-integrations:connectors:source-snowflake:dockerBuildx
```

## Reproducing bugs

The remote-backend harness for this connector is documented in
[`.agents/skills/source-snowflake-e2e-tests/SKILL.md`](.agents/skills/source-snowflake-e2e-tests/SKILL.md).
It creates a per-run `PROVEFIX_<run_id>` schema in the shared Snowflake
integration account using a GSM key-pair secret; there is no local container,
and `--reset=backend` is rejected. The `poe e2e-local` task is the entrypoint.

The worked example is
`.agents/skills/source-snowflake-e2e-tests/cases/cursor-upper-bound.sh`.
After a run, check for leaked schemas with
`sweep-orphans.sh --older-than-hours=0 --dry-run`.

## Troubleshooting

Files under `airbyte-integrations/connectors/source-snowflake/`, including
`.agents/`, are treated as connector changes by CI. The matrix detector
requires a `dockerImageTag` bump and a changelog entry when these files
change. Do not edit metadata solely to bypass this check without confirming
the required versioning decision.
