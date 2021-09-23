# Namespaces

## High-Level Overview

{% hint style="info" %}
The high-level overview contains all the information you need to use Namespaces when pulling from APIs. Information past that can be read for advanced or educational purposes.
{% endhint %}

When looking through our connector docs, you'll notice that some sources and destinations support "Namespaces." These allow you to organize and separate your data into groups in the destination if the destination supports it. For example, in a database, a namespace could be a schema in the database. If your desired destination doesn't support it, you can ignore this feature.

Note that this is the location that both your normalized and raw data will get written to. Your raw data will show up with the prefix `_airbyte_raw_` in the namespace you define. If you don't enable basic normalization, you will only receive the raw tables. 

If only your destination supports namespaces, you have two simple options. **This is the most likely case**, as all HTTP APIs currently don't support Namespaces.

1. Replicate to the default namespace in the destination, which will differ based on your destination.
2. Create a "Custom Format" to rename the namespace that your data will be replicated into.

If both your desired source and destination support namespaces, your use case is probably replication-focused and more advanced, so continue reading.

## What is a Namespace?

Technical systems often group their underlying data into namespaces with each namespace's data isolated from another namespace. This isolation allows for better organisation and flexibility, leading to better usability.

An example of a namespace is the RDMS's `schema` concept. Some common use cases for schemas are enforcing permissions, segregating test and production data and general data organisation.

## Syncing

The Airbyte Protocol supports namespaces and allows Sources to define namespaces, and Destinations to write to various namespaces.

If the Source does not support namespaces, the data will be replicated into the Destination's default namespace. For databases, the default namespace is the schema provided in the destination configuration.

If the Destination does not support namespaces, the [namespace field](https://github.com/airbytehq/airbyte/blob/master/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L64) is ignored.

## Destination namespace configuration

As part of the [connections sync settings](connections/README.md), it is possible to configure the namespace used by:
1. destination connectors: to store the `_airbyte_raw_*` tables.
2. basic normalization: to store the final normalized tables.

Note that custom transformation outputs are not affected by the namespace settings from Airbyte: It is up to the configuration of the custom dbt project, and how it is written to handle its [custom schemas](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/using-custom-schemas). The default target schema for dbt in this case, will always be the destination namespace.

Available options for namespace configurations are:

### - Mirror source structure

Some sources (such as databases based on JDBC for example) are providing namespace informations from which a stream has been extracted from. Whenever a source is able to fill this field in the catalog.json file, the destination will try to reproduce exactly the same namespace when this configuraton is set.
For sources or streams where the source namespace is not known, the behavior will fall back to the "Destination Connector settings".

### - Destination connector settings

All stream will be replicated and store in the default namespace defined on the destination settings page.
In the destinations, namespace refers to:

| Destination Connector | Namespace setting |
| :--- | :--- |
| BigQuery | dataset |
| MSSQL | schema |
| MySql | database |
| Oracle DB | schema |
| Postgres | schema |
| Redshift | schema |
| Snowflake | schema |
| S3 | path prefix |

### - Custom format

When replicating multiple sources into the same destination, conflicts on tables being overwritten by syncs can occur.

For example, a Github source can be replicated into a "github" schema.
But if we have multiple connections to different GitHub repositories (similar in multi-tenant scenarios):

- we'd probably wish to keep the same table names (to keep consistent queries downstream)
- but store them in different namespaces (to avoid mixing data from different "tenants")

To solve this, we can either:

- use a specific namespace for each connection, thus this option of custom format.
- or, use prefix to stream names as described below.

Note that we can use a template format string using variables that will be resolved during replication as follow:

- `${SOURCE_NAMESPACE}`: will be replaced by the namespace provided by the source if available

### Examples

The following table summarises how this works. We assume an example of replication configurations between a Postgres Source and Snowflake Destination (with settings of schema = "my_schema"):

| Namespace Configuration | Source Namespace | Source Table Name | Destination Namespace | Destination Table Name |
| :--- | :--- | :--- | :--- | :--- |
| Mirror source structure | public | my_table | public | my_table |
| Mirror source structure | | my_table | my_schema | my_table |
| Destination connector settings | public | my_table | my_schema | my_table |
| Destination connector settings | | my_table | my_schema | my_table |
| Custom format = "custom" | public | my_table | custom | my_table |
| Custom format = "${SOURCE_NAMESPACE}" | public | my_table | public | my_table |
| Custom format = "my_${SOURCE_NAMESPACE}_schema" | public | my_table | my_public_schema | my_table |
| Custom format = "   " | public | my_table | my_schema | my_table |

## Requirements

* Both Source and Destination connectors need to support namespaces.
* Relevant Source and Destination connectors need to be at least version `0.3.0` or later.
* Airbyte version `0.21.0-alpha` or later.

## Current Support

### Sources

* MSSQL
* MYSQL
* Oracle DB
* Postgres
* Redshift

### Destination

* BigQuery
* MSSQL
* MySql
* Oracle DB
* Postgres
* Redshift
* Snowflake
* S3
