# Kafka

This page guides you through the process of setting up the Kafka source connector.

## Step 1: Set up Kafka

To use the Kafka source connector, you'll need:

* [A Kafka cluster 1.0 or above](https://kafka.apache.org/quickstart)
* Airbyte user should be allowed to read messages from topics, and these topics should be created before reading from Kafka.

## Step 2: Setup the Kafka source in Airbyte

In the Airbyte UI, create a new connection and select "Kafka" from the Source dropdown. Enter the name for the Kafka connector.

### For Airbyte Open Source:

1. In the Connection Configuration section, under Source, enter the following configuration data:

```json

    {
      "bootstrap_servers": "<YOUR