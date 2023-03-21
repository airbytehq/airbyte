# Redshift

## Overview

The Redshift source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

This Redshift source connector is built on top of the source-jdbc code base and is configured to rely on JDBC 4.2 standard drivers provided by Amazon via Mulesoft [here](https://mvnrepository.com/artifact/com.amazon.redshift/redshift-jdbc42) as described in Redshift documentation [here](https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-install.html).

### Sync overview

#### Resulting schema

The Redshift source does not alter the schema present in your warehouse. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Features

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Coming soon |  |
| Replicate Incremental Deletes | Coming soon |  |
| Logical Replication \(WAL\) | Coming soon |  |
| SSL Support | Yes |  |
| SSH Tunnel Connection | Coming soon |  |
| Namespaces | Yes | Enabled by default |
| Schema Selection | Yes | Multiple schemas may be used at one time. Keep empty to process all of existing schemas |

#### Incremental Sync

Incremental sync \(copying only the data that has changed\) for this source is coming soon.

## Getting started

### Requirements

1. Active Redshift cluster
2. Allow connections from Airbyte to your Redshift cluster \(if they exist in separate VPCs\)

### Setup guide

#### 1. Make sure your cluster is active and accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your Redshift cluster is via the check connection tool in the UI. You can check AWS Redshift documentation with a tutorial on how to properly configure your cluster's access [here](https://docs.aws.amazon.com/redshift/latest/gsg/rs-gsg-authorize-cluster-access.html)

#### 2. Fill up connection info

Next is to provide the necessary information on how to connect to your cluster such as the `host` whcih is part of the connection string or Endpoint accessible [here](https://docs.aws.amazon.com/redshift/latest/gsg/rs-gsg-connect-to-cluster.html#rs-gsg-how-to-get-connection-string) without the `port` and `database` name \(it typically includes the cluster-id, region and end with `.redshift.amazonaws.com`\).

## Encryption

All Redshift connections are encrypted using SSL

## Changelog

| Version | Date       | Pull Request | Subject                                                                                                   |
|:--------|:-----------| :-----       |:----------------------------------------------------------------------------------------------------------|
| 0.3.16  | 2022-12-14 | [20436](https://github.com/airbytehq/airbyte/pull/20346)   | Consolidate date/time values mapping for JDBC sources                          |
| 0.3.15  | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238) | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.3.14  | 2022-09-01 | [16258](https://github.com/airbytehq/airbyte/pull/16258) | Emit state messages more frequently |
| 0.3.13  | 2022-05-25 |  | Added JDBC URL params                                                                                     |
| 0.3.12  | 2022-08-18 | [14356](https://github.com/airbytehq/airbyte/pull/14356) | DB Sources: only show a table can sync incrementally if at least one column can be used as a cursor field |
| 0.3.11  | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574) | Removed additionalProperties:false from JDBC source connectors                                            |
| 0.3.10  | 2022-04-29 | [12480](https://github.com/airbytehq/airbyte/pull/12480) | Query tables with adaptive fetch size to optimize JDBC memory consumption                                 |0
| 0.3.9   | 2022-02-21 | [9744](https://github.com/airbytehq/airbyte/pull/9744) | List only the tables on which the user has SELECT permissions.                                            
| 0.3.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                              |
| 0.3.7   | 2022-01-26 | [9721](https://github.com/airbytehq/airbyte/pull/9721) | Added schema selection                                                                                    |
| 0.3.6   | 2022-01-20 | [8617](https://github.com/airbytehq/airbyte/pull/8617) | Update connector fields title/description                                                                 |
| 0.3.5   | 2021-12-24 | [8958](https://github.com/airbytehq/airbyte/pull/8958) | Add support for JdbcType.ARRAY                                                                            |
| 0.3.4   | 2021-10-21 | [7234](https://github.com/airbytehq/airbyte/pull/7234) | Allow SSL traffic only                                                                                    |
| 0.3.3   | 2021-10-12 | [6965](https://github.com/airbytehq/airbyte/pull/6965) | Added SSL Support                                                                                         |
| 0.3.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator                                                                               |
