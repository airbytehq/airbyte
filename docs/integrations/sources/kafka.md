# Kafka

## Overview

The Airbyte Kafka source allows you to sync data from Kafka. Each Kafka topic is written to the corresponding stream.

### Sync overview

#### Output schema

Each Kafka topic will be output into a stream.

Currently, this connector only reads data with JSON format. More formats (e.g. Apache Avro) will be supported in 
the future.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | No |  |

## Getting started

### Requirements

To use the Kafka source, you'll need:

* A Kafka cluster 1.0 or above.

### Setup guide

#### Network Access

Make sure your Kafka brokers can be accessed by Airbyte.

#### **Permissions**

Airbyte should be allowed to read messages from topics, and these topics should be created before reading from Kafka.

#### Target topics

You can determine the topics from which messages are read via the `topic_pattern` configuration parameter.
Messages can be read from a hardcoded, pre-defined topic.

To read all messages from a single hardcoded topic, enter its name in the `topic_pattern` field 
e.g: setting `topic_pattern` to `my-topic-name` will read all messages from that topic.

You can determine the topic partitions from which messages are read via the `topic_partitions` configuration parameter.   

### Setup the Kafka destination in Airbyte

You should now have all the requirements needed to configure Kafka as a destination in the UI. You can configure the 
following parameters on the Kafka destination (though many of these are optional or have default values):

* **Bootstrap servers**
* **Topic pattern**
* **Topic partition**
* **Test topic**
* **Group ID**
* **Max poll records**
* **SASL JAAS config**
* **SASL mechanism**
* **Client ID**
* **Enable auto commit**
* **Auto commit interval ms**
* **Client DNS lookup**
* **Retry backoff ms**
* **Request timeout ms**
* **Receive buffer bytes**
* **Repeated calls**

More info about this can be found in the [Kafka consumer configs documentation site](https://kafka.apache.org/documentation/#consumerconfigs).

## Changelog
