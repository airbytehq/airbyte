# Weaviate

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | No |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | No |  |
| Namespaces | No |  |
| Provide vector | No |  |

#### Output Schema

Each stream will be output into its own class in Weaviate. The record fields will be stored as fields
in the Weaviate class.

Dynamic Schema: Weaviate will automatically create a schema for the stream if no class was defined unless
you have disabled the Dynamic Schema feature in Weaviate. You can also create the class in Weaviate in advance
if you need more control over the schema in Weaviate. 

IDs: If your source table has an int based id stored as field name `id` then the
ID will automatically be converted to a UUID. Weaviate only supports ID to be a UUID.


## Getting Started

Airbyte Cloud only supports connecting to your Weaviate Instance instance with TLS encryption and with a username and
password.

## Getting Started \(Airbyte Open-Source\)

#### Requirements

To use the ClickHouse destination, you'll need:

* A Weaviate cluster version 21.8.10.19 or above

#### Configure Network Access

Make sure your Weaviate database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a Weaviate user or use a Weaviate instance that's accessible to all


### Setup the ClickHouse Destination in Airbyte

You should now have all the requirements needed to configure Weaviate as a destination in the UI. You'll need the following information to configure the Weaviate destination:

* **URL** for example http://localhost:8080 or https://my-wcs.semi.network
* **Username**
* **Password**


## Changelog

| Version | Date       | Pull Request | Subject                                      |
|:--------|:-----------| :--- |:---------------------------------------------|
| 0.1.0   | 2021-11-04 | [\#20094](https://github.com/airbytehq/airbyte/pull/20094) | Add ClickHouse destination                   |

