# Kafka

## Overview

The Airbyte Kafka destination allows you to sync data to Kafka. Each stream is written to the corresponding Kafka topic.

## Prerequisites

- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your Kafka connector to version `0.1.10` or newer

### Sync overview

#### Output schema

Each stream will be output into a Kafka topic.

Currently, this connector only writes data with JSON format. More formats \(e.g. Apache Avro\) will be supported in the future.

Each record will contain in its key either:
- A uuid assigned by Airbyte (default behavior)
- A partition key extracted from record data (when `partition_key_field` is configured)

And in its value these 4 fields:

- `_airbyte_ab_id`: the key used for the record (UUID or partition key)
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
- `_airbyte_data`: a json blob representing the event data.
- `_airbyte_stream`: the name of each record's stream.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | No |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

## Getting started

### Requirements

To use the Kafka destination, you'll need:

- A Kafka cluster 1.0 or above.

### Setup guide

#### Network Access

Make sure your Kafka brokers can be accessed by Airbyte.

#### **Permissions**

Airbyte should be allowed to write messages into topics, and these topics should be created before writing into Kafka or, at least, enable the configuration in the brokers `auto.create.topics.enable` \(which is not recommended for production environments\).

Note that if you choose to use dynamic topic names, you will probably need to enable `auto.create.topics.enable` to avoid your connection failing if there was an update to the source connector's schema. Otherwise a hardcoded topic name may be best.

#### Target topics

You can determine the topics to which messages are written via the `topic_pattern` configuration parameter. Messages can be written to either a hardcoded, pre-defined topic, or dynamically written to different topics based on the [namespace](https://docs.airbyte.com/understanding-airbyte/namespaces) or stream they came from.

To write all messages to a single hardcoded topic, enter its name in the `topic_pattern` field e.g: setting `topic_pattern` to `my-topic-name` will write all messages from all streams and namespaces to that topic.

To define the output topics dynamically, you can leverage the `{namespace}` and `{stream}` pattern variables, which cause messages to be written to different topics based on the values present when producing the records. For example, setting the `topic_pattern` parameter to `airbyte_syncs/{namespace}/{stream}` means that messages from namespace `n1` and stream `s1` will get written to the topic `airbyte_syncs/n1/s1`, and messages from `s2` to `airbyte_syncs/n1/s2` etc.

If you define output topic dynamically, you might want to enable `auto.create.topics.enable` to avoid your connection failing if there was an update to the source connector's schema. Otherwise, you'll need to manually create topics in Kafka as they are added/updated in the source, which is the recommended option for production environments.

**NOTICE**: a naming convention transformation will be applied to the target topic name using `StandardNameTransformer` so that some special characters will be replaced.

#### Partition Routing

The Kafka destination connector supports configurable partition routing using record fields as message keys. This allows related records to be sent to the same Kafka partition, ensuring ordering guarantees for related data.

**Configuration:**
Add the `partition_key_field` parameter to your connector configuration to enable partition routing.

**Supported Field Types:**
- **Single Field**: `"user_id"` - Routes records by a single field value
- **Multiple Fields**: `"user_id,order_id"` - Concatenates multiple fields with "|" delimiter
- **Nested Fields**: `"user.id"` - Uses dot notation for nested JSON objects
- **Mixed**: `"user_id,user.email,order.date"` - Combines different field types

**Behavior:**
- **Field Present**: Uses the field value(s) as the Kafka message key
- **Field Missing**: Falls back to random UUID (existing behavior)
- **Null Values**: Treated as missing field, falls back to UUID
- **Multiple Fields**: Concatenated with "|" delimiter

**Examples:**

```json
{
  "partition_key_field": "value.user_id",
  "topic_pattern": "orders.{stream}"
}
```
All records with the same `user_id` will go to the same partition.

```json
{
  "partition_key_field": "value.user_id,value.order_id",
  "topic_pattern": "orders.{stream}"
}
```
Records with the same combination of `user_id` and `order_id` will go to the same partition.

```json
{
  "partition_key_field": "value.user.id",
  "topic_pattern": "users.{stream}"
}
```
Uses nested `user.id` field from JSON structure as partition key.

**Backward Compatibility:**
If `partition_key_field` is not specified, the connector uses random UUID keys (existing behavior).

### Setup the Kafka destination in Airbyte

You should now have all the requirements needed to configure Kafka as a destination in the UI. You can configure the following parameters on the Kafka destination \(though many of these are optional or have default values\):

- **Bootstrap servers**
- **Topic pattern**
- **Partition key field**
- **Test topic**
- **Sync producer**
- **Security protocol**
- **SASL JAAS config**
- **SASL mechanism**
- **Client ID**
- **ACKs**
- **Enable idempotence**
- **Compression type**
- **Batch size**
- **Linger ms**
- **Max in flight requests per connection**
- **Client DNS lookup**
- **Buffer memory**
- **Max request size**
- **Retries**
- **Socket connection setup timeout**
- **Socket connection setup max timeout**
- **Max block ms**
- **Request timeout**
- **Delivery timeout**
- **Send buffer bytes**
- **Receive buffer bytes**

More info about this can be found in the [Kafka producer configs documentation site](https://kafka.apache.org/documentation/#producerconfigs).

_NOTE_: Some configurations for SSL are not available yet.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). The namespace is incorporated into the topic name via the `{namespace}` variable in the `topic_pattern` configuration.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------------------------  |
| 0.2.0   | 2024-03-19 | [PR](https://github.com/airbytehq/airbyte/pull/75225) | Add configurable partition routing support for deterministic record distribution  |
| 0.1.11  | 2025-03-28 | [56450](https://github.com/airbytehq/airbyte/pull/56450) | Add support for other SASL Mechanisms when SASL_PLAINTEXT protocol is selected |
| 0.1.10  | 2022-08-04 | [15287](https://github.com/airbytehq/airbyte/pull/15287) | Update Kafka destination to use outputRecordCollector to properly store state  |
| 0.1.9   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors                         |
| 0.1.7   | 2022-04-19 | [12134](https://github.com/airbytehq/airbyte/pull/12134) | Add PLAIN Auth                                                                 |
| 0.1.6   | 2022-02-15 | [10186](https://github.com/airbytehq/airbyte/pull/10186) | Add SCRAM-SHA-512 Auth                                                         |
| 0.1.5   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                   |
| 0.1.4   | 2022-01-31 | [9905](https://github.com/airbytehq/airbyte/pull/9905)   | Fix SASL config read issue                                                     |
| 0.1.3   | 2021-12-30 | [8809](https://github.com/airbytehq/airbyte/pull/8809)   | Update connector fields title/description                                      |
| 0.1.2   | 2021-09-14 | [6040](https://github.com/airbytehq/airbyte/pull/6040)   | Change spec.json and config parser                                             |
| 0.1.1   | 2021-07-30 | [5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                   |
| 0.1.0   | 2021-07-21 | [3746](https://github.com/airbytehq/airbyte/pull/3746)   | Initial Release                                                                |

</details>