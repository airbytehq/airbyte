# Contributing to source-snowflake

A Kotlin connector on the Bulk CDK (`extract` core + `extract-jdbc` toolkit). Needs JDK 21 and
Docker. CI compiles with warnings as errors, so prefix Gradle with `CI=true` locally.

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
