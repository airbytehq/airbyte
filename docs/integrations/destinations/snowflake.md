# Snowflake

## Overview

The Airbyte Snowflake destination allows you to sync data to Snowflake.

### Sync overview

#### Output schema

Each stream will be output into its own table in Snowflake. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Snowflake is `VARCHAR`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Snowflake is `TIMESTAMP WITH TIME ZONE`.
* `_airbyte_data`: a json blob representing with the event data. The column type in Snowflake is `VARIANT`.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | Yes |  |

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
to role identifier($airbyte_role);

commit;

begin;

USE DATABASE identifier($airbyte_database);

-- create schema for Airbyte data
CREATE SCHEMA IF NOT EXISTS identifier($airbyte_schema);

commit;

begin;

-- grant Airbyte schema access
grant OWNERSHIP
on schema identifier($airbyte_schema)
to role identifier($airbyte_role);

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

## Notes about Snowflake Naming Conventions

From [Snowflake Identifiers syntax](https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html):

### Unquoted Identifiers:

* Start with a letter \(A-Z, a-z\) or an underscore \(“\_”\).
* Contain only letters, underscores, decimal digits \(0-9\), and dollar signs \(“$”\).
* Are case-insensitive.

When an identifier is unquoted, it is stored and resolved in uppercase.

### Quoted Identifiers:

* The identifier is case-sensitive.
* Delimited identifiers \(i.e. identifiers enclosed in double quotes\) can start with and contain any valid characters, including:
  * Numbers
  * Special characters \(., ', !, @, \#, $, %, ^, &, \*, etc.\)
  * Extended ASCII and non-ASCII characters
  * Blank spaces

When an identifier is double-quoted, it is stored and resolved exactly as entered, including case.

### Note

* Regardless of whether an identifier is unquoted or double-quoted, the maximum number of characters allowed is 255 \(including blank spaces\).
* Identifiers can also be specified using string literals, session variables or bind variables. For details, see SQL Variables.
* If an object is created using a double-quoted identifier, when referenced in a query or any other SQL statement, the identifier must be specified exactly as created, including the double quotes. Failure to include the quotes might result in an Object does not exist error \(or similar type of error\).
* Also, note that the entire identifier must be enclosed in quotes when referenced in a query/SQL statement. This is particularly important if periods \(.\) are used in identifiers because periods are also used in fully-qualified object names to separate each object.

Therefore, Airbyte Snowflake destination will create tables and schemas using the Unquoted identifiers when possible or fallback to Quoted Identifiers if the names are containing special characters.

## Cloud Storage Staging

By default, Airbyte uses batches of `INSERT` commands to add data to a temporary table before copying it over to the final table in Snowflake. This is too slow for larger/multi-GB replications. For those larger replications we recommend configuring using cloud storage to allow batch writes and loading.

### AWS S3

For AWS S3, you will need to create a bucket and provide credentials to access the bucket. We recommend creating a bucket that is only used for Airbyte to stage data to Snowflake. Airbyte needs read/write access to interact with this bucket.

### Google Cloud Storage \(GCS\)

First you will need to create a GCS bucket.

Then you will need to run the script below:

* You must run the script as the account admin for Snowflake. 
* You should replace `AIRBYTE_ROLE` with the role you used for Airbyte's Snowflake configuration.
* Replace `YOURBUCKETNAME` with your bucket name
* The stage name can be modified to any valid name.
* `gcs_airbyte_integration` must be used

The script:

```text
create storage INTEGRATION gcs_airbyte_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = GCS
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('gcs://YOURBUCKETNAME');

create stage gcs_airbyte_stage
  url = 'gcs://io_airbyte_test_staging'
  storage_integration = gcs_airbyte_integration;

GRANT USAGE ON integration gcs_airbyte_integration TO ROLE AIRBYTE_ROLE;
GRANT USAGE ON stage gcs_airbyte_stage TO ROLE AIRBYTE_ROLE;

DESC STORAGE INTEGRATION gcs_airbyte_integration;
```

The final query should show a `STORAGE_GCP_SERVICE_ACCOUNT` property with an email as the property value.

Finally, you need to add read/write permissions to your bucket with that email.


| Version | Date      | Pull Request | Subject |
| :------ | :-------- | :-----       | :------ |
| 0.3.13  | 2021-09-01 | [#5784](https://github.com/airbytehq/airbyte/pull/5784) | Updated query timeout from 30 minutes to 3 hours |
| 0.3.12  | 2021-07-30 | [#5125](https://github.com/airbytehq/airbyte/pull/5125) | Enable `additionalPropertities` in spec.json |
| 0.3.11  | 2021-07-21 | [#3555](https://github.com/airbytehq/airbyte/pull/3555) | Partial Success in BufferedStreamConsumer |
| 0.3.10  | 2021-07-12 | [#4713](https://github.com/airbytehq/airbyte/pull/4713)| Tag traffic with `airbyte` label to enable optimization opportunities from Snowflake |

