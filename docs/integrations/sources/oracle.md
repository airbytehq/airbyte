# Oracle DB

## Overview

The Oracle Database source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Resulting schema

The Oracle source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Data type mapping

Oracle data types are mapped to the following data types when synchronizing data.
You can check the test values examples [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-oracle/src/test-integration/java/io/airbyte/integrations/source/oracle/OracleSourceComprehensiveTest.java).
If you can't find the data type you are looking for or have any problems feel free to add a new test!

| Oracle Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `binary_double` | number |  |
| `binary_float` | number |  |
| `blob` | string |  |
| `char` | string |  |
| `char(3 char)` | string |  |
| `clob` | string |  |
| `date` | string |  |
| `decimal` | number |  |
| `float` | number |  |
| `float(5)` | number |  |
| `integer` | number |  |
| `interval year to month` | string |  |
| `long raw` | string |  |
| `number` | number |  |
| `number(6, 2)` | number |  |
| `nvarchar(3)` | string |  |
| `raw` | string |  |
| `timestamp` | string |  |
| `timestamp with local time zone` | string |  |
| `timestamp with time zone` | string |  |
| `varchar2` | string |  |
| `varchar2(256)` | string |  |
| `xmltype` | string |  |

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take feedback on preferred mappings.

### Features

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Replicate Incremental Deletes | Coming soon |  |
| Logical Replication \(WAL\) | Coming soon |  |
| SSL Support | Coming soon |  |
| SSH Tunnel Connection | Coming soon |  |
| LogMiner | Coming soon |  |
| Flashback | Coming soon |  |
| Namespaces | Yes | Enabled by default |

## Getting started

### Requirements

1. Oracle `11g` or above
2. Allow connections from Airbyte to your Oracle database \(if they exist in separate VPCs\)
3. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your Oracle instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER airbyte IDENTIFIED BY <your_password_here>;
GRANT CREATE SESSION TO airbyte;
```

Next, grant the user read-only access to the relevant tables. The simplest way is to grant read access to all tables in the schema as follows:

```sql
GRANT SELECT ANY TABLE TO airbyte;
```

Or you can be more granular:

```sql
GRANT SELECT ON "<schema_a>"."<table_1>" TO airbyte;
GRANT SELECT ON "<schema_b>"."<table_2>" TO airbyte;
```

Your database user should now be ready for use with Airbyte.


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.3.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator |