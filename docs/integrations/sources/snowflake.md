# Snowflake Source Connector

## Overview

The Snowflake source connector allows you to sync data from Snowflake. It supports both Full Refresh Sync and Incremental Sync. You can choose if this connector will copy only the new or updated data or all rows in the tables and columns you set up for replication every time a sync is run.

This Snowflake source connector is built on top of the source-jdbc code base and is configured to rely on JDBC 3.13.22 [Snowflake driver](https://github.com/snowflakedb/snowflake-jdbc) as described in the Snowflake [documentation](https://docs.snowflake.com/en/user-guide/jdbc.html).

### Resulting schema

The Snowflake source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

### Features

| Feature                  | Supported?(Yes/No) | Notes |
| :---                     | :---               | :---  |
| Full Refresh Sync        | Yes                |       |
| Incremental - Append Sync| Yes                |       |
| Namespaces               | Yes                |       |

## Getting started

### Requirements

To configure the Snowflake source connector, you'll need the following information:

1. Host
2. Role
3. Warehouse
4. Database
5. Schema
6. Authentication: You can choose between Username & Password or OAuth2 for authentication.
7. For Username & Password: Username and Password
8. For OAuth2: Client ID, Client Secret, Access Token, and Refresh Token
9. JDBC URL Params (Optional)

To set up replication, it's recommended to create a dedicated read-only Airbyte user and role with access to all schemas you want to replicate.

### Setup guide

#### Step 1: Find Your Snowflake Account Host

Your Snowflake host domain includes the account, region, cloud environment, and ends with snowflakecomputing.com. You can find it in the Snowflake URL after logging in to the Snowflake Web UI. It should look something like this: `accountname.us-east-2.aws.snowflakecomputing.com`

Refer to the Snowflake [documentation](https://docs.snowflake.com/en/user-guide/admin-account-identifier.html) for more details.

#### Step 2: Create a dedicated read-only user with access to the relevant schemas (Recommended but optional)

This step is optional but highly recommended for better permission control and auditing. Alternatively, you can use Airbyte with an existing user in your database.

To create a dedicated database user, run the following commands against your database:

```sql
-- set variables (these need to be uppercase)
SET AIRBYTE_ROLE = 'AIRBYTE_ROLE';
SET AIRBYTE_USERNAME = 'AIRBYTE_USER';

-- set user password
SET AIRBYTE_PASSWORD = '<your_airbyte_password>';

BEGIN;

-- create Airbyte role
CREATE ROLE IF NOT EXISTS $AIRBYTE_ROLE;

-- create Airbyte user
CREATE USER IF NOT EXISTS $AIRBYTE_USERNAME
PASSWORD = $AIRBYTE_PASSWORD
DEFAULT_ROLE = $AIRBYTE_ROLE
DEFAULT_WAREHOUSE= $AIRBYTE_WAREHOUSE;

-- grant Airbyte schema access
GRANT OWNERSHIP ON SCHEMA $AIRBYTE_SCHEMA TO ROLE $AIRBYTE_ROLE;

COMMIT;
```

You can limit this grant down to specific schemas instead of the whole database. Note that to replicate data from multiple Snowflake databases, you can re-run the command above to grant access to all the relevant schemas, but you'll need to set up multiple sources connecting to the same db on multiple schemas.

#### Step 3: Configure the Snowflake Source Connector in Airbyte

Based on the authentication method you choose, fill the required fields in the Airbyte connection form:

**Username and Password Authentication:**

- Host: Your Snowflake host domain found in Step 1.
- Role: The role you created in Step 2 for Airbyte to access Snowflake (e.g., AIRBYTE_ROLE).
- Warehouse: The name of your Snowflake warehouse.
- Database: The name of your Snowflake database.
- Schema: The schema that contains the tables you want to replicate.
- Username: The username you created in Step 2 to allow Airbyte to access the database (e.g., AIRBYTE_USER).
- Password: The password associated with the username.
- JDBC URL Params (Optional): Additional properties to pass to the JDBC URL string when connecting to the database. Format as `key=value` pairs separated by the `&` symbol (e.g. `key1=value1&key2=value2&key3=value3`).

**OAuth 2.0 Authentication:**

- Host: Your Snowflake host domain found in Step 1.
- Role: The role you created in Step 2 for Airbyte to access Snowflake (e.g., AIRBYTE_ROLE).
- Warehouse: The name of your Snowflake warehouse.
- Database: The name of your Snowflake database.
- Schema: The schema that contains the tables you want to replicate.
- Client ID: The Client ID of your Snowflake developer application.
- Client Secret: The Client Secret of your Snowflake developer application.
- Access Token: The Access Token for making authenticated requests.
- Refresh Token: The Refresh Token for making authenticated requests.
- JDBC URL Params (Optional): Additional properties to pass to the JDBC URL string when connecting to the database. Format as `key=value` pairs separated by the `&` symbol (e.g. `key1=value1&key2=value2&key3=value3`).

For more information on Snowflake connection parameters, refer to the Snowflake [documentation](https://docs.snowflake.com/en/user-guide/jdbc-configure.html#connection-parameters).

You are now ready to use the Snowflake source connector with Airbyte.

### Network policies

By default, Snowflake allows users to connect to the service from any computer or device IP address. A security administrator (i.e., users with the SECURITYADMIN role) or higher can create a network policy to allow or deny access to a single IP address or a list of addresses.

If you have any issues connecting with Airbyte Cloud, please make sure that the list of IP addresses is on the allowed list.

To determine whether a network policy is set on your account or for a specific user, execute the _SHOW PARAMETERS_ command.

**Account**

```sql
SHOW PARAMETERS LIKE 'network_policy' IN ACCOUNT;
```

**User**

```sql
SHOW PARAMETERS LIKE 'network_policy' IN USER <username>;
```

For more details on network policies, please check the Snowflake [documentation](https://docs.snowflake.com/en/user-guide/network-policies.html#).