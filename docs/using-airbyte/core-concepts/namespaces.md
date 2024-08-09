---
products: all
---

# Namespaces

## What is a Namespace?

Systems often group their underlying data into namespaces with each namespace's data isolated from other namespaces.

An example of a namespace is the RDMS's `schema` concept. Namespaces can be used to isolate data, which allows you to logically organize data, separate test data from production data, and enforce permissions. 

## Requirements

- Both Source and Destination connectors need to support namespaces.
- Relevant Source and Destination connectors need to be at least version `0.3.0` or later.
- Airbyte version `0.21.0-alpha` or later.

## Namespace use in Airbyte

In most cases, namespaces are schemas in the database you're replicating to. In a Source, the namespace is the location from where the data is replicated to the Destination. In a Destination, the namespace is the location where the replicated data is stored in the Destination.

Airbyte supports namespaces, allowing Sources to define namespaces, and Destinations to write to various namespaces.

During the connection setup process, you can choose the specific location within the Destination where your data will be written. Note: The default configuration is **Destination-defined**.

If a Source provides namespace information, the Destination will mirror the same namespace when this configuration is set. When the Source or stream's namespace is not known, the behavior you'll observe is a default to the "Destination default" option.

Most of our Destinations support this feature. To learn if your connector supports this, head to the individual connector page to learn more. Remember that in order to make use of namespaces, both the Source and Destination connectors you are using need to support them.

| Destination Namespace | Description                                                                                                                                                                                                                                                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Custom                | All streams will be replicated to a single user-defined namespace. See<a href="./using-airbyte/core-concepts/namespaces#custom"> Custom format</a> for more details                                                                                                                                                                       |
| Destination-defined   | All streams will be replicated to the single default namespace defined in the Destination's settings.                                                                                                                                                                                                                                       |
| Source-defined        | Some sources (i.e., databases) provide namespace information for a stream. 

### Custom

When replicating multiple sources into the same Destination, you may create table conflicts where tables are overwritten by different syncs. Using a custom namespace will ensure data is synced accurately.

For example, a Github Source can be replicated into a `github` schema. However, you may have multiple connections writing from different GitHub repositories \(common in multi-tenant scenarios\).

:::tip
To write more than 1 table with the same name to your Destination, Airbyte recommends writing the connections to unique namespaces to avoid mixing data from the different GitHub repositories.
:::

You can enter plain text (most common) or, alternatively, add a dynamic parameter `${SOURCE_NAMESPACE}`, which uses the namespace provided by the Source, if available.

### Destination-defined

All streams will be replicated and stored in the default namespace defined on the Destination settings page, which is typically defined during setup for the Destination. Depending on your Destination, the namespace refers to:

| Destination Connector | Namespace setting |
| :-------------------- | :---------------- |
| BigQuery              | dataset           |
| MSSQL                 | schema            |
| MySql                 | database          |
| Oracle DB             | schema            |
| Postgres              | schema            |
| Redshift              | schema            |
| Snowflake             | schema            |
| S3                    | path prefix       |

:::tip
If you prefer to replicate multiple sources into the same namespace, use the `Stream Prefix` configuration to differentiate data from these sources to ensure no streams collide when writing to the Destination.
:::

### Source-Defined

Some sources \(such as databases based on JDBC (Java Database Connectivity)\) provide namespace information from which a stream has been extracted. Whenever a source is able to fill this field in the catalog.json file, the Destination will try to write to exactly the same namespace when this configuration is set. For sources or streams where the Source namespace is not known, the behavior will fall back to the default namespace defined in the Destination configuration. Most APIs do not provide namespace information.

### Examples

:::info
If the Source does not support namespaces, the data will be replicated into the Destination's default namespace. If the Destination does not support namespaces, any preference set in the connection is ignored.
:::

The following table summarises how this works. In this example, we're looking at the replication configuration between a Postgres Source and Snowflake Destination \(with settings of schema = "my_schema"\):

| Namespace Configuration                              | Source Namespace | Source Table Name | Destination Namespace | Destination Table Name |
| :--------------------------------------------------- | :--------------- | :---------------- | :-------------------- | :--------------------- |
| Destination default                                  | public           | my_table          | my_schema             | my_table               |
| Destination default                                  |                  | my_table          | my_schema             | my_table               |
| Mirror source structure                              | public           | my_table          | public                | my_table               |
| Mirror source structure                              |                  | my_table          | my_schema             | my_table               |
| Custom format = "custom"                             | public           | my_table          | custom                | my_table               |
| Custom format = `"${SOURCE\_NAMESPACE}"`             | public           | my_table          | public                | my_table               |
| Custom format = `"my\_${SOURCE\_NAMESPACE}\_schema"` | public           | my_table          | my_public_schema      | my_table               |
| Custom format = " "                                  | public           | my_table          | my_schema             | my_table               |

## Using Namespaces with Basic Normalization

As part of the connection settings, it is possible to configure the namespace used in several ways: 

1. Using Destination connectors: to store the `_airbyte_raw_*` tables. 
2. With basic normalization: to store the final normalized tables.

When basic normalization is enabled, this is the location that both your normalized and raw data will get written to. Your raw data will show up with the prefix `_airbyte_raw_` in the namespace you define. If you don't enable basic normalization, you will only receive the raw tables.

:::note
Custom transformation outputs are not affected by the namespace settings from Airbyte: It is dependent upon the configuration of the custom dbt project, and how it is written to handle its [custom schemas](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/using-custom-schemas). The default target schema for dbt in this case, will always be the Destination namespace.
:::