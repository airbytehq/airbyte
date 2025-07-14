# Connector Builder

Connector Builder is a no-code tool that’s part of the Airbyte UI.
It provides an intuitive user interface on top of the [declarative component schema](https://github.com/airbytehq/airbyte-python-cdk/blob/main/airbyte_cdk/sources/declarative/declarative_component_schema.yaml), which defines the structure and validation rules for [low-code YAML connectors](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/yaml-overview). The UI automatically generates forms and validation based on this schema, letting you develop a connector to use in data syncs without ever needing to leave your Airbyte workspace.
Connector Builder offers the most straightforward method for building, contributing, and maintaining connectors.

## How it works

The Connector Builder UI is powered by Airbyte's declarative component schema, which serves as the foundation for all low-code connectors. This schema defines every component, property, and validation rule available for building connectors. The UI automatically generates forms, input validation, and configuration options directly from this schema, ensuring that your connector configurations are always valid and complete.

When you configure a connector in the Builder, you're essentially creating a YAML manifest that conforms to the declarative component schema. The UI guides you through this process with intuitive forms, real-time validation, and helpful descriptions—all derived automatically from the schema definitions.

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

The concept pages in this section of the docs share more details related to the following topics: [authentication](./authentication.md), [record processing](./record-processing.mdx), [pagination](./pagination.md), [incremental sync](./incremental-sync.md), [partitioning](./partitioning.md), and [error handling](./error-handling.md).

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
