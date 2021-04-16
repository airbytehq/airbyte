# Redshift

## Overview

The Airbyte Redshift destination allows you to sync data to Redshift.

This Redshift destination connector has two replication strategies:
1) INSERT: Replicates data via SQL INSERT queries. This is built on top of the destination-jdbc code base and is configured to rely on JDBC 4.2 standard drivers provided by Amazon via Mulesoft [here](https://mvnrepository.com/artifact/com.amazon.redshift/redshift-jdbc42) as described in Redshift documentation [here](https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-install.html). Not recommended for production workloads as this does not scale well.
2) COPY: Replicates data by first uploading data to an S3 bucket and issuing a COPY command. This is the recommended loading approach described by Redshift [best practices](https://docs.aws.amazon.com/redshift/latest/dg/c_loading-data-best-practices.html). Requires an S3 bucket and credentials.

Airbyte automatically picks an approach depending on the given configuration - if S3 configuration is present, Airbyte will use the COPY strategy and vice versa.

We recommend users use INSERT for testing, to avoid any additional setup, and switch to COPY for production workloads.

### Sync overview

#### Output schema

Each stream will be output into its own raw table in Redshift. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Redshift is `VARCHAR`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Redshift is `TIMESTAMP WITH TIME ZONE`.
* `_airbyte_data`: a json blob representing with the event data. The column type in Redshift is `VARCHAR` but can be be parsed with JSON functions.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

## Getting started

### Requirements

1. Active Redshift cluster
2. Allow connections from Airbyte to your Redshift cluster \(if they exist in separate VPCs\)
3. A staging S3 bucket with credentials (for the COPY strategy).

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

#### 2a. Fill up S3 info (for COPY strategy)

Provide the required S3 info.

* **S3 Bucket Name**
  * See [this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) to create an S3 bucket.
* **S3 Bucket Region**
  * Place the S3 bucket and the Redshift cluster in the same region to save on networking costs.
* **Access Key Id**
  * See [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) on how to generate an access key.
  * We recommend creating an Airbyte-specific user. This user will require [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html) to objects in the staging bucket. 
* **Secret Access Key**
  * Corresponding key to the above key id.

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

