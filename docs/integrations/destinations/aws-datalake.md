# AWS Datalake

This page contains the setup guide and reference information for the AWS Datalake destination connector.

The AWS Datalake destination connector allows you to sync data to AWS. It will write data as JSON files in S3 and 
will make it available through a [Lake Formation Governed Table](https://docs.aws.amazon.com/lake-formation/latest/dg/governed-tables.html) in the Glue Data Catalog so that the data is available throughout other AWS services such as Athena, Glue jobs, EMR, Redshift, etc.

## Prerequisites

To use this destination connector, you will need:
* An AWS account
* An S3 bucket where the data will be written
* An AWS Lake Formation database where tables will be created (one per stream)
* AWS credentials in the form of either the pair Access key ID / Secret key ID or a role with the following permissions:

    * Writing objects in the S3 bucket
    * Updating of the Lake Formation database

Please check the Setup guide below if you need guidance creating those.

## Setup guide

You should now have all the requirements needed to configure AWS Datalake as a destination in the UI. You'll need the
following information to configure the destination:

- Aws Account Id : The account ID of your AWS account. You will find the instructions to setup a new AWS account [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/).
- Aws Region : The region in which your resources are deployed
- Authentication mode : The AWS Datalake connector lets you authenticate with either a user or a role. In both case, you will have to make sure
that appropriate policies are in place. Select "ROLE" if you are using a role, "USER" if using a user with Access key / Secret Access key.
- Target Role Arn : The name of the role, if "Authentication mode" was "ROLE". You will find the instructions to create a new role [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-service.html).
- Access Key Id : The Access Key ID of the user if "Authentication mode" was "USER". You will find the instructions to create a new user [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html). Make sure to select "Programmatic Access" so that you get secret access keys.
- Secret Access Key : The Secret Access Key ID of the user if "Authentication mode" was "USER"
- S3 Bucket Name : The bucket in which the data will be written. You will find the instructions to create a new S3 bucket [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html).
- Target S3 Bucket Prefix : A prefix to prepend to the file name when writing to the bucket
- Database : The database in which the tables will be created. You will find the instructions to create a new Lakeformation Database [here](https://docs.aws.amazon.com/lake-formation/latest/dg/creating-database.html).

**Assigning proper permissions**

The policy used by the user or the role must have access to the following services:

* AWS Lake Formation
* AWS Glue
* AWS S3

You can use [the AWS policy generator](https://awspolicygen.s3.amazonaws.com/policygen.html) to help you generate an appropriate policy.

Please also make sure that the role or user you will use has appropriate permissions on the database in AWS Lakeformation. You will find more information about Lake Formation permissions in the [AWS Lake Formation Developer Guide](https://docs.aws.amazon.com/lake-formation/latest/dg/lake-formation-permissions.html).

## Supported sync modes

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | No |  |


## Data type map

The Glue tables will be created with schema information provided by the source, i.e : You will find the same columns
and types in the destination table as in the source except for the following types which will be translated for compatibility with the Glue Data Catalog:

|Type in the source| Type in the destination|
| :--- | :--- |
| number | float |
| integer | int |



## Changelog

| 0.1.1 | 2022-04-20 | [\#11811](https://github.com/airbytehq/airbyte/pull/11811) | Fix name of required param in specification |
| 0.1.0 | 2022-03-29 | [\#10760](https://github.com/airbytehq/airbyte/pull/10760) | Initial release |