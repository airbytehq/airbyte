# Kafka

This page guides you through the process of setting up the Kafka source connector in Airbyte.

## Step 1: Set up Kafka

To use the Kafka source connector, you'll need:

* A running Kafka Cluster version 1.0 or above. You can download Kafka from [the Apache Kafka website](https://kafka.apache.org/quickstart). Follow [the Kafka documentation](https://kafka.apache.org/documentation.html#quickstart) to set up and run a single-broker Kafka cluster.
* An authentication method set up for your Kafka cluster. Our Kafka connector supports both SASL/PLAIN and SSL authentication methods.

## Step 2: Configure Kafka source in Airbyte

You'll need the following information from Kafka to