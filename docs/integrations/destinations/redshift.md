# Redshift

This page guides you through the process of setting up the Redshift destination connector.

## Prerequisites

The Airbyte Redshift destination allows you to sync data to Redshift.

This Redshift destination connector has two replication strategies:

1. INSERT: Replicates data via SQL INSERT queries. This is built on top of the destination-jdbc code base and is configured to rely on JDBC 4.2 standard drivers provided by Amazon via Mulesoft [here](https://mvnrepository.com/artifact/com.amazon.redshift/redshift-jdbc42) as described in Redshift documentation [here](https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-install.html). **Not recommended for production workloads as this does not scale well**.

For INSERT strategy:
* **Host**
* **Port**
* **Username**
* **Password**
* **Schema**
* **Database**
    * This database needs to exist within the cluster provided.

2. COPY: Replicates data by first uploading data to an S3 bucket and issuing a COPY command. This is the recommended loading approach described by Redshift [best practices](https://docs.aws.amazon.com/redshift/latest/dg/c_loading-data-best-practices.html). Requires an S3 bucket and credentials.

Airbyte automatically picks an approach depending on the given configuration - if S3 configuration is present, Airbyte will use the COPY strategy and vice versa.

For COPY strategy:

* **S3 Bucket Name**
    * See [this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) to create an S3 bucket.
* **S3 Bucket Region**
    * Place the S3 bucket and the Redshift cluster in the same region to save on networking costs.
* **Access Key Id**
    * See [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) on how to generate an access key.
    * We recommend creating an Airbyte-specific user. This user will require [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html) to objects in the staging bucket.
* **Secret Access Key**
    * Corresponding key to the above key id.
* **Part Size**
    * Affects the size limit of an individual Redshift table. Optional. Increase this if syncing tables larger than 100GB. Files are streamed to S3 in parts. This determines the size of each part, in MBs. As S3 has a limit of 10,000 parts per file, part size affects the table size. This is 10MB by default, resulting in a default table limit of 100GB. Note, a larger part size will result in larger memory requirements. A rule of thumb is to multiply the part size by 10 to get the memory requirement. Modify this with care.
* **S3 Filename pattern**
    * The pattern allows you to set the file-name format for the S3 staging file(s), next placeholders combinations are currently supported: {date}, {date:yyyy_MM}, {timestamp}, {timestamp:millis}, {timestamp:micros}, {part_number}, {sync_id}, {format_extension}. Please, don't use empty space and not supportable placeholders, as they won't recognized.

Optional parameters:
* **Bucket Path**
    * The directory within the S3 bucket to place the staging data. For example, if you set this to `yourFavoriteSubdirectory`, we will place the staging data inside `s3://yourBucket/yourFavoriteSubdirectory`. If not provided, defaults to the root directory.
* **Purge Staging Data**
    * Whether to delete the staging files from S3 after completing the sync. Specifically, the connector will create CSV files named `bucketPath/namespace/streamName/syncDate_epochMillis_randomUuid.csv` containing three columns (`ab_id`, `data`, `emitted_at`). Normally these files are deleted after the `COPY` command completes; if you want to keep them for other purposes, set `purge_staging_data` to `false`.


## Step 1: Set up Redshift

1. [Log in](https://aws.amazon.com/console/) to AWS Management console.
   If you don't have a AWS account already, you’ll need to [create](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/) one in order to use the API.
2. Go to the AWS Redshift service
3. [Create](https://docs.aws.amazon.com/ses/latest/dg/event-publishing-redshift-cluster.html) and activate AWS Redshift cluster if you don't have one ready
4. (Optional) [Allow](https://aws.amazon.com/premiumsupport/knowledge-center/cannot-connect-redshift-cluster/) connections from Airbyte to your Redshift cluster \(if they exist in separate VPCs\)
5. (Optional) [Create](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) a staging S3 bucket \(for the COPY strategy\).

## Step 2: Set up the destination connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **+ new destination**.
3. On the destination setup page, select **Redshift** from the Destination type dropdown and enter a name for this connector.
4. Fill in all the required fields to use the INSERT or COPY strategy
5. Click `Set up destination`.

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **+ new destination**.
3. On the destination setup page, select **Redshift** from the Destination type dropdown and enter a name for this connector.
4. Fill in all the required fields to use the INSERT or COPY strategy
5. Click `Set up destination`.


## Supported sync modes

The Redshift destination connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):
- Full Refresh
- Incremental - Append Sync
- Incremental - Deduped History

## Performance considerations

Synchronization performance depends on the amount of data to be transferred.
Cluster scaling issues can be resolved directly using the cluster settings in the AWS Redshift console

## Connector-specific features & highlights

### Notes about Redshift Naming Conventions

From [Redshift Names & Identifiers](https://docs.aws.amazon.com/redshift/latest/dg/r_names.html):

#### Standard Identifiers

* Begin with an ASCII single-byte alphabetic character or underscore character, or a UTF-8 multibyte character two to four bytes long.
* Subsequent characters can be ASCII single-byte alphanumeric characters, underscores, or dollar signs, or UTF-8 multibyte characters two to four bytes long.
* Be between 1 and 127 bytes in length, not including quotation marks for delimited identifiers.
* Contain no quotation marks and no spaces.

#### Delimited Identifiers

Delimited identifiers \(also known as quoted identifiers\) begin and end with double quotation marks \("\). If you use a delimited identifier, you must use the double quotation marks for every reference to that object. The identifier can contain any standard UTF-8 printable characters other than the double quotation mark itself. Therefore, you can create column or table names that include otherwise illegal characters, such as spaces or the percent symbol. ASCII letters in delimited identifiers are case-insensitive and are folded to lowercase. To use a double quotation mark in a string, you must precede it with another double quotation mark character.

Therefore, Airbyte Redshift destination will create tables and schemas using the Unquoted identifiers when possible or fallback to Quoted Identifiers if the names are containing special characters.

### Data Size Limitations

Redshift specifies a maximum limit of 1MB (and 65535 bytes for any VARCHAR fields within the JSON record) to store the raw JSON record data. Thus, when a row is too big to fit, the Redshift destination fails to load such data and currently ignores that record.
See docs for [SUPER](https://docs.aws.amazon.com/redshift/latest/dg/r_SUPER_type.html) and [SUPER limitations](https://docs.aws.amazon.com/redshift/latest/dg/limitations-super.html)

### Encryption

All Redshift connections are encrypted using SSL

### Output schema

Each stream will be output into its own raw table in Redshift. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Redshift is `VARCHAR`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Redshift is `TIMESTAMP WITH TIME ZONE`.
* `_airbyte_data`: a json blob representing with the event data. The column type in Redshift is `VARCHAR` but can be be parsed with JSON functions.

## Data type mapping

| Redshift Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `boolean` | `boolean` | |
| `int` | `integer` | |
| `float` | `number` | |
| `varchar` | `string` | |
| `date/varchar` | `date` | |
| `time/varchar` | `time` | |
| `timestamptz/varchar` | `timestamp_with_timezone` | |
| `varchar` | `array` | |
| `varchar` | `object` | |

## Changelog

| Version | Date       | Pull Request                                               | Subject                                                                                                                                                                                                          |
|:--------|:-----------|:-----------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.3.47  | 2022-07-15 | [\#14494](https://github.com/airbytehq/airbyte/pull/14494) | Make S3 output filename configurable.                                                                                                                                                                            |
| 0.3.46  | 2022-06-27 | [\#14190](https://github.com/airbytehq/airbyte/pull/13916) | Correctly cleanup S3 bucket when using a configured bucket path for S3 staging operations.                                                                                                                       |
| 0.3.45  | 2022-06-25 | [\#13916](https://github.com/airbytehq/airbyte/pull/13916) | Use the configured bucket path for S3 staging operations.                                                                                                                                                        |
| 0.3.44  | 2022-06-24 | [\#14114](https://github.com/airbytehq/airbyte/pull/14114) | Remove "additionalProperties": false from specs for connectors with staging                                                                                                                                      |
| 0.3.43  | 2022-06-24 | [\#13690](https://github.com/airbytehq/airbyte/pull/13690) | Improved discovery for NOT SUPER column                                                                                                                                                                          |
| 0.3.42  | 2022-06-21 | [\#14013](https://github.com/airbytehq/airbyte/pull/14013) | Add an option to use encryption with staging in Redshift Destination                                                                                                                                             |
| 0.3.40  | 2022-06-17 | [\#13753](https://github.com/airbytehq/airbyte/pull/13753) | Deprecate and remove PART_SIZE_MB fields from connectors based on StreamTransferManager                                                                                                                          |
| 0.3.39  | 2022-06-02 | [13415](https://github.com/airbytehq/airbyte/pull/13415)   | Add dropdown to select Uploading Method. <br /> **PLEASE NOTICE**: After this update your **uploading method** will be set to **Standard**, you will need to reconfigure the method to use **S3 Staging** again. | 
| 0.3.37  | 2022-05-23 | [13090](https://github.com/airbytehq/airbyte/pull/13090)   | Removed redshiftDataTmpTableMode. Some refactoring.                                                                                                                                                              | 
| 0.3.36  | 2022-05-23 | [12820](https://github.com/airbytehq/airbyte/pull/12820)   | Improved 'check' operation performance                                                                                                                                                                           |
| 0.3.35  | 2022-05-18 | [12940](https://github.com/airbytehq/airbyte/pull/12940)   | Fixed maximum record size for SUPER type                                                                                                                                                                         |
| 0.3.34  | 2022-05-16 | [12869](https://github.com/airbytehq/airbyte/pull/12869)   | Fixed NPE in S3 staging check                                                                                                                                                                                    |
| 0.3.33  | 2022-05-04 | [12601](https://github.com/airbytehq/airbyte/pull/12601)   | Apply buffering strategy for S3 staging                                                                                                                                                                          |
| 0.3.32  | 2022-04-20 | [12085](https://github.com/airbytehq/airbyte/pull/12085)   | Fixed bug with switching between INSERT and COPY config                                                                                                                                                          |
| 0.3.31  | 2022-04-19 | [\#12064](https://github.com/airbytehq/airbyte/pull/12064) | Added option to support SUPER datatype in _airbyte_raw_** table                                                                                                                                                  |
| 0.3.29  | 2022-04-05 | [11729](https://github.com/airbytehq/airbyte/pull/11729)   | Fixed bug with dashes in schema name                                                                                                                                                                             |                                                                   |
| 0.3.28  | 2022-03-18 | [\#11254](https://github.com/airbytehq/airbyte/pull/11254) | Fixed missing records during S3 staging                                                                                                                                                                          |
| 0.3.27  | 2022-02-25 | [10421](https://github.com/airbytehq/airbyte/pull/10421)   | Refactor JDBC parameters handling                                                                                                                                                                                |
| 0.3.25  | 2022-02-14 | [#9920](https://github.com/airbytehq/airbyte/pull/9920)    | Updated the size of staging files for S3 staging. Also, added closure of S3 writers to staging files when data has been written to an staging file.                                                              |
| 0.3.24  | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                                                                                                     |
| 0.3.23  | 2021-12-16 | [\#8855](https://github.com/airbytehq/airbyte/pull/8855)   | Add `purgeStagingData` option to enable/disable deleting the staging data                                                                                                                                        |
| 0.3.22  | 2021-12-15 | [#8607](https://github.com/airbytehq/airbyte/pull/8607)    | Accept a path for the staging data                                                                                                                                                                               |
| 0.3.21  | 2021-12-10 | [#8562](https://github.com/airbytehq/airbyte/pull/8562)    | Moving classes around for better dependency management                                                                                                                                                           |
| 0.3.20  | 2021-11-08 | [#7719](https://github.com/airbytehq/airbyte/pull/7719)    | Improve handling of wide rows by buffering records based on their byte size rather than their count                                                                                                              |
| 0.3.19  | 2021-10-21 | [7234](https://github.com/airbytehq/airbyte/pull/7234)     | Allow SSL traffic only                                                                                                                                                                                           |
| 0.3.17  | 2021-10-12 | [6965](https://github.com/airbytehq/airbyte/pull/6965)     | Added SSL Support                                                                                                                                                                                                |
| 0.3.16  | 2021-10-11 | [6949](https://github.com/airbytehq/airbyte/pull/6949)     | Each stream was split into files of 10,000 records each for copying using S3 or GCS                                                                                                                              |
| 0.3.14  | 2021-10-08 | [5924](https://github.com/airbytehq/airbyte/pull/5924)     | Fixed AWS S3 Staging COPY is writing records from different table in the same raw table                                                                                                                          |
| 0.3.13  | 2021-09-02 | [5745](https://github.com/airbytehq/airbyte/pull/5745)     | Disable STATUPDATE flag when using S3 staging to speed up performance                                                                                                                                            |
| 0.3.12  | 2021-07-21 | [3555](https://github.com/airbytehq/airbyte/pull/3555)     | Enable partial checkpointing for halfway syncs                                                                                                                                                                   |
| 0.3.11  | 2021-07-20 | [4874](https://github.com/airbytehq/airbyte/pull/4874)     | allow `additionalProperties` in connector spec                                                                                                                                                                   |


