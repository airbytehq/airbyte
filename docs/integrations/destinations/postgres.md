# Postgres

## Overview

The Airbyte Postgres destination allows you to sync data to Postgres.

This Postgres destination is based on the [Singer Postgres Target](https://github.com/datamill-co/target-postgres).

### Sync overview

#### Output schema

Each stream will be output into its own table in Postgres. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Postgres is `VARCHAR`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Postgres is `TIMESTAMP WITH TIME ZONE`.
* `_airbyte_data`: a json blob representing with the event data. The column type in Postgres is `JSONB`.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | Yes |  |

## Getting started

### Requirements

To use the Postgres destination, you'll need:

* A Postgres server version 9.4 or above

### Setup guide

#### Network Access

Make sure your Postgres database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a Postgres user that can create tables and write rows. We highly recommend creating an Airbyte-specific user for this purpose.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

### Setup the Postgres destination in Airbyte

You should now have all the requirements needed to configure Postgres as a destination in the UI. You'll need the following information to configure the Postgres destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Schema**
* **Database**
  * This database needs to exist within the schema provided.

## Notes about Postgres Naming Conventions

From [Postgres SQL Identifiers syntax](https://www.postgresql.org/docs/9.0/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS):

* SQL identifiers and key words must begin with a letter \(a-z, but also letters with diacritical marks and non-Latin letters\) or an underscore \(\_\).
* Subsequent characters in an identifier or key word can be letters, underscores, digits \(0-9\), or dollar signs \($\).

  Note that dollar signs are not allowed in identifiers according to the letter of the SQL standard, so their use might render applications less portable. The SQL standard will not define a key word that contains digits or starts or ends with an underscore, so identifiers of this form are safe against possible conflict with future extensions of the standard.

* The system uses no more than NAMEDATALEN-1 bytes of an identifier; longer names can be written in commands, but they will be truncated. By default, NAMEDATALEN is 64 so the maximum identifier length is 63 bytes
* Quoted identifiers can contain any character, except the character with code zero. \(To include a double quote, write two double quotes.\) This allows constructing table or column names that would otherwise not be possible, such as ones containing spaces or ampersands. The length limitation still applies.
* Quoting an identifier also makes it case-sensitive, whereas unquoted names are always folded to lower case.
* If you want to write portable applications you are advised to always quote a particular name or never quote it.

Therefore, Airbyte Postgres destination will create tables and schemas using the Unquoted identifiers when possible or fallback to Quoted Identifiers if the names are containing special characters.

## Changelog
| Version | Date | Pull Request | Subject |
| :--- | :---  | :--- | :--- |
| 0.3.10 | 2021-08-11 | [#5336](https://github.com/airbytehq/airbyte/pull/5336) |  🐛 Destination Postgres: fix \u0000(NULL) value processing |
