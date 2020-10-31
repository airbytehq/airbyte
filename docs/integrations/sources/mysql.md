# MySQL

## Overview

The MySQL source supports Full Refresh syncs.

### Sync overview

#### Resulting schema

The MySQL source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

#### Data type mapping

MySQL data types are mapped to the following data types when synchronizing data:

| MySQL Type | Resulting Type | Notes |
| :--- | :--- | :--- |
| `array` | array |  |
| `binary` | string |  |
| `date` | string |  |
| `datetime` | string |  |
| `enum` | string |  |
| `numeric` | string | includes integer, etc |
| `string` | string | includes integer, etc |

If you do not see a type in this list, assume that it is coerced into a string. We are happy to take feedback on preferred mappings.

**Note:** arrays for all the above types as well as custom types are supported, although they may be de-nested depending on the destination. Byte arrays are currently unsupported.

### Features

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| Logical Replication \(WAL\) | No |
| SSL Support | Yes |
| SSH Tunnel Connection | No |

## Getting started

### Requirements

1. MySQL Server `8.0`, `5.7`, or `5.6`.
3. Create a dedicated read-only Airbyte user with access to all tables needed for replication

### Setup guide

#### 1. Make sure your database is accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your MySQL instance is via the check connection tool in the UI.

#### 2. Create a dedicated read-only user with access to the relevant tables \(Recommended but optional\)

This step is optional but highly recommended to allow for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
CREATE USER 'airbyte'@'%' IDENTIFIED BY 'your_password_here';
```

Then give it access to the relevant schema:

```sql
GRANT SELECT ON <database name>.* TO 'airbyte'@'%';
```

You can limit this grant down to specific tables instead of the whole database. Note that to replicate data from multiple MySQL schemas, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same db on multiple schemas.

Your database user should now be ready for use with Airbyte.

