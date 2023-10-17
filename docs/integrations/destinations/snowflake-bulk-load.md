# Snowflake (Bulk Load)

This is an experimental version of the Snowflake connector, which bulk loads raw files from S3.

## Prerequisites

- A Snowflake account with the [ACCOUNTADMIN](https://docs.snowflake.com/en/user-guide/security-access-control-considerations.html) role. If you don’t have an account with the `ACCOUNTADMIN` role, contact your Snowflake administrator to set one up for you.
- An AWS account.

### Network policies

By default, Snowflake allows users to connect to the service from any computer or device IP address. A security administrator (i.e. users with the `SECURITYADMIN` role) or higher can create a network policy to allow or deny access to a single IP address or a list of addresses.

If you have any issues connecting with Airbyte Cloud please make sure that the list of IP addresses is on the allowed list

To determine whether a network policy is set on your account or for a specific user, execute the _SHOW PARAMETERS_ command.

**Account**

```sql
SHOW PARAMETERS LIKE 'network_policy' IN ACCOUNT;
```

**User**

```sql
SHOW PARAMETERS LIKE 'network_policy' IN USER <username>;
```

To read more please check official [Snowflake documentation](https://docs.snowflake.com/en/user-guide/network-policies.html#)

## Setup guide

### Step 1: Set up file format and S3 stages

The bulk load process requires a pre-created file format object and a pre-created external stage in Snowflake.

Create a file format object:

```sql
CREATE FILE_FORMAT my_file_format ...
```

Create an external stage:

```sql
CREATE EXTERNAL STAGE my_s3_stage ...
```

The file format name and stage name will be provided to the connector configuration.

### Step 2: Set up Airbyte-specific entities in Snowflake

To set up the Snowflake destination connector, you first need to create Airbyte-specific Snowflake entities (a warehouse, database, schema, user, and role) with the `OWNERSHIP` permission to write data into Snowflake, track costs pertaining to Airbyte, and control permissions at a granular level.

You can use the following script in a new [Snowflake worksheet](https://docs.snowflake.com/en/user-guide/ui-worksheet.html) to create the entities:

1. [Log into your Snowflake account](https://www.snowflake.com/login/).
2. Edit the following script to change the password to a more secure password and to change the names of other resources if you so desire.

    **Note:** Make sure you follow the [Snowflake identifier requirements] (https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html) while renaming the resources.

    ```sql
    -- set variables (these need to be uppercase)
    set airbyte_role = 'AIRBYTE_ROLE';
    set airbyte_username = 'AIRBYTE_USER';
    set airbyte_warehouse = 'AIRBYTE_WAREHOUSE';
    set airbyte_database = 'AIRBYTE_DATABASE';
    set airbyte_schema = 'AIRBYTE_SCHEMA';

    -- set user password
    set airbyte_password = 'password';

    begin;

    -- create Airbyte role
    use role securityadmin;
    create role if not exists identifier($airbyte_role);
    grant role identifier($airbyte_role) to role SYSADMIN;

    -- create Airbyte user
    create user if not exists identifier($airbyte_username)
    password = $airbyte_password
    default_role = $airbyte_role
    default_warehouse = $airbyte_warehouse;

    grant role identifier($airbyte_role) to user identifier($airbyte_username);

    -- change role to sysadmin for warehouse / database steps
    use role sysadmin;

    -- create Airbyte warehouse
    create warehouse if not exists identifier($airbyte_warehouse)
    warehouse_size = xsmall
    warehouse_type = standard
    auto_suspend = 60
    auto_resume = true
    initially_suspended = true;

    -- create Airbyte database
    create database if not exists identifier($airbyte_database);

    -- grant Airbyte warehouse access
    grant USAGE
    on warehouse identifier($airbyte_warehouse)
    to role identifier($airbyte_role);

    -- grant Airbyte database access
    grant OWNERSHIP
    on database identifier($airbyte_database)
    to role identifier($airbyte_role);

    commit;

    begin;

    USE DATABASE identifier($airbyte_database);

    -- create schema for Airbyte data
    CREATE SCHEMA IF NOT EXISTS identifier($airbyte_schema);

    commit;

    begin;

    -- grant Airbyte schema access
    grant OWNERSHIP
    on schema identifier($airbyte_schema)
    to role identifier($airbyte_role);

    commit;
    ```

3. Run the script using the [Worksheet page](https://docs.snowflake.com/en/user-guide/ui-worksheet.html) or [Snowsight](https://docs.snowflake.com/en/user-guide/ui-snowsight-gs.html). Make sure to select the **All Queries** checkbox.

### Step 3: Set up Snowflake as a destination in Airbyte

Navigate to the Airbyte UI to set up Snowflake as a destination. You can authenticate using username/password or OAuth 2.0:

### Login and Password

| Field                                                                                                 | Description                                                                                                                                                                                       |
|-------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Host](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html)                        | The host domain of the snowflake instance (must include the account, region, cloud environment, and end with snowflakecomputing.com). Example: `accountname.us-east-2.aws.snowflakecomputing.com` |
| [Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles)          | The role you created in Step 1 for Airbyte to access Snowflake. Example: `AIRBYTE_ROLE`                                                                                                           |
| [Warehouse](https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses) | The warehouse you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_WAREHOUSE`                                                                                                   |
| [Database](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)   | The database you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_DATABASE`                                                                                                     |
| [Schema](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)     | The default schema used as the target schema for all statements issued from the connection that do not explicitly specify a schema name.                                                          |
| Username                                                                                              | The username you created in Step 1 to allow Airbyte to access the database. Example: `AIRBYTE_USER`                                                                                               |
| Password                                                                                              | The password associated with the username.                                                                                                                                                        |
| [JDBC URL Params](https://docs.snowflake.com/en/user-guide/jdbc-parameters.html) (Optional)           | Additional properties to pass to the JDBC URL string when connecting to the database formatted as `key=value` pairs separated by the symbol `&`. Example: `key1=value1&key2=value2&key3=value3`   |

### OAuth 2.0

| Field                                                                                                 | Description                                                                                                                                                                                       |
|:------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Host](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html)                        | The host domain of the snowflake instance (must include the account, region, cloud environment, and end with snowflakecomputing.com). Example: `accountname.us-east-2.aws.snowflakecomputing.com` |
| [Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview.html#roles)          | The role you created in Step 1 for Airbyte to access Snowflake. Example: `AIRBYTE_ROLE`                                                                                                           |
| [Warehouse](https://docs.snowflake.com/en/user-guide/warehouses-overview.html#overview-of-warehouses) | The warehouse you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_WAREHOUSE`                                                                                                   |
| [Database](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)   | The database you created in Step 1 for Airbyte to sync data into. Example: `AIRBYTE_DATABASE`                                                                                                     |
| [Schema](https://docs.snowflake.com/en/sql-reference/ddl-database.html#database-schema-share-ddl)     | The default schema used as the target schema for all statements issued from the connection that do not explicitly specify a schema name.                                                          |
| Username                                                                                              | The username you created in Step 1 to allow Airbyte to access the database. Example: `AIRBYTE_USER`                                                                                               |
| OAuth2                                                                                                | The Login name and password to obtain auth token.                                                                                                                                                 |
| [JDBC URL Params](https://docs.snowflake.com/en/user-guide/jdbc-parameters.html) (Optional)           | Additional properties to pass to the JDBC URL string when connecting to the database formatted as `key=value` pairs separated by the symbol `&`. Example: `key1=value1&key2=value2&key3=value3`   |

### Key pair authentication

    In order to configure key pair authentication you will need a private/public key pair.
    If you do not have the key pair yet, you can generate one using openssl command line tool
    Use this command in order to generate an unencrypted private key file:

       `openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt`

    Alternatively, use this command to generate an encrypted private key file:

      `openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -v1 PBE-SHA1-RC4-128 -out rsa_key.p8`

    Once you have your private key, you need to generate a matching public key.
    You can do so with the following command:

      `openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub`

    Finally, you need to add the public key to your Snowflake user account.
    You can do so with the following SQL command in Snowflake:

      `alter user <user_name> set rsa_public_key=<public_key_value>;`

    and replace <user_name> with your user name and <public_key_value> with your public key.

To use AWS S3 as the cloud storage, enter the information for the S3 bucket you created in Step 2:

| Field                          | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| S3 Bucket Name                 | The name of the staging S3 bucket (Example: `airbyte.staging`). Airbyte will write files to this bucket and read them via statements on Snowflake.                                                                                                                                                                                                                                                                                                                                                                                                      |
| S3 Bucket Region               | The S3 staging bucket region used.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| S3 Key Id \*                   | The Access Key ID granting access to the S3 staging bucket. Airbyte requires Read and Write permissions for the bucket.                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| S3 Access Key \*               | The corresponding secret to the S3 Key ID.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Stream Part Size (Optional)    | Increase this if syncing tables larger than 100GB. Files are streamed to S3 in parts. This determines the size of each part, in MBs. As S3 has a limit of 10,000 parts per file, part size affects the table size. This is 5MB by default, resulting in a default limit of 100GB tables. <br/>Note, a larger part size will result in larger memory requirements. A rule of thumb is to multiply the part size by 10 to get the memory requirement. Modify this with care. (e.g. 5)                                                                     |
| Purge Staging Files and Tables | Determines whether to delete the staging files from S3 after completing the sync. Specifically, the connector will create CSV files named `bucketPath/namespace/streamName/syncDate_epochMillis_randomUuid.csv` containing three columns (`ab_id`, `data`, `emitted_at`). Normally these files are deleted after sync; if you want to keep them for other purposes, set `purge_staging_data` to false.                                                                                                                                                  |
| Encryption                     | Whether files on S3 are encrypted. You probably don't need to enable this, but it can provide an additional layer of security if you are sharing your data storage with other applications. If you do use encryption, you must choose between ephemeral keys (Airbyte will automatically generate a new key for each sync, and nobody but Airbyte and Snowflake will be able to read the data on S3) or providing your own key (if you have the "Purge staging files and tables" option disabled, and you want to be able to decrypt the data yourself) |
| S3 Filename pattern (Optional) | The pattern allows you to set the file-name format for the S3 staging file(s), next placeholders combinations are currently supported: {date}, {date:yyyy_MM}, {timestamp}, {timestamp:millis}, {timestamp:micros}, {part_number}, {sync_id}, {format_extension}. Please, don't use empty space and not supportable placeholders, as they won't recognized.                                                                                                                                                                                             |

To use a Google Cloud Storage bucket, enter the information for the bucket you created in Step 2:

| Field                          | Description                                                                                                                                                                                                                                                                                                                                                                                          |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| GCP Project ID                 | The name of the GCP project ID for your credentials. (Example: `my-project`)                                                                                                                                                                                                                                                                                                                         |
| GCP Bucket Name                | The name of the staging bucket. Airbyte will write files to this bucket and read them via statements on Snowflake. (Example: `airbyte-staging`)                                                                                                                                                                                                                                                      |
| Google Application Credentials | The contents of the JSON key file that has read/write permissions to the staging GCS bucket. You will separately need to grant bucket access to your Snowflake GCP service account. See the [Google Cloud docs](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) for more information on how to generate a JSON key for your service account. |

## Output schema

Airbyte outputs each stream into its own table with the following columns in Snowflake:

| Airbyte field        | Description                                                    | Column type              |
|----------------------|----------------------------------------------------------------|--------------------------|
| \_airbyte_ab_id      | A UUID assigned to each processed event                        | VARCHAR                  |
| \_airbyte_emitted_at | A timestamp for when the event was pulled from the data source | TIMESTAMP WITH TIME ZONE |
| \_airbyte_data       | A JSON blob with the event data.                               | VARIANT                  |

**Note:** By default, Airbyte creates permanent tables. If you prefer transient tables, create a dedicated transient database for Airbyte. For more information, refer to [Working with Temporary and Transient Tables](https://docs.snowflake.com/en/user-guide/tables-temp-transient.html)

## Supported sync modes

The Snowflake destination supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Changelog

| Version         | Date       | Pull Request                                               | Subject                                                                                                                                                         |
|:----------------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.1.0           | 2023-10-17 | <!-- TODO: PR Link --> | New experimental connector for bulk load. |
