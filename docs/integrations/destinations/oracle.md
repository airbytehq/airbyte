# Oracle

## Overview

The Airbyte Oracle destination allows you to sync data to Oracle.

### Sync overview

#### Output schema

Each stream will be output into its own table in Oracle. Each table will contain 3 columns:

* `airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Oracle is `VARCHAR(64)`.
* `airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Oracle is `TIMESTAMP WITH TIME ZONE`.
* `airbyte_data`: a json blob representing with the event data. The column type in Oracles is `NCLOB`.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | Yes |  |

## Getting started

### Requirements

To use the Oracle destination, you'll need:

* An Oracle server version 11 or above

### Setup guide

#### Network Access

Make sure your Oracle database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need an Oracle user with permissions to create tables and write rows, and to create other users with the same permissions in order to support namespaces. We highly recommend creating an Airbyte-specific user for this purpose.

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
| 0.1.4 | 2021-07-30 | [#5125](https://github.com/airbytehq/airbyte/pull/5125) | Enable `additionalPropertities` in spec.json |
| 0.1.3 | 2021-07-21 | [#3555](https://github.com/airbytehq/airbyte/pull/3555) | Partial Success in BufferedStreamConsumer |
| 0.1.2 | 2021-07-20 | [4874](https://github.com/airbytehq/airbyte/pull/4874) | Require `sid` instead of `database` in connector specification |
