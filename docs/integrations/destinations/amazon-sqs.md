# Amazon SQS

:::warning

This connector is archived. It's no longer available in the Airbyte Cloud or Airbyte Open Source connector catalogs, and it doesn't receive updates or support from the Airbyte team. For more information, see [Archived connectors](../connector-support-levels.md#archived-connectors).

:::

## Overview

The Amazon SQS destination sends each record from your source to a single Amazon SQS queue. It supports both standard and FIFO queues.

## Prerequisites

- An Amazon SQS queue. See [Create a queue](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/creating-sqs-standard-queues.html) in the AWS documentation.
- An AWS IAM access key ID and secret access key for an IAM user with the following permissions on the queue:
  - `sqs:SendMessage`
  - `sqs:GetQueueAttributes`

The connector always authenticates with an access key. Although the access key fields appear as optional in the configuration form, the connection check and syncs fail if you don't provide them.

## Setup guide

### Step 1: Create an IAM user and access key

1. In the AWS IAM console, create an IAM user for Airbyte.
2. Attach a policy that grants the required permissions on your queue. For example:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": ["sqs:SendMessage", "sqs:GetQueueAttributes"],
         "Resource": "arn:aws:sqs:<region>:<account-id>:<queue-name>"
       }
     ]
   }
   ```

3. [Create an access key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey) for the user and save the access key ID and secret access key.

### Step 2: Set up the destination in Airbyte

Provide the following configuration:

- **Queue URL**: The full URL of the queue, for example `https://sqs.eu-west-1.amazonaws.com/1234567890/example-queue`. The connector treats the queue as a FIFO queue if the URL ends in `.fifo`.
- **AWS Region**: The region of the queue, for example `eu-west-1`.
- **AWS IAM Access Key ID** and **AWS IAM Secret Key**: The credentials from Step 1.
- **Message Delay** (optional): The number of seconds to delay each message before consumers can receive it. Amazon SQS accepts values from 0 to 900. Don't set this for FIFO queues. See [Amazon SQS message timers](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-timers.html).
- **Message Body Key** (optional): The name of a top-level field in the record to use as the message body. See [Use the Message Body Key](#use-the-message-body-key).
- **Message Group Id**: Required for FIFO queues and ignored for standard queues. See [FIFO queues](#fifo-queues).

## Message format

All streams are written to the same queue. The connector sends one message per record and doesn't batch messages.

By default, the message body is the record's data serialized as a JSON string. The stream name and other Airbyte metadata aren't included in the body. Each message has one [message attribute](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-metadata.html), `airbyte_emitted_at`, a `String` attribute that contains the time the source emitted the record, in milliseconds since the Unix epoch.

Amazon SQS limits the size of each message. Records larger than the limit fail to send. See [Amazon SQS message quotas](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/quotas-messages.html).

### Use the Message Body Key

Set **Message Body Key** to send the value of one top-level field as the message body instead of the whole record. Nested fields aren't supported. Use this to send text or XML messages.

The field's value must be a string. If the value is an object, array, or number, the message fails to send. If a record doesn't contain the field, or the field is `null`, the sync fails.

For example, with this input record:

```json
{
  "my_xml_field": "<something>value</something>"
}
```

Setting **Message Body Key** to `my_xml_field` produces this message body:

```xml
<something>value</something>
```

### FIFO queues

When the queue URL ends in `.fifo`, the connector checks that the queue is a FIFO queue and requires **Message Group Id**. Every message is sent with the same message group ID, so Amazon SQS delivers all records in order as a single group.

How the connector handles deduplication depends on the queue's [content-based deduplication](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/using-messagededuplicationid-property.html) setting:

- **Disabled**: The connector generates a random deduplication ID for each message, so Amazon SQS doesn't deduplicate any records.
- **Enabled**: Amazon SQS deduplicates messages based on their body. Records with identical message bodies sent within the five-minute deduplication interval are delivered only once.

Amazon SQS doesn't support per-message delays on FIFO queues. Leave **Message Delay** empty and configure a delay on the queue instead.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | No |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

## Namespace support

This destination does not support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                           |
|:--------|:-----------| :-------------------------------------------------------- | :-------------------------------- |
| 0.1.18 | 2026-11-03 | [90866](https://github.com/airbytehq/airbyte/pull/90866) | Archive connector |
| 0.1.17  | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies                                  |
| 0.1.16  | 2024-08-03 | [43278](https://github.com/airbytehq/airbyte/pull/43278) | Update dependencies |
| 0.1.15  | 2024-07-27 | [42795](https://github.com/airbytehq/airbyte/pull/42795) | Update dependencies |
| 0.1.14  | 2024-07-20 | [42165](https://github.com/airbytehq/airbyte/pull/42165) | Update dependencies |
| 0.1.13  | 2024-07-13 | [41733](https://github.com/airbytehq/airbyte/pull/41733) | Update dependencies |
| 0.1.12  | 2024-07-10 | [41439](https://github.com/airbytehq/airbyte/pull/41439) | Update dependencies |
| 0.1.11  | 2024-07-09 | [41237](https://github.com/airbytehq/airbyte/pull/41237) | Update dependencies |
| 0.1.10  | 2024-07-06 | [40960](https://github.com/airbytehq/airbyte/pull/40960) | Update dependencies |
| 0.1.9   | 2024-06-29 | [40622](https://github.com/airbytehq/airbyte/pull/40622) | Update dependencies |
| 0.1.8   | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.1.7   | 2024-06-26 | [40536](https://github.com/airbytehq/airbyte/pull/40536) | Update dependencies |
| 0.1.6   | 2024-06-25 | [40461](https://github.com/airbytehq/airbyte/pull/40461) | Update dependencies |
| 0.1.5   | 2024-06-22 | [40075](https://github.com/airbytehq/airbyte/pull/40075) | Update dependencies |
| 0.1.4   | 2024-06-04 | [39070](https://github.com/airbytehq/airbyte/pull/39070) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3   | 2024-05-21 | [38493](https://github.com/airbytehq/airbyte/pull/38493) | [autopull] base image + poetry + up_to_date |
| 0.1.2   | 2024-03-05 | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector              |
| 0.1.1   | 2024-01-03 | [#33924](https://github.com/airbytehq/airbyte/pull/33924) | Add new ap-southeast-3 AWS region |
| 0.1.0   | 2021-10-27 | [#0000](https://github.com/airbytehq/airbyte/pull/0000)   | Initial version                   |

</details>
