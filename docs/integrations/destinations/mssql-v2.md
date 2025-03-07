# MSSQL (V2)

:::danger
This connector is in early access and **should not be used for production**. It is subject to breaking changes without notice.
:::

## MSSQL with Azure Blob Storage (Bulk Upload)

:::caution
The **Azure Blob Storage Bulk Upload** feature is also in early access and may change in backward-incompatible ways.

We appreciate your feedback as we continue to refine it!
:::

This document describes how to set up and use the **Microsoft SQL Server (MSSQL) connector** with the **Azure Blob Storage Bulk Upload** feature. By staging data in an Azure Blob Storage container and using `BULK INSERT`, you can significantly improve ingestion speed and reduce network overhead for large or frequent data loads.

---

## Why Use Azure Blob Storage Bulk Upload?

When handling high data volumes or frequent syncs, row-by-row inserts into MSSQL can become slow and resource-intensive. By staging files in Azure Blob Storage first, you can:
1. **Aggregate Data into Bulk Files**: Data is written to Blob Storage in batches, reducing overhead.
2. **Perform Bulk Ingestion**: MSSQL uses `BULK INSERT` to directly load these files, typically resulting in faster performance compared to conventional row-by-row inserts.

---

## Prerequisites

1. **A Microsoft SQL Server Instance**
    - Compatible with on-premises SQL Server or Azure SQL Database.
2. **Azure Blob Storage Account**
    - A storage account and container (e.g., `bulk-staging`) where data files will be placed.
3. **Permissions**
    - **Blob Storage**: ability to create, read, and delete objects within the designated container.
    - **MSSQL**: ability to create or modify tables, and permission to execute `BULK INSERT`.

---

## Setup Guide

Follow these steps to configure MSSQL with Azure Blob Storage for bulk uploads.

### 1. Set Up Azure Blob Storage

1. **Create a Storage Account & Container**
    - In the Azure Portal, create (or reuse) a Storage Account.
    - Within that account, create a container (e.g., `bulk-staging`) for staging your data files.
2. **Establish Access Credentials**
    - Use a **Shared Access Signature (SAS)** scoped to your container.
    - Ensure the SAS token or role assignments include permissions such as **Read**, **Write**, **Delete**, and **List**.

### 2. Configure MSSQL

See the official [Microsoft documentation](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-data-source-transact-sql?view=sql-server-2017&tabs=dedicated#e-create-an-external-data-source-for-bulk-operations-retrieving-data-from-azure-storage) for more details. Below is a simplified overview:

1. **(Optional) Create a Master Encryption Key**  
   If your environment requires a master key to store credentials securely, create one:
   ```sql
   CREATE MASTER KEY ENCRYPTION BY PASSWORD = '<your_password>';
   ```

2. **Create a Database Scoped Credential**  
   Configure a credential that grants MSSQL access to your Blob Storage using the SAS token:
   ```sql
   CREATE DATABASE SCOPED CREDENTIAL <credential_name>
   WITH IDENTITY = 'SHARED ACCESS SIGNATURE',
        SECRET = '<your_sas_token>';
   ```

3. **Create an External Data Source**  
   Point MSSQL to your Blob container using the credential:
   ```sql
   CREATE EXTERNAL DATA SOURCE <data_source_name>
   WITH (
       TYPE = BLOB_STORAGE,
       LOCATION = 'https://<storage_account>.blob.core.windows.net/<container_name>',
       CREDENTIAL = <credential_name>
   );
   ```
   You’ll reference `<data_source_name>` when configuring the connector.

### 3. Connector Configuration

You’ll need to supply:

1. **MSSQL Connection Details**
    - The server hostname/IP, port, database name, and authentication (username/password).
2. **Bulk Load Data Source**
    - The name of the external data source you created (e.g., `<data_source_name>`).
3. **Azure Storage Account & Container**
    - The name of the storage account and container.
4. **SAS Token**
    - The token that grants Blob Storage access.

---

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                |
|:--------|:-----------|:----------------------------------------------------------|:-------------------------------------------------------|
| 0.1.14  | 2025-03-05 | [54159](https://github.com/airbytehq/airbyte/pull/54159)  | RC12: Support For Bulk Insert Using Azure Blob Storage |
| 0.1.13  | 2025-03-04 | [55193](https://github.com/airbytehq/airbyte/pull/55193)  | RC11: Increase decimal precision                       |
| 0.1.12  | 2025-02-24 | [54648](https://github.com/airbytehq/airbyte/pull/54648)  | RC10: Fix index column names with hyphens              |
| 0.1.11  | 2025-02-21 | [54197](https://github.com/airbytehq/airbyte/pull/54197)  | RC9: Fix index column names with invalid characters    |
| 0.1.10  | 2025-02-20 | [54186](https://github.com/airbytehq/airbyte/pull/54186)  | RC8: Fix String support                                |
| 0.1.9   | 2025-02-11 | [53364](https://github.com/airbytehq/airbyte/pull/53364)  | RC7: Revert deletion change                            |
| 0.1.8   | 2025-02-11 | [53364](https://github.com/airbytehq/airbyte/pull/53364)  | RC6: Break up deletes into loop to reduce locking      |
| 0.1.7   | 2025-02-07 | [53236](https://github.com/airbytehq/airbyte/pull/53236)  | RC5: Use rowlock hint                                  |
| 0.1.6   | 2025-02-06 | [53192](https://github.com/airbytehq/airbyte/pull/53192)  | RC4: Fix config, timehandling, performance tweak       |
| 0.1.5   | 2025-02-04 | [53174](https://github.com/airbytehq/airbyte/pull/53174)  | RC3: Fix metadata.yaml for publish                     |
| 0.1.4   | 2025-02-04 | [52704](https://github.com/airbytehq/airbyte/pull/52704)  | RC2: Performance improvement                           |
| 0.1.3   | 2025-01-24 | [52096](https://github.com/airbytehq/airbyte/pull/52096)  | Release candidate                                      |
| 0.1.2   | 2025-01-10 | [51508](https://github.com/airbytehq/airbyte/pull/51508)  | Use a non-root base image                              |
| 0.1.1   | 2024-12-18 | [49870](https://github.com/airbytehq/airbyte/pull/49870)  | Use a base image: airbyte/java-connector-base:1.0.0    |
| 0.1.0   | 2024-12-16 | [\#49460](https://github.com/airbytehq/airbyte/pull/49460)| Initial commit                                         |

</details>
