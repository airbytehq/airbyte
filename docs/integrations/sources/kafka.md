# Kafka

This page guides you through the process of setting up the Kafka source connector in Airbyte.

# Set up guide

## Step 1: Set up Kafka

To use the Kafka source connector, you'll need:

* [A Kafka cluster 1.0 or above](https://kafka.apache.org/quickstart)
* Airbyte user should be allowed to read messages from topics, and these topics should be created before reading from Kafka.

## Step 2: Configure the Kafka source in Airbyte

To configure the Kafka source, you'll need the following information:

* **Bootstrap Servers**: A list of host/port pairs used for establishing the initial connection to the Kafka cluster (e.g., `kafka-broker1:9092,kafka-broker2:9092`). For more information on finding these values, see the Kafka documentation on [configuring Kafka listeners](https://kafka.apache.org/documentation/#listeners).

* **Subscription Method**: You can choose to manually assign a list of partitions or subscribe to all topics matching the specified pattern to get dynamically assigned partitions. Refer to the Kafka documentation on [topic subscription and partition assignment](https://kafka.apache.org/documentation/#theconsumer) for more information.

* **List of Topics**: Provide a list of topics the Airbyte user has read access to.

* **Group ID**: A unique identifier for the consumer group (e.g., `group.id`). Check the Kafka documentation on [consumer group coordination](https://kafka.apache.org/documentation/#intro_consumers) for more information.

* **Protocol**: The Protocol used to communicate with brokers. Options include `PLAINTEXT`, `SASL_PLAINTEXT`, and `SASL_SSL`. See the Kafka documentation on [security](https://kafka.apache.org/documentation/#security) for more details.

* **Client ID**: An ID string to pass to the server when making requests, allowing the server to track the source of requests beyond just the IP/port (e.g., `airbyte-consumer`). Refer to the Kafka documentation on [monitoring](https://kafka.apache.org/documentation/#monitoring) for more information.

* **Test Topic**: The Topic to test for Airbyte's ability to consume messages (e.g., `test.topic`).

* **Message Format**: The serialization type for message values. Options include `JSON` and `AVRO`. If using `AVRO`, provide the information for connecting to the Schema Registry server, including the URL, username, and password. For more information on the Avro serializer/deserializer, see the [Confluent documentation](https://docs.confluent.io/platform/current/schema-registry/serdes-develop/serdes-avro.html).

Use the information you've gathered to fill in the appropriate fields on the Kafka connector configuration form in Airbyte.