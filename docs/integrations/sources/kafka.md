# Kafka

This page guides you through the process of setting up the Kafka source connector.

## Set up guide

### Step 1: Set up Kafka

To use the Kafka source connector, you'll need:

* [A Kafka cluster 1.0 or above](https://kafka.apache.org/quickstart)
* Airbyte user should be allowed to read messages from topics, and these topics should be created before reading from Kafka.

### Step 2: Setup the Kafka source in Airbyte

You'll need the following information to configure the Kafka source:

* **Group ID** - The Group ID is how you distinguish different consumer groups. (e.g. group.id)
* **Protocol** - The Protocol used to communicate with brokers.
