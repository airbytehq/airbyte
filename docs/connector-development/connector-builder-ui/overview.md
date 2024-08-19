# Connector Builder Intro

Connector Builder is a no-code tool that’s part of the Airbyte UI. It provides an intuitive user interface on top of the [low-code YAML format](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/yaml-overview) and lets you develop a connector to use in data syncs without ever needing to leave your Airbyte workspace. Connector Builder offers the most straightforward method for building and maintaining connectors.

We recommend that you determine whether the connector you want can be built with the Connector Builder before looking at the Low-Code CDK or Python CDK. Our [compatibility guide](./connector-builder-compatibility.md) can help you decide if Connector Builder is the right tool to use. 

## When should I use Connector Builder?

First, check if the API you want to use has an available connector in the [catalog](../../integrations). If you find it there, you can use it as is. If you need to update an existing connector, see the guide for updates. 

Generally, you can build a connector with the Connector Builder if you want to connect to an HTTP API that returns a collection of records as JSON and has fixed endpoints. For more detailed information on requirements, refer to the [compatibility guide](./connector-builder-compatibility.md). 

## Getting started

The high-level process for using Connector Builder is as follows:

1. Access Connector Builder in the Airbyte web app by selecting "Builder" in the left-hand sidebar. 
2. Iterate on your low-code connector by providing details for global configuration and user inputs. User inputs are the variables your connector will ask an end-user to provide when they configure a connector for use in a connection. 
3. Once the connector is ready, publish it. This makes it available in your local workspace
4. Configure a Source based on the released connector
5. Use the Source in a connection to sync data

The concept pages in this section of the docs share more details related to the following topics: [authentication](./authentication.md), [record processing](./record-processing.mdx), [pagination](./pagination.md), [incremental sync](./incremental-sync.md), [partitioning](./partitioning.md), and [error handling](./error-handling.md). 

:::tip
Do not hardcode things like API keys or passwords while configuring a connector in the builder. They will be used, but not saved, during development when you provide them as Testing Values. For use in production, these should be passed in as user inputs after publishing the connector to the workspace, when you configure a source using your connector. 

Follow [the tutorial](./tutorial.mdx) for an example of what this looks like in practice.
:::

## Exporting the connector

:::info
If you choose to contribute your connector to the Airbyte connector catalog, making it publicly available outside of your workspace, you'll need to export it and go through the process of submitting it for review. 
:::

Connector Builder leverages the [low-code CDK](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/yaml-overview) under the hood, turning all configurations into the YAML format. Typically, it's not necessary to interact with the YAML representation. However, you can export the connector YAML into a file and build a docker image containing the connector which can be shared more widely:

1. Use Connector Builder to iterate on your low-code connector
2. Export the YAML into a low-code connector module on your local machine
3. Build the connector's Docker image
4. Use the built connector image in Airbyte

Once you're done iterating on your connector in the UI, you'll need to export the low-code YAML representation of the connector to your local filesystem into a connector module. This YAML can be downloaded by clicking the `Download Config` button in the bottom-left.

Create a low-code connector module using the connector generator (see [this YAML tutorial for an example](../config-based/tutorial/1-create-source.md)) using the name you'd like to use for your connector. After creating the connector, overwrite the contents of `airbyte-integrations/connectors/source-<connector name>/source_<connector name>/manifest.yaml` with the YAML you created in the UI.

Follow the instructions in the connector README to build the Docker image. Typically this will be something like `docker build . -t airbyte/source-<name>:<version>`.

From this point on your connector is a regular low-code CDK connector. It can now be distributed as a docker image and be made part of the regular Airbyte connector catalog. For more information, read the [overview page for the publishing process](/connector-development/#publishing-a-connector).

:::note
Connector Builder UI is in beta, which means it’s still in active development and may include backward-incompatible changes. Share feedback and requests with us on our Slack channel or email us at feedback@airbyte.io

Developer updates will be announced via our #help-connector-development Slack channel. If you are using the CDK, please join to stay up to date on changes and issues.
:::