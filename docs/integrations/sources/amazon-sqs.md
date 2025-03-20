# Amazon SQS

## Overview

The Amazon SQS source syncs the SQS API, refer: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/Welcome.html. It supports full refresh sync and could be viewed in builder with low-code support.

## Getting started

### Requirements

- AWS IAM Access Key
- AWS IAM Secret Key
- AWS SQS Queue URL
- AWS Region
- Action target

### Setup guide

- [Create IAM Keys](https://aws.amazon.com/premiumsupport/knowledge-center/create-access-key/)
- [Create SQS Queue](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-getting-started.html#step-create-queue)

### Supported Streams

This Source is capable of syncing the following core Action that would be received as streams for sync:

- [RecieveMessage](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ReceiveMessage.html)
- [QueueAttributes](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_GetQueueAttributes.html)

Other Actions are in beta which might require more/less parameters

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| Namespaces        | No                   |       |

### Performance considerations

The rate of lookup requests for `RecieveMessage` stream is limited to two per second, per account, per region. This connector gracefully retries when encountering a throttling error. However if the errors continue repeatedly after multiple retries \(for example if you setup many instances of this connector using the same account and region\), the connector sync will fail.


### Output schema

This source will output one stream for the configured SQS Queue. The stream record data will have
three fields:

- id (a UUIDv4 as a STRING)
- body (message body as a STRING)
- attributes (attributes of the messages as an OBJECT or NULL)

### Properties

Required properties are 'Queue URL', 'AWS Region' and 'Delete Messages After Read' as noted in
**bold** below.

- **Queue URL** (STRING)
  - The full AWS endpoint URL of the queue e.g.
    `https://sqs.eu-west-1.amazonaws.com/1234567890/example-queue-url`
- **AWS Region** (STRING)
  - The region code for the SQS Queue e.g. eu-west-1
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
  - Default: 20
- **AWS IAM Access Key ID** (STRING)
  - The Access Key for the IAM User with permissions on this Queue
- **AWS IAM Secret Key** (STRING)
  - The Secret Key for the IAM User with permissions on this Queue
- **Target** (STRING)
  - The targeted action resource for the fetch

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                           |
| :------ | :--------- | :-------------------------------------------------------- | :-------------------------------- |
| 1.0.7 | 2025-03-08 | [54832](https://github.com/airbytehq/airbyte/pull/54832) | Update dependencies |
| 1.0.6 | 2025-03-01 | [54738](https://github.com/airbytehq/airbyte/pull/54738) | fix: Update source-amazon-sqs to use nltk 3.9.1 or higher |
| 1.0.5 | 2025-02-22 | [54271](https://github.com/airbytehq/airbyte/pull/54271) | Update dependencies |
| 1.0.4 | 2025-02-15 | [53936](https://github.com/airbytehq/airbyte/pull/53936) | Update dependencies |
| 1.0.3 | 2025-02-01 | [52878](https://github.com/airbytehq/airbyte/pull/52878) | Update dependencies |
| 1.0.2 | 2025-01-25 | [52163](https://github.com/airbytehq/airbyte/pull/52163) | Update dependencies |
| 1.0.1 | 2025-01-18 | [51742](https://github.com/airbytehq/airbyte/pull/51742) | Update dependencies |
| 1.0.0 | 2024-11-07 | [41064](https://github.com/airbytehq/airbyte/pull/41064) | Migrate to low code |
| 0.1.1   | 2024-01-03 | [#33924](https://github.com/airbytehq/airbyte/pull/33924) | Add new ap-southeast-3 AWS region |
| 0.1.0   | 2021-10-10 | [\#0000](https://github.com/airbytehq/airbyte/pull/0000)  | Initial version                   |

</details>
