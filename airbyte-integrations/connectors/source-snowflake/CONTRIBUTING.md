# Contributing to source-snowflake

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/platform/connector-development).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Snowflake timestamps round up to microseconds** -- Sub-microsecond timestamps round up to microseconds, with maximum-date sentinels capped, preserving incremental cursor boundaries.
2. **Programmatic access-token authentication omits the JDBC username** -- Programmatic access-token authentication identifies the user from the token, rather than a JDBC username.
3. **Metadata error tolerance is limited to discovery** -- Discovery can continue past certain object-level metadata errors, but the same tolerance does not apply to CHECK or READ.
4. **The SSH tunnel field is retained for compatibility** -- The retained SSH field is for compatibility, not evidence that SSH tunneling is supported for Snowflake.
5. **TIME columns use a Snowflake-specific reader** -- Snowflake `TIME` values retain fractional precision and do not round past midnight.
6. **CHECK validates the default warehouse, database, and schema** -- By default, CHECK rejects invalid or unauthorized settings as configuration errors; JDBC URL parameters can override this validation.
7. **Metadata schema filters disable JDBC wildcard matching** -- By default, schema names containing `_` or `%` are matched literally, avoiding broad scans and similarly named schemas.
8. **NTZ cursor bounds are bound as TIMESTAMP_NTZ** -- Session time zone settings cannot shift an incremental cursor boundary.

## Build and unit tests

```bash
CI=true ./gradlew :airbyte-integrations:connectors:source-snowflake:test
./gradlew :airbyte-integrations:connectors:source-snowflake:spotbugsMain
./gradlew :airbyte-integrations:connectors:source-snowflake:assemble   # builds airbyte/source-snowflake:dev
```

`src/test/resources/expected-spec.json` is a snapshot of the generated spec. When the specification
class changes, regenerate it deliberately: run `docker run --rm airbyte/source-snowflake:dev spec`,
take the `spec` object of the `SPEC` message, and format it with `prettier` (the pre-commit hook does
this for JSON files).

## Live tests against a real Snowflake account

`src/test-integration` holds tests that run the connector in-process against a real account. They
read the first existing file of:

- `secrets/config_key_pair.json` (`SECRET_SOURCE-SNOWFLAKE_KEY_PAIR__CREDS` in GSM, the one declared in
  `metadata.yaml`; `poe fetch-secrets` or `uvx airbyte-internal-ops secrets fetch` from this directory)
- `secrets/config.json` (local; the directory is gitignored)

The key pair file comes first because the fetch writes *every* GSM secret labelled
`connector:source-snowflake` (`config_key_pair.json`, `config.json`, `config_test.json`), and the
legacy `config.json` secret is a password login that Snowflake now rejects with "Multi-factor
authentication is required".

The file has the shape of the connector spec, for example:

```json
{
  "host": "<account>.snowflakecomputing.com",
  "role": "AIRBYTE_ROLE",
  "warehouse": "AIRBYTE_WAREHOUSE",
  "database": "AIRBYTE_DATABASE",
  "credentials": { "auth_type": "Key Pair Authentication", "username": "AIRBYTE_USER", "private_key": "-----BEGIN PRIVATE KEY-----\n..." }
}
```

Each test class creates its own schema `AIRBYTEIT<timestamp><letters>` in the configured database,
seeds it from `src/test-integration/resources/seed.sql` and drops it afterwards, so the role needs
`CREATE SCHEMA` on the database and `USAGE` on the warehouse. Without a secrets file the tests are
skipped, not failed.

```bash
./gradlew :airbyte-integrations:connectors:source-snowflake:integrationTestNonDocker
```

Test schema names avoid `_` on purpose: the Snowflake JDBC driver treats `_` and `%` in a schema
filter as LIKE wildcards and then lists the whole database (minutes on a large account, and it can
match other schemas). Keep that in mind when testing manually with the `schema` option.

## Smoke-testing the image

```bash
./gradlew :airbyte-integrations:connectors:source-snowflake:assemble
docker run --rm -v "$PWD/secrets:/secrets" airbyte/source-snowflake:dev check --config /secrets/config.json
docker run --rm -v "$PWD/secrets:/secrets" airbyte/source-snowflake:dev discover --config /secrets/config.json
```

For protocol sweeps of a published image against the shared integration account (prove-fix
comparisons, cursor canary), use the harness in `.agents/skills/source-snowflake-e2e-tests/SKILL.md`
(`poe e2e-local`); it fetches the same GSM secret.

## Formatting

Kotlin is formatted with ktfmt (kotlinlang style) through spotless:
`mvn -f spotless-maven-pom.xml spotless:apply` from the repository root.

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
