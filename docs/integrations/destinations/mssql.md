# MS SQL Server

## Overview

The Airbyte MS SQL Server destination allows you to sync data to SQL Server databases.

### Sync overview

#### Output schema

{% hint style="warning" %}
Tables in MSSQL destinations will be prefixed by `_airbyte_raw` due to the fact that MSSQL does not currently support basic normalization. This prefix cannot be removed and this is normal behavior.
{% endhint %}

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
  

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.8   | 2021-08-07 | [#5272](https://github.com/airbytehq/airbyte/pull/5272) | Add batch method to insert records  |
| 0.1.7   | 2021-07-30 | [#5125](https://github.com/airbytehq/airbyte/pull/5125) | Enable `additionalPropertities` in spec.json |
| 0.1.6   | 2021-06-21 | [#3555](https://github.com/airbytehq/airbyte/pull/3555) | Partial Success in BufferedStreamConsumer |
| 0.1.5   | 2021-07-20 | [#4874](https://github.com/airbytehq/airbyte/pull/4874) | declare object types correctly in spec |
| 0.1.4   | 2021-06-17 | [#3744](https://github.com/airbytehq/airbyte/pull/3744) | Fix doc/params in specification file |
| 0.1.3   | 2021-05-28 | [#3728](https://github.com/airbytehq/airbyte/pull/3973) | Change dockerfile entrypoint |
| 0.1.2   | 2021-05-13 | [#3367](https://github.com/airbytehq/airbyte/pull/3671) | Fix handle symbols unicode |
| 0.1.1   | 2021-05-11 | [#3566](https://github.com/airbytehq/airbyte/pull/3195) | MS SQL Server Destination Release! |
