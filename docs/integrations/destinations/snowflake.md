# Snowflake

## Overview

The Airbyte Snowflake destination allows you to sync data to Snowflake.

### Sync overview

#### Output schema

Each stream will be output into its own table in Snowflake. Each table will contain 3 columns:

* `ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Snowflake is `VARCHAR`.
* `emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Snowflake is `TIMESTAMP WITH TIME ZONE`.
* `data`: a json blob representing with the event data. The column type in Snowflake is `VARIANT`.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |

## Getting started

We recommend creating an Airbyte-specific warehouse, database, schema, user, and role for writing data into Snowflake so it is possible to track costs specifically related to Airbyte \(including the cost of running this warehouse\) and control permissions at a granular level. Since the Airbyte user creates, drops, and alters tables, `OWNERSHIP` permissions are required in Snowflake. If you are not following the recommended script below, please limit the `OWNERSHIP` permissions to only the necessary database and schema for the Airbyte user.

We provide the following script to create these resources. Before running, you must change the password to something secure. You may change the names of the other resources if you desire.

```text
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
to role identifier($airbyte_role)
revoke current grants;

commit;

begin;

USE DATABASE identifier($airbyte_database);

-- create schema for Airbyte data
CREATE SCHEMA IF NOT EXISTS identifier($airbyte_schema);

commit;
```

### Setup the Snowflake destination in Airbyte

You should now have all the requirements needed to configure Snowflake as a destination in the UI. You'll need the following information to configure the Snowflake destination:

* **Host**
* **Role**
* **Warehouse**
* **Database**
* **Schema**
* **Username**
* **Password**

