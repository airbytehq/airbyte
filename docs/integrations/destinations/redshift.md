# Redshift

## Overview

The Airbyte Redshift destination allows you to sync data to Redshift.

This Redshift destination connector is built on top of the destination-jdbc code base and is configured to rely on JDBC 4.2 standard drivers provided by Amazon via Mulesoft [here](https://mvnrepository.com/artifact/com.amazon.redshift/redshift-jdbc42) as described in Redshift documentation [here](https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-install.html).

### Sync overview

#### Output schema

Each stream will be output into its own raw table in Redshift. Each table will contain 3 columns:

* `ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Redshift is `VARCHAR`.
* `emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Redshift is `TIMESTAMP WITH TIME ZONE`.
* `data`: a json blob representing with the event data. The column type in Redshift is `VARCHAR` but can be be parsed with JSON functions.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

## Getting started

### Requirements

1. Active Redshift cluster
2. Allow connections from Airbyte to your Redshift cluster \(if they exist in separate VPCs\)

### Setup guide

#### 1. Make sure your cluster is active and accessible from the machine running Airbyte

This is dependent on your networking setup. The easiest way to verify if Airbyte is able to connect to your Redshift cluster is via the check connection tool in the UI. You can check AWS Redshift documentation with a tutorial on how to properly configure your cluster's access [here](https://docs.aws.amazon.com/redshift/latest/gsg/rs-gsg-authorize-cluster-access.html)

#### 2. Fill up connection info

Next is to provide the necessary information on how to connect to your cluster such as the `host` whcih is part of the connection string or Endpoint accessible [here](https://docs.aws.amazon.com/redshift/latest/gsg/rs-gsg-connect-to-cluster.html#rs-gsg-how-to-get-connection-string) without the `port` and `database` name \(it typically includes the cluster-id, region and end with `.redshift.amazonaws.com`\).

You should have all the requirements needed to configure Redshift as a destination in the UI. You'll need the following information to configure the destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Schema**
* **Database**
  * This database needs to exist within the cluster provided.

## Notes about Redshift Naming Conventions

From [Redshift Names & Identifiers](https://docs.aws.amazon.com/redshift/latest/dg/r_names.html):

### Standard Identifiers

* Begin with an ASCII single-byte alphabetic character or underscore character, or a UTF-8 multibyte character two to four bytes long.
* Subsequent characters can be ASCII single-byte alphanumeric characters, underscores, or dollar signs, or UTF-8 multibyte characters two to four bytes long.
* Be between 1 and 127 bytes in length, not including quotation marks for delimited identifiers.
* Contain no quotation marks and no spaces.

### Delimited Identifiers

Delimited identifiers \(also known as quoted identifiers\) begin and end with double quotation marks \("\). If you use a delimited identifier, you must use the double quotation marks for every reference to that object. The identifier can contain any standard UTF-8 printable characters other than the double quotation mark itself. Therefore, you can create column or table names that include otherwise illegal characters, such as spaces or the percent symbol. ASCII letters in delimited identifiers are case-insensitive and are folded to lowercase. To use a double quotation mark in a string, you must precede it with another double quotation mark character.

Therefore, Airbyte Redshift destination will create tables and schemas using the Unquoted identifiers when possible or fallback to Quoted Identifiers if the names are containing special characters.

