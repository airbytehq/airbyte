# Amazon SQS

## Sync overview

This source will sync messages from an [SQS Queue](https://docs.aws.amazon.com/sqs/index.html).

### Output schema

This source will output one stream for the configured SQS Queue. The stream record data will have
three fields:

- id (a UUIDv4 as a STRING)
- body (message body as a STRING)
- attributes (attributes of the messages as an OBJECT or NULL)

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | yes                  |       |
| Incremental Sync  | no                   |       |
| Namespaces        | no                   |       |

### Performance considerations

## Getting started

### Requirements

- AWS IAM Access Key
- AWS IAM Secret Key
- AWS SQS Queue

### Properties

Required properties are 'Queue URL', 'AWS Region' and 'Delete Messages After Read' as noted in
**bold** below.

- **Queue URL** (STRING)
  - The full AWS endpoint URL of the queue e.g.
    `https://sqs.eu-west-1.amazonaws.com/1234567890/example-queue-url`
- **AWS Region** (STRING)
  - The region code for the SQS Queue e.g. eu-west-1
- **Delete Messages After Read** (BOOLEAN)
  - **WARNING:** Setting this option to TRUE can result in data loss, do not enable this option
    unless you understand the risk. See the **Data loss warning** section below.
  - Should the message be deleted from the SQS Queue after being read? This prevents the message
    being read more than once
  - By default messages are NOT deleted, thus can be re-read after the `Message Visibility Timeout`
  - Default: False
- Max Batch Size (INTEGER)
  - The max amount of messages to consume in a single poll e.g. 5
  - Minimum of 1, maximum of 10
  - Default: 10
- Max Wait Time (INTEGER)
  - The max amount of time (in seconds) to poll for messages before commiting a batch (or timing
    out) unless we fill a batch (as per `Max Batch Size`)
  - Minimum of 1, maximum of 20
  - Default: 20
- Message Attributes To Return (STRING)
  - A comma separated list of Attributes to return for each message
  - Default: All
- Message Visibility Timeout (INTEGER)
  - After a message is read, how much time (in seconds) should the message be hidden from other
    consumers
  - After this timeout, the message is not deleted and can be re-read
  - Default: 30
- AWS IAM Access Key ID (STRING)
  - The Access Key for the IAM User with permissions on this Queue
  - If `Delete Messages After Read` is `false` then only `sqs:ReceiveMessage`
  - If `Delete Messages After Read` is `true` then `sqs:DeleteMessage` is also needed
- AWS IAM Secret Key (STRING)
  - The Secret Key for the IAM User with permissions on this Queue

### Data loss warning

When enabling **Delete Messages After Read**, the Source will delete messages from the SQS Queue
after reading them. The message is deleted _after_ the configured Destination takes the message from
this Source, but makes no guarentee that the downstream destination has commited/persisted the
message. This means that it is possible for the Airbyte Destination to read the message from the
Source, the Source deletes the message, then the downstream application fails - resulting in the
message being lost permanently.

Extra care should be taken to understand this risk before enabling this option.

### Setup guide

- [Create IAM Keys](https://aws.amazon.com/premiumsupport/knowledge-center/create-access-key/)
- [Create SQS Queue](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-getting-started.html#step-create-queue)

> **NOTE**:
>
> - If `Delete Messages After Read` is `false` then the IAM User needs only `sqs:ReceiveMessage` in
>   the AWS IAM Policy
> - If `Delete Messages After Read` is `true` then both `sqs:ReceiveMessage` and `sqs:DeleteMessage`
>   are needed in the AWS IAM Policy

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                           |
| :------ | :--------- | :-------------------------------------------------------- | :-------------------------------- |
| 0.1.1   | 2024-01-03 | [#33924](https://github.com/airbytehq/airbyte/pull/33924) | Add new ap-southeast-3 AWS region |
| 0.1.0   | 2021-10-10 | [\#0000](https://github.com/airbytehq/airbyte/pull/0000)  | Initial version                   |

</details>