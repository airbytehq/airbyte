import KeypairExample from '@site/static/_databricks_keypair_generation.md';

# Databricks

## Getting started

### Requirements

You'll need the following information to configure the Databricks source:

1. **Host**
3. **HTTP Path**
5. **Schema**
6. **Personal Access Token**
8. **JDBC URL Params** (Optional)

### Setup guide

#### Connection parameters

Additional information about Databricks connection parameters can be found in the [Databricks documentation](https://docs.databricks.com/aws/en/integrations/jdbc/).

### Authentication
Currently only supports personal access token authentication

#### Login and Password

| Field                                                                                                 | Description                                                                                                                                                                                       |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Host                       | The host domain of the databricks instance  |                                                                                                         |
| HTTP Path | The http path of the warehouse you created for Airbyte to sync data from.                                                                               |
| Database  | The database/catalog you created want to sync. Example: `AIRBYTE_DATABASE`                                                                                                     |
| Schema     | The schema whose tables this replication is targeting. If no schema is specified, all tables with permission will be presented regardless of their schema.                                        |
| Personal Access Token                         | The personal access token you created to allow Airbyte to access the database.                                                                                             |                                                                                                                                                    |
| [JDBC URL Params](https://docs.databricks.com/en/user-guide/jdbc-parameters.html) (Optional)           | Additional properties to pass to the JDBC URL string when connecting to the database formatted as `key=value` pairs separated by the symbol `&`. Example: `key1=value1&key2=value2&key3=value3`   |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                   |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|                                                                       |
| 0.0.1   | 2025-09-30 | [66975](https://github.com/airbytehq/airbyte/pull/66975)   | Initial commit                                                                                                               |

</details>
