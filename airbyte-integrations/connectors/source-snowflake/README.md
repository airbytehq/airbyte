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
  "username": "AIRBYTE_USER",
  "password": "SOMEPASSWORD"
}
```

## For Airbyte employees
Put the contents of the `Snowflake Insert Test Creds` secret on Lastpass into `secrets/config.json` to be able to run integration tests locally.
