# Amazon SQS

## Overview

The Airbyte SQS destination allows you to sync data to Amazon SQS. It currently supports sending all
streams to a single Queue.

### Sync overview

#### Output schema

All streams will be output into a single SQS Queue.

Amazon SQS messages can only contain JSON, XML or text, and this connector supports writing messages
in all three formats. See the **Writing Text or XML messages** section for more info.

#### Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | No                   |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | No                   |       |

## Getting started

### Requirements

- AWS IAM Access Key
- AWS IAM Secret Key
- AWS SQS Queue

#### Permissions

If the target SQS Queue is not public, you will need the following permissions on the Queue:

- `sqs:SendMessage`

### Properties

Required properties are 'Queue URL' and 'AWS Region' as noted in **bold** below.

- **Queue URL** (STRING)
  - The full AWS endpoint URL of the queue
    e.g.`https://sqs.eu-west-1.amazonaws.com/1234567890/example-queue-url`
- **AWS Region** (STRING)
  - The region code for the SQS Queue e.g. eu-west-1
- Message Delay (INT)
  - Time in seconds that this message should be hidden from consumers.
  - See the
    [AWS SQS documentation](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-timers.html)
    for more detail.
- AWS IAM Access Key ID (STRING)
  - The Access Key for the IAM User with permissions on this Queue
  - Permission `sqs:SendMessage` is required
- AWS IAM Secret Key (STRING)
  - The Secret Key for the IAM User with permissions on this Queue
- Message Body Key (STRING)
  - Rather than sending the entire Record as the Message Body, use this property to reference a Key
    in the Record to use as the message body. The value of this property should be the Key name in
    the input Record. The key must be at the top level of the Record, nested Keys are not supported.
- Message Group Id (STRING)
  - When using a FIFO queue, this property is **required**.
  - See the
    [AWS SQS documentation](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/using-messagegroupid-property.html)
    for more detail.

### Setup guide

- [Create IAM Keys](https://aws.amazon.com/premiumsupport/knowledge-center/create-access-key/)
- [Create SQS Queue](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-getting-started.html#step-create-queue)

#### Using the Message Body Key

This property allows you to reference a Key within the input Record as using that properties Value
as the SQS Message Body.

For example, with the input Record:

```
{
  "parent_with_child": {
    "child": "child_value"
  },
  "parent": "parent_value"
}
```

To send _only_ the `parent_with_child` object, we can set `Message Body Key` to `parent_with_child`.
Giving an output SQS Message of:

```
{
  "child": "child_value"
}
```

#### Writing Text or XML messages

To output Text or XML, the data must be contained within a String field in the input data, and then
referenced by setting the `Message Body Key` property.

For example, with an input Record as:

```
{
  "my_xml_field": "<something>value</something>"
}
```

To send a pure XML message, you would set the `Message Body Key` to `my_xml_field`.

The output SQS message would contain:

```
<something>value</something>
```

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                           |
|:--------|:-----------| :-------------------------------------------------------- | :-------------------------------- |
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
