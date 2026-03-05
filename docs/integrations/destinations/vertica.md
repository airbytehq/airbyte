# vertica

This page guides you through the process of setting up the vertica destination connector.

## Prerequisites

To use the Vertica destination, you'll need:

- A V
  ertica server version 11.0 or above

Airbyte Cloud only supports connecting to your Vertica instances with SSL or TLS encryption. TLS is
used by default. Other than that, you can proceed with the open-source instructions below.

You'll need the following information to configure the Vertica destination:

- **Host** - The host name of the server.
- **Port** - The port number the server is listening on. Defaults to the VSQL™ standard port number (5433).
- **Username**
- **Password**
- **Default Schema Name** - Specify the schema (or several schemas separated by commas) to be set in the search-path. These schemas will be used to resolve unqualified object names used in statements executed over this connection.
- **Database** - The database name. The default is to connect to a database with the same name as the user name.
- **JDBC URL Params** (optional)

[Refer to this guide for more details](https://www.vertica.com/docs/12.0.4/HTML/Content/Authoring/ConnectingToVertica/ClientJDBC/JDBCConnectionProperties.htm)

#### Configure Network Access

Make sure your Vertica database can be accessed by Airbyte. If your database is within a VPC, you
may need to allow access from the IP you're using to expose Airbyte.

## Step 1: Set up Vertica

#### **Permissions**

You need a Vertica user with the following permissions:

- can create tables and write rows.
- can create schemas e.g:

You can create such a user by running:

```
CREATE USER airbyte_user WITH PASSWORD '<password>';
GRANT CREATE, TEMPORARY ON DATABASE <database> TO airbyte_user;
```

You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.

## Step 2: Set up the Vertica connector in Airbyte

#### Target Database

You will need to choose an existing database or create a new database that will be used to store
synced data from Airbyte.

## Naming Conventions

From [Vertica SQL Identifiers syntax](https://www.vertica.com/docs/12.0.x/HTML/Content/Authoring/ConnectingToVertica/ClientJDBC/ExecutingQueriesThroughJDBC.htm?tocpath=Connecting%20to%20Vertica%7CClient%20Libraries%7CProgramming%20JDBC%20Client%20Applications%7C_____4):

- SQL identifiers and key words must begin with a letter \(a-z, but also letters with diacritical
  marks and non-Latin letters\) or an underscore \(\_\).
- Subsequent characters in an identifier or key word can be letters, underscores, digits \(0-9\), or
  dollar signs \($\).

  Note that dollar signs are not allowed in identifiers according to the SQL standard,
  so their use might render applications less portable. The SQL standard will not define a key word
  that contains digits or starts or ends with an underscore, so identifiers of this form are safe
  against possible conflict with future extensions of the standard.

- The system uses no more than NAMEDATALEN-1 bytes of an identifier; longer names can be written in
  commands, but they will be truncated. By default, NAMEDATALEN is 64 so the maximum identifier
  length is 63 bytes
- Quoted identifiers can contain any character, except the character with code zero. \(To include a
  double quote, write two double quotes.\) This allows constructing table or column names that would
  otherwise not be possible, such as ones containing spaces or ampersands. The length limitation
  still applies.
- Quoting an identifier also makes it case-sensitive, whereas unquoted names are always folded to
  lower case.
- In order to make your applications portable and less error-prone, use consistent quoting with each name (either always quote it or never quote it).

Note, that Airbyte Vertica destination will create tables and schemas using the Unquoted
identifiers when possible or fallback to Quoted Identifiers if the names are containing special
characters.

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **new destination**.
3. On the Set up the destination page, enter the name for the Vertica connector
   and select **Vertica** from the Destination type dropdown.
4. Enter a name for your source.
5. For the **Host**, **Port**, and **DB Name**, enter the hostname, port number, and name for your Vertica database.
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
10. To customize the JDBC connection beyond common options, specify additional supported [JDBC URL parameters](https://www.vertica.com/docs/12.0.x/HTML/Content/Authoring/ConnectingToVertica/ClientJDBC/JDBCConnectionProperties.htm) as key-value pairs separated by the symbol & in the **JDBC URL Parameters (Advanced)** field.

    Example: key1=value1&key2=value2&key3=value3

    These parameters will be added at the end of the JDBC URL that the AirByte will use to connect to your Vertica database.

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

The Vertica destination connector supports the
following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | No                   |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | No                   |       |

## Schema map

#### Output Schema

Each stream will be mapped to a separate table in Vertica. Each table will contain 3 columns:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in
  Vertica is `VARCHAR`.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
  The column type in Vertica is `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_data`: a json blob representing with the event data. The column type in Vertica
  is `JSONB`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                 |
| :------ | :--------- | :--------------------------------------------------------- | :---------------------- |
| 0.1.0   | 2023-05-29 | [\#25682](https://github.com/airbytehq/airbyte/pull/25682) | Add Vertica Destination |

</details>