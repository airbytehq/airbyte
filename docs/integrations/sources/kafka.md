# Kafka

This page guides you through the process of setting up the Kafka source connector in Airbyte.

## Step 1: Set up Kafka

To use the Kafka source connector, you'll need:

* A Kafka cluster 1.0 or above
* Airbyte user should be allowed to read messages from topics, and these topics should be created before reading from Kafka.

## Step 2: Setup the Kafka source in Airbyte

You'll need the following information to configure the Kafka source:

### General

* **Name** - Enter a name for the Kafka connector.
* **Source Type** - Select Kafka from the dropdown.

### Connection

* **Bootstrap Servers** - A list of host/port