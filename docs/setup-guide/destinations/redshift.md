# Redshift

This page contains the setup guide and reference information for Redshift.

## Prerequisites

The Redshift destination in Daspire has two replication strategies. Daspire automatically picks an approach depending on the given configuration - if S3 configuration is present, Daspire will use the COPY strategy and vice versa.

1. **INSERT:** Replicates data via SQL INSERT queries. This is built on top of the destination-jdbc code base and is configured to rely on JDBC 4.2 standard drivers provided by Amazon via Mulesoft [here](https://mvnrepository.com/artifact/com.amazon.redshift/redshift-jdbc42) as described in Redshift documentation [here](https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-install.html). **Not recommended for production workloads as this does not scale well**.

For INSERT strategy:

* **Host**
* **Port**
* **Username**
* **Password**
* **Schema**
* **Database**
  * This database needs to exist within the cluster provided.
* **JDBC URL Params** (optional)

2. **COPY:** Replicates data by first uploading data to an S3 bucket and issuing a COPY command. This is the recommended loading approach described by Redshift [best practices](https://docs.aws.amazon.com/redshift/latest/dg/c_loading-data-best-practices.html). Requires an S3 bucket and credentials.

For COPY strategy:

* **S3 Bucket Name**
  * See [this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) to create an S3 bucket.

* **S3 Bucket Region**
  * Place the S3 bucket and the Redshift cluster in the same region to save on networking costs.

* **Access Key Id**
  * See [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) on how to generate an access key.
  * We recommend creating a Daspire-specific user. This user will require [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html) to objects in the staging bucket.

* **Secret Access Key**
  * Corresponding key to the above key id.

* **Part Size**
  * Affects the size limit of an individual Redshift table. Optional. Increase this if syncing tables larger than 100GB. Files are streamed to S3 in parts. This determines the size of each part, in MBs. As S3 has a limit of 10,000 parts per file, part size affects the table size. This is 10MB by default, resulting in a default table limit of 100GB. Note, a larger part size will result in larger memory requirements. A rule of thumb is to multiply the part size by 10 to get the memory requirement. Modify this with care.

* **S3 Filename pattern**
  * The pattern allows you to set the file-name format for the S3 staging file(s), next placeholders combinations are currently supported: {date}, {date:yyyy\_MM}, {timestamp}, {timestamp:millis}, {timestamp:micros}, {part\_number}, {sync\_id}, {format\_extension}. Please, don't use empty space and not supportable placeholders, as they won't recognized.

Optional parameters:

* **Bucket Path**
  * The directory within the S3 bucket to place the staging data. For example, if you set this to `yourFavoriteSubdirectory`, we will place the staging data inside `s3://yourBucket/yourFavoriteSubdirectory`. If not provided, defaults to the root directory.

* **Purge Staging Data**
  * Whether to delete the staging files from S3 after completing the sync. Specifically, the connector will create CSV files named `bucketPath/namespace/streamName/syncDate_epochMillis_randomUuid.csv` containing three columns (`ab_id`, `data`, `emitted_at`). Normally these files are deleted after the COPY command completes; if you want to keep them for other purposes, set `purge_staging_data` to `false`.

## Setup guide

### Step 1: Set up Redshift

1. [Log in](https://aws.amazon.com/console/) to AWS Management console. If you don't have a AWS account already, you'll need to [create](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/) one in order to use the API.

2. Go to the AWS Redshift service

3. [Create](https://docs.aws.amazon.com/ses/latest/dg/event-publishing-redshift-cluster.html) and activate AWS Redshift cluster if you don't have one ready

4. (Optional) [Allow](https://aws.amazon.com/premiumsupport/knowledge-center/cannot-connect-redshift-cluster/) connections from Daspire to your Redshift cluster (if they exist in separate VPCs)

5. (Optional) [Create](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) a staging S3 bucket (for the COPY strategy).

### Step 2: Set up the destination connector in Daspire

1. Go to Daspire dashboard.

2. In the left navigation bar, click **Destinations**. In the top-right corner, click **+ New Destination**.

3. On the destination setup page, select **Redshift** from the Destination type dropdown and enter a name for this connector.

4. Fill in all the required fields to use the INSERT or COPY strategy.

5. Click **Save & Test**.

## Supported sync modes

The Redshift destination connector supports the following sync modes:

* Full Refresh
* Incremental - Append Sync
* Incremental - Deduped History

## Performance considerations

Synchronization performance depends on the amount of data to be transferred. Cluster scaling issues can be resolved directly using the cluster settings in the AWS Redshift console

## Destination-specific features & highlights

### Notes about Redshift Naming Conventions

From [Redshift Names & Identifiers](https://docs.aws.amazon.com/redshift/latest/dg/r_names.html):

#### Standard Identifiers

* Begin with an ASCII single-byte alphabetic character or underscore character, or a UTF-8 multibyte character two to four bytes long.

* Subsequent characters can be ASCII single-byte alphanumeric characters, underscores, or dollar signs, or UTF-8 multibyte characters two to four bytes long.

* Be between 1 and 127 bytes in length, not including quotation marks for delimited identifiers.

* Contain no quotation marks and no spaces.

#### Delimited Identifiers

Delimited identifiers (also known as quoted identifiers) begin and end with double quotation marks ("). If you use a delimited identifier, you must use the double quotation marks for every reference to that object. The identifier can contain any standard UTF-8 printable characters other than the double quotation mark itself. Therefore, you can create column or table names that include otherwise illegal characters, such as spaces or the percent symbol. ASCII letters in delimited identifiers are case-insensitive and are folded to lowercase. To use a double quotation mark in a string, you must precede it with another double quotation mark character.

Therefore, Daspire Redshift destination will create tables and schemes using the Unquoted identifiers when possible or fallback to Quoted Identifiers if the names contain special characters.

### Data Size Limitations

Redshift specifies a maximum limit of 1MB (and 65535 bytes for any VARCHAR fields within the JSON record) to store the raw JSON record data. Thus, when a row is too big to fit, the Redshift destination fails to load such data and currently ignores that record. See docs for [SUPER](https://docs.aws.amazon.com/redshift/latest/dg/r_SUPER_type.html) and [SUPER limitations](https://docs.aws.amazon.com/redshift/latest/dg/limitations-super.html)

### Encryption

All Redshift connections are encrypted using SSL

## Output schema

Each stream will be output into its own raw table in Redshift. Each table will contain 3 columns:

* `_daspire_ab_id`: a uuid assigned by Daspire to each event that is processed. The column type in Redshift is VARCHAR.

* `_daspire_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Redshift is TIMESTAMP WITH TIME ZONE.

* `_daspire_data`: a json blob representing with the event data. The column type in Redshift is VARCHAR but can be be parsed with JSON functions.

## Data type mapping

| Redshift Type | Daspire Type |
| --- | --- |
| `boolean` | `boolean` |
| `int` | `integer` |
| `float` | `number` |
| `varchar` | `string` |
| `date/varchar` | `date` |
| `time/varchar` | `time` |
| `timestamptz/varchar` | `timestamp_with_timezone` |
| `varchar` | `array` |
| `varchar` | `object` |