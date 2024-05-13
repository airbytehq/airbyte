# S3-Glue

This page guides you through the process of setting up the S3 destination connector with Glue.

## Prerequisites

List of required fields:

- **Access Key ID**
- **Secret Access Key**
- **S3 Bucket Name**
- **S3 Bucket Path**
- **S3 Bucket Region**
- **Glue database**
- **Glue serialization library**

1. Allow connections from Airbyte server to your AWS S3/ Minio S3 cluster \(if they exist in
   separate VPCs\).
2. An S3 bucket with credentials or an instance profile with read/write permissions configured for
   the host (ec2, eks).
3. [Enforce encryption of data in transit](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html#transit)
4. Allow permissions to access the AWS Glue service from the Airbyte connector

## Step 1: Set up S3

[Sign in](https://console.aws.amazon.com/iam/) to your AWS account. Use an existing or create new
[Access Key ID and Secret Access Key](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#:~:text=IAM%20User%20Guide.-,Programmatic%20access,-You%20must%20provide).

Prepare S3 bucket that will be used as destination, see
[this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) to create
an S3 bucket.

NOTE: If the S3 cluster is not configured to use TLS, the connection to Amazon S3 silently reverts
to an unencrypted connection. Airbyte recommends all connections be configured to use TLS/SSL as
support for AWS's
[shared responsibility model](https://aws.amazon.com/compliance/shared-responsibility-model/)

## Step 2: Set up Glue

[Sign in](https://console.aws.amazon.com/iam/) to your AWS account. Use an existing or create new
[Access Key ID and Secret Access Key](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#:~:text=IAM%20User%20Guide.-,Programmatic%20access,-You%20must%20provide).

Prepare the Glue database that will be used as destination, see
[this](https://docs.aws.amazon.com/glue/latest/dg/console-databases.html) to create a Glue database

## Step 3: Set up the S3-Glue destination connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **+ new
   destination**.
3. On the destination setup page, select **S3** from the Destination type dropdown and enter a name
   for this connector.
4. Configure fields:
   - **Access Key Id**
     - See
       [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
       on how to generate an access key.
     - We recommend creating an Airbyte-specific user. This user will require
       [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html)
       to objects in the bucket.
   - **Secret Access Key**
     - Corresponding key to the above key id.
   - **S3 Bucket Name**
     - See [this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)
       to create an S3 bucket.
   - **S3 Bucket Path**
     - Subdirectory under the above bucket to sync the data into.
   - **S3 Bucket Region**
     - See
       [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions)
       for all region codes.
   - **S3 Path Format**
     - Additional string format on how to store data under S3 Bucket Path. Default value is
       `${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_`.
   - **S3 Endpoint**
     - Leave empty if using AWS S3, fill in S3 URL if using Minio S3.
   - **S3 Filename pattern**
     - The pattern allows you to set the file-name format for the S3 staging file(s), next
       placeholders combinations are currently supported: `{date}`, `{date:yyyy_MM}`, `{timestamp}`,
       `{timestamp:millis}`, `{timestamp:micros}`, `{part_number}`, `{sync_id}`,
       `{format_extension}`. Please, don't use empty space and not supportable placeholders, as they
       won't recognized.
   - **Glue database**
     - The Glue database name that was previously created through the management console or the cli.
   - **Glue serialization library**
     - The library that your query engine will use for reading and writing data in your lake
5. Click `Set up destination`.

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **+ new
   destination**.
3. On the destination setup page, select **S3** from the Destination type dropdown and enter a name
   for this connector.
4. Configure fields:

   - **Access Key Id**
     - See
       [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
       on how to generate an access key.
     - See
       [this](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html)
       on how to create a instanceprofile.
     - We recommend creating an Airbyte-specific user. This user will require
       [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html)
       to objects in the staging bucket.
     - If the Access Key and Secret Access Key are not provided, the authentication will rely on the
       instanceprofile.
   - **Secret Access Key**
     - Corresponding key to the above key id.
   - Make sure your S3 bucket is accessible from the machine running Airbyte.
     - This depends on your networking setup.
     - You can check AWS S3 documentation with a tutorial on how to properly configure your S3's
       access
       [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-overview.html).
     - If you use instance profile authentication, make sure the role has permission to read/write
       on the bucket.
     - The easiest way to verify if Airbyte is able to connect to your S3 bucket is via the check
       connection tool in the UI.
   - **S3 Bucket Name**
     - See [this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)
       to create an S3 bucket.
   - **S3 Bucket Path**
     - Subdirectory under the above bucket to sync the data into.
   - **S3 Bucket Region**
     - See
       [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions)
       for all region codes.
   - **S3 Path Format**
     - Additional string format on how to store data under S3 Bucket Path. Default value is
       `${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_`.
   - **S3 Endpoint**
     - Leave empty if using AWS S3, fill in S3 URL if using Minio S3.
   - **S3 Filename pattern**
     - The pattern allows you to set the file-name format for the S3 staging file(s), next
       placeholders combinations are currently supported: `{date}`, `{date:yyyy_MM}`, `{timestamp}`,
       `{timestamp:millis}`, `{timestamp:micros}`, `{part_number}`, `{sync_id}`,
       `{format_extension}`. Please, don't use empty space and not supportable placeholders, as they
       won't recognized.
   - **Glue database**
     - The Glue database name that was previously created through the management console or the cli.
   - **Glue serialization library**
     - The library that your query engine will use for reading and writing data in your lake

5. Click `Set up destination`.

In order for everything to work correctly, it is also necessary that the user whose "S3 Key Id" and
"S3 Access Key" are used have access to both the bucket and its contents. Policies to use:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::YOUR_BUCKET_NAME/*",
        "arn:aws:s3:::YOUR_BUCKET_NAME"
      ]
    }
  ]
}
```

For setting up the necessary Glue policies see
[this](https://docs.aws.amazon.com/glue/latest/dg/glue-resource-policies.html) and
[this](https://docs.aws.amazon.com/glue/latest/dg/create-service-policy.html)

The full path of the output data with the default S3 Path Format
`${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}_` is:

```text
<bucket-name>/<source-namespace-if-exists>/<stream-name>/<upload-date>_<epoch>_<partition-id>.<format-extension>
```

For example:

```text
testing_bucket/data_output_path/public/users/2021_01_01_1234567890_0.csv.gz
↑              ↑                ↑      ↑     ↑          ↑          ↑ ↑
|              |                |      |     |          |          | format extension
|              |                |      |     |          |          unique incremental part id
|              |                |      |     |          milliseconds since epoch
|              |                |      |     upload date in YYYY_MM_DD
|              |                |      stream name
|              |                source namespace (if it exists)
|              bucket path
bucket name
```

The rationales behind this naming pattern are:

1. Each stream has its own directory.
2. The data output files can be sorted by upload time.
3. The upload time composes of a date part and millis part so that it is both readable and unique.

But it is possible to further customize by using the available variables to format the bucket path:

- `${NAMESPACE}`: Namespace where the stream comes from or configured by the connection namespace
  fields.
- `${STREAM_NAME}`: Name of the stream
- `${YEAR}`: Year in which the sync was writing the output data in.
- `${MONTH}`: Month in which the sync was writing the output data in.
- `${DAY}`: Day in which the sync was writing the output data in.
- `${HOUR}`: Hour in which the sync was writing the output data in.
- `${MINUTE}` : Minute in which the sync was writing the output data in.
- `${SECOND}`: Second in which the sync was writing the output data in.
- `${MILLISECOND}`: Millisecond in which the sync was writing the output data in.
- `${EPOCH}`: Milliseconds since Epoch in which the sync was writing the output data in.
- `${UUID}`: random uuid string

Note:

- Multiple `/` characters in the S3 path are collapsed into a single `/` character.
- If the output bucket contains too many files, the part id variable is using a `UUID` instead. It
  uses sequential ID otherwise.

Please note that the stream name may contain a prefix, if it is configured on the connection. A data
sync may create multiple files as the output files can be partitioned by size (targeting a size of
200MB compressed or lower) .

## Supported sync modes

| Feature                        | Support | Notes                                                                                                                                                                                                    |
| :----------------------------- | :-----: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Full Refresh Sync              |   ✅    | Warning: this mode deletes all previously synced data in the configured bucket path.                                                                                                                     |
| Incremental - Append Sync      |   ✅    | Warning: Airbyte provides at-least-once delivery. Depending on your source, you may see duplicated data. Learn more [here](/using-airbyte/core-concepts/sync-modes/incremental-append#inclusive-cursors) |
| Incremental - Append + Deduped |   ❌    |                                                                                                                                                                                                          |
| Namespaces                     |   ❌    | Setting a specific bucket path is equivalent to having separate namespaces.                                                                                                                              |

The Airbyte S3 destination allows you to sync data to AWS S3 or Minio S3. Each stream is written to
its own directory under the bucket. ⚠️ Please note that under "Full Refresh Sync" mode, data in the
configured bucket and path will be wiped out before each sync. We recommend you to provision a
dedicated S3 resource for this sync to prevent unexpected data deletion from misconfiguration. ⚠️

## Supported Output schema

Each stream will be outputted to its dedicated directory according to the configuration. The
complete datastore of each stream includes all the output files under that directory. You can think
of the directory as equivalent of a Table in the database world.

- Under Full Refresh Sync mode, old output files will be purged before new files are created.
- Under Incremental - Append Sync mode, new output files will be added that only contain the new
  data.

### JSON Lines \(JSONL\)

[JSON Lines](https://jsonlines.org/) is a text format with one JSON per line. Each line has a
structure as follows:

```json
{
  "_airbyte_ab_id": "<uuid>",
  "_airbyte_emitted_at": "<timestamp-in-millis>",
  "_airbyte_data": "<json-data-from-source><optional>"
}
```

For example, given the following two json objects from a source:

```json
[
  {
    "user_id": 123,
    "name": {
      "first": "John",
      "last": "Doe"
    }
  },
  {
    "user_id": 456,
    "name": {
      "first": "Jane",
      "last": "Roe"
    }
  }
]
```

depending on whether you want to flatten your data or not (**_available as a configuration
option_**)

The json objects can have the following formats:

```text
{ "_airbyte_ab_id": "26d73cde-7eb1-4e1e-b7db-a4c03b4cf206", "_airbyte_emitted_at": "1622135805000", "_airbyte_data": { "user_id": 123, "name": { "first": "John", "last": "Doe" } } }
{ "_airbyte_ab_id": "0a61de1b-9cdd-4455-a739-93572c9a5f20", "_airbyte_emitted_at": "1631948170000", "_airbyte_data": { "user_id": 456, "name": { "first": "Jane", "last": "Roe" } } }
```

```text
{ "_airbyte_ab_id": "26d73cde-7eb1-4e1e-b7db-a4c03b4cf206", "_airbyte_emitted_at": "1622135805000", "user_id": 123, "name": { "first": "John", "last": "Doe" } }
{ "_airbyte_ab_id": "0a61de1b-9cdd-4455-a739-93572c9a5f20", "_airbyte_emitted_at": "1631948170000", "user_id": 456, "name": { "first": "Jane", "last": "Roe" } }
```

Output files can be compressed. The default option is GZIP compression. If compression is selected,
the output filename will have an extra extension (GZIP: `.jsonl.gz`).

## CHANGELOG

| Version | Date       | Pull Request                                              | Subject                                                                                 |
| :------ | :--------- | :-------------------------------------------------------- | :-------------------------------------------------------------------------------------- |
| 0.1.8   | 2024-01-03 | [#33924](https://github.com/airbytehq/airbyte/pull/33924) | Add new ap-southeast-3 AWS region                                                       |
| 0.1.7   | 2023-05-01 | [25724](https://github.com/airbytehq/airbyte/pull/25724)  | Fix decimal type creation syntax to avoid overflow                                      |
| 0.1.6   | 2023-04-13 | [25178](https://github.com/airbytehq/airbyte/pull/25178)  | Fix decimal precision and scale to allow for a wider range of numeric values            |
| 0.1.5   | 2023-04-11 | [25048](https://github.com/airbytehq/airbyte/pull/25048)  | Fix config schema to support new JSONL flattening configuration interface               |
| 0.1.4   | 2023-03-10 | [23950](https://github.com/airbytehq/airbyte/pull/23950)  | Fix schema syntax error for struct fields and handle missing `items` in array fields    |
| 0.1.3   | 2023-02-10 | [22822](https://github.com/airbytehq/airbyte/pull/22822)  | Fix data type for \_ab_emitted_at column in table definition                            |
| 0.1.2   | 2023-02-01 | [22220](https://github.com/airbytehq/airbyte/pull/22220)  | Fix race condition in test, table metadata, add Airbyte sync fields to table definition |
| 0.1.1   | 2022-12-13 | [19907](https://github.com/airbytehq/airbyte/pull/19907)  | Fix parsing empty object in schema                                                      |
| 0.1.0   | 2022-11-17 | [18695](https://github.com/airbytehq/airbyte/pull/18695)  | Initial Commit                                                                          |
