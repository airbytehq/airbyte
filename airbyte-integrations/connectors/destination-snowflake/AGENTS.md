> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# destination-snowflake: Contributor notes

## Setting up integration test resources

Run this SQL as `ACCOUNTADMIN` to create an integration test environment. Replace the placeholder password and bucket name before running it.

```sql
CREATE WAREHOUSE INTEGRATION_TEST_WAREHOUSE_DESTINATION WITH WAREHOUSE_SIZE = 'XSMALL' WAREHOUSE_TYPE = 'STANDARD' AUTO_SUSPEND = 600 AUTO_RESUME = TRUE;

CREATE DATABASE INTEGRATION_TEST_DESTINATION;
CREATE SCHEMA INTEGRATION_TEST_DESTINATION.RESTRICTED_SCHEMA;

CREATE ROLE INTEGRATION_TESTER_DESTINATION;

CREATE STORAGE INTEGRATION IF NOT EXISTS GCS_AIRBYTE_INTEGRATION
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = GCS
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('gcs://bucketname');

CREATE STAGE IF NOT EXISTS GCS_AIRBYTE_STAGE
  url = 'gcs://bucketname'
  storage_integration = GCS_AIRBYTE_INTEGRATION;

GRANT ALL PRIVILEGES ON WAREHOUSE INTEGRATION_TEST_WAREHOUSE_DESTINATION TO ROLE INTEGRATION_TESTER_DESTINATION;
GRANT ALL PRIVILEGES ON DATABASE INTEGRATION_TEST_DESTINATION TO ROLE INTEGRATION_TESTER_DESTINATION;

GRANT ALL PRIVILEGES ON FUTURE SCHEMAS IN DATABASE INTEGRATION_TEST_DESTINATION TO ROLE INTEGRATION_TESTER_DESTINATION;
GRANT ALL PRIVILEGES ON FUTURE TABLES IN DATABASE INTEGRATION_TEST_DESTINATION TO ROLE INTEGRATION_TESTER_DESTINATION;

GRANT USAGE ON INTEGRATION GCS_AIRBYTE_INTEGRATION TO ROLE INTEGRATION_TESTER_DESTINATION;
GRANT USAGE ON STAGE GCS_AIRBYTE_STAGE TO ROLE INTEGRATION_TESTER_DESTINATION;

CREATE USER INTEGRATION_TEST_USER_DESTINATION PASSWORD='test' DEFAULT_ROLE=INTEGRATION_TESTER_DESTINATION DEFAULT_WAREHOUSE=INTEGRATION_TEST_WAREHOUSE_DESTINATION MUST_CHANGE_PASSWORD=false;

GRANT ROLE INTEGRATION_TESTER_DESTINATION TO USER INTEGRATION_TEST_USER_DESTINATION;

CREATE SCHEMA INTEGRATION_TEST_DESTINATION.TEST_SCHEMA;

DESC STORAGE INTEGRATION GCS_AIRBYTE_INTEGRATION;
```

The final `DESC STORAGE INTEGRATION` query returns a `STORAGE_GCP_SERVICE_ACCOUNT` value. Grant that service account read and write permissions on the configured GCS bucket.

To recreate the environment from scratch:

```sql
DROP DATABASE IF EXISTS INTEGRATION_TEST_DESTINATION;
DROP USER IF EXISTS INTEGRATION_TEST_USER_DESTINATION;
DROP ROLE IF EXISTS INTEGRATION_TESTER_DESTINATION;
DROP WAREHOUSE IF EXISTS INTEGRATION_TEST_WAREHOUSE_DESTINATION;
```

## Error-case users

Log in as `INTEGRATION_TEST_USER_DESTINATION` and run this SQL to set up error-case user resources:

```sql
drop schema if exists INTEGRATION_TEST_DESTINATION.TEXT_SCHEMA;
create schema INTEGRATION_TEST_DESTINATION.TEXT_SCHEMA;
grant ownership on schema INTEGRATION_TEST_DESTINATION.TEXT_SCHEMA to role INTEGRATION_TESTER_DESTINATION revoke current grants;
grant all privileges on schema INTEGRATION_TEST_DESTINATION.TEXT_SCHEMA to role NO_ACTIVE_WAREHOUSE_ROLE;
```

## Integration test layout and cleanup

`SnowflakeInsertAcceptanceTest` runs the full CDK acceptance suite. The other `*AcceptanceTest`
variants each cover one dimension (`QUOTED_IDENTIFIERS_IGNORE_CASE`, protobuf/socket input,
`NUMBER(38,9)`, raw-tables mode) and only run the tests whose behavior depends on it; the rest are
`@Disabled` with a reason. Keep it that way when adding tests: add to the full suite, and to a
variant only if the variant's dimension changes the behavior.

Every artifact the tests create lives in a `test`-prefixed schema: final tables in the per-test
namespace, and raw tables, temp tables and stages in the per-JVM `test..._internal` schema that
`SnowflakeMigrationConfigurationUpdater` points `raw_data_schema` at. `SnowflakeDataCleaner` runs
once per test JVM and drops `test*` schemas older than 24 hours. Runs from before this scheme left
`test*` tables and `airbyte_stage_test*` stages behind in `overridden_raw_dataset` and
`AIRBYTE_INTERNAL`; those need a one-off manual `DROP`.
