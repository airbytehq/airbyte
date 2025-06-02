# SAP HANA Source Connector for Airbyte

## Overview

The SAP HANA source connector for Airbyte allows you to extract data from your SAP HANA database and load it into your desired destination. SAP HANA is an in-memory, column-oriented, relational database management system developed and marketed by SAP SE. This connector enables you to integrate your SAP HANA data into your data pipelines for analytics, reporting, or data warehousing.

## Prerequisites

Before using this connector, please ensure you have the following:

1.  **SAP HANA Instance**: An accessible SAP HANA database instance (HANA DB 2.0 SPS 05 or later recommended).
2.  **`hdbcli` Driver**: The SAP HANA Python client driver (`hdbcli`) must be available in the environment where Airbyte is running. For Airbyte Cloud, this is generally handled. For self-hosted Airbyte, you might need to ensure this driver is installed or can be installed by the connector.
3.  **Database User**: A dedicated SAP HANA database user with the necessary permissions:
    *   `CONNECT` system privilege to connect to the database.
    *   `SELECT` privileges on the specific schemas and tables you want to replicate.
    *   Access to system views like `SYS.TABLES`, `SYS.COLUMNS`, `SYS.TABLE_COLUMNS`, `SYS.INDEXES`, and `SYS.INDEX_COLUMNS` within the schemas you intend to replicate, for schema discovery. If you restrict access to specific schemas, ensure the user can still query metadata for those schemas.

## Setup Guide

To configure the SAP HANA source connector in Airbyte:

1.  **Navigate to Sources**: In the Airbyte UI, go to "Sources" and click "+ New source".
2.  **Select Source Type**: Choose "SAP HANA" from the list of available source types.
3.  **Configure Connection Parameters**: Fill in the following fields:

    *   **`host`** (Required, String): This is the hostname or IP address of your SAP HANA instance.
        *Example: `hana.example.com` or `192.168.1.100`*
    *   **`port`** (Required, Integer): Specify the port number for your SAP HANA instance. This is typically a SQL port, often in the format `3<instance_number>15` (e.g., `30015`, `39015`). Consult your SAP HANA administrator for the correct port.
        *Example: `30015`*
    *   **`username`** (Required, String): The username for the SAP HANA database user that Airbyte will use to connect and read data.
        *Example: `AIRBYTE_USER`*
    *   **`password`** (Required, String, Secret): The password for the specified SAP HANA database user. This field is marked as secret and will be encrypted by Airbyte.
        *Example: `your_secure_password`*
    *   **`database`** (Required, String): The name of the specific database (tenant database) within your SAP HANA system to connect to. For systems not using multi-tenant database containers (MDC), this might be the system database name or might not be explicitly required by all client tools, but it's good practice to specify. For MDC systems, this is the name of the tenant database.
        *Example: `HXE` or `MY_TENANT_DB`*

4.  **Test and Save**: Click "Set up source". Airbyte will test the connection and, if successful, save the configuration.

## Features

*   **Data Extraction**: Extracts data from specified tables within your SAP HANA database.
*   **Schema Discovery**: Automatically discovers the schema (tables, columns, data types) of your SAP HANA database.
*   **Data Type Mapping**: Converts SAP HANA data types to JSON schema types compatible with Airbyte destinations. Supported types include (but are not limited to):
    *   `NVARCHAR`, `VARCHAR`, `CHAR`, `NCHAR` -> `string`
    *   `SMALLINT`, `INTEGER`, `BIGINT`, `TINYINT` -> `integer`
    *   `DECIMAL`, `REAL`, `DOUBLE`, `FLOAT` -> `number`
    *   `DATE`, `TIMESTAMP`, `SECONDDATE` -> `string` (with `date` or `date-time` format)
    *   `BOOLEAN` -> `boolean`
    *   `BLOB`, `CLOB`, `NCLOB`, `TEXT` -> `string`
*   **Sync Modes**:
    *   **Full Refresh - Overwrite**: Fetches all data from the source table and replaces existing data in the destination.
    *   **Full Refresh - Append**: Fetches all data from the source table and appends it to the existing data in the destination.
    *   *(Incremental syncs are planned for future versions based on suitable cursor fields like modification timestamps or incrementing IDs if available in tables).*

## Performance Considerations

*   **Network Latency**: Ensure low network latency between your Airbyte instance and your SAP HANA database for optimal performance.
*   **User Permissions**: Granting overly broad permissions can be a security risk. Grant only the necessary `SELECT` permissions on the required schemas/tables.
*   **Table Size**: For very large tables, the initial full refresh sync might take a considerable amount of time. Plan accordingly.
*   **`hdbcli` Driver**: Ensure the `hdbcli` driver is up-to-date for potential performance improvements and bug fixes.
*   **Query Complexity**: The connector uses simple `SELECT *` queries. If more complex transformations are needed, consider using downstream tools after data is loaded into your destination.

## Troubleshooting

*   **Connection Errors**:
    *   Verify `host`, `port`, `username`, `password`, and `database` details are correct.
    *   Check firewall rules to ensure Airbyte can reach the SAP HANA instance on the specified port.
    *   Ensure the `hdbcli` driver is correctly installed and accessible by Airbyte.
    *   Confirm the SAP HANA user has `CONNECT` privileges.
*   **Data Issues / Missing Tables**:
    *   Ensure the SAP HANA user has `SELECT` permissions on the tables you are trying to sync.
    *   Verify that the tables are not in schemas excluded by default (e.g., `SYS`, `_SYS_REPO`).
*   **`AttributeError: type object 'AirbyteConnectionStatus' has no attribute 'Status'` (During Development/Testing)**:
    *   This was an issue in older CDK versions or incorrect test code. Ensure status comparisons use string literals like `"SUCCEEDED"` or `"FAILED"`. The connector code itself uses these string literals.

---

This README provides a starting point. Further details can be added as the connector evolves.
