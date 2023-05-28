# Kafka

This page guides you through the process of setting up the Kafka source connector.

# Kafka Source Connector Setup Guide

This guide will walk you through setting up the Kafka Source Connector in Airbyte.

## Prerequisites

Before you start, you must have the following:

* A Kafka cluster running version 1.0 or above. Follow the [Kafka Quickstart](https://kafka.apache.org/quickstart) to set up a Kafka cluster.
* Airbyte user should be allowed to read messages from topics. Ensure that these topics are created before reading from Kafka.

## Setup Guide

1. **Group ID**: Enter a unique identifier for your consumer group (e.g. group.id).

2. **Protocol**: Select the communication protocol used with brokers. Available options are `PLAINTEXT`, `SASL_PLAINTEXT`, and `SASL_SSL`. Depending on your choice, you might need to provide additional configuration details (e.g. for `SASL_SSL`, the SASL Mechanism and SASL JAAS Config are required).

3. **Client ID**: Enter an ID string to pass to the server when making requests. This allows tracking the source of requests beyond IP/port, by including a logical application name in server-side request logging (e.g. airbyte-consumer).

4. **Subscription Method**: Choose between manually assigning a list of partitions or subscribing to all topics matching a specified pattern to get dynamically assigned partitions. Provide either a list of topic:partition pairs (e.g. sample.topic:0, sample.topic:1) or a Topic pattern (e.g. sample.topic).

5. **Bootstrap Servers**: Enter a list of host/port pairs for establishing the initial connection to the Kafka cluster (e.g. kafka-broker1:9092,kafka-broker2:9092). The connector will use all servers for bootstrapping and discovering the full set of servers.

6. **Message Format**: Choose either `JSON` or `AVRO` serialization format for messages. If you select `AVRO`, provide the schema registry URL (e.g. http://localhost:8081) and the schema registry username and password if applicable.

7. **Test Topic**: Enter a topic to test if Airbyte can consume messages from it (e.g. test.topic).

You can also configure the optional settings, such as the maximum number of records returned in a single call to poll(), auto commit interval, client DNS lookup, retry backoff, request timeout, receive buffer size, and auto offset reset policy.

Once you have entered the required information and set the optional configurations as needed, click the "Set up source" button to complete the setup.

## Supported Sync Modes

The Kafka source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported?(Yes/No) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | No |  |

## Supported Formats

* JSON: Supports JSON value messages only. The current implementation does not support schema registry.

* AVRO: Deserializes messages using the Confluent API. For more information, refer to the [Confluent AVRO documentation](https://docs.confluent.io/platform/current/schema-registry/serdes-develop/serdes-avro.html).

## Changelog

| Version | Date       | Pull Request                                           | Subject                                   |
| :------ | :--------  | :------------------------------------------------------| :---------------------------------------- |
| 0.2.3 | 2022-12-06 | [19587](https://github.com/airbytehq/airbyte/pull/19587) | Fix missing data before consumer is closed |
| 0.2.2 | 2022-11-04 | [18648](https://github.com/airbytehq/airbyte/pull/18648) | Add missing record_count increment for JSON|
| 0.2.1 | 2022-11-04 | This version was the same as 0.2.0 and was committed so using 0.2.2 next to keep versions in order|
| 0.2.0 | 2022-08-22 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Added AVRO format support and Support for maximum records to process|
| 0.1.7 | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.1.6   | 2022-05-29 | [12903](https://github.com/airbytehq/airbyte/pull/12903) | Add Polling Time to Specification (default 100 ms) |
| 0.1.5   | 2022-04-19 | [12134](https://github.com/airbytehq/airbyte/pull/12134) | Add PLAIN Auth |
| 0.1.4   | 2022-02-15 | [10186](https://github.com/airbytehq/airbyte/pull/10186) | Add SCRAM-SHA-512 Auth |
| 0.1.3   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.1.2   | 2021-12-21 | [8865](https://github.com/airbytehq/airbyte/pull/8865) | Fix SASL config read issue                |
| 0.1.1   | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524) | Update connector fields title/description |
