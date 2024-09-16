# Yellowbrick

This page guides you through the process of setting up the Yellowbrick destination connector.

## Prerequisites

Airbyte Cloud only supports connecting to your Yellowbrick instances with SSL or TLS encryption. TLS is
used by default. Other than that, you can proceed with the open-source instructions below.

You'll need the following information to configure the Yellowbrick destination:

- **Host** - The host name of the server.
- **Port** - The port number the server is listening on. Defaults to the PostgreSQL™ standard port number (5432).
- **Username**
- **Password**
- **Default Schema Name** - Specify the schema (or several schemas separated by commas) to be set in the search-path. These schemas will be used to resolve unqualified object names used in statements executed over this connection.
- **Database** - The database name. The default is to connect to a database with the same name as the user name.
- **JDBC URL Params** (optional)

[Refer to this guide for more details](https://docs.yellowbrick.com/6.9.0/client_tools/setup_database_connection.html)

#### Configure Network Access

Make sure your Yellowbrick database can be accessed by Airbyte. If your database is within a VPC, you
may need to allow access from the IP you're using to expose Airbyte.

## Step 1: Set up Yellowbrick

#### **Permissions**

You need a Yellowbrick user with the following permissions:

- can create tables and write rows.
- can create schemas e.g:

You can create such a user by running:

```
CREATE USER airbyte_user WITH ENCRYPTED PASSWORD '<password>';
GRANT CREATE, TEMPORARY ON DATABASE <database> TO airbyte_user;
```

You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.

## Step 2: Set up the Yellowbrick connector in Airbyte

#### Target Database

You will need to choose an existing database or create a new database that will be used to store
synced data from Airbyte.

## Naming Conventions

From [Yellowbrick SQL Identifiers syntax](https://docs.yellowbrick.com/6.9.0/ybd_sqlref/sql_identifiers.html#sql-identifiers-1)

Note the following restrictions on unquoted SQL identifiers:

- SQL identifiers that are not quoted must begin with a letter (a-z) or an underscore (_). The pg_ prefix is also disallowed and reserved for system objects.
- Subsequent characters in an unquoted identifier can be letters, digits (0-9), or underscores. Unquoted SQL identifiers are case-insensitive.
- Special characters such as #, $, and so on, are not allowed anywhere in an unquoted identifier.
- Unquoted SQL identifiers are case-insensitive.
- Quoted identifiers (or delimited identifiers) are names enclosed in double quotes ("). Quoted identifiers are case-sensitive. By using quoted identifiers, you can create object names that contain explicit uppercase and lowercase letters, as well as special characters. However, you cannot use double quotes within object names.
- Space characters are not allowed in database names.

:::info

Airbyte Yellowbrick destination will create raw tables and schemas using the Unquoted
identifiers by replacing any special characters with an underscore. All final tables and their corresponding
columns are created using Quoted identifiers preserving the case sensitivity.

:::

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **new destination**.
3. On the Set up the destination page, enter the name for the Yellowbrick connector
   and select **Yellowbrick** from the Destination type dropdown.
4. Enter a name for your source.
5. For the **Host**, **Port**, and **DB Name**, enter the hostname, port number, and name for your Yellowbrick database.
6. List the **Default Schemas**.
   :::note
   The schema names are case sensitive. The 'public' schema is set by default. Multiple schemas may be used at one time. No schemas set explicitly - will sync all of existing.
   :::
7. For **User** and **Password**, enter the username and password you created in [Step 1](#step-1-optional-create-a-dedicated-read-only-user).
8. For Airbyte Open Source, toggle the switch to connect using SSL. For Airbyte Cloud uses SSL by default.
9. For SSL Modes, select:
   - **disable** to disable encrypted communication between Airbyte and the source
   - **allow** to enable encrypted communication only when required by the source
   - **prefer** to allow unencrypted communication only when the source doesn't support encryption
   - **require** to always require encryption. Note: The connection will fail if the source doesn't support encryption.
   - **verify-ca** to always require encryption and verify that the source has a valid SSL certificate
   - **verify-full** to always require encryption and verify the identity of the source
10. To customize the JDBC connection beyond common options, specify additional supported [JDBC URL parameters](https://jdbc.postgresql.org/documentation/head/connect.html) as key-value pairs separated by the symbol & in the **JDBC URL Parameters (Advanced)** field.

    Example: key1=value1&key2=value2&key3=value3

    These parameters will be added at the end of the JDBC URL that the AirByte will use to connect to your Yellowbrick database.

    The connector now supports `connectTimeout` and defaults to 60 seconds. Setting connectTimeout to 0 seconds will set the timeout to the longest time available.

    **Note:** Do not use the following keys in JDBC URL Params field as they will be overwritten by Airbyte:
    `currentSchema`, `user`, `password`, `ssl`, and `sslmode`.

    :::warning
    This is an advanced configuration option. Users are advised to use it with caution.
    :::

11. For SSH Tunnel Method, select:

    - **No Tunnel** for a direct connection to the database
    - **SSH Key Authentication** to use an RSA Private as your secret for establishing the SSH tunnel
    - **Password Authentication** to use a password as your secret for establishing the SSH tunnel

    :::warning
    Since Airbyte Cloud requires encrypted communication, select **SSH Key Authentication** or **Password Authentication** if you selected **disable**, **allow**, or **prefer** as the **SSL Mode**; otherwise, the connection will fail.
    :::

12. Click **Set up destination**.

## Supported sync modes

The Yellowbrick destination connector supports the
following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |
| Namespaces                     | Yes                  |       |

## Schema map

### Output Schema (Raw Tables)

Each stream will be mapped to a separate raw table in Yellowbrick. The default schema in which the raw tables are
created is `airbyte_internal`. This can be overridden in the configuration.
Each table will contain 3 columns:

- `_airbyte_raw_id`: a uuid assigned by Airbyte to each event that is processed. The column type in
  Yellowbrick is `VARCHAR`.
- `_airbyte_extracted_at`: a timestamp representing when the event was pulled from the data source.
  The column type in Yellowbrick is `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_loaded_at`: a timestamp representing when the row was processed into final table.
  The column type in Yellowbrick is `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_data`: a json blob representing with the event data. The column type in Yellowbrick
  is `JSONB`.

### Final Tables Data type mapping

| Airbyte Type               | Yellowbrick Type         |
| :------------------------- | :----------------------- |
| string                     | VARCHAR                  |
| number                     | DECIMAL                  |
| integer                    | BIGINT                   |
| boolean                    | BOOLEAN                  |
| object                     | VARCHAR                  |
| array                      | VARCHAR                  |
| timestamp_with_timezone    | TIMESTAMP WITH TIME ZONE |
| timestamp_without_timezone | TIMESTAMP                |
| time_with_timezone         | TIME WITH TIME ZONE      |
| time_without_timezone      | TIME                     |
| date                       | DATE                     |

## Tutorials

- Comming soon.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject         |
| :------ | :--------- | :--------------------------------------------------------- | :-------------- |
| 0.0.3 | 2024-08-06 | [\#43342](https://github.com/airbytehq/airbyte/pull/43342) | Remove explicit Kotlin dependency. |
| 0.0.2   | 2024-05-17 | [\#38329](https://github.com/airbytehq/airbyte/pull/38329) | Update CDK      |
| 0.0.1   | 2024-03-02 | [\#35775](https://github.com/airbytehq/airbyte/pull/35775) | Initial release |

</details>
