# Firebolt

This page guides you through the process of setting up the Firebolt destination connector.

## Prerequisites

This Firebolt destination connector has two replication strategies:

1. SQL: Replicates data via SQL INSERT queries. This leverages [Firebolt SDK](https://pypi.org/project/firebolt-sdk/) to execute queries directly on Firebolt [Engines](https://docs.firebolt.io/working-with-engines/understanding-engine-fundamentals.html). **Not recommended for production workloads as this does not scale well**.

2. S3: Replicates data by first uploading data to an S3 bucket, creating an External Table and writing into a final Fact Table. This is the recommended loading [approach](https://docs.firebolt.io/loading-data/loading-data.html). Requires an S3 bucket and credentials in addition to Firebolt credentials.

For SQL strategy:
* **Host**
* **Username**
* **Password**
* **Database**
* **Engine (optional)**


Airbyte automatically picks an approach depending on the given configuration - if S3 configuration is present, Airbyte will use the S3 strategy.

For S3 strategy:

* **Username**
* **Password**
* **Database**
* **S3 Bucket Name**
    * See [this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) to create an S3 bucket.
* **S3 Bucket Region**
    * Create the S3 bucket on the same region as the Firebolt database.
* **Access Key Id**
    * See [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) on how to generate an access key.
    * We recommend creating an Airbyte-specific user. This user will require [read, write and delete permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html) to objects in the staging bucket.
* **Secret Access Key**
    * Corresponding key to the above key id.
* **Host (optional)**
    * Firebolt backend URL. Can be left blank for most usecases.
* **Engine (optional)**
    * If connecting to a non-default engine you should specify its name or url here.

## Setup guide

1. Create a Firebolt account following the [guide](https://docs.firebolt.io/managing-your-account/creating-an-account.html)
1. Follow the getting started [tutorial](https://docs.firebolt.io/getting-started.html) to setup a database.
1. Create a General Purpose (read-write) engine as described in [here](https://docs.firebolt.io/working-with-engines/working-with-engines-using-the-firebolt-manager.html)
1. (Optional) [Create](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) a staging S3 bucket \(for the S3 strategy\).
1. (Optional) [Create](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-iam-policies.html) an IAM with programmatic access to read, write and delete objects from an S3 bucket.


## Supported sync modes

The Firebolt destination connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):
- Full Refresh
- Incremental - Append Sync


## Connector-specific features & highlights


### Output schema

Each stream will be output into its own raw [Fact table](https://docs.firebolt.io/working-with-tables.html#fact-and-dimension-tables) in Firebolt. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Firebolt is `VARCHAR`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Firebolt is `TIMESTAMP`.
* `_airbyte_data`: a json blob representing the event data. The column type in Firebolt is `VARCHAR` but can be be parsed with JSON functions.


## Changelog

| Version | Date       | Pull Request | Subject |
|:--------|:-----------| :-----       | :------ |
| 0.1.0  | 2022-05-18 | [13118](https://github.com/airbytehq/airbyte/pull/13118) | New Destination: Firebolt |
