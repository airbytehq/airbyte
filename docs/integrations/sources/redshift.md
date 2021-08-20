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


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.3.2   | 2021-08-13 | [4699](https://github.com/airbytehq/airbyte/pull/4699) | Added json config validator |