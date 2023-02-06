# Weaviate

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | No |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | No |  |
| Namespaces | No |  |
| Provide vector | Yes |  |

#### Output Schema

Each stream will be output into its [own class](https://weaviate.io/developers/weaviate/current/core-knowledge/basics.html#class-collections) in [Weaviate](https://weaviate.io). The record fields will be stored as fields
in the Weaviate class.

**Uploading Vectors:** Use the vectors configuration if you want to upload
vectors from a source database into Weaviate. You can do this by specifying
the stream name and vector field name in the following format:
```
<stream_name>.<vector_field_name>, <stream_name2>.<vector_field_name>
```
For example, if you have a table named `my_table` and the vector is stored using the column `vector` then
you should use the following `vectors`configuration: `my_table.vector`.

Dynamic Schema: Weaviate will automatically create a schema for the stream if no class was defined unless
you have disabled the Dynamic Schema feature in Weaviate. You can also create the class in Weaviate in advance
if you need more control over the schema in Weaviate. 

IDs: If your source table has an int based id stored as field name `id` then the
ID will automatically be converted to a UUID. Weaviate only supports the ID to be a UUID.
For example, if the record has `id=1` then this would become a uuid of
`00000000-0000-0000-0000-000000000001`.

Any field name starting with an upper case letter will be converted to lower case. For example,
if you have a field name `USD` then that field will become `uSD`. This is due to a limitation
in Weaviate, see [this issue in Weaviate](https://github.com/semi-technologies/weaviate/issues/2438).

## Getting Started

Airbyte Cloud only supports connecting to your Weaviate Instance instance with TLS encryption and with a username and
password.

## Getting Started \(Airbyte Open-Source\)

#### Requirements

To use the Weaviate destination, you'll need:

* A Weaviate cluster version 21.8.10.19 or above

#### Configure Network Access

Make sure your Weaviate database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a Weaviate user or use a Weaviate instance that's accessible to all


### Setup the Weaviate Destination in Airbyte

You should now have all the requirements needed to configure Weaviate as a destination in the UI. You'll need the following information to configure the Weaviate destination:

* **URL** for example http://localhost:8080 or https://my-wcs.semi.network
* **Username** (Optional)
* **Password** (Optional)
* **Batch Size** (Optional, defaults to 100)
* **Vectors** a comma separated list of `<stream_name.vector_field_name>` to specify the field
* **ID Schema** a comma separated list of `<stream_name.id_field_name>` to specify the field
  name that contains the ID of a record


## Changelog

| Version | Date       | Pull Request | Subject                                      |
|:--------|:-----------| :--- |:---------------------------------------------|
| 0.1.0   | 2022-12-06 | [\#20094](https://github.com/airbytehq/airbyte/pull/20094) | Add Weaviate destination                   |

