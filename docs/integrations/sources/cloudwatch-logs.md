# Cloudwatch Logs

<HideInUI>

This page contains the setup guide and reference information for the [Cloudwatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html) source connector.

</HideInUI>

:::warning
Reading logs from Cloudwatch may incur costs. Please refer to the [official AWS Cloudwatch pricing page](https://aws.amazon.com/cloudwatch/pricing/) for more information.
:::

## Prerequisites

## Setup guide

### Step 1: Set up Cloudwatch Logs

You need to authenticate the connection. This can be done either by using:
- An `IAM User` (with `AWS Access Key ID` and `Secret Access Key`)
- An `IAM Role` (with `Role ARN`).

Begin by creating a policy with the necessary permissions:

#### Create a Policy

1. Log in to your Amazon AWS account and open the [IAM console](https://console.aws.amazon.com/iam/home#home).
2. In the IAM dashboard, select **Policies**, then click **Create Policy**.
3. Select the **JSON** tab, then paste the following JSON into the Policy editor (be sure to substitute in your bucket name):

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:DescribeLogGroups"
            ],
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Action": [
                "logs:GetLogEvents",
                "logs:FilterLogEvents",
                "logs:DescribeLogStreams",
                "logs:GetLogRecord"
            ],
            "Effect": "Allow",
            "Resource": [
                "*"
            ]
        }
    ]
}
```

4. Give your policy a descriptive name, then click **Create policy**.

#### Option 1: Using an IAM User

1. In the IAM dashboard, click **Users**. Select an existing IAM user or create a new one by clicking **Add users**.
2. If you are using an _existing_ IAM user, click the **Add permissions** dropdown menu and select **Add permissions**. If you are creating a _new_ user, you will be taken to the Permissions screen after selecting a name.
3. Select **Attach policies directly**, then find and check the box for your new policy. Click **Next**, then **Add permissions**.
4. After successfully creating your user, select the **Security credentials** tab and click **Create access key**. You will be prompted to select a use case and add optional tags to your access key. Click **Create access key** to generate the keys.

:::caution
Your `Secret Access Key` will only be visible once upon creation. Be sure to copy and store it securely for future use.
:::

For more information on managing your access keys, please refer to the
[official AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).


#### Option 2: Using an IAM Role (Most secure)

<!-- env:oss -->
:::note
Cloudwatch authentication using an IAM role requires Airbyte to be running in AWS and the airbyte instance to have an AWS IAM user or role with the `sts:AssumeRole` permission.
:::

1. In the IAM dashboard, click **Roles**, then **Create role**.

2. Choose the **AWS account** trusted entity type.

3. Set up a trust relationship for the role. This allows the Airbyte instance's AWS user/role to assume this role.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "{airbyte-instance-iam-user-or-role-arn}"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

4. Complete the role creation and note the Role ARN.

<!-- /env:oss -->

### Step 2: Set up the Cloudwatch Logs connector in Airbyte

### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Cloudwatch Logs from the Source type dropdown.
4. Enter a name for the Cloudwatch Logs connector.

#### Delivery Method

<FieldAnchor field="delivery_method.delivery_type">

Choose a [delivery method](../../platform/using-airbyte/delivery-methods) for your data. 

</FieldAnchor>

## Supported sync modes

The Cloudwatch Logs source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature                                        | Supported? |
| :--------------------------------------------- | :--------- |
| Full Refresh Sync                              | Yes        |
| Incremental Sync                               | Yes        |

## Supported Streams

There is no predefined streams. The streams are based on the accessible Cloudwatch Log Groups in your AWS account.
## State

To perform incremental syncs, Airbyte syncs cloudwatch logs from oldest to newest based on the timestamp of the log events. The state is stored as the timestamp of the latest log event that has been synced for each log group.

## Cloudwatch Logs Settings

- **AWS Region**: The AWS region where your Cloudwatch Logs are hosted (e.g., `us-east-1`).
- **AWS Role ARN**: The Amazon Resource Name (ARN) of the IAM Role to assume for accessing Cloudwatch Logs. This is an alternative to using AWS Access Key ID and Secret Access Key.
- **AWS Access Key ID**: One half of the [required credentials](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) for accessing a private bucket.
- **AWS Secret Access Key**: The other half of the [required credentials](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) for accessing a private bucket.
- **Log Group Prefix**: An optional parameter to filter log groups by prefix. Only log groups with names that start with the specified prefix will be replicated."
- **Session Duration**: An optional parameter that specifies the duration, in seconds, of the role session when assuming an IAM Role. The default value is 3600 seconds (1 hour). The minimum value is 900 seconds (15 minutes), and the maximum value is 43200 seconds (12 hours).
- **Custom Log Reports**: An optional list of custom log reports to include. Each entry:
  - **Log Group Name**: The name of the Cloudwatch Log Group to include.
  - **Log Stream Names**: An optional list of specific Log Stream names within the Log Group to include. If left empty, all Log Streams within the specified Log Group will be included.
  - **Filter Pattern**: An optional filter pattern to apply when retrieving log events from the specified Log Group. This allows for more granular control over which log events are replicated based on specific criteria.
- **Start Date**: An optional parameter that marks a starting date and time in UTC for data replication. Use the provided datepicker (recommended) or enter the desired date programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. Leaving this field blank will replicate logs from the earliest available log event.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version     | Date       | Pull Request                                                                                                    | Subject                                  |
|:------------|:-----------|:----------------------------------------------------------------------------------------------------------------|:-----------------------------------------|
| 0.1.0       | 2026-01-11 | [71295](https://github.com/airbytehq/airbyte/pull/71295)                                                          | Created Cloudwatch Logs source connector |

</details>
