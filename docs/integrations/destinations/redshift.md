# Redshift

This page guides you through the process of setting up the Redshift destination connector.

## Prerequisites

The Airbyte Redshift destination allows you to sync data to Redshift. Airbyte replicates data by first uploading data to an S3 bucket and issuing a COPY command. This is the recommended loading approach described by Redshift [best practices](https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-single-copy-command.html). Requires an S3 bucket and credentials. Data is copied into S3 as multiple files with a manifest file.

### Configuration Options

- **Host**
- **Port**
- **Username**
- **Password**
- **Schema**
- **Database**
  - This database needs to exist within the cluster provided.
- **S3 Bucket Name**
  - See [this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) to
    create an S3 bucket.
- **S3 Bucket Region**
  - Place the S3 bucket and the Redshift cluster in the same region to save on networking costs.
- **Access Key Id**
  - See
    [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
    on how to generate an access key.
  - We recommend creating an Airbyte-specific user. This user will require
    [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html)
    to objects in the staging bucket.
- **Secret Access Key**
  - Corresponding key to the above key id.

Optional parameters:

- **Bucket Path**
  - The directory within the S3 bucket to place the staging data. For example, if you set this to
    `yourFavoriteSubdirectory`, we will place the staging data inside
    `s3://yourBucket/yourFavoriteSubdirectory`. If not provided, defaults to the root directory.
- **S3 Filename pattern**
  - The pattern allows you to set the file-name format for the S3 staging file(s), next placeholders combinations are currently supported: `{date}`, `{date:yyyy_MM}`, `{timestamp}`,
    `{timestamp:millis}`, `{timestamp:micros}`, `{part_number}`, `{sync_id}`, `{format_extension}`.
    The pattern you supply will apply to anything under the Bucket Path. If this field is left blank, everything syncs under the Bucket Path. Please, don't use empty space and not supportable placeholders, as they won't recognized.
- **Purge Staging Data**
  - Whether to delete the staging files from S3 after completing the sync. Specifically, the
    connector will create CSV files named
    `bucketPath/namespace/streamName/syncDate_epochMillis_randomUuid.csv` containing three columns
    (`ab_id`, `data`, `emitted_at`). Normally these files are deleted after the `COPY` command
    completes; if you want to keep them for other purposes, set `purge_staging_data` to `false`.

NOTE: S3 staging does not use the SSH Tunnel option for copying data, if configured. SSH Tunnel
supports the SQL connection only. S3 is secured through public HTTPS access only. Subsequent typing
and deduping queries on final table are executed over using provided SSH Tunnel configuration.

## Step 1: Set up Redshift

1. [Log in](https://aws.amazon.com/console/) to AWS Management console. If you don't have a AWS
   account already, you’ll need to
   [create](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)
   one in order to use the API.
2. Go to the AWS Redshift service.
3. [Create](https://docs.aws.amazon.com/ses/latest/dg/event-publishing-redshift-cluster.html) and
   activate AWS Redshift cluster if you don't have one ready.
4. (Optional)
   [Allow](https://aws.amazon.com/premiumsupport/knowledge-center/cannot-connect-redshift-cluster/)
   connections from Airbyte to your Redshift cluster \(if they exist in separate VPCs\).
5. (Optional)
   [Create](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) a
   staging S3 bucket \(for the COPY strategy\).

### Permissions in Redshift

Airbyte writes data into two schemas, whichever schema you want your data to land in, e.g.
`my_schema` and a "Raw Data" schema that Airbyte uses to improve ELT reliability. By default, this
raw data schema is `airbyte_internal` but this can be overridden in the Redshift Destination's
advanced settings. Airbyte also needs to query Redshift's
[SVV_TABLE_INFO](https://docs.aws.amazon.com/redshift/latest/dg/r_SVV_TABLE_INFO.html) table for
metadata about the tables airbyte manages.

To ensure the `airbyte_user` has the correction permissions to:

- create schemas in your database
- grant usage to any existing schemas you want Airbyte to use
- grant select to the `svv_table_info` table

You can execute the following SQL statements

```sql
GRANT CREATE ON DATABASE database_name TO airbyte_user; -- add create schema permission
GRANT usage, create on schema my_schema TO airbyte_user; -- add create table permission
GRANT SELECT ON TABLE SVV_TABLE_INFO TO airbyte_user; -- add select permission for svv_table_info
```

### Optional Use of SSH Bastion Host

This connector supports the use of a Bastion host as a gateway to a private Redshift cluster via SSH
Tunneling. Setup of the host is beyond the scope of this document but several tutorials are
available online to fascilitate this task. Enter the bastion host, port and credentials in the
destination configuration.

## Step 2: Set up the destination connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **+ new
   destination**.
3. On the destination setup page, select **Redshift** from the Destination type dropdown and enter a
   name for this connector.
4. Fill in all the required fields to use the INSERT or COPY strategy.
5. Click `Set up destination`.

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **+ new
   destination**.
3. On the destination setup page, select **Redshift** from the Destination type dropdown and enter a
   name for this connector.
4. Fill in all the required fields to use the INSERT or COPY strategy.
5. Click `Set up destination`.

## Supported sync modes

The Redshift destination connector supports the following
[sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):

- Full Refresh
- Incremental - Append Sync
- Incremental - Append + Deduped

## Performance considerations

Synchronization performance depends on the amount of data to be transferred. Cluster scaling issues
can be resolved directly using the cluster settings in the AWS Redshift console.

## Connector-specific features & highlights

### Notes about Redshift Naming Conventions

From [Redshift Names & Identifiers](https://docs.aws.amazon.com/redshift/latest/dg/r_names.html):

#### Standard Identifiers

- Begin with an ASCII single-byte alphabetic character or underscore character, or a UTF-8 multibyte
  character two to four bytes long.
- Subsequent characters can be ASCII single-byte alphanumeric characters, underscores, or dollar
  signs, or UTF-8 multibyte characters two to four bytes long.
- Be between 1 and 127 bytes in length, not including quotation marks for delimited identifiers.
- Contain no quotation marks and no spaces.

#### Delimited Identifiers

Delimited identifiers \(also known as quoted identifiers\) begin and end with double quotation marks
\("\). If you use a delimited identifier, you must use the double quotation marks for every
reference to that object. The identifier can contain any standard UTF-8 printable characters other
than the double quotation mark itself. Therefore, you can create column or table names that include
otherwise illegal characters, such as spaces or the percent symbol. ASCII letters in delimited
identifiers are case-insensitive and are folded to lowercase. To use a double quotation mark in a
string, you must precede it with another double quotation mark character.

Therefore, Airbyte Redshift destination will create tables and schemas using the Unquoted
identifiers when possible or fallback to Quoted Identifiers if the names are containing special
characters.

### Data Size Limitations

Redshift specifies a maximum limit of 16MB (and 65535 bytes for any VARCHAR fields within the JSON
record) to store the raw JSON record data. Thus, when a row is too big to fit, the destination
connector will do one of the following.

1. Null the value if the varchar size > 65535, The corresponding key information is added to
   `_airbyte_meta`.
2. Null the whole record while trying to preserve the Primary Keys and cursor field declared as part
   of your stream configuration, if the total record size is > 16MB.
   - For DEDUPE sync mode, if we do not find Primary key(s), we fail the sync.
   - For OVERWRITE and APPEND mode, syncs will succeed with empty records emitted, if we fail to
     find Primary key(s).

See AWS docs for [SUPER](https://docs.aws.amazon.com/redshift/latest/dg/r_SUPER_type.html) and
[SUPER limitations](https://docs.aws.amazon.com/redshift/latest/dg/limitations-super.html).

### Encryption

All Redshift connections are encrypted using SSL.

### Output schema

Each stream will be output into its own raw table in Redshift. Each table will contain 3 columns:

- `_airbyte_raw_id`: a uuid assigned by Airbyte to each event that is processed. The column type in
  Redshift is `VARCHAR`.
- `_airbyte_extracted_at`: a timestamp representing when the event was pulled from the data source.
  The column type in Redshift is `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_loaded_at`: a timestamp representing when the row was processed into final table. The
  column type in Redshift is `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_data`: a json blob representing with the event data. The column type in Redshift is
  `SUPER`.

## Data type map

| Airbyte type                        | Redshift type                          |
| :---------------------------------- | :------------------------------------- |
| STRING                              | VARCHAR                                |
| STRING (BASE64)                     | VARCHAR                                |
| STRING (BIG_NUMBER)                 | VARCHAR                                |
| STRING (BIG_INTEGER)                | VARCHAR                                |
| NUMBER                              | DECIMAL / NUMERIC                      |
| INTEGER                             | BIGINT / INT8                          |
| BOOLEAN                             | BOOLEAN / BOOL                         |
| STRING (TIMESTAMP_WITH_TIMEZONE)    | TIMESTAMPTZ / TIMESTAMP WITH TIME ZONE |
| STRING (TIMESTAMP_WITHOUT_TIMEZONE) | TIMESTAMP                              |
| STRING (TIME_WITH_TIMEZONE)         | TIMETZ / TIME WITH TIME ZONE           |
| STRING (TIME_WITHOUT_TIMEZONE)      | TIME                                   |
| DATE                                | DATE                                   |
| OBJECT                              | SUPER                                  |
| ARRAY                               | SUPER                                  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                                                                                                                          |
| :------ | :--------- | :--------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 3.5.0   | 2024-09-18 | [45435](https://github.com/airbytehq/airbyte/pull/45435)   | upgrade all dependencies                                                                                                                                                                          |
| 3.4.4   | 2024-08-20 | [44476](https://github.com/airbytehq/airbyte/pull/44476)   | Increase message parsing limit to 100mb                                                                                                                                                                          |
| 3.4.3   | 2024-08-22 | [44526](https://github.com/airbytehq/airbyte/pull/44526)   | Revert protocol compliance fix                                                                                                                                                                                   |
| 3.4.2   | 2024-08-15 | [42506](https://github.com/airbytehq/airbyte/pull/42506)   | Fix bug in refreshes logic (already mitigated in platform, just fixing protocol compliance)                                                                                                                      |
| 3.4.1   | 2024-08-13 | [xxx](https://github.com/airbytehq/airbyte/pull/xxx)       | Simplify Redshift Options                                                                                                                                                                                        |
| 3.4.0   | 2024-07-23 | [42445](https://github.com/airbytehq/airbyte/pull/42445)   | Respect the `drop cascade` option on raw tables                                                                                                                                                                  |
| 3.3.1   | 2024-07-15 | [41968](https://github.com/airbytehq/airbyte/pull/41968)   | Don't hang forever on empty stream list; shorten error message on INCOMPLETE stream status                                                                                                                       |
| 3.3.0   | 2024-07-02 | [40567](https://github.com/airbytehq/airbyte/pull/40567)   | Support for [refreshes](../../operator-guides/refreshes.md) and resumable full refresh. WARNING: You must upgrade to platform 0.63.7 before upgrading to this connector version.                                 |
| 3.2.0   | 2024-07-02 | [40201](https://github.com/airbytehq/airbyte/pull/40201)   | Add `_airbyte_generation_id` column, and add `sync_id` to `_airbyte_meta` column                                                                                                                                 |
| 3.1.1   | 2024-06-26 | [39008](https://github.com/airbytehq/airbyte/pull/39008)   | Internal code changes                                                                                                                                                                                            |
| 3.1.0   | 2024-06-26 | [39141](https://github.com/airbytehq/airbyte/pull/39141)   | Remove nonfunctional "encrypted staging" option                                                                                                                                                                  |
| 3.0.0   | 2024-06-04 | [38886](https://github.com/airbytehq/airbyte/pull/38886)   | Remove standard inserts mode                                                                                                                                                                                     |
| 2.6.4   | 2024-05-31 | [38825](https://github.com/airbytehq/airbyte/pull/38825)   | Adopt CDK 0.35.15                                                                                                                                                                                                |
| 2.6.3   | 2024-05-31 | [38803](https://github.com/airbytehq/airbyte/pull/38803)   | Source auto-conversion to Kotlin                                                                                                                                                                                 |
| 2.6.2   | 2024-05-14 | [38189](https://github.com/airbytehq/airbyte/pull/38189)   | adding an option to DROP CASCADE on resets                                                                                                                                                                       |
| 2.6.1   | 2024-05-13 | [\#38126](https://github.com/airbytehq/airbyte/pull/38126) | Adapt to signature changes in `StreamConfig`                                                                                                                                                                     |
| 2.6.0   | 2024-05-08 | [\#37713](https://github.com/airbytehq/airbyte/pull/37713) | Remove option for incremental typing and deduping                                                                                                                                                                |
| 2.5.0   | 2024-05-06 | [\#34613](https://github.com/airbytehq/airbyte/pull/34613) | Upgrade Redshift driver to work with Cluster patch 181; Adapt to CDK 0.33.0; Minor signature changes                                                                                                             |
| 2.4.3   | 2024-04-10 | [\#36973](https://github.com/airbytehq/airbyte/pull/36973) | Limit the Standard inserts SQL statement to less than 16MB                                                                                                                                                       |
| 2.4.2   | 2024-04-05 | [\#36365](https://github.com/airbytehq/airbyte/pull/36365) | Remove unused config option                                                                                                                                                                                      |
| 2.4.1   | 2024-04-04 | [#36846](https://github.com/airbytehq/airbyte/pull/36846)  | Remove duplicate S3 Region                                                                                                                                                                                       |
| 2.4.0   | 2024-03-21 | [\#36589](https://github.com/airbytehq/airbyte/pull/36589) | Adapt to Kotlin cdk 0.28.19                                                                                                                                                                                      |
| 2.3.2   | 2024-03-21 | [\#36374](https://github.com/airbytehq/airbyte/pull/36374) | Supress Jooq DataAccessException error message in logs                                                                                                                                                           |
| 2.3.1   | 2024-03-18 | [\#36255](https://github.com/airbytehq/airbyte/pull/36255) | Mark as Certified-GA                                                                                                                                                                                             |
| 2.3.0   | 2024-03-18 | [\#36203](https://github.com/airbytehq/airbyte/pull/36203) | CDK 0.25.0; Record nulling for VARCHAR > 64K & record > 16MB (super limit)                                                                                                                                       |
| 2.2.0   | 2024-03-14 | [\#35981](https://github.com/airbytehq/airbyte/pull/35981) | CDK 0.24.0; `_airbyte_meta` in Raw table for tracking upstream data modifications.                                                                                                                               |
| 2.1.10  | 2024-03-07 | [\#35899](https://github.com/airbytehq/airbyte/pull/35899) | Adopt CDK 0.23.18; Null safety check in state parsing                                                                                                                                                            |
| 2.1.9   | 2024-03-04 | [\#35316](https://github.com/airbytehq/airbyte/pull/35316) | Update to CDK 0.23.11; Adopt migration framework                                                                                                                                                                 |
| 2.1.8   | 2024-02-09 | [\#35354](https://github.com/airbytehq/airbyte/pull/35354) | Update to CDK 0.23.0; Gather required initial state upfront, remove dependency on svv_table_info for table empty check                                                                                           |
| 2.1.7   | 2024-02-09 | [\#34562](https://github.com/airbytehq/airbyte/pull/34562) | Switch back to jooq-based sql execution for standard insert                                                                                                                                                      |
| 2.1.6   | 2024-02-08 | [\#34502](https://github.com/airbytehq/airbyte/pull/34502) | Update to CDK version 0.17.0                                                                                                                                                                                     |
| 2.1.5   | 2024-01-30 | [\#34680](https://github.com/airbytehq/airbyte/pull/34680) | Update to CDK version 0.16.3                                                                                                                                                                                     |
| 2.1.4   | 2024-01-29 | [\#34634](https://github.com/airbytehq/airbyte/pull/34634) | Use lowercase raw schema and table in T+D [CDK changes](https://github.com/airbytehq/airbyte/pull/34533)                                                                                                         |
| 2.1.3   | 2024-01-26 | [\#34544](https://github.com/airbytehq/airbyte/pull/34544) | Proper string-escaping in raw tables                                                                                                                                                                             |
| 2.1.2   | 2024-01-24 | [\#34451](https://github.com/airbytehq/airbyte/pull/34451) | Improve logging for unparseable input                                                                                                                                                                            |
| 2.1.1   | 2024-01-24 | [\#34458](https://github.com/airbytehq/airbyte/pull/34458) | Improve error reporting                                                                                                                                                                                          |
| 2.1.0   | 2024-01-24 | [\#34467](https://github.com/airbytehq/airbyte/pull/34467) | Upgrade CDK to 0.14.0                                                                                                                                                                                            |
| 2.0.0   | 2024-01-23 | [\#34077](https://github.com/airbytehq/airbyte/pull/34077) | Destinations V2                                                                                                                                                                                                  |
| 0.8.0   | 2024-01-18 | [\#34236](https://github.com/airbytehq/airbyte/pull/34236) | Upgrade CDK to 0.13.0                                                                                                                                                                                            |
| 0.7.15  | 2024-01-11 | [\#34186](https://github.com/airbytehq/airbyte/pull/34186) | Update check method with svv_table_info permission check, fix bug where s3 staging files were not being deleted.                                                                                                 |
| 0.7.14  | 2024-01-08 | [\#34014](https://github.com/airbytehq/airbyte/pull/34014) | Update order of options in spec                                                                                                                                                                                  |
| 0.7.13  | 2024-01-05 | [\#33948](https://github.com/airbytehq/airbyte/pull/33948) | Fix NPE when prepare tables fail; Add case sensitive session for super; Bastion heartbeats added                                                                                                                 |
| 0.7.12  | 2024-01-03 | [\#33924](https://github.com/airbytehq/airbyte/pull/33924) | Add new ap-southeast-3 AWS region                                                                                                                                                                                |
| 0.7.11  | 2024-01-04 | [\#33730](https://github.com/airbytehq/airbyte/pull/33730) | Internal code structure changes                                                                                                                                                                                  |
| 0.7.10  | 2024-01-04 | [\#33728](https://github.com/airbytehq/airbyte/pull/33728) | Allow users to disable final table creation                                                                                                                                                                      |
| 0.7.9   | 2024-01-03 | [\#33877](https://github.com/airbytehq/airbyte/pull/33877) | Fix Jooq StackOverflowError                                                                                                                                                                                      |
| 0.7.8   | 2023-12-28 | [\#33788](https://github.com/airbytehq/airbyte/pull/33788) | Thread-safe fix for file part names (s3 staging files)                                                                                                                                                           |
| 0.7.7   | 2024-01-04 | [\#33728](https://github.com/airbytehq/airbyte/pull/33728) | Add option to only type and dedupe at the end of the sync                                                                                                                                                        |
| 0.7.6   | 2023-12-20 | [\#33704](https://github.com/airbytehq/airbyte/pull/33704) | Only run T+D on a stream if it had any records during the sync                                                                                                                                                   |
| 0.7.5   | 2023-12-18 | [\#33124](https://github.com/airbytehq/airbyte/pull/33124) | Make Schema Creation Separate from Table Creation                                                                                                                                                                |
| 0.7.4   | 2023-12-13 | [\#33369](https://github.com/airbytehq/airbyte/pull/33369) | Use jdbc common sql implementation                                                                                                                                                                               |
| 0.7.3   | 2023-12-12 | [\#33367](https://github.com/airbytehq/airbyte/pull/33367) | DV2: fix migration logic                                                                                                                                                                                         |
| 0.7.2   | 2023-12-11 | [\#33335](https://github.com/airbytehq/airbyte/pull/33335) | DV2: improve data type mapping                                                                                                                                                                                   |
| 0.7.1   | 2023-12-11 | [\#33307](https://github.com/airbytehq/airbyte/pull/33307) | ~DV2: improve data type mapping~ No changes                                                                                                                                                                      |
| 0.7.0   | 2023-12-05 | [\#32326](https://github.com/airbytehq/airbyte/pull/32326) | Opt in beta for v2 destination                                                                                                                                                                                   |
| 0.6.11  | 2023-11-29 | [\#32888](https://github.com/airbytehq/airbyte/pull/32888) | Use the new async framework.                                                                                                                                                                                     |
| 0.6.10  | 2023-11-06 | [\#32193](https://github.com/airbytehq/airbyte/pull/32193) | Adopt java CDK version 0.4.1.                                                                                                                                                                                    |
| 0.6.9   | 2023-10-10 | [\#31083](https://github.com/airbytehq/airbyte/pull/31083) | Fix precision of numeric values in async destinations                                                                                                                                                            |
| 0.6.8   | 2023-10-10 | [\#31218](https://github.com/airbytehq/airbyte/pull/31218) | Clarify configuration groups                                                                                                                                                                                     |
| 0.6.7   | 2023-10-06 | [\#31153](https://github.com/airbytehq/airbyte/pull/31153) | Increase jvm GC retries                                                                                                                                                                                          |
| 0.6.6   | 2023-10-06 | [\#31129](https://github.com/airbytehq/airbyte/pull/31129) | Reduce async buffer size                                                                                                                                                                                         |
| 0.6.5   | 2023-08-18 | [\#28619](https://github.com/airbytehq/airbyte/pull/29640) | Fix duplicate staging object names in concurrent environment (e.g. async)                                                                                                                                        |
| 0.6.4   | 2023-08-10 | [\#28619](https://github.com/airbytehq/airbyte/pull/28619) | Use async method for staging                                                                                                                                                                                     |
| 0.6.3   | 2023-08-07 | [\#29188](https://github.com/airbytehq/airbyte/pull/29188) | Internal code refactoring                                                                                                                                                                                        |
| 0.6.2   | 2023-07-24 | [\#28618](https://github.com/airbytehq/airbyte/pull/28618) | Add hooks in preparation for destinations v2 implementation                                                                                                                                                      |
| 0.6.1   | 2023-07-14 | [\#28345](https://github.com/airbytehq/airbyte/pull/28345) | Increment patch to trigger a rebuild                                                                                                                                                                             |
| 0.6.0   | 2023-06-27 | [\#27993](https://github.com/airbytehq/airbyte/pull/27993) | destination-redshift will fail syncs if records or properties are too large, rather than silently skipping records and succeeding                                                                                |
| 0.5.0   | 2023-06-27 | [\#27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2                                                                                                                                                                                             |
| 0.4.9   | 2023-06-21 | [\#27555](https://github.com/airbytehq/airbyte/pull/27555) | Reduce image size                                                                                                                                                                                                |
| 0.4.8   | 2023-05-17 | [\#26165](https://github.com/airbytehq/airbyte/pull/26165) | Internal code change for future development (install normalization packages inside connector)                                                                                                                    |
| 0.4.7   | 2023-05-01 | [\#25698](https://github.com/airbytehq/airbyte/pull/25698) | Remove old VARCHAR to SUPER migration Java functionality                                                                                                                                                         |
| 0.4.6   | 2023-04-27 | [\#25346](https://github.com/airbytehq/airbyte/pull/25346) | Internal code cleanup                                                                                                                                                                                            |
| 0.4.5   | 2023-03-30 | [\#24736](https://github.com/airbytehq/airbyte/pull/24736) | Improve behavior when throttled by AWS API                                                                                                                                                                       |
| 0.4.4   | 2023-03-29 | [\#24671](https://github.com/airbytehq/airbyte/pull/24671) | Fail faster in certain error cases                                                                                                                                                                               |
| 0.4.3   | 2023-03-17 | [\#23788](https://github.com/airbytehq/airbyte/pull/23788) | S3-Parquet: added handler to process null values in arrays                                                                                                                                                       |
| 0.4.2   | 2023-03-10 | [\#23931](https://github.com/airbytehq/airbyte/pull/23931) | Added support for periodic buffer flush                                                                                                                                                                          |
| 0.4.1   | 2023-03-10 | [\#23466](https://github.com/airbytehq/airbyte/pull/23466) | Changed S3 Avro type from Int to Long                                                                                                                                                                            |
| 0.4.0   | 2023-02-28 | [\#23523](https://github.com/airbytehq/airbyte/pull/23523) | Add SSH Bastion Host configuration options                                                                                                                                                                       |
| 0.3.56  | 2023-01-26 | [\#21890](https://github.com/airbytehq/airbyte/pull/21890) | Fixed configurable parameter for number of file buffers                                                                                                                                                          |
| 0.3.55  | 2023-01-26 | [\#20631](https://github.com/airbytehq/airbyte/pull/20631) | Added support for destination checkpointing with staging                                                                                                                                                         |
| 0.3.54  | 2023-01-18 | [\#21087](https://github.com/airbytehq/airbyte/pull/21087) | Wrap Authentication Errors as Config Exceptions                                                                                                                                                                  |
| 0.3.53  | 2023-01-03 | [\#17273](https://github.com/airbytehq/airbyte/pull/17273) | Flatten JSON arrays to fix maximum size check for SUPER field                                                                                                                                                    |
| 0.3.52  | 2022-12-30 | [\#20879](https://github.com/airbytehq/airbyte/pull/20879) | Added configurable parameter for number of file buffers (⛔ this version has a bug and will not work; use `0.3.56` instead)                                                                                      |
| 0.3.51  | 2022-10-26 | [\#18434](https://github.com/airbytehq/airbyte/pull/18434) | Fix empty S3 bucket path handling                                                                                                                                                                                |
| 0.3.50  | 2022-09-14 | [\#15668](https://github.com/airbytehq/airbyte/pull/15668) | Wrap logs in AirbyteLogMessage                                                                                                                                                                                   |
| 0.3.49  | 2022-09-01 | [\#16243](https://github.com/airbytehq/airbyte/pull/16243) | Fix Json to Avro conversion when there is field name clash from combined restrictions (`anyOf`, `oneOf`, `allOf` fields)                                                                                         |
| 0.3.48  | 2022-09-01 |                                                            | Added JDBC URL params                                                                                                                                                                                            |
| 0.3.47  | 2022-07-15 | [\#14494](https://github.com/airbytehq/airbyte/pull/14494) | Make S3 output filename configurable.                                                                                                                                                                            |
| 0.3.46  | 2022-06-27 | [\#14190](https://github.com/airbytehq/airbyte/pull/13916) | Correctly cleanup S3 bucket when using a configured bucket path for S3 staging operations.                                                                                                                       |
| 0.3.45  | 2022-06-25 | [\#13916](https://github.com/airbytehq/airbyte/pull/13916) | Use the configured bucket path for S3 staging operations.                                                                                                                                                        |
| 0.3.44  | 2022-06-24 | [\#14114](https://github.com/airbytehq/airbyte/pull/14114) | Remove "additionalProperties": false from specs for connectors with staging                                                                                                                                      |
| 0.3.43  | 2022-06-24 | [\#13690](https://github.com/airbytehq/airbyte/pull/13690) | Improved discovery for NOT SUPER column                                                                                                                                                                          |
| 0.3.42  | 2022-06-21 | [\#14013](https://github.com/airbytehq/airbyte/pull/14013) | Add an option to use encryption with staging in Redshift Destination                                                                                                                                             |
| 0.3.40  | 2022-06-17 | [\#13753](https://github.com/airbytehq/airbyte/pull/13753) | Deprecate and remove PART\*SIZE_MB fields from connectors based on StreamTransferManager                                                                                                                         |
| 0.3.39  | 2022-06-02 | [\#13415](https://github.com/airbytehq/airbyte/pull/13415) | Add dropdown to select Uploading Method. <br /> **PLEASE NOTICE**: After this update your **uploading method** will be set to **Standard**, you will need to reconfigure the method to use **S3 Staging** again. |
| 0.3.37  | 2022-05-23 | [\#13090](https://github.com/airbytehq/airbyte/pull/13090) | Removed redshiftDataTmpTableMode. Some refactoring.                                                                                                                                                              |
| 0.3.36  | 2022-05-23 | [\#12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance                                                                                                                                                                           |
| 0.3.35  | 2022-05-18 | [\#12940](https://github.com/airbytehq/airbyte/pull/12940) | Fixed maximum record size for SUPER type                                                                                                                                                                         |
| 0.3.34  | 2022-05-16 | [\#12869](https://github.com/airbytehq/airbyte/pull/12869) | Fixed NPE in S3 staging check                                                                                                                                                                                    |
| 0.3.33  | 2022-05-04 | [\#12601](https://github.com/airbytehq/airbyte/pull/12601) | Apply buffering strategy for S3 staging                                                                                                                                                                          |
| 0.3.32  | 2022-04-20 | [\#12085](https://github.com/airbytehq/airbyte/pull/12085) | Fixed bug with switching between INSERT and COPY config                                                                                                                                                          |
| 0.3.31  | 2022-04-19 | [\#12064](https://github.com/airbytehq/airbyte/pull/12064) | Added option to support SUPER datatype in \_airbyte_raw\*\*\* table                                                                                                                                              |
| 0.3.29  | 2022-04-05 | [\#11729](https://github.com/airbytehq/airbyte/pull/11729) | Fixed bug with dashes in schema name                                                                                                                                                                             |
| 0.3.28  | 2022-03-18 | [\#11254](https://github.com/airbytehq/airbyte/pull/11254) | Fixed missing records during S3 staging                                                                                                                                                                          |
| 0.3.27  | 2022-02-25 | [\#10421](https://github.com/airbytehq/airbyte/pull/10421) | Refactor JDBC parameters handling                                                                                                                                                                                |
| 0.3.25  | 2022-02-14 | [\#9920](https://github.com/airbytehq/airbyte/pull/9920)   | Updated the size of staging files for S3 staging. Also, added closure of S3 writers to staging files when data has been written to an staging file.                                                              |
| 0.3.24  | 2022-02-14 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                                                                                                     |
| 0.3.23  | 2021-12-16 | [\#8855](https://github.com/airbytehq/airbyte/pull/8855)   | Add `purgeStagingData` option to enable/disable deleting the staging data                                                                                                                                        |
| 0.3.22  | 2021-12-15 | [\#8607](https://github.com/airbytehq/airbyte/pull/8607)   | Accept a path for the staging data                                                                                                                                                                               |
| 0.3.21  | 2021-12-10 | [\#8562](https://github.com/airbytehq/airbyte/pull/8562)   | Moving classes around for better dependency management                                                                                                                                                           |
| 0.3.20  | 2021-11-08 | [\#7719](https://github.com/airbytehq/airbyte/pull/7719)   | Improve handling of wide rows by buffering records based on their byte size rather than their count                                                                                                              |
| 0.3.19  | 2021-10-21 | [\#7234](https://github.com/airbytehq/airbyte/pull/7234)   | Allow SSL traffic only                                                                                                                                                                                           |
| 0.3.17  | 2021-10-12 | [\#6965](https://github.com/airbytehq/airbyte/pull/6965)   | Added SSL Support                                                                                                                                                                                                |
| 0.3.16  | 2021-10-11 | [\#6949](https://github.com/airbytehq/airbyte/pull/6949)   | Each stream was split into files of 10,000 records each for copying using S3 or GCS                                                                                                                              |
| 0.3.14  | 2021-10-08 | [\#5924](https://github.com/airbytehq/airbyte/pull/5924)   | Fixed AWS S3 Staging COPY is writing records from different table in the same raw table                                                                                                                          |
| 0.3.13  | 2021-09-02 | [\#5745](https://github.com/airbytehq/airbyte/pull/5745)   | Disable STATUPDATE flag when using S3 staging to speed up performance                                                                                                                                            |
| 0.3.12  | 2021-07-21 | [\#3555](https://github.com/airbytehq/airbyte/pull/3555)   | Enable partial checkpointing for halfway syncs                                                                                                                                                                   |
| 0.3.11  | 2021-07-20 | [\#4874](https://github.com/airbytehq/airbyte/pull/4874)   | allow `additionalProperties` in connector spec                                                                                                                                                                   |

</details>
