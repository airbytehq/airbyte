# MQTT

## Overview

The Airbyte MQTT destination allows you to sync data to any MQTT system compliance with version 3.1.X. Each stream is written to the corresponding MQTT topic.

## Prerequisites

- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your MQTT connector to the latest version

### Sync overview

#### Output schema

Each stream will be output into a MQTT topic.

This connector writes data with JSON format (in bytes).

Each record will contain in its payload these 4 fields:

- `_airbyte_ab_id`: an uuid assigned by Airbyte to each event that is processed.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
- `_airbyte_data`: a json blob representing with the event data.
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

To use the MQTT destination, you'll need:

- A MQTT broker implementing MQTT protocol version 3.1.X.

### Setup guide

#### Network Access

Make sure your MQTT broker can be accessed by Airbyte.

#### **Permissions**

Airbyte should be allowed to write messages into topics. Based on the MQTT broker you have deployed, check if you'll need some specific permissions.

#### Target topics

You can determine the topics to which messages are written via the `topic_pattern` configuration parameter. Messages can be written to either a hardcoded, pre-defined topic, or dynamically written to different topics based on the [namespace](https://docs.airbyte.com/understanding-airbyte/namespaces) or stream they came from.

To write all messages to a single hardcoded topic, enter its name in the `topic_pattern` field e.g: setting `topic_pattern` to `path1/path2/my-topic-name` will write all messages from all streams and namespaces to that topic.

To define the output topics dynamically, you can leverage the `{namespace}` and `{stream}` pattern variables, which cause messages to be written to different topics based on the values present when producing the records. For example, setting the `topic_pattern` parameter to `airbyte_syncs/{namespace}/{stream}` means that messages from namespace `n1` and stream `s1` will get written to the topic `airbyte_syncs/n1/s1`, and messages from `s2` to `airbyte_syncs/n1/s2` etc.

### Setup the MQTT destination in Airbyte

You should now have all the requirements needed to configure MQTT as a destination in the UI. You can configure the following parameters on the MQTT destination \(though many of these are optional or have default values\):

- **MQTT broker host**
- **MQTT broker port**
- **Use TLS**
- **Username**
- **Password**
- **Topic pattern**
- **Test topic**
- **Client ID**
- **Sync publisher**
- **Connect timeout**
- **Automatic reconnect**
- **Clean session**
- **Message retained**
- **Message QoS**

More info about this can be found in the [OASIS MQTT standard site](http://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html).

_NOTE_: MQTT version 5 is not supported yet.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                         |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------- |
| 0.1.3   | 2022-09-02 | [16263](https://github.com/airbytehq/airbyte/pull/16263) | Marked password field in spec as airbyte_secret |
| 0.1.2   | 2022-07-12 | [14648](https://github.com/airbytehq/airbyte/pull/14648) | Include lifecycle management                    |
| 0.1.1   | 2022-05-24 | [13099](https://github.com/airbytehq/airbyte/pull/13099) | Fixed build's tests                             |

</details>