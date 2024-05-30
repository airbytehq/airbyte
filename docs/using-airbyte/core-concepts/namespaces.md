---
products: all
---

# Namespaces

Namespaces are used to generally organize data, separate tests and production data, and enforce permissions. In most cases, namespaces are schemas in the database you're replicating to.

As a part of connection setup, you select where in the destination you want to write your data. Note: The default configuration is **Destination-defined**.

| Destination Namespace | Description                                                                                                                                                                                                                                                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Custom                | All streams will be replicated to a single user-defined namespace. See<a href="/understanding-airbyte/namespaces#--custom-format"> Custom format</a> for more details                                                                                                                                                                       |
| Destination-defined   | All streams will be replicated to the single default namespace defined in the Destination's settings.                                                                                                                                                                                                                                       |
| Source-defined        | Some sources (for example, databases) provide namespace information for a stream. If a source provides namespace information, the destination will mirror the same namespace when this configuration is set. For sources or streams where the source namespace is not known, the behavior will default to the "Destination default" option. |

Most of our destinations support this feature. To learn if your connector supports this, head to the individual connector page to learn more. If your desired destination doesn't support it, you can ignore this feature.

## What is a Namespace?

Systems often group their underlying data into namespaces with each namespace's data isolated from another namespace. This isolation allows for better organisation and flexibility, leading to better usability.

An example of a namespace is the RDMS's `schema` concept. Some common use cases for schemas are enforcing permissions, segregating test and production data and general data organisation.

In a source, the namespace is the location from where the data is replicated to the destination. In a destination, the namespace is the location where the replicated data is stored in the destination.

Airbyte supports namespaces and allows Sources to define namespaces, and Destinations to write to various namespaces. In Airbyte, the following options are available and are set on each individual connection.

### Custom

When replicating multiple sources into the same destination, you may create table conflicts where tables are overwritten by different syncs. This is where using a custom namespace will ensure data is synced accurately.

For example, a Github source can be replicated into a `github` schema. However, you may have multiple connections writing from different GitHub repositories \(common in multi-tenant scenarios\).

:::tip
To write more than 1 table with the same name to your destination, Airbyte recommends writing the connections to unique namespaces to avoid mixing data from the different GitHub repositories.
:::

You can enter plain text (most common) or additionally add a dynamic parameter `${SOURCE_NAMESPACE}`, which uses the namespace provided by the source if available.

### Destination-defined

All streams will be replicated and stored in the default namespace defined on the destination settings page, which is typically defined when the destination was set up. Depending on your destination, the namespace refers to:

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
If you prefer to replicate multiple sources into the same namespace, use the `Stream Prefix` configuration to differentiate data from these sources to ensure no streams collide when writing to the destination.
:::

### Source-Defined

Some sources \(such as databases based on JDBC\) provide namespace information from which a stream has been extracted. Whenever a source is able to fill this field in the catalog.json file, the destination will try to write to exactly the same namespace when this configuration is set. For sources or streams where the source namespace is not known, the behavior will fall back to the default namespace defined in the destination configuration. Most APIs do not provide namespace information.

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

As part of the connection settings, it is possible to configure the namespace used by: 1. destination connectors: to store the `_airbyte_raw_*` tables. 2. basic normalization: to store the final normalized tables.

When basic normalization is enabled, this is the location that both your normalized and raw data will get written to. Your raw data will show up with the prefix `_airbyte_raw_` in the namespace you define. If you don't enable basic normalization, you will only receive the raw tables.

:::note
Note custom transformation outputs are not affected by the namespace settings from Airbyte: It is up to the configuration of the custom dbt project, and how it is written to handle its [custom schemas](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/using-custom-schemas). The default target schema for dbt in this case, will always be the destination namespace.
:::

## Requirements

- Both Source and Destination connectors need to support namespaces.
- Relevant Source and Destination connectors need to be at least version `0.3.0` or later.
- Airbyte version `0.21.0-alpha` or later.
