# MS SQL Server

## Overview

The Airbyte MS SQL Server destination allows you to sync data to SQL Server databases.

### Sync overview

#### Output schema

Each stream will be output into its own table in SQL Server. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in SQL Server is `VARCHAR(64)`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in SQL Server is `DATETIMEOFFSET(7)`.
* `_airbyte_data`: a JSON blob representing with the event data. The column type in SQL Server is `NVARCHAR(MAX)`.

#####  Microsoft SQL Server specifics or why NVARCHAR type is used here:
* NVARCHAR is Unicode - 2 bytes per character, therefore max. of 1 billion characters; will handle East Asian, Arabic, Hebrew, Cyrillic etc. characters just fine.
* VARCHAR is non-Unicode - 1 byte per character, max. capacity is 2 billion characters, but limited to the character set you're SQL Server is using, basically - no support for those languages mentioned before

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | Yes |  |

## Getting started

### Requirements

To use the SQL Server destination, you'll need:

MS SQL Server: `Azure SQL Database`, `Azure Synapse Analytics`, `Azure SQL Managed Instance`, `SQL Server 2019`, `SQL Server 2017`, `SQL Server 2016`, `SQL Server 2014`, `SQL Server 2012`, or `PDW 2008R2 AU34`.

### Setup guide

#### Network Access

Make sure your SQL Server database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a user configured in SQL Server that can create tables and write rows. We highly recommend creating an Airbyte-specific user for this purpose.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

#### SSL configuration (optional)

Airbyte supports a SSL-encrypted connection to the database.  If you want to use SSL to securely access your database, ensure that [the server is configured to use an SSL certificate.](https://support.microsoft.com/en-us/topic/how-to-enable-ssl-encryption-for-an-instance-of-sql-server-by-using-microsoft-management-console-1c7ae22f-8518-2b3e-93eb-d735af9e344c)

### Setup the MSSQL destination in Airbyte

You should now have all the requirements needed to configure SQL Server as a destination in the UI. You'll need the following information to configure the MSSQL destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Schema**
* **Database**
    * This database needs to exist within the schema provided.
* **SSL Method**:
  * The SSL configuration supports three modes: Unencrypted, Encrypted (trust server certificate), and Encrypted (verify certificate).
    * **Unencrypted**: Do not use SSL encryption on the database connection
    * **Encrypted (trust server certificate)**: Use SSL encryption without verifying the server's certificate.  This is useful for self-signed certificates in testing scenarios, but should not be used in production.
    * **Encrypted (verify certificate)**: Use the server's SSL certificate, after standard certificate verification.
  * **Host Name In Certificate** (optional): When using certificate verification, this property can be set to specify an expected name for added security.  If this value is present, and the server's certificate's host name does not match it, certificate verification will fail.
  