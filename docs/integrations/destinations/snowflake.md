# Snowflake

Setting up the Snowflake destination connector involves setting up Snowflake entities (warehouse, database, schema, user, and role) in the Snowflake console, setting up the data loading method (internal stage, AWS S3, or Google Cloud Storage bucket), and configuring the Snowflake destination connector using the Airbyte UI.

This page describes the step-by-step process of setting up the Snowflake destination connector.

## Prerequisites

- A Snowflake account with the [ACCOUNTADMIN](https://docs.snowflake.com/en/user-guide/security-access-control-considerations.html) role. If you don’t have an account with the `ACCOUNTADMIN` role, contact your Snowflake administrator to set one up for you.
- (Optional) An AWS, or Google Cloud Storage.

### Network policies

By default, Snowflake allows users to connect to the service from any computer or device IP address. A security administrator (i.e. users with the SECURITYADMIN role) or higher can create a network policy to allow or deny access to a single IP address or a list of addresses.

If you have any issues connecting with Airbyte Cloud please make sure that the list of IP addresses is on the allowed list

To determine whether a network policy is set on your account or for a specific user, execute the _SHOW PARAMETERS_ command.

**Account**

        SHOW PARAMETERS LIKE 'network_policy' IN ACCOUNT;

**User**

        SHOW PARAMETERS LIKE 'network_policy' IN USER <username>;

To read more please check official [Snowflake documentation](https://docs.snowflake.com/en/user-guide/network-policies.html#)

## Setup guide

### Step 1: Set up Airbyte-specific entities in Snowflake

To set up the Snowflake destination connector, you first need to create Airbyte-specific Snowflake entities (a warehouse, database, schema, user, and role) with the `OWNERSHIP` permission to write data into Snowflake, track costs pertaining to Airbyte, and control permissions at a granular level.

You can use the following script in a new [Snowflake worksheet](https://docs.snowflake.com/en/user-guide/ui-worksheet.html) to create the entities:

1.  [Log into your Snowflake account](https://www.snowflake.com/login/).
2.  Edit the following script to change the password to a more secure password and to change the names of other resources if you so desire.

    **Note:** Make sure you follow the [Snowflake identifier requirements](https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html) while renaming the resources.

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

3.  Run the script using the [Worksheet page](https://docs.snowflake.com/en/user-guide/ui-worksheet.html) or [Snowsight](https://docs.snowflake.com/en/user-guide/ui-snowsight-gs.html). Make sure to select the **All Queries** checkbox.

### Step 2: Set up a data loading method

By default, Airbyte uses Snowflake’s [Internal Stage](https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage.html) to load data. You can also load data using an [Amazon S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html), or [Google Cloud Storage bucket](https://cloud.google.com/storage/docs/introduction).

Make sure the database and schema have the `USAGE` privilege.

#### Using an Amazon S3 bucket

To use an Amazon S3 bucket, [create a new Amazon S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) with read/write access for Airbyte to stage data to Snowflake.

#### Using a Google Cloud Storage bucket

To use a Google Cloud Storage bucket:

1. Navigate to the Google Cloud Console and [create a new bucket](https://cloud.google.com/storage/docs/creating-buckets) with read/write access for Airbyte to stage data to Snowflake.
2. [Generate a JSON key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) for your service account.
3. Edit the following script to replace `AIRBYTE_ROLE` with the role you used for Airbyte's Snowflake configuration and `YOURBUCKETNAME` with your bucket name.

   ```text
   create storage INTEGRATION gcs_airbyte_integration
     TYPE = EXTERNAL_STAGE
     STORAGE_PROVIDER = GCS
     ENABLED = TRUE
     STORAGE_ALLOWED_LOCATIONS = ('gcs://YOURBUCKETNAME');

   create stage gcs_airbyte_stage
     url = 'gcs://YOURBUCKETNAME'
     storage_integration = gcs_airbyte_integration;

   GRANT USAGE ON integration gcs_airbyte_integration TO ROLE AIRBYTE_ROLE;
   GRANT USAGE ON stage gcs_airbyte_stage TO ROLE AIRBYTE_ROLE;

   DESC STORAGE INTEGRATION gcs_airbyte_integration;
   ```

   The final query should show a `STORAGE_GCP_SERVICE_ACCOUNT` property with an email as the property value. Add read/write permissions to your bucket with that email.

4. Navigate to the Snowflake UI and run the script as a [Snowflake account admin](https://docs.snowflake.com/en/user-guide/security-access-control-considerations.html) using the [Worksheet page](https://docs.snowflake.com/en/user-guide/ui-worksheet.html) or [Snowsight](https://docs.snowflake.com/en/user-guide/ui-snowsight-gs.html).

### Step 3: Set up Snowflake as a destination in Airbyte

Navigate to the Airbyte UI to set up Snowflake as a destination. You can authenticate using username/password or OAuth 2.0:

### Login and Password

| Field                                                                                                 | Description                                                                                                                                                                                       |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
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
| :---------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
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
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
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
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GCP Project ID                 | The name of the GCP project ID for your credentials. (Example: `my-project`)                                                                                                                                                                                                                                                                                                                         |
| GCP Bucket Name                | The name of the staging bucket. Airbyte will write files to this bucket and read them via statements on Snowflake. (Example: `airbyte-staging`)                                                                                                                                                                                                                                                      |
| Google Application Credentials | The contents of the JSON key file that has read/write permissions to the staging GCS bucket. You will separately need to grant bucket access to your Snowflake GCP service account. See the [Google Cloud docs](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys) for more information on how to generate a JSON key for your service account. |

## Output schema

Airbyte outputs each stream into its own table with the following columns in Snowflake:

| Airbyte field        | Description                                                    | Column type              |
| -------------------- | -------------------------------------------------------------- | ------------------------ |
| \_airbyte_ab_id      | A UUID assigned to each processed event                        | VARCHAR                  |
| \_airbyte_emitted_at | A timestamp for when the event was pulled from the data source | TIMESTAMP WITH TIME ZONE |
| \_airbyte_data       | A JSON blob with the event data.                               | VARIANT                  |

**Note:** By default, Airbyte creates permanent tables. If you prefer transient tables, create a dedicated transient database for Airbyte. For more information, refer to[ Working with Temporary and Transient Tables](https://docs.snowflake.com/en/user-guide/tables-temp-transient.html)

## Supported sync modes

The Snowflake destination supports the following sync modes:

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Snowflake tutorials

Now that you have set up the Snowflake destination connector, check out the following Snowflake tutorials:

- [Build a data ingestion pipeline from Mailchimp to Snowflake](https://airbyte.com/tutorials/data-ingestion-pipeline-mailchimp-snowflake)
- [Replicate data from a PostgreSQL database to Snowflake](https://airbyte.com/tutorials/postgresql-database-to-snowflake)
- [Migrate your data from Redshift to Snowflake](https://airbyte.com/tutorials/redshift-to-snowflake)
- [Orchestrate ELT pipelines with Prefect, Airbyte and dbt](https://airbyte.com/tutorials/elt-pipeline-prefect-airbyte-dbt)

## Troubleshooting

### 'Current role does not have permissions on the target schema'

If you receive an error stating `Current role does not have permissions on the target schema` make sure that the
Snowflake destination `SCHEMA` is one that the role you've provided has permissions on. When creating a connection,
it may allow you to select `Mirror source structure` for the `Destination namespace`, which if you have followed
some of our default examples and tutorials may result in the connection trying to write to a `PUBLIC` schema.

A quick fix could be to edit your connection's 'Replication' settings from `Mirror source structure` to `Destination Default`.
Otherwise, make sure to grant the role the required permissions in the desired namespace.

## Changelog

| Version         | Date       | Pull Request                                               | Subject                                                                                                                                             |
|:----------------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.2.0           | 2023-07--5 | [\#27935](https://github.com/airbytehq/airbyte/pull/27935) | Enable Faster Snowflake Syncs with Asynchronous writes                                                                                               |
| 1.1.0           | 2023-06-27 | [\#27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2                                                                                                                                |
| 1.0.6           | 2023-06-21 | [\#27555](https://github.com/airbytehq/airbyte/pull/27555) | Reduce image size                                                                                                                                   |
| 1.0.5           | 2023-05-31 | [\#25782](https://github.com/airbytehq/airbyte/pull/25782) | Internal scaffolding for future development                                                                                                         |
| 1.0.4           | 2023-05-19 | [\#26323](https://github.com/airbytehq/airbyte/pull/26323) | Prevent infinite retry loop under specific circumstances                                                                                            |
| 1.0.3           | 2023-05-15 | [\#26081](https://github.com/airbytehq/airbyte/pull/26081) | Reverts splits bases                                                                                                                                |
| 1.0.2           | 2023-05-05 | [\#25649](https://github.com/airbytehq/airbyte/pull/25649) | Splits bases (reverted)                                                                                                                             |
| 1.0.1           | 2023-04-29 | [\#25570](https://github.com/airbytehq/airbyte/pull/25570) | Internal library update                                                                                                                             |
| 1.0.0           | 2023-05-02 | [\#25739](https://github.com/airbytehq/airbyte/pull/25739) | Removed Azure Blob Storage as a loading method                                                                                                      |
| 0.4.63          | 2023-04-27 | [\#25346](https://github.com/airbytehq/airbyte/pull/25346) | Added FlushBufferFunction interface                                                                                                                 |
| 0.4.61          | 2023-03-30 | [\#24736](https://github.com/airbytehq/airbyte/pull/24736) | Improve behavior when throttled by AWS API                                                                                                          |
| 0.4.60          | 2023-03-30 | [\#24698](https://github.com/airbytehq/airbyte/pull/24698) | Add option in spec to allow increasing the stream buffer size to 50                                                                                 |
| 0.4.59          | 2023-03-23 | [\#23904](https://github.com/airbytehq/airbyte/pull/24405) | Fail faster in certain error cases                                                                                                                  |
| 0.4.58          | 2023-03-27 | [\#24615](https://github.com/airbytehq/airbyte/pull/24615) | Fixed host validation by pattern on UI                                                                                                              |
| 0.4.56 (broken) | 2023-03-22 | [\#23904](https://github.com/airbytehq/airbyte/pull/23904) | Added host validation by pattern on UI                                                                                                              |
| 0.4.54          | 2023-03-17 | [\#23788](https://github.com/airbytehq/airbyte/pull/23788) | S3-Parquet: added handler to process null values in arrays                                                                                          |
| 0.4.53          | 2023-03-15 | [\#24058](https://github.com/airbytehq/airbyte/pull/24058) | added write attempt to internal staging Check method                                                                                                |
| 0.4.52          | 2023-03-10 | [\#23931](https://github.com/airbytehq/airbyte/pull/23931) | Added support for periodic buffer flush                                                                                                             |
| 0.4.51          | 2023-03-10 | [\#23466](https://github.com/airbytehq/airbyte/pull/23466) | Changed S3 Avro type from Int to Long                                                                                                               |
| 0.4.49          | 2023-02-27 | [\#23360](https://github.com/airbytehq/airbyte/pull/23360) | Added logging for flushing and writing data to destination storage                                                                                  |
| 0.4.48          | 2023-02-23 | [\#22877](https://github.com/airbytehq/airbyte/pull/22877) | Add handler for IP not in whitelist error and more handlers for insufficient permission error                                                       |
| 0.4.47          | 2023-01-30 | [\#21912](https://github.com/airbytehq/airbyte/pull/21912) | Catch "Create" Table and Stage Known Permissions and rethrow as ConfigExceptions                                                                    |
| 0.4.46          | 2023-01-26 | [\#20631](https://github.com/airbytehq/airbyte/pull/20631) | Added support for destination checkpointing with staging                                                                                            |
| 0.4.45          | 2023-01-25 | [\#21087](https://github.com/airbytehq/airbyte/pull/21764) | Catch Known Permissions and rethrow as ConfigExceptions                                                                                             |
| 0.4.44          | 2023-01-20 | [\#21087](https://github.com/airbytehq/airbyte/pull/21087) | Wrap Authentication Errors as Config Exceptions                                                                                                     |
| 0.4.43          | 2023-01-20 | [\#21450](https://github.com/airbytehq/airbyte/pull/21450) | Updated Check methods to handle more possible s3 and gcs stagings issues                                                                            |
| 0.4.42          | 2023-01-12 | [\#21342](https://github.com/airbytehq/airbyte/pull/21342) | Better handling for conflicting destination streams                                                                                                 |
| 0.4.41          | 2022-12-16 | [\#20566](https://github.com/airbytehq/airbyte/pull/20566) | Improve spec to adhere to standards                                                                                                                 |
| 0.4.40          | 2022-11-11 | [\#19302](https://github.com/airbytehq/airbyte/pull/19302) | Set jdbc application env variable depends on env - airbyte_oss or airbyte_cloud                                                                     |
| 0.4.39          | 2022-11-09 | [\#18970](https://github.com/airbytehq/airbyte/pull/18970) | Updated "check" connection method to handle more errors                                                                                             |
| 0.4.38          | 2022-09-26 | [\#17115](https://github.com/airbytehq/airbyte/pull/17115) | Added connection string identifier                                                                                                                  |
| 0.4.37          | 2022-09-21 | [\#16839](https://github.com/airbytehq/airbyte/pull/16839) | Update JDBC driver for Snowflake to 3.13.19                                                                                                         |
| 0.4.36          | 2022-09-14 | [\#15668](https://github.com/airbytehq/airbyte/pull/15668) | Wrap logs in AirbyteLogMessage                                                                                                                      |
| 0.4.35          | 2022-09-01 | [\#16243](https://github.com/airbytehq/airbyte/pull/16243) | Fix Json to Avro conversion when there is field name clash from combined restrictions (`anyOf`, `oneOf`, `allOf` fields).                           |
| 0.4.34          | 2022-07-23 | [\#14388](https://github.com/airbytehq/airbyte/pull/14388) | Add support for key pair authentication                                                                                                             |
| 0.4.33          | 2022-07-15 | [\#14494](https://github.com/airbytehq/airbyte/pull/14494) | Make S3 output filename configurable.                                                                                                               |
| 0.4.32          | 2022-07-14 | [\#14618](https://github.com/airbytehq/airbyte/pull/14618) | Removed additionalProperties: false from JDBC destination connectors                                                                                |
| 0.4.31          | 2022-07-07 | [\#13729](https://github.com/airbytehq/airbyte/pull/13729) | Improve configuration field description                                                                                                             |
| 0.4.30          | 2022-06-24 | [\#14114](https://github.com/airbytehq/airbyte/pull/14114) | Remove "additionalProperties": false from specs for connectors with staging                                                                         |
| 0.4.29          | 2022-06-17 | [\#13753](https://github.com/airbytehq/airbyte/pull/13753) | Deprecate and remove PART_SIZE_MB fields from connectors based on StreamTransferManager                                                             |
| 0.4.28          | 2022-05-18 | [\#12952](https://github.com/airbytehq/airbyte/pull/12952) | Apply buffering strategy on GCS staging                                                                                                             |
| 0.4.27          | 2022-05-17 | [\#12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance                                                                                                              |
| 0.4.26          | 2022-05-12 | [\#12805](https://github.com/airbytehq/airbyte/pull/12805) | Updated to latest base-java to emit AirbyteTraceMessages on error.                                                                                  |
| 0.4.25          | 2022-05-03 | [\#12452](https://github.com/airbytehq/airbyte/pull/12452) | Add support for encrypted staging on S3; fix the purge_staging_files option                                                                         |
| 0.4.24          | 2022-03-24 | [\#11093](https://github.com/airbytehq/airbyte/pull/11093) | Added OAuth support (Compatible with Airbyte Version 0.35.60+)                                                                                      |
| 0.4.22          | 2022-03-18 | [\#10793](https://github.com/airbytehq/airbyte/pull/10793) | Fix namespace with invalid characters                                                                                                               |
| 0.4.21          | 2022-03-18 | [\#11071](https://github.com/airbytehq/airbyte/pull/11071) | Switch to compressed on-disk buffering before staging to s3/internal stage                                                                          |
| 0.4.20          | 2022-03-14 | [\#10341](https://github.com/airbytehq/airbyte/pull/10341) | Add Azure blob staging support                                                                                                                      |
| 0.4.19          | 2022-03-11 | [\#10699](https://github.com/airbytehq/airbyte/pull/10699) | Added unit tests                                                                                                                                    |
| 0.4.17          | 2022-02-25 | [\#10421](https://github.com/airbytehq/airbyte/pull/10421) | Refactor JDBC parameters handling                                                                                                                   |
| 0.4.16          | 2022-02-25 | [\#10627](https://github.com/airbytehq/airbyte/pull/10627) | Add try catch to make sure all handlers are closed                                                                                                  |
| 0.4.15          | 2022-02-22 | [\#10459](https://github.com/airbytehq/airbyte/pull/10459) | Add FailureTrackingAirbyteMessageConsumer                                                                                                           |
| 0.4.14          | 2022-02-17 | [\#10394](https://github.com/airbytehq/airbyte/pull/10394) | Reduce memory footprint.                                                                                                                            |
| 0.4.13          | 2022-02-16 | [\#10212](https://github.com/airbytehq/airbyte/pull/10212) | Execute COPY command in parallel for S3 and GCS staging                                                                                             |
| 0.4.12          | 2022-02-15 | [\#10342](https://github.com/airbytehq/airbyte/pull/10342) | Use connection pool, and fix connection leak.                                                                                                       |
| 0.4.11          | 2022-02-14 | [\#9920](https://github.com/airbytehq/airbyte/pull/9920)   | Updated the size of staging files for S3 staging. Also, added closure of S3 writers to staging files when data has been written to an staging file. |
| 0.4.10          | 2022-02-14 | [\#10297](https://github.com/airbytehq/airbyte/pull/10297) | Halve the record buffer size to reduce memory consumption.                                                                                          |
| 0.4.9           | 2022-02-14 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `ExitOnOutOfMemoryError` JVM flag.                                                                                                              |
| 0.4.8           | 2022-02-01 | [\#9959](https://github.com/airbytehq/airbyte/pull/9959)   | Fix null pointer exception from buffered stream consumer.                                                                                           |
| 0.4.7           | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745)   | Integrate with Sentry.                                                                                                                              |
| 0.4.6           | 2022-01-28 | [\#9623](https://github.com/airbytehq/airbyte/pull/9623)   | Add jdbc_url_params support for optional JDBC parameters                                                                                            |
| 0.4.5           | 2021-12-29 | [\#9184](https://github.com/airbytehq/airbyte/pull/9184)   | Update connector fields title/description                                                                                                           |
| 0.4.4           | 2022-01-24 | [\#9743](https://github.com/airbytehq/airbyte/pull/9743)   | Fixed bug with dashes in schema name                                                                                                                |
| 0.4.3           | 2022-01-20 | [\#9531](https://github.com/airbytehq/airbyte/pull/9531)   | Start using new S3StreamCopier and expose the purgeStagingData option                                                                               |
| 0.4.2           | 2022-01-10 | [\#9141](https://github.com/airbytehq/airbyte/pull/9141)   | Fixed duplicate rows on retries                                                                                                                     |
| 0.4.1           | 2021-01-06 | [\#9311](https://github.com/airbytehq/airbyte/pull/9311)   | Update сreating schema during check                                                                                                                 |
| 0.4.0           | 2021-12-27 | [\#9063](https://github.com/airbytehq/airbyte/pull/9063)   | Updated normalization to produce permanent tables                                                                                                   |
| 0.3.24          | 2021-12-23 | [\#8869](https://github.com/airbytehq/airbyte/pull/8869)   | Changed staging approach to Byte-Buffered                                                                                                           |
| 0.3.23          | 2021-12-22 | [\#9039](https://github.com/airbytehq/airbyte/pull/9039)   | Added part_size configuration in UI for S3 loading method                                                                                           |
| 0.3.22          | 2021-12-21 | [\#9006](https://github.com/airbytehq/airbyte/pull/9006)   | Updated jdbc schema naming to follow Snowflake Naming Conventions                                                                                   |
| 0.3.21          | 2021-12-15 | [\#8781](https://github.com/airbytehq/airbyte/pull/8781)   | Updated check method to verify permissions to create/drop stage for internal staging; compatibility fix for Java 17                                 |
| 0.3.20          | 2021-12-10 | [\#8562](https://github.com/airbytehq/airbyte/pull/8562)   | Moving classes around for better dependency management; compatibility fix for Java 17                                                               |
| 0.3.19          | 2021-12-06 | [\#8528](https://github.com/airbytehq/airbyte/pull/8528)   | Set Internal Staging as default choice                                                                                                              |
| 0.3.18          | 2021-11-26 | [\#8253](https://github.com/airbytehq/airbyte/pull/8253)   | Snowflake Internal Staging Support                                                                                                                  |
| 0.3.17          | 2021-11-08 | [\#7719](https://github.com/airbytehq/airbyte/pull/7719)   | Improve handling of wide rows by buffering records based on their byte size rather than their count                                                 |
| 0.3.15          | 2021-10-11 | [\#6949](https://github.com/airbytehq/airbyte/pull/6949)   | Each stream was split into files of 10,000 records each for copying using S3 or GCS                                                                 |
| 0.3.14          | 2021-09-08 | [\#5924](https://github.com/airbytehq/airbyte/pull/5924)   | Fixed AWS S3 Staging COPY is writing records from different table in the same raw table                                                             |
| 0.3.13          | 2021-09-01 | [\#5784](https://github.com/airbytehq/airbyte/pull/5784)   | Updated query timeout from 30 minutes to 3 hours                                                                                                    |
| 0.3.12          | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                                                                                        |
| 0.3.11          | 2021-07-21 | [\#3555](https://github.com/airbytehq/airbyte/pull/3555)   | Partial Success in BufferedStreamConsumer                                                                                                           |
| 0.3.10          | 2021-07-12 | [\#4713](https://github.com/airbytehq/airbyte/pull/4713)   | Tag traffic with `airbyte` label to enable optimization opportunities from Snowflake                                                                |
