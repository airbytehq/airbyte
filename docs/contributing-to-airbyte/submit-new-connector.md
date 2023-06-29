# Submit a New Connector

### New connectors

It's easy to add your own connector to Airbyte!

For sources, simply head over to our [Python CDK](../connector-development/cdk-python/).

:::info
The CDK currently does not support creating destinations, but it will very soon.
:::

* See [Building new connectors](../connector-development/) to get started.
* Since we frequently build connectors in Python, on top of Singer or in Java, we've created generator libraries to get you started quickly: [Build Python Source Connectors](../connector-development/tutorials/building-a-python-source.md) and [Build Java Destination Connectors](../connector-development/tutorials/building-a-java-destination.md)
* Integration tests \(tests that run a connector's image against an external resource\) can be run one of three ways, as detailed [here](../connector-development/testing-connectors/connector-acceptance-tests-reference.md)

**Please note that, at no point in time, we will ask you to maintain your connector.** The goal is that the Airbyte team and the community helps maintain the connector.