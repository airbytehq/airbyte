# Microsoft SQL Server \(MSSQL\)

## Overview

The MSSQL source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Resulting schema

The MSSQL source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Data type mapping

MSSQL data types are mapped to the following data types when synchronizing data:

| MSSQL Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `bigint` | number |  |
| `numeric` | number |  |
| `bit` | boolean |  |
| `smallint` | number |  |
| `decimal` | number |  |
| `int` | number |  |
| `tinyint` | number |  |
| `float` | number |  |
| everything else | string |  |

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take feedback on preferred mappings.

### Features

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync - Append | Yes |
| Replicate Incremental Deletes | Coming soon |
| Logical Replication \(WAL\) | Coming soon |
| SSL Support | Yes |
| SSH Tunnel Connection | Coming soon |

## Getting started

### Requirements

1. MSSQL Server `Azure SQL Database`, `Azure Synapse Analytics`, `Azure SQL Managed Instance`, `SQL Server 2019`, `SQL Server 2017`, `SQL Server 2016`, `SQL Server 2014`, `SQL Server 2012`, `PDW 2008R2 AU34`.
2. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your MSSQL instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

_Coming soon: suggestions on how to create this user._

Your database user should now be ready for use with Airbyte.

