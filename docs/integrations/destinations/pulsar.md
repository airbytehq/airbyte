# Pulsar

## Overview

The Airbyte Pulsar destination allows you to sync data to Pulsar. Each stream is written to the corresponding Pulsar topic.

## Prerequisites

- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your Pulsar connector to version `0.1.3` or newer

### Sync overview

#### Output schema

Each stream will be output into a Pulsar topic.

Currently, this connector only writes data with JSON format. More formats \(e.g. Apache Avro\) will be supported in the future.

Each record will contain in its key the uuid assigned by Airbyte, and in the value these 3 fields:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
- `_airbyte_data`: a json blob representing with the event data encoded in base64 .
- `_airbyte_stream`: the name of each record's stream.

#### Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | No                   |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | Yes                  |       |

## Getting started

### Requirements

To use the Pulsar destination, you'll need:

- A Pulsar cluster 2.8 or above.

### Setup guide

#### Network Access

Make sure your Pulsar brokers can be accessed by Airbyte.

#### **Permissions**

Airbyte should be allowed to write messages into topics, and these topics should be created before writing into Pulsar or, at least, enable the configuration in the brokers `allowAutoTopicCreation` \(which is not recommended for production environments\).

Note that if you choose to use dynamic topic names, you will probably need to enable `allowAutoTopicCreation` to avoid your connection failing if there was an update to the source connector's schema. Otherwise a hardcoded topic name may be best.

Also, notice that the messages will be sent to topics based on the configured Pulsar `topic_tenant` and `topic_namespace` configs with their `topic_type`.

#### Target topics

You can determine the topics to which messages are written via the `topic_pattern` configuration parameter in its corresponding Pulsar `topic_tenant`-`topic_namespace`. Messages can be written to either a hardcoded, pre-defined topic, or dynamically written to different topics based on the [namespace](https://docs.airbyte.com/understanding-airbyte/namespaces) or stream they came from.

To write all messages to a single hardcoded topic, enter its name in the `topic_pattern` field e.g: setting `topic_pattern` to `my-topic-name` will write all messages from all streams and namespaces to that topic.

To define the output topics dynamically, you can leverage the `{namespace}` and `{stream}` pattern variables, which cause messages to be written to different topics based on the values present when producing the records. For example, setting the `topic_pattern` parameter to `airbyte_syncs/{namespace}/{stream}` means that messages from namespace `n1` and stream `s1` will get written to the topic `airbyte_syncs/n1/s1`, and messages from `s2` to `airbyte_syncs/n1/s2` etc.

If you define output topic dynamically, you might want to enable `allowAutoTopicCreation` to avoid your connection failing if there was an update to the source connector's schema. Otherwise, you'll need to manually create topics in Pulsar as they are added/updated in the source, which is the recommended option for production environments.

**NOTICE**: a naming convention transformation will be applied to the target topic name using the `StandardNameTransformer` so that some special characters will be replaced.

### Setup the Pulsar destination in Airbyte

You should now have all the requirements needed to configure Pulsar as a destination in the UI. You can configure the following parameters on the Pulsar destination \(though many of these are optional or have default values\):

- **Pulsar brokers**
- **Use TLS**
- **Topic type**
- **Topic tenant**
- **Topic namespace**
- **Topic pattern**
- **Test topic**
- **Producer name**
- **Sync producer**
- **Compression type**
- **Message send timeout**
- **Max pending messages**
- **Max pending messages across partitions**
- **Enable batching**
- **Batching max messages**
- **Batching max publish delay**
- **Block if queue is full**

More info about this can be found in the [Pulsar producer configs documentation site](https://pulsar.apache.org/docs/en/client-libraries-java/#producer).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                        |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------------------------------- |
| 0.1.3   | 2022-08-05 | [15349](https://github.com/airbytehq/airbyte/pull/15349) | Update Pulsar destination to use outputRecordCollector to properly store state |

</details>