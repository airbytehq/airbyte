# Kafka

This page guides you through the process of setting up the Kafka source connector.

# Set up guide

## Step 1: Set up Kafka

To use the Kafka source connector, you'll need:

- [A Kafka cluster 1.0 or above](https://kafka.apache.org/quickstart)
- Airbyte user should be allowed to read messages from topics, and these topics should be created before reading from Kafka.

## Step 2: Setup the Kafka source in Airbyte

You'll need the following information to configure the Kafka source:

- **Bootstrap Servers** - A list of host/port pairs to use for establishing the initial connection to the Kafka cluster.
- **MessageFormat** - How to deserialize messages; choose either:
  - **JSON**
  - **AVRO** if choosing avro, several other options are available
    - Deserialization strategy - To deserialize Avro binary, set the [_subject name strategy_][subject-name-strategy] for choosing the schema from the registry
    - Schema Registry URL - Host/port to connect to the schema registry server
    - Username and password, optional to authenticate to the schema registry server
- **Protocol** - The Protocol used to communicate with brokers. If using SASL, this includes how to authenticate to the brokers.
  - **PLAINTEXT** - no authentication and no encryption
  - **SASL PLAINTEXT** - no encryption; a `SASL JAAS Config` is needed to authenticate
  - **SASL SSL** - encrypted
    - **SASL JAAS Config** configures authentication to the brokers
    - **SASL Mechanism** appropriate to your brokers' auth mechanism
    - **OAUTHBEARER token endpoint URL** Optional; If using SASL Mechanism `OAUTHBEARER`, set to the token endpoint URL; note this does not apply to schema registry auth
- **Subscription Method** - You can choose to manually assign a list of partitions, or subscribe to all topics matching specified pattern to get dynamically assigned partitions.
  - **List of topic** - comma separated `topic:partition`s, each partition becomes a stream in the connection
  - **Topic pattern** - a pattern to use, each matching topic becomes a stream in the connection

Some optional fields that are recommended to set according to your use
- **Client ID** - An ID string to pass to the brokers when making requests. The purpose of this is to be able to track the source of requests beyond just ip/port by allowing a logical application name to be included in server-side request logging. (e.g. airbyte-consumer)
- **Group ID** - The Group ID is how you distinguish different consumer groups. (e.g. group.id)
- **Test Topic** - The Topic to test whether Airbyte can consume messages. (e.g. test.topic)
- **Polling Time** - Amount of time in milliseconds Kafka connector should try to poll for messages, per sync

### For Airbyte Open Source:

1. Go to the Airbyte UI and in the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
2. On the Set up the source page, enter the name for the Kafka connector and select **Kafka** from the Source type dropdown.
3. Follow the [Setup the Kafka source in Airbyte](kafka.md#step-2-setup-the-kafka-source-in-airbyte)

## Supported sync modes

The Kafka source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

## Supported Format

JSON - Json value messages. It does not support schema registry now.

AVRO - deserialize Using confluent API. Please refer (https://docs.confluent.io/platform/current/schema-registry/serdes-develop/serdes-avro.html)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                                                       | Subject                                                              |
| :------ | :--------- |:---------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------|
| 0.3.0   | 2025-02-18 | [53231](https://github.com/airbytehq/airbyte/pull/53231)                                           | Add configurations for OAUTHBEARER SASL Mechanism                    |
| 0.2.8 | 2025-02-07 | [53221](https://github.com/airbytehq/airbyte/pull/53221)                                           | For AVRO MessageFormat, schema_registry_password is a secret         |
| 0.2.7 | 2025-01-10 | [51480](https://github.com/airbytehq/airbyte/pull/51480)                                           | Use a non root base image                                            |
| 0.2.6 | 2024-12-18 | [49907](https://github.com/airbytehq/airbyte/pull/49907)                                           | Use a base image: airbyte/java-connector-base:1.0.0                  |
| 0.2.5 | 2024-06-12 | [32538](https://github.com/airbytehq/airbyte/pull/32538)                                           | Fix empty airbyte data column                                        |
| 0.2.4 | 2024-02-13 | [35229](https://github.com/airbytehq/airbyte/pull/35229)                                           | Adopt CDK 0.20.4                                                     |
| 0.2.4 | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453)                                           | bump CDK version                                                     |
| 0.2.3 | 2022-12-06 | [19587](https://github.com/airbytehq/airbyte/pull/19587)                                           | Fix missing data before consumer is closed                           |
| 0.2.2 | 2022-11-04 | [18648](https://github.com/airbytehq/airbyte/pull/18648)                                           | Add missing record_count increment for JSON                          |
| 0.2.1   | 2022-11-04 | This version was the same as 0.2.0 and was committed so using 0.2.2 next to keep versions in order |
| 0.2.0   | 2022-08-22 | [13864](https://github.com/airbytehq/airbyte/pull/13864)                                           | Added AVRO format support and Support for maximum records to process |
| 0.1.7   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864)                                           | Updated stacktrace format for any trace message errors               |
| 0.1.6   | 2022-05-29 | [12903](https://github.com/airbytehq/airbyte/pull/12903)                                           | Add Polling Time to Specification (default 100 ms)                   |
| 0.1.5   | 2022-04-19 | [12134](https://github.com/airbytehq/airbyte/pull/12134)                                           | Add PLAIN Auth                                                       |
| 0.1.4   | 2022-02-15 | [10186](https://github.com/airbytehq/airbyte/pull/10186)                                           | Add SCRAM-SHA-512 Auth                                               |
| 0.1.3   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)                                           | Add `-XX:+ExitOnOutOfMemoryError` JVM option                         |
| 0.1.2   | 2021-12-21 | [8865](https://github.com/airbytehq/airbyte/pull/8865)                                             | Fix SASL config read issue                                           |
| 0.1.1   | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524)                                             | Update connector fields title/description                            |

</details>
