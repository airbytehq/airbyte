# Exasol

Exasol is the in-memory database built for analytics.

## Sync overview

### Output schema

Each Airbyte Stream becomes an Exasol table and each Airbyte Field becomes an Exasol column. Each Exasol table created by Airbyte will contain 3 columns:

- `_AIRBYTE_AB_ID`: a uuid assigned by Airbyte to each event that is processed. The column type in Exasol is `VARCHAR(64)`.
- `_AIRBYTE_DATA`: a json blob representing with the event data. The column type in Exasol is `VARCHAR(2000000)`.
- `_AIRBYTE_EMITTED_AT`: a timestamp representing when the event was pulled from the data source. The column type in Exasol is `TIMESTAMP`.

### Features

The Exasol destination supports the following features:

| Feature                        | Supported? (Yes/No) | Notes |
| :----------------------------- | :------------------ | :---- |
| Full Refresh Sync              | Yes                 |       |
| Incremental - Append Sync      | Yes                 |       |
| Incremental - Append + Deduped | No                  |       |
| Normalization                  | No                  |       |
| Namespaces                     | Yes                 |       |
| SSL connection                 | Yes                 | TLS   |
| SSH Tunnel Support             | No                  |       |

### Limitations

#### Maximum data size two million characters

Exasol does not have a special data type for storing data of arbitrary length or JSON. That's why this connector uses type `VARCHAR(2000000)` for storing Airbyte data.

## Getting started

### Requirements

To use the Exasol destination, you'll need Exasol database version 7.1 or above.

#### Network Access

Make sure your Exasol database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

As Airbyte namespaces allow to store data into different schemas, there are different scenarios requiring different permissions assigned to the user account. The following table describes 4 scenarios regarding the login user and the destination user.

| Login user   | Destination user   | Required permissions                                          | Comment                                                                    |
| :----------- | :----------------- | :------------------------------------------------------------ | :------------------------------------------------------------------------- |
| DBA User     | Any user           | -                                                             |                                                                            |
| Regular user | Same user as login | Create, drop and write table, create session                  |                                                                            |
| Regular user | Any existing user  | Create, drop and write ANY table, create session              | Grants can be provided on a system level by DBA or by target user directly |
| Regular user | Not existing user  | Create, drop and write ANY table, create user, create session | Grants should be provided on a system level by DBA                         |

We highly recommend creating an Airbyte-specific user for this purpose.

### Setup guide

You should now have all the requirements needed to configure Exasol as a destination in the UI. You'll need the following information to configure the Exasol destination:

- Host
- Port
- Fingerprint of the Exasol server's TLS certificate (if the database uses a self-signed certificate)
- Username
- Password

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------- |
| 0.1.1   | 2023-02-21 | [xxx](https://github.com/airbytehq/airbyte/pull/xxx)     | Fix the build                             |
| 0.1.0   | 2023-01-?? | [21200](https://github.com/airbytehq/airbyte/pull/21200) | Initial version of the Exasol destination |

</details>