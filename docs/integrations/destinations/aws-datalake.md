# AWS Datalake

This page contains the setup guide and reference information for the AWS Datalake destination
connector.

The AWS Datalake destination connector allows you to sync data to AWS. It will write data as JSON
files in S3 and will make it available through a
[Lake Formation Governed Table](https://docs.aws.amazon.com/lake-formation/latest/dg/governed-tables.html)
in the Glue Data Catalog so that the data is available throughout other AWS services such as Athena,
Glue jobs, EMR, Redshift, etc.

## Prerequisites

To use this destination connector, you will need:

- An AWS account
- An S3 bucket where the data will be written
- An AWS Lake Formation database where tables will be created (one per stream)
- AWS credentials in the form of either the pair Access key ID / Secret key ID or a role with the
  following permissions:

  - Writing objects in the S3 bucket
  - Updating of the Lake Formation database

Please check the Setup guide below if you need guidance creating those.

## Setup guide

You should now have all the requirements needed to configure AWS Datalake as a destination in the
UI. You'll need the following information to configure the destination:

- Aws Account Id : The account ID of your AWS account. You will find the instructions to setup a new
  AWS account
  [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/).
- Aws Region : The region in which your resources are deployed
- Authentication mode : The AWS Datalake connector lets you authenticate with either a user or a
  role. In both case, you will have to make sure that appropriate policies are in place. Select
  "ROLE" if you are using a role, "USER" if using a user with Access key / Secret Access key.
- Target Role Arn : The name of the role, if "Authentication mode" was "ROLE". You will find the
  instructions to create a new role
  [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html).
- Access Key Id : The Access Key ID of the user if "Authentication mode" was "USER". You will find
  the instructions to create a new user
  [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html). Make sure to select
  "Programmatic Access" so that you get secret access keys.
- Secret Access Key : The Secret Access Key ID of the user if "Authentication mode" was "USER"
- S3 Bucket Name : The bucket in which the data will be written. You will find the instructions to
  create a new S3 bucket
  [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html).
- Target S3 Bucket Prefix : A prefix to prepend to the file name when writing to the bucket
- Database : The database in which the tables will be created. You will find the instructions to
  create a new Lakeformation Database
  [here](https://docs.aws.amazon.com/lake-formation/latest/dg/creating-database.html).

**Assigning proper permissions**

The policy used by the user or the role must have access to the following services:

- AWS Lake Formation
- AWS Glue
- AWS S3

You can use [the AWS policy generator](https://awspolicygen.s3.amazonaws.com/policygen.html) to help
you generate an appropriate policy.

Please also make sure that the role or user you will use has appropriate permissions on the database
in AWS Lakeformation. You will find more information about Lake Formation permissions in the
[AWS Lake Formation Developer Guide](https://docs.aws.amazon.com/lake-formation/latest/dg/lake-formation-permissions.html).

## Supported sync modes

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

## Data type map

The Glue tables will be created with schema information provided by the source, i.e : You will find
the same columns and types in the destination table as in the source except for the following types
which will be translated for compatibility with the Glue Data Catalog:

| Type in the source | Type in the destination |
| :----------------- | :---------------------- |
| number             | float                   |
| integer            | int                     |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                              |
|:--------| :--------- | :--------------------------------------------------------- | :--------------------------------------------------- |
| 0.1.43 | 2025-01-11 | [51289](https://github.com/airbytehq/airbyte/pull/51289) | Update dependencies |
| 0.1.42 | 2025-01-04 | [50914](https://github.com/airbytehq/airbyte/pull/50914) | Update dependencies |
| 0.1.41 | 2024-12-28 | [50458](https://github.com/airbytehq/airbyte/pull/50458) | Update dependencies |
| 0.1.40 | 2024-12-21 | [50220](https://github.com/airbytehq/airbyte/pull/50220) | Update dependencies |
| 0.1.39 | 2024-12-14 | [48945](https://github.com/airbytehq/airbyte/pull/48945) | Update dependencies |
| 0.1.38 | 2024-11-25 | [48671](https://github.com/airbytehq/airbyte/pull/48671) | Update dependencies |
| 0.1.37 | 2024-11-04 | [48243](https://github.com/airbytehq/airbyte/pull/48243) | Update dependencies |
| 0.1.36 | 2024-10-29 | [47878](https://github.com/airbytehq/airbyte/pull/47878) | Update dependencies |
| 0.1.35 | 2024-10-28 | [47590](https://github.com/airbytehq/airbyte/pull/47590) | Update dependencies |
| 0.1.34 | 2024-10-22 | [47091](https://github.com/airbytehq/airbyte/pull/47091) | Update dependencies |
| 0.1.33 | 2024-10-12 | [46790](https://github.com/airbytehq/airbyte/pull/46790) | Update dependencies |
| 0.1.32 | 2024-10-05 | [46400](https://github.com/airbytehq/airbyte/pull/46400) | Update dependencies |
| 0.1.31 | 2024-09-28 | [46126](https://github.com/airbytehq/airbyte/pull/46126) | Update dependencies |
| 0.1.30 | 2024-09-21 | [45821](https://github.com/airbytehq/airbyte/pull/45821) | Update dependencies |
| 0.1.29 | 2024-09-14 | [45533](https://github.com/airbytehq/airbyte/pull/45533) | Update dependencies |
| 0.1.28 | 2024-09-07 | [45328](https://github.com/airbytehq/airbyte/pull/45328) | Update dependencies |
| 0.1.27 | 2024-08-31 | [45032](https://github.com/airbytehq/airbyte/pull/45032) | Update dependencies |
| 0.1.26 | 2024-08-24 | [44677](https://github.com/airbytehq/airbyte/pull/44677) | Update dependencies |
| 0.1.25 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.1.24 | 2024-08-17 | [44341](https://github.com/airbytehq/airbyte/pull/44341) | Update dependencies |
| 0.1.23 | 2024-08-12 | [43822](https://github.com/airbytehq/airbyte/pull/43822) | Update dependencies |
| 0.1.22 | 2024-08-10 | [43497](https://github.com/airbytehq/airbyte/pull/43497) | Update dependencies |
| 0.1.21 | 2024-08-03 | [43139](https://github.com/airbytehq/airbyte/pull/43139) | Update dependencies |
| 0.1.20 | 2024-07-27 | [42821](https://github.com/airbytehq/airbyte/pull/42821) | Update dependencies |
| 0.1.19 | 2024-07-20 | [42174](https://github.com/airbytehq/airbyte/pull/42174) | Update dependencies |
| 0.1.18 | 2024-07-13 | [41819](https://github.com/airbytehq/airbyte/pull/41819) | Update dependencies |
| 0.1.17 | 2024-07-10 | [41590](https://github.com/airbytehq/airbyte/pull/41590) | Update dependencies |
| 0.1.16 | 2024-07-09 | [41083](https://github.com/airbytehq/airbyte/pull/41083) | Update dependencies |
| 0.1.15 | 2024-07-06 | [40907](https://github.com/airbytehq/airbyte/pull/40907) | Update dependencies |
| 0.1.14 | 2024-06-29 | [40631](https://github.com/airbytehq/airbyte/pull/40631) | Update dependencies |
| 0.1.13 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.1.12 | 2024-06-26 | [40535](https://github.com/airbytehq/airbyte/pull/40535) | Update dependencies |
| 0.1.11 | 2024-06-25 | [40458](https://github.com/airbytehq/airbyte/pull/40458) | Update dependencies |
| 0.1.10 | 2024-06-22 | [39958](https://github.com/airbytehq/airbyte/pull/39958) | Update dependencies |
| 0.1.9 | 2024-06-04 | [39033](https://github.com/airbytehq/airbyte/pull/39033) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.8 | 2024-05-20 | [38413](https://github.com/airbytehq/airbyte/pull/38413) | [autopull] base image + poetry + up_to_date |
| `0.1.7` | 2024-04-29 | [#33853](https://github.com/airbytehq/airbyte/pull/33853)  | Enable STS Role Credential Refresh for Long Sync     |
| `0.1.6` | 2024-03-22 | [#36386](https://github.com/airbytehq/airbyte/pull/36386)  | Support new state message protocol                   |
| `0.1.5` | 2024-01-03 | [#33924](https://github.com/airbytehq/airbyte/pull/33924)  | Add new ap-southeast-3 AWS region                    |
| `0.1.4` | 2023-10-25 | [\#29221](https://github.com/airbytehq/airbyte/pull/29221) | Upgrade AWSWrangler                                  |
| `0.1.3` | 2023-03-28 | [\#24642](https://github.com/airbytehq/airbyte/pull/24642) | Prefer airbyte type for complex types when available |
| `0.1.2` | 2022-09-26 | [\#17193](https://github.com/airbytehq/airbyte/pull/17193) | Fix schema keyerror and add parquet support          |
| `0.1.1` | 2022-04-20 | [\#11811](https://github.com/airbytehq/airbyte/pull/11811) | Fix name of required param in specification          |
| `0.1.0` | 2022-03-29 | [\#10760](https://github.com/airbytehq/airbyte/pull/10760) | Initial release                                      |

</details>
