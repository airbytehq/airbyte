# Snowflake Source

## Documentation
* [User Documentation](https://docs.airbyte.io/integrations/sources/snowflake)

## Community Contributor
1. Look at the integration documentation to see how to create a warehouse/database/schema/user/role for Airbyte to sync into.
1. Create a file at `secrets/config.json` with the following format:
```
{
  "host": "ACCOUNT.REGION.PROVIDER.snowflakecomputing.com",
  "role": "AIRBYTE_ROLE",
  "warehouse": "AIRBYTE_WAREHOUSE",
  "database": "AIRBYTE_DATABASE",
  "schema": "AIRBYTE_SCHEMA",
  "credentails" {
    "auth_type": "username/password",
    "username": "AIRBYTE_USER",
    "password": "SOMEPASSWORD"
  }
}
```
3. Create a file at `secrets/config_auth.json` with the following format:
```
{
  "host": "ACCOUNT.REGION.PROVIDER.snowflakecomputing.com",
  "role": "AIRBYTE_ROLE",
  "warehouse": "AIRBYTE_WAREHOUSE",
  "database": "AIRBYTE_DATABASE",
  "schema": "AIRBYTE_SCHEMA",
  "credentails" {
    "auth_type": "OAuth",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "refresh_token": "refresh_token"
  }
}
```
## For Airbyte employees
Put the contents of the `Snowflake Insert Test Creds` secret on Lastpass into `secrets/config.json` to be able to run integration tests locally.
