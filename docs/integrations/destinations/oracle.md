# Oracle

## Overview

The Airbyte Oracle destination allows you to sync data to Oracle.

### Sync overview

#### Output schema

Each stream will be output into its own table in Oracle. Each table will contain 3 columns:

* `_AIRBYTE_AB_ID`: a uuid assigned by Airbyte to each event that is processed. The column type in Oracle is `VARCHAR(64)`.
* `_AIRBYTE_EMITTED_AT`: a timestamp representing when the event was pulled from the data source. The column type in Oracle is `TIMESTAMP WITH TIME ZONE`.
* `_AIRBYTE_DATA`: a json blob representing with the event data. The column type in Oracles is `NCLOB`.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | Yes |  |
| Basic Normalization | Yes | Only for raw tables, doesn't support for nested json yet |


## Getting started

### Requirements

To use the Oracle destination, you'll need:

* An Oracle server version 18 or above
* It's possible to use Oracle 12+ but you need to configure the table name length to 120 chars.

### Setup guide

#### Network Access

Make sure your Oracle database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

As Airbyte namespaces allows us to store data into different schemas, we have different scenarios and list of required permissions:

| Login user | Destination user | Required permissions | Comment |
| :--- | :--- | :--- | :--- |
| DBA User | Any user | - | |
| Regular user | Same user as login | Create, drop and write table, create session | |
| Regular user | Any existing user | Create, drop and write ANY table, create session | Grants can be provided on a system level by DBA or by target user directly |
| Regular user | Not existing user | Create, drop and write ANY table, create user, create session | Grants should be provided on a system level by DBA | 

We highly recommend creating an Airbyte-specific user for this purpose.

### Setup the Oracle destination in Airbyte

You should now have all the requirements needed to configure Oracle as a destination in the UI. You'll need the following information to configure the Oracle destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Database**

## Changelog
| Version | Date | Pull Request | Subject |
| :--- | :---  | :--- | :--- |
| 0.1.7 | 2021-08-30 | [#5746](https://github.com/airbytehq/airbyte/pull/5746) | Use default column name for raw tables |
| 0.1.6 | 2021-08-23 | [#5542](https://github.com/airbytehq/airbyte/pull/5542) | Remove support for Oracle 11g to allow normalization |
| 0.1.5 | 2021-08-10 | [#5307](https://github.com/airbytehq/airbyte/pull/5307) | 🐛 Destination Oracle: Fix destination check for users without dba role |
| 0.1.4 | 2021-07-30 | [#5125](https://github.com/airbytehq/airbyte/pull/5125) | Enable `additionalPropertities` in spec.json |
| 0.1.3 | 2021-07-21 | [#3555](https://github.com/airbytehq/airbyte/pull/3555) | Partial Success in BufferedStreamConsumer |
| 0.1.2 | 2021-07-20 | [4874](https://github.com/airbytehq/airbyte/pull/4874) | Require `sid` instead of `database` in connector specification |
