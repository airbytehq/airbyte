# Redshift

Setting up the Redshift destination connector involves setting up Redshift entities (cluster,
database, schema, user) in the AWS console, configuring an S3 bucket for staging, and configuring
the Redshift destination connector using the Airbyte UI.

This page describes the step-by-step process of setting up the Redshift destination connector.

## Prerequisites

- An [AWS account](https://aws.amazon.com/console/) with access to Amazon Redshift
- A Redshift cluster ([provisioned](https://docs.aws.amazon.com/redshift/latest/gsg/new-user.html)
  or [serverless](https://docs.aws.amazon.com/redshift/latest/gsg/new-user-serverless.html))
- An [S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) for staging data
- AWS IAM credentials
  with [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html)
  to the S3 bucket

NOTE: The Redshift destination
uses [S3 staging with COPY](https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-single-copy-command.html) as
the loading method. This is the recommended approach described by Redshift best practices. Data is uploaded to S3 as
multiple files along with a manifest file, then loaded into Redshift via the COPY command.

## Setup guide

### Step 1: Set up Airbyte-specific entities in Redshift

To set up the Redshift destination connector, you first need to create Airbyte-specific Redshift
entities (a database, schema, and user) with the appropriate permissions to write data into
Redshift and manage staging operations.

You can use the following script in the
[Redshift Query Editor](https://docs.aws.amazon.com/redshift/latest/mgmt/query-editor-v2-using.html)
to create the entities:

1. [Log into your AWS account](https://aws.amazon.com/console/) and navigate to the Redshift service.
2. Open the Query Editor and connect to your cluster.
3. Edit the following script to change the password to a more secure password and to change the names of other resources
   as needed.

```sql
-- create a Database for Airbyte data (if it does not already exist)
CREATE
DATABASE airbyte_database;
```

4. **Switch your connection** to `airbyte_database` in the Query Editor. Redshift does not support switching databases
   within a session, so you must select `airbyte_database` from the database dropdown before running the remaining
   statements.

TIP: You can verify you are connected to the correct database by running:

```sql
SELECT CURRENT_DATABASE();
```

5. Run the following script to create the schema, user, and grants:

```sql
-- create a schema for Airbyte data (if it does not already exist)
CREATE SCHEMA IF NOT EXISTS airbyte_schema;

-- create Airbyte user
CREATE
USER airbyte_user PASSWORD 'your_secure_password_here';

-- grant permissions on the database
GRANT CREATE
ON DATABASE airbyte_database TO airbyte_user;

-- grant permissions on the target schema
GRANT USAGE, CREATE
ON SCHEMA airbyte_schema TO airbyte_user;
```

6. Verify the script ran successfully in the Query Editor.

NOTE: Our integration automatically creates the necessary schemas in your Redshift database. To enable this, ensure the
connection user has `CREATE` privileges on the database. If you prefer to create schemas manually, grant `USAGE` and
`CREATE` privileges on those schemas to the Airbyte user.

### Step 2: Set up S3 staging

Airbyte stages data in S3 before loading it into Redshift via the COPY command. You need to
configure an S3 bucket and IAM credentials for this purpose.

1. [Create an S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)
   if you don't already have one for staging.
2. Place the S3 bucket in the **same AWS region** as your Redshift cluster to minimize networking
   costs and improve performance.
3. [Create an IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) (or
   use an existing one)
   with [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html)
   to the staging bucket.
4. [Generate an access key](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
   for the IAM user.

See the [S3 Staging fields](#s3-staging-fields) table for the full list of required and optional
S3 configuration parameters.

NOTE: S3 staging does not use the SSH Tunnel option for copying data. SSH Tunnel supports the SQL connection only. S3 is
secured through public HTTPS access only. Subsequent queries on the destination tables are executed using the provided
SSH Tunnel configuration.

#### Optional: SSH Bastion Host

This connector supports the use of a Bastion host as a gateway to a private Redshift cluster via SSH
Tunneling. Enter the bastion host, port, and credentials in the destination configuration.

### Step 3: Set up Redshift as a destination in Airbyte

Navigate to the Airbyte UI to set up Redshift as a destination:

1. [Log into your Airbyte account](https://cloud.airbyte.com/workspaces).
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **+ new
   destination**.
3. On the destination setup page, select **Redshift** from the Destination type dropdown and enter a
   name for this connector.
4. Fill in the required fields using the configuration reference below.
5. Click **Set up destination**.

#### Connection fields

| Field                                                                                                           | Description                                                                                                                                                                          |
|:----------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Host](https://docs.aws.amazon.com/redshift/latest/mgmt/managing-clusters-console.html#obtain-cluster-endpoint) | The endpoint of your Redshift cluster or serverless workgroup. Provisioned clusters end with `.redshift.amazonaws.com`; serverless workgroups end with `.redshift-serverless.amazonaws.com`. Example: `my-cluster.abc123xyz.us-east-1.redshift.amazonaws.com` |
| Port                                                                                                            | Port of the database. Default: `5439`                                                                                                                                                |
| Username                                                                                                        | The username you created in Step 1 to allow Airbyte to access the database. Example: `airbyte_user`                                                                                  |
| Password                                                                                                        | The password associated with the username.                                                                                                                                           |
| [Database](https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_DATABASE.html)                               | The name of the database you want to sync data into. This database must already exist within your Redshift cluster. Example: `airbyte_database`                                      |
| [Default Schema](https://docs.aws.amazon.com/redshift/latest/dg/r_CREATE_SCHEMA.html)                           | The default schema tables are written to if the source does not specify a namespace. Default: `public`                                                                               |

#### S3 Staging fields

| Field                                                                                                                        | Description                                                                                                                                                                                                                                                    |
|:-----------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [S3 Bucket Name](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)                          | The name of the staging S3 bucket you created in Step 2. Example: `airbyte-staging-bucket`                                                                                                                                                                     |
| S3 Bucket Region                                                                                                             | The region of the S3 staging bucket. Place in the same region as your Redshift cluster to reduce costs. Example: `us-east-1`                                                                                                                                   |
| [S3 Access Key ID](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) | The AWS Access Key ID for an IAM user with read and write permissions to the staging bucket.                                                                                                                                                                   |
| S3 Secret Access Key                                                                                                         | The corresponding AWS Secret Access Key for the Access Key ID.                                                                                                                                                                                                 |
| S3 Bucket Path (Optional)                                                                                                    | The directory under the S3 bucket where staging data will be written. If not provided, defaults to the root directory. Example: `data_sync/redshift`                                                                                                           |
| S3 Filename Pattern (Optional)                                                                                               | The pattern for S3 staging file names. Supported placeholders: `{date}`, `{date:yyyy_MM}`, `{timestamp}`, `{timestamp:millis}`, `{timestamp:micros}`, `{part_number}`, `{sync_id}`, `{format_extension}`. Do not use empty spaces or unsupported placeholders. |
| Purge Staging Data (Optional)                                                                                                | Whether to delete the staging files from S3 after completing the sync. Default: `true`. Set to `false` to retain files for debugging or auditing.                                                                                                              |

#### Advanced fields

| Field                                                                                                                                         | Description                                                                                                                                                               |
|:----------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [JDBC URL Params](https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-configuration-options.html) (Optional)                              | Additional properties to pass to the JDBC URL string when connecting to the database, formatted as `key=value` pairs separated by `&`. Example: `key1=value1&key2=value2` |
| [SSH Tunnel Method](https://docs.airbyte.com/platform/using-airbyte/configuring-connections/configuring-the-connection#ssh-tunnel) (Optional) | Whether to initiate an SSH tunnel before connecting to the database, and if so, which kind of authentication to use.                                                      |
| Drop CASCADE (Optional)                                                                                                                       | Whether to use `CASCADE` when dropping tables and columns. **Warning:** This deletes data in all dependent objects (views, etc.), including during schema evolution. Default: `false`. |

## Output schema

Airbyte writes each stream directly into a final table in Redshift with typed columns.

### Final Table schema

The final table contains these fields, in addition to the columns declared in your stream schema:

- `_airbyte_raw_id`: A UUID assigned by Airbyte to each event that is processed. Column type: `VARCHAR(36)`.
- `_airbyte_extracted_at`: A timestamp representing when the event was pulled from the data source. Column type:
  `TIMESTAMP WITH TIME ZONE`.
- `_airbyte_meta`: A JSON object containing metadata about the record, such as changes applied during syncing. Column
  type: `SUPER`.
- `_airbyte_generation_id`: An identifier for the generation of the sync that produced this record. Column type:
  `BIGINT`.

See [Airbyte metadata fields](/platform/understanding-airbyte/airbyte-metadata-fields) for more information about these
fields.

NOTE: As of version 4.0.0, the Redshift destination writes data directly to final tables
with [direct load](https://docs.airbyte.com/platform/using-airbyte/core-concepts/direct-load-tables). Raw tables (
`_airbyte_raw_*`) are no longer created. If you are upgrading from an older version, see
the [migration guide](redshift-migrations.md) for details.

### Schema naming

- Redshift lowercases all schema, table, and column names and replaces special characters with
  underscores, following the rules defined in
  [Redshift Names & Identifiers](https://docs.aws.amazon.com/redshift/latest/dg/r_names.html).
- Identifiers are limited to 127 characters. Names that exceed this limit are truncated to 118 characters with an
  underscore and an 8-character hash suffix to avoid collisions.

## Data type map

| Airbyte type                        | Redshift type      |
|:------------------------------------|:-------------------|
| STRING                              | VARCHAR(65535)     |
| STRING (BASE64)                     | VARCHAR(65535)     |
| STRING (BIG_NUMBER)                 | VARCHAR(65535)     |
| STRING (BIG_INTEGER)                | VARCHAR(65535)     |
| NUMBER                              | DECIMAL(38,9)      |
| INTEGER                             | BIGINT             |
| BOOLEAN                             | BOOLEAN            |
| STRING (TIMESTAMP_WITH_TIMEZONE)    | TIMESTAMPTZ        |
| STRING (TIMESTAMP_WITHOUT_TIMEZONE) | TIMESTAMP          |
| STRING (TIME_WITH_TIMEZONE)         | TIMETZ             |
| STRING (TIME_WITHOUT_TIMEZONE)      | TIME               |
| DATE                                | DATE               |
| OBJECT                              | SUPER              |
| ARRAY                               | SUPER              |
| UNKNOWN                             | VARCHAR(65535)     |

### Precision and size limits

Redshift enforces size limits on certain data types. When a value exceeds a limit, Airbyte nulls the value and records
the change in the `_airbyte_meta` column.

- **VARCHAR**: Maximum 65,535 bytes.
- **SUPER**: Maximum 16 MB per record. See the AWS documentation
  on [SUPER type](https://docs.aws.amazon.com/redshift/latest/dg/r_SUPER_type.html)
  and [SUPER limitations](https://docs.aws.amazon.com/redshift/latest/dg/limitations-super.html).
- **BIGINT**: Stores values in the range -2^63 to 2^63-1. If an integer value falls outside this range, Airbyte nulls
  the value and records the change in `_airbyte_meta`.
- **NUMERIC(38, 9)**: Redshift supports a maximum precision of 38 and scale of 9. If the source value has a scale
  greater than 9, Redshift silently rounds it — this is not recorded in `_airbyte_meta`. If the precision exceeds 38,
  Airbyte nulls the value and records the change in `_airbyte_meta`.

### Schema evolution

This connector supports automatic schema evolution. When the source schema changes, the connector automatically adds new
columns to destination tables. The connector requires `CREATE` and `ALTER TABLE` privileges on destination schemas and
tables to support this feature.

## Supported sync modes

The Redshift destination connector supports the following
[sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

| Sync Mode                                                                                                                                     | Supported? |
|:----------------------------------------------------------------------------------------------------------------------------------------------|:----------:|
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite)                   |    Yes     |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append)                         |    Yes     |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) |    Yes     |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append)                      |    Yes     |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped)    |    Yes     |

### Encryption

All Redshift connections are encrypted using SSL.

## Troubleshooting

### 'Cannot connect to Redshift cluster'

If your Redshift cluster is in a private VPC, you may need to:

1. [Allow connections](https://aws.amazon.com/premiumsupport/knowledge-center/cannot-connect-redshift-cluster/) from
   Airbyte to your Redshift cluster (if they exist in separate VPCs).
2. Configure an SSH Bastion Host (see [Step 2](#optional-ssh-bastion-host)) to tunnel through to the private cluster.
3. For Airbyte Cloud, ensure
   the [Airbyte IP addresses](https://docs.airbyte.com/platform/using-airbyte/configuring-connections/configuring-the-connection#allow-list-ip-addresses)
   are allowed in your Redshift cluster's security group and network policy.

### 'S3 access denied' during staging

Ensure your IAM credentials
have [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html)
to the staging S3 bucket. Verify that:

- The Access Key ID and Secret Access Key are correct.
- The IAM user has a policy allowing `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, and `s3:ListBucket` on the
  staging bucket.
- There is no S3 bucket policy blocking access.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). The namespace maps to a Redshift schema.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                                                                                                                          |
|:--------|:-----------|:-----------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 4.0.4 | 2026-07-17 | [PLACEHOLDER_PR](https://github.com/airbytehq/airbyte/pull/PLACEHOLDER_PR) | Fix schema-evolution sync failure by tolerantly casting VARCHAR to numeric types (scientific-notation and un-castable values no longer abort the sync) |
| 4.0.3 | 2026-07-09 | [81552](https://github.com/airbytehq/airbyte/pull/81552) | fix: narrow SQLException handling to only treat table-not-found as missing |
| 4.0.2 | 2026-06-05 | [79161](https://github.com/airbytehq/airbyte/pull/79161) | fix: validate nested string sizes within SUPER columns to prevent COPY error 1224 |
| 4.0.1 | 2026-06-04 | [79135](https://github.com/airbytehq/airbyte/pull/79135) | fix: resolve sslmode/sslfactory conflict in jdbc_url_params |
| 4.0.0 | 2026-06-02 | [79095](https://github.com/airbytehq/airbyte/pull/79095) | Full rewrite using direct load (removal of raw tables), pre-insertion data validation with `_airbyte_meta` tracking, updated dependencies: Redshift JDBC 2.2.7, AWS SDK v2 2.31.1 |
| 3.5.4 | 2026-03-23 | [75286](https://github.com/airbytehq/airbyte/pull/75286) | Fix misleading SSH error when SQLException has null sqlState during connection check |
| 3.5.3 | 2025-03-24 | [56355](https://github.com/airbytehq/airbyte/pull/56355) | Upgrade to airbyte/java-connector-base:2.0.1 to be M4 compatible. |
| 3.5.2 | 2025-01-14 | [51500](https://github.com/airbytehq/airbyte/pull/51500) | Use a non root base image |
| 3.5.1 | 2025-01-06 | [49903](https://github.com/airbytehq/airbyte/pull/49903) | Use a base image: airbyte/java-connector-base:1.0.0 |
| 3.5.0 | 2024-09-18 | [45435](https://github.com/airbytehq/airbyte/pull/45435) | upgrade all dependencies |
| 3.4.4 | 2024-08-20 | [44476](https://github.com/airbytehq/airbyte/pull/44476) | Increase message parsing limit to 100mb |
| 3.4.3 | 2024-08-22 | [44526](https://github.com/airbytehq/airbyte/pull/44526) | Revert protocol compliance fix |
| 3.4.2 | 2024-08-15 | [42506](https://github.com/airbytehq/airbyte/pull/42506) | Fix bug in refreshes logic (already mitigated in platform, just fixing protocol compliance) |
| 3.4.1 | 2024-08-14 | [44020](https://github.com/airbytehq/airbyte/pull/44020) | Simplify Redshift Options |
| 3.4.0 | 2024-07-23 | [42445](https://github.com/airbytehq/airbyte/pull/42445) | Respect the `drop cascade` option on raw tables |
| 3.3.1 | 2024-07-15 | [41968](https://github.com/airbytehq/airbyte/pull/41968) | Don't hang forever on empty stream list; shorten error message on INCOMPLETE stream status |
| 3.3.0 | 2024-07-02 | [40567](https://github.com/airbytehq/airbyte/pull/40567) | Support for [refreshes](../../platform/operator-guides/refreshes) and resumable full refresh. WARNING: You must upgrade to platform 0.63.7 before upgrading to this connector version. |
| 3.2.0 | 2024-07-02 | [40201](https://github.com/airbytehq/airbyte/pull/40201) | Add `_airbyte_generation_id` column, and add `sync_id` to `_airbyte_meta` column |
| 3.1.1 | 2024-06-26 | [39008](https://github.com/airbytehq/airbyte/pull/39008) | Internal code changes |
| 3.1.0 | 2024-06-26 | [39141](https://github.com/airbytehq/airbyte/pull/39141) | Remove nonfunctional "encrypted staging" option |
| 3.0.0 | 2024-06-04 | [38886](https://github.com/airbytehq/airbyte/pull/38886) | Remove standard inserts mode |
| 2.6.4 | 2024-05-31 | [38825](https://github.com/airbytehq/airbyte/pull/38825) | Adopt CDK 0.35.15 |
| 2.6.3 | 2024-05-31 | [38803](https://github.com/airbytehq/airbyte/pull/38803) | Source auto-conversion to Kotlin |
| 2.6.2 | 2024-05-14 | [38189](https://github.com/airbytehq/airbyte/pull/38189) | adding an option to DROP CASCADE on resets |
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
| 0.3.52  | 2022-12-30 | [\#20879](https://github.com/airbytehq/airbyte/pull/20879) | Added configurable parameter for number of file buffers (this version has a bug and will not work; use `0.3.56` instead)                                                                                         |
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
