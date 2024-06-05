# Postgres

This page guides you through the process of setting up the Postgres destination connector.

## Warning

:::warning

Postgres, while an excellent relational database, is not a data warehouse. Please only consider using postgres as a destination for small data volumes (e.g. less than 10GB) or for testing purposes. For larger data volumes, we recommend using a data warehouse like BigQuery, Snowflake, or Redshift. Learn more [here](/integrations/destinations/postgres/postgres-troubleshooting#postgres-is-not-a-data-warehouse).

:::

## Prerequisites

To use the Postgres destination, you'll need:

- A Postgres server version 9.5 or above

Airbyte Cloud only supports connecting to your Postgres instances with SSL or TLS encryption. TLS is
used by default. Other than that, you can proceed with the open-source instructions below.

You'll need the following information to configure the Postgres destination:

- **Host** - The host name of the server.
- **Port** - The port number the server is listening on. Defaults to the PostgreSQL™ standard port
  number (5432).
- **Username**
- **Password**
- **Default Schema Name** - Specify the schema (or several schemas separated by commas) to be set in
  the search-path. These schemas will be used to resolve unqualified object names used in statements
  executed over this connection.
- **Database** - The database name. The default is to connect to a database with the same name as
  the user name.
- **JDBC URL Params** (optional)

[Refer to this guide for more details](https://jdbc.postgresql.org/documentation/use/#connecting-to-the-database)

#### Configure Network Access

Make sure your Postgres database can be accessed by Airbyte. If your database is within a VPC, you
may need to allow access from the IP you're using to expose Airbyte.

## Step 1: Set up Postgres

#### **Permissions**

You need a Postgres user with the following permissions:

- can create tables and write rows.
- can create schemas e.g:

You can create such a user by running:

```
CREATE USER airbyte_user WITH PASSWORD '<password>';
GRANT CREATE, TEMPORARY ON DATABASE <database> TO airbyte_user;
```

You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.

## Step 2: Set up the Postgres connector in Airbyte

#### Target Database

You will need to choose an existing database or create a new database that will be used to store
synced data from Airbyte.

## Naming Conventions

From
[Postgres SQL Identifiers syntax](https://www.postgresql.org/docs/9.0/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS):

- SQL identifiers and key words must begin with a letter \(a-z, but also letters with diacritical
  marks and non-Latin letters\) or an underscore \(\_\).
- Subsequent characters in an identifier or key word can be letters, underscores, digits \(0-9\), or
  dollar signs \($\).

  Note that dollar signs are not allowed in identifiers according to the SQL standard, so their use
  might render applications less portable. The SQL standard will not define a key word that contains
  digits or starts or ends with an underscore, so identifiers of this form are safe against possible
  conflict with future extensions of the standard.

- The system uses no more than NAMEDATALEN-1 bytes of an identifier; longer names can be written in
  commands, but they will be truncated. By default, NAMEDATALEN is 64 so the maximum identifier
  length is 63 bytes
- Quoted identifiers can contain any character, except the character with code zero. \(To include a
  double quote, write two double quotes.\) This allows constructing table or column names that would
  otherwise not be possible, such as ones containing spaces or ampersands. The length limitation
  still applies.
- Quoting an identifier also makes it case-sensitive, whereas unquoted names are always folded to
  lower case.
- In order to make your applications portable and less error-prone, use consistent quoting with each
  name (either always quote it or never quote it).

:::info

Airbyte Postgres destination will create raw tables and schemas using the Unquoted identifiers by
replacing any special characters with an underscore. All final tables and their corresponding
columns are created using Quoted identifiers preserving the case sensitivity. Special characters in final
tables are replaced with underscores.

:::

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **new
   destination**.
3. On the Set up the destination page, enter the name for the Postgres connector and select
   **Postgres** from the Destination type dropdown.
4. Enter a name for your source.
5. For the **Host**, **Port**, and **DB Name**, enter the hostname, port number, and name for your
   Postgres database.
6. List the **Default Schemas**.

:::note

The schema names are case sensitive. The 'public' schema is set by default. Multiple schemas may be
used at one time. No schemas set explicitly - will sync all of existing.

:::

7. For **User** and **Password**, enter the username and password you created in
   [Step 1](#step-1-optional-create-a-dedicated-read-only-user).
8. For Airbyte Open Source, toggle the switch to connect using SSL. For Airbyte Cloud uses SSL by
   default.
9. For SSL Modes, select:
   - **disable** to disable encrypted communication between Airbyte and the source
   - **allow** to enable encrypted communication only when required by the source
   - **prefer** to allow unencrypted communication only when the source doesn't support encryption
   - **require** to always require encryption. Note: The connection will fail if the source doesn't
     support encryption.
   - **verify-ca** to always require encryption and verify that the source has a valid SSL
     certificate
   - **verify-full** to always require encryption and verify the identity of the source
10. To customize the JDBC connection beyond common options, specify additional supported
    [JDBC URL parameters](https://jdbc.postgresql.org/documentation/head/connect.html) as key-value
    pairs separated by the symbol & in the **JDBC URL Parameters (Advanced)** field.

    Example: key1=value1&key2=value2&key3=value3

    These parameters will be added at the end of the JDBC URL that the AirByte will use to connect
    to your Postgres database.

    The connector now supports `connectTimeout` and defaults to 60 seconds. Setting connectTimeout
    to 0 seconds will set the timeout to the longest time available.

    **Note:** Do not use the following keys in JDBC URL Params field as they will be overwritten by
    Airbyte: `currentSchema`, `user`, `password`, `ssl`, and `sslmode`.

:::warning

This is an advanced configuration option. Users are advised to use it with caution.

:::

11. For SSH Tunnel Method, select:

    - **No Tunnel** for a direct connection to the database
    - **SSH Key Authentication** to use an RSA Private as your secret for establishing the SSH
      tunnel
    - **Password Authentication** to use a password as your secret for establishing the SSH tunnel

:::warning

Since Airbyte Cloud requires encrypted communication, select **SSH Key Authentication** or
**Password Authentication** if you selected **disable**, **allow**, or **prefer** as the **SSL
Mode**; otherwise, the connection will fail.

:::

12. Click **Set up destination**.

## Supported sync modes

The Postgres destination connector supports the
following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |
| Namespaces                     | Yes                  |       |

## Schema map

### Output Schema (Raw Tables)

Each stream will be mapped to a separate raw table in Postgres. The default schema in which the raw
tables are created is `airbyte_internal`. This can be overridden in the configuration. Each table
will contain 3 columns:

- `_airbyte_raw_id`: a uuid assigned by Airbyte to each event that is processed. The column type in
  Postgres is `VARCHAR`.
- `_airbyte_extracted_at`: a timestamp representing when the event was pulled from the data source.
  The column type in Postgres is `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_loaded_at`: a timestamp representing when the row was processed into final table. The
  column type in Postgres is `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_data`: a json blob representing with the event data. The column type in Postgres is
  `JSONB`.

### Final Tables Data type mapping

| Airbyte Type               | Postgres Type            |
| :------------------------- | :----------------------- |
| string                     | VARCHAR                  |
| number                     | DECIMAL                  |
| integer                    | BIGINT                   |
| boolean                    | BOOLEAN                  |
| object                     | JSONB                    |
| array                      | JSONB                    |
| timestamp_with_timezone    | TIMESTAMP WITH TIME ZONE |
| timestamp_without_timezone | TIMESTAMP                |
| time_with_timezone         | TIME WITH TIME ZONE      |
| time_without_timezone      | TIME                     |
| date                       | DATE                     |

### Naming limitations

Postgres restricts all identifiers to 63 characters or less. If your stream includes column names
longer than 63 characters, they will be truncated to this length. If this results in two columns
having the same name, Airbyte may modify these column names to avoid the collision.

## Creating dependent objects

:::caution

This section involves running `DROP ... CASCADE` on the tables that Airbyte produces. Make sure you
fully understand the consequences before enabling this option. **Permanent** data loss is possible
with this option!

:::

You may want to create objects that depend on the tables generated by Airbyte, such as views. If you
do so, we strongly recommend:

- Using a tool like `dbt` to automate the creation
- And using an orchestrator to trigger `dbt`.

This is because you will need to enable the "Drop tables with CASCADE" option. The connector
sometimes needs to recreate the tables; if you have created dependent objects, Postgres will require
the connector to run drop statements with CASCADE enabled. However, this will cause the connector to
**also drop the dependent objects**. Therefore, you MUST have a way to recreate those dependent
objects from scratch.

## Tutorials

Now that you have set up the Postgres destination connector, check out the following tutorials:

- [Migrate from mysql to postgres](https://airbyte.com/tutorials/migrate-from-mysql-to-postgresql)
- [Postgres replication](https://airbyte.com/tutorials/postgres-replication)

## Vendor-Specific Connector Limitations

:::warning

Not all implementations or deployments of a database will be the same. This section lists specific limitations and known issues with the connector based on _how_ or
_where_ it is deployed.

:::

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                  |
| :------ | :--------- | :--------------------------------------------------------- | :------------------------------------------------------------------------------------------------------- |
| 2.0.10  | 2024-05-07 | [\#37660](https://github.com/airbytehq/airbyte/pull/37660) | Adopt CDK 0.33.2                                                                                         |
| 2.0.9   | 2024-04-11 | [\#36974](https://github.com/airbytehq/airbyte/pull/36974) | Add option to drop with `CASCADE`                                                                        |
| 2.0.8   | 2024-04-10 | [\#36805](https://github.com/airbytehq/airbyte/pull/36805) | Adopt CDK 0.29.10 to improve long column name handling                                                   |
| 2.0.7   | 2024-04-08 | [\#36768](https://github.com/airbytehq/airbyte/pull/36768) | Adopt CDK 0.29.7 to improve destination state handling                                                   |
| 2.0.6   | 2024-04-05 | [\#36620](https://github.com/airbytehq/airbyte/pull/36620) | Adopt CDK 0.29.3 to use Kotlin CDK                                                                       |
| 2.0.5   | 2024-03-07 | [\#35899](https://github.com/airbytehq/airbyte/pull/35899) | Adopt CDK 0.27.3; Bugfix for case-senstive table names in v1-v2 migration, `_airbyte_meta` in raw tables |
| 2.0.4   | 2024-03-07 | [\#35899](https://github.com/airbytehq/airbyte/pull/35899) | Adopt CDK 0.23.18; Null safety check in state parsing                                                    |
| 2.0.3   | 2024-03-01 | [\#35528](https://github.com/airbytehq/airbyte/pull/35528) | Adopt CDK 0.23.11; Use Migration framework                                                               |
| 2.0.2   | 2024-03-01 | [\#35760](https://github.com/airbytehq/airbyte/pull/35760) | Mark as certified, add PSQL exception to deinterpolator                                                  |
| 2.0.1   | 2024-02-22 | [\#35385](https://github.com/airbytehq/airbyte/pull/35385) | Upgrade CDK to 0.23.0; Gathering required initial state upfront                                          |
| 2.0.0   | 2024-02-09 | [\#35042](https://github.com/airbytehq/airbyte/pull/35042) | GA release V2 destinations format.                                                                       |
| 0.6.3   | 2024-02-06 | [\#34891](https://github.com/airbytehq/airbyte/pull/34891) | Remove varchar limit, use system defaults                                                                |
| 0.6.2   | 2024-01-30 | [\#34683](https://github.com/airbytehq/airbyte/pull/34683) | CDK Upgrade 0.16.3; Fix dependency mismatches in slf4j lib                                               |
| 0.6.1   | 2024-01-29 | [\#34630](https://github.com/airbytehq/airbyte/pull/34630) | CDK Upgrade; Use lowercase raw table in T+D queries.                                                     |
| 0.6.0   | 2024-01-19 | [\#34372](https://github.com/airbytehq/airbyte/pull/34372) | Add dv2 flag in spec                                                                                     |
| 0.5.5   | 2024-01-18 | [\#34236](https://github.com/airbytehq/airbyte/pull/34236) | Upgrade CDK to 0.13.1; Add indexes in raw table for query optimization                                   |
| 0.5.4   | 2024-01-11 | [\#34177](https://github.com/airbytehq/airbyte/pull/34177) | Add code for DV2 beta (no user-visible changes)                                                          |
| 0.5.3   | 2024-01-10 | [\#34135](https://github.com/airbytehq/airbyte/pull/34135) | Use published CDK missed in previous release                                                             |
| 0.5.2   | 2024-01-08 | [\#33875](https://github.com/airbytehq/airbyte/pull/33875) | Update CDK to get Tunnel heartbeats feature                                                              |
| 0.5.1   | 2024-01-04 | [\#33873](https://github.com/airbytehq/airbyte/pull/33873) | Install normalization to enable DV2 beta                                                                 |
| 0.5.0   | 2023-12-18 | [\#33507](https://github.com/airbytehq/airbyte/pull/33507) | Upgrade to latest CDK; Fix DATs and tests                                                                |
| 0.4.0   | 2023-06-27 | [\#27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2                                                                                     |
| 0.3.27  | 2023-04-04 | [\#24604](https://github.com/airbytehq/airbyte/pull/24604) | Support for destination checkpointing                                                                    |
| 0.3.26  | 2022-09-27 | [\#17299](https://github.com/airbytehq/airbyte/pull/17299) | Improve error handling for strict-encrypt postgres destination                                           |
| 0.3.24  | 2022-09-08 | [\#16046](https://github.com/airbytehq/airbyte/pull/16046) | Fix missing database name URL Encoding                                                                   |
| 0.3.23  | 2022-07-18 | [\#16260](https://github.com/airbytehq/airbyte/pull/16260) | Prevent traffic going on an unsecured channel in strict-encryption version of destination postgres       |
| 0.3.22  | 2022-07-18 | [\#13840](https://github.com/airbytehq/airbyte/pull/13840) | Added the ability to connect using different SSL modes and SSL certificates                              |
| 0.3.21  | 2022-07-06 | [\#14479](https://github.com/airbytehq/airbyte/pull/14479) | Publish amd64 and arm64 versions of the connector                                                        |
| 0.3.20  | 2022-05-17 | [\#12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance                                                                   |
| 0.3.19  | 2022-04-25 | [\#12195](https://github.com/airbytehq/airbyte/pull/12195) | Add support for additional JDBC URL Params input                                                         |
| 0.3.18  | 2022-04-12 | [\#11729](https://github.com/airbytehq/airbyte/pull/11514) | Bump mina-sshd from 2.7.0 to 2.8.0                                                                       |
| 0.3.17  | 2022-04-05 | [\#11729](https://github.com/airbytehq/airbyte/pull/11729) | Fixed bug with dashes in schema name                                                                     |
| 0.3.15  | 2022-02-25 | [\#10421](https://github.com/airbytehq/airbyte/pull/10421) | Refactor JDBC parameters handling                                                                        |
| 0.3.14  | 2022-02-14 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256) | (unpublished) Add `-XX:+ExitOnOutOfMemoryError` JVM option                                               |
| 0.3.13  | 2021-12-01 | [\#8371](https://github.com/airbytehq/airbyte/pull/8371)   | Fixed incorrect handling "\n" in ssh key                                                                 |
| 0.3.12  | 2021-11-08 | [\#7719](https://github.com/airbytehq/airbyte/pull/7719)   | Improve handling of wide rows by buffering records based on their byte size rather than their count      |
| 0.3.11  | 2021-09-07 | [\#5743](https://github.com/airbytehq/airbyte/pull/5743)   | Add SSH Tunnel support                                                                                   |
| 0.3.10  | 2021-08-11 | [\#5336](https://github.com/airbytehq/airbyte/pull/5336)   | Destination Postgres: fix \u0000\(NULL\) value processing                                                |

</details>