# Connector Builder

Connector Builder is a no-code tool that’s part of the Airbyte UI. It provides an intuitive user interface on top of the [low-code YAML format](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/yaml-overview), letting you develop a connector to use in data syncs without ever needing to leave your Airbyte workspace. You can seamlessly switch between the visual UI and direct YAML editing as needed. Connector Builder offers the most straightforward method for building, contributing to, and maintaining source connectors.

## For creating source connectors only

The Connector Builder is only for creating source connectors. You can't currently use the Connector Builder to create destination connectors.

## How it works

The Connector Builder provides a visual interface that has the same capabilities as writing [low-code YAML connectors](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/yaml-overview) directly. Instead of writing YAML code, you configure your connector through intuitive forms with built-in validation and helpful guidance.

When you build a connector in the UI, you're creating a YAML manifest behind the scenes. The Builder ensures your configuration is always valid and complete, with real-time feedback and clear error messages. You can export this YAML manifest at any time or switch to direct YAML editing if you prefer a code-first approach.

## When should I use Connector Builder?

First, check if the API you want to use has an available connector in the [catalog](/integrations). If you find it there, you can use it as is.
If the connector you're looking for doesn't already exist and you'd like to try creating your own implementation, the Connector Builder should be your first destination.

## Getting started

The high-level process for using Connector Builder is as follows:

1. Access Connector Builder in the Airbyte web app by selecting "Builder" in the left-hand sidebar
2. Configure your connector using the schema-driven forms for global configuration, user inputs, and streams
3. Once the connector is ready, publish it to your workspace, or contribute it to the Airbyte catalog
4. Configure a Source based on the released connector
5. Use the Source in a connection to sync data

The concept pages in this section of the docs share more details related to the following topics: [global configuration](./global-configuration.md), [authentication](./authentication.md), [record processing](./record-processing.mdx), [pagination](./pagination.md), [incremental sync](./incremental-sync.md), [partitioning](./partitioning.md), and [error handling](./error-handling.md).

:::tip
Do not hardcode things like API keys or passwords while configuring a connector in the builder. They will be used, but not saved, during development when you provide them as Testing Values. For use in production, these should be passed in as user inputs after publishing the connector to the workspace, when you configure a source using your connector.

Follow [the tutorial](./tutorial.mdx) for an example of what this looks like in practice.
:::

## Contributing the connector

If you'd like to share your connector with other Airbyte users, you can contribute it to Airbyte's GitHub repository right from the Builder.

1. Click "Publish" chevron -> "Contribute to Marketplace"
2. Fill out the form: add the connector description, and provide your GitHub PAT (Personal Access Token) to create a pull request
3. Click "Contribute" to submit the connector to the Airbyte catalog

Reviews typically take under a week.

You can also export the YAML manifest file for your connector and share it with others. The manifest file contains all the connector configuration structured according to the declarative component schema, including the global configuration, streams, and user inputs.

## Disabled in low-resource mode

If you install Airbyte with abctl using low-resource mode, you are unable to access the Connector Builder. To access the Connector Builder, allocate Airbyte's [suggested resources](/platform/using-airbyte/getting-started/oss-quickstart#suggested-resources) and re-deploy Airbyte without setting the `--low-resource-mode` flag.
