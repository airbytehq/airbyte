# Snowflake Destination

## Documentation

- [User Documentation](https://docs.airbyte.io/integrations/destinations/snowflake)

## Community Contributor

1. Look at the integration documentation to see how to create a warehouse/database/schema/user/role for Airbyte to sync into.
1. Create a file at `secrets/config.json` with the following format:

```
{
  "host": "testhost.snowflakecomputing.com",
  "role": "AIRBYTE_ROLE",
  "warehouse": "AIRBYTE_WAREHOUSE",
  "database": "AIRBYTE_DATABASE",
  "schema": "AIRBYTE_SCHEMA",
  "username": "AIRBYTE_USER",
  "credentials": {
    "password": "test"
  }
}
```

## For Airbyte employees

Put the contents of the following LastPass secrets into corresponding files under the `secrets` directory:

| LastPass Secret                                                                                        | File                                     |
| ------------------------------------------------------------------------------------------------------ | ---------------------------------------- |
| `destination snowflake - test creds (secrets/config.json)`                                             | `secrets/config.json`                    |
| `destination snowflake - insert test creds (secrets/insert_config.json)`                               | `secrets/insert_config.json`             |
| `destination snowflake - internal staging test creds (secrets/internal_staging_config.json)`           | `secrets/internal_staging_config.json`   |
| `destination snowflake - internal staging key pair (secrets/config_key_pair.json)`                     | `secrets/config_key_pair.json`           |
| `destination snowflake - internal staging key pair encrypted (secrets/config_key_pair_encrypted.json)` | `secrets/config_key_pair_encrypted.json` |
| `destination snowflake - s3 staging test creds (secrets/copy_s3_config.json)`                          | `secrets/copy_s3_config.json`            |
| `destination snowflake - s3 staging encrypted test creds (secrets/copy_s3_encrypted_config.json)`      | `secrets/copy_s3_encrypted_config.json`  |
| `destination snowflake - gcs staging test creds (secrets/copy_gcs_config.json)`                        | `secrets/copy_gcs_config.json`           |

The query timeout for insert data to table has been updated from 30 minutes to 3 hours.

## Setting up an integration user

Here is the SQL to make an integration environment in Snowflake for this destination via an ACCOUNTADMIN. Be sure to give a real password.

```sql
CREATE WAREHOUSE INTEGRATION_TEST_WAREHOUSE_DESTINATION WITH WAREHOUSE_SIZE = 'XSMALL' WAREHOUSE_TYPE = 'STANDARD' AUTO_SUSPEND = 600 AUTO_RESUME = TRUE;

CREATE DATABASE INTEGRATION_TEST_DESTINATION;
CREATE SCHEMA INTEGRATION_TEST_DESTINATION.RESTRICTED_SCHEMA;

CREATE ROLE INTEGRATION_TESTER_DESTINATION;

# put real bucket name here and remove this comment
CREATE STORAGE INTEGRATION IF NOT EXISTS GCS_AIRBYTE_INTEGRATION
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = GCS
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('gcs://bucketname');

# put real bucket name here and remove this comment
CREATE STAGE IF NOT EXISTS GCS_AIRBYTE_STAGE
  url = 'gcs://bucketname'
  storage_integration = GCS_AIRBYTE_INTEGRATION;

GRANT ALL PRIVILEGES ON WAREHOUSE INTEGRATION_TEST_WAREHOUSE_DESTINATION TO ROLE INTEGRATION_TESTER_DESTINATION;
GRANT ALL PRIVILEGES ON DATABASE INTEGRATION_TEST_DESTINATION TO ROLE INTEGRATION_TESTER_DESTINATION;

GRANT ALL PRIVILEGES ON FUTURE SCHEMAS IN DATABASE INTEGRATION_TEST_DESTINATION TO ROLE INTEGRATION_TESTER_DESTINATION;
GRANT ALL PRIVILEGES ON FUTURE TABLES IN DATABASE INTEGRATION_TEST_DESTINATION TO ROLE INTEGRATION_TESTER_DESTINATION;

GRANT USAGE ON INTEGRATION GCS_AIRBYTE_INTEGRATION TO ROLE INTEGRATION_TESTER_DESTINATION;
GRANT USAGE ON STAGE GCS_AIRBYTE_STAGE TO ROLE INTEGRATION_TESTER_DESTINATION;

# Add real password here and remove this comment
CREATE USER INTEGRATION_TEST_USER_DESTINATION PASSWORD='test' DEFAULT_ROLE=INTEGRATION_TESTER_DESTINATION DEFAULT_WAREHOUSE=INTEGRATION_TEST_WAREHOUSE_DESTINATION MUST_CHANGE_PASSWORD=false;

GRANT ROLE INTEGRATION_TESTER_DESTINATION TO USER INTEGRATION_TEST_USER_DESTINATION;

CREATE SCHEMA INTEGRATION_TEST_DESTINATION.TEST_SCHEMA;

DESC STORAGE INTEGRATION GCS_AIRBYTE_INTEGRATION;
```

That last query (`DESC STORAGE`) will show a `STORAGE_GCP_SERVICE_ACCOUNT` property with an email as the property value. Add read/write permissions to your bucket with that email if it's not already there.

If you ever need to start over, use this:

```sql
DROP DATABASE IF EXISTS INTEGRATION_TEST_DESTINATION;
DROP USER IF EXISTS INTEGRATION_TEST_USER_DESTINATION;
DROP ROLE IF EXISTS INTEGRATION_TESTER_DESTINATION;
DROP WAREHOUSE IF EXISTS INTEGRATION_TEST_WAREHOUSE_DESTINATION;
```
