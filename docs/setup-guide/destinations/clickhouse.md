# ClickHouse

## Prerequisites

### Server

A ClickHouse server version 21.8.10.19 or above

### Configure Network Access

Make sure your ClickHouse database can be accessed by Daspire. If your database is within a VPC, you may need to allow access from the IP you're using to expose Daspire.

### Permissions

You need a ClickHouse user with the following permissions:

* can create tables and write rows.
* can create databases e.g:

You can create such a user by running the following command:

```
GRANT CREATE ON * TO daspire_user;
```

You can also use a pre-existing user but we highly recommend creating a dedicated user for Daspire.

### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Daspire.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Incremental - Deduped History | Yes |
| Namespaces | Yes |

### Output Schema

Each stream will be output into its own table in ClickHouse. Each table will contain 3 columns:

* `_daspire_ab_id`: a uuid assigned by Daspire to each event that is processed. The column type in ClickHouse is `String`.

* `_daspire_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in ClickHouse is `DateTime64`.

* `_daspire_data`: a json blob representing the event data. The column type in ClickHouse is `String`.

## Setup guide

You should now have all the requirements needed to configure ClickHouse as a destination in the UI. You'll need the following information to configure the ClickHouse destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Database**
* **Jdbc\_url\_params**

### Naming conventions

From [ClickHouse SQL Identifiers syntax](https://clickhouse.com/docs/en/sql-reference/syntax/):

* SQL identifiers and keywords must begin with a letter (a-z, but also letters with diacritical marks and non-Latin letters) or an underscore (\_).

* Subsequent characters in an identifier or keyword can be letters, underscores, or digits (0-9).

* Identifiers can be quoted or non-quoted. The latter is preferred.

* If you want to use identifiers the same as keywords or you want to use other symbols in identifiers, quote it using double quotes or backticks, for example, `id`.

* If you want to write portable applications, you are advised to always quote a particular name or never quote it.

Therefore, the Daspire ClickHouse destination will create tables and schemas using the Unquoted identifiers when possible or fallback to Quoted Identifiers if the names contain special characters.