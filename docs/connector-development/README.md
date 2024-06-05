# Connector Development

### Before you start

Before building a new connector, review [Airbyte's data protocol specification](../understanding-airbyte/airbyte-protocol.md). As you begin, you should also familiarize yourself with our guide to [Best Practices for Connector Development](./best-practices.md).

If you need support along the way, visit the [Slack channel](https://airbytehq.slack.com/archives/C027KKE4BCZ) we have dedicated to helping users with connector development where you can search previous discussions or ask a question of your own. 

### Process overview

The first step in creating a new connector is to choose the tools you’ll use to build it. There are three basic approaches Airbyte provides to start developing a connector. To understand which approach you should take, review the [compatibility guide](./connector-builder-ui/connector-builder-compatibility.md).

After building and testing your connector, you’ll need to publish it. This makes it available in your workspace. At that point, you can use the connector you’ve built to move some data! 

If you want to contribute what you’ve built to the Airbyte Cloud and OSS connector catalog, follow the steps provided in the [contribution guide for submitting new connectors](../contributing-to-airbyte/submit-new-connector.md). 

### Connector development options
| Tool                   | Description                                                                                                                                                                                                      |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Connector Builder](./connector-builder-ui/overview.md)           | We recommend Connector Builder for developing a connector for an API source. If you’re using Airbyte Cloud, no local developer environment is required to create a new connection with the Connector Builder because you configure it directly in the Airbyte web UI. This tool guides you through creating and testing a connection. Refer to our [tutorial](./connector-builder-ui/tutorial.mdx) on the Connector Builder to guide you through the basics.  |
| [Low Code Connector Development Kit (CDK)](./config-based/low-code-cdk-overview.md)           | This framework lets you build source connectors for HTTP API sources. The Low-code CDK is a declarative framework that allows you to describe the connector using a [YAML schema](./schema-reference) without writing Python code. It’s flexible enough to include [custom Python components](./config-based/advanced-topics.md#custom-components) in conjunction with this method if necessary.                                                                                                                        |
| [Python Connector Development Kit (CDK)](./cdk-python/basic-concepts.md)       | While this method provides the most flexibility to developers, it also requires the most code and maintenance. This library provides classes that work out-of-the-box for most scenarios you’ll encounter along with the generators to make the connector scaffolds for you. We maintain an [in-depth guide](./tutorials/custom-python-connector/0-getting-started.md) to building a connector using the Python CDK.                                                                                                                                           |


Most database sources and destinations are written in Java. API sources and destinations are written
in Python using the [Low-code CDK](config-based/low-code-cdk-overview.md) or
[Python CDK](cdk-python/).

### Community maintained CDKs

- The [Typescript CDK](https://github.com/faros-ai/airbyte-connectors) is actively maintained by
  Faros.ai for use in their product.
- The [Airbyte Dotnet CDK](https://github.com/mrhamburg/airbyte.cdk.dotnet) in C#.
