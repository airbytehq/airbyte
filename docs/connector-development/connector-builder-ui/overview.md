# Connector Builder Intro

The connector builder UI provides an intuitive UI on top of the [low-code YAML format](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/yaml-overview) and to use built connectors for syncs within the same workspace directly from within the UI. We recommend using it to iterate on your low-code connectors.

:::caution
The connector builder UI is in beta, which means it’s still in active development and may include backward-incompatible changes. Share feedback and requests with us on our Slack channel or email us at feedback@airbyte.io

**The connector builder does not yet have a link in the sidebar, to navigate to it manually change the URL path in your browser's address bar to `/<your workspace id>/connector-builder`**

Developer updates will be announced via our #help-connector-development Slack channel. If you are using the CDK, please join to stay up to date on changes and issues.
:::


## When should I use the connector builder?

The connector builder is the right tool if the following points are met:
* You want to integrate with a JSON-based HTTP API as a source of records
* The API you want to integrate with doesn't exist yet as a connector in the [connector catalog](/category/sources).
* The API is suitable for the connector builder as per the
[compatibility guide](./connector-builder-compatibility.md).

## Getting started

The high level flow for using the connector builder is as follows:

1. Access the connector builder in the Airbyte webapp
2. Use the connector builder to iterate on your low-code connector
3. Once the connector is ready, publish it to the local workspace
4. Configure a Source based on the released connector
5. Use the Source in a connection to sync data

Follow [the tutorial](./tutorial.mdx) for an example of this flow. The concept pages in the side bar to the left go into greater detail of more complex configurations.

## Connector vs. configured source vs. connection

When building a connector, it's important to differentiate between the connector, the configured source based on a connector and the connection:

The **connector** defines the functionality how to access an API or a database, for example protocol, URL paths to access, the way requests need to be structured and how to extract records from responses.

:::info
While configuring a connector in the builder, make sure to not hardcode things like API keys or passwords - these should be passed in as user input when configuring a Source based on your connector.

Follow [the tutorial](./tutorial.mdx) for an example how this looks like in practice.
:::

The **configured source** is configuring a connector to actually extract records. The exact fields of the configuration depend on the connector, but in most cases it provides authentication information (username and password, api key) and information about which data to extract, for example start date to sync records from, a search query records have to match.

The **connection** links up a configured source and a configured destination to perform syncs. It defines things like the replication frequency (e.g. hourly, daily, manually) and which streams to replicate.

## Exporting the connector

:::info
This section is only relevant if you want to contribute your connector back to the Airbyte connector catalog to make it available outside of your workspace.
:::

The connector builder leverages the [low-code CDK](https://docs.airbyte.com/connector-development/config-based/understanding-the-yaml-file/yaml-overview) under the hood, turning all configurations into the YAML format. While in most cases it's not necessary to interact with the YAML representation, it can be used to export the connector specification into a file and build a docker image containing the connector which can be shared more widely:

1. Use the connector builder to iterate on your low-code connector
2. Export the YAML into a low-code connector module on your local machine
3. Build the connector's Docker image
4. Use the built connector image in Airbyte

Once you're done iterating on your connector in the UI, you'll need to export the low-code YAML representation of the connector to your local filesystem into a connector module. This YAML can be downloaded by clicking the `Download Config` button in the bottom-left.

Create a low-code connector module using the connector generator (see [this YAML tutorial for an example](../config-based/tutorial/1-create-source.md)) using the name you'd like to use for your connector. After creating the connector, overwrite the contents of `airbyte-integrations/connectors/source-<connector name>/source_<connector name>/manifest.yaml` with the YAML you created in the UI.

Follow the instructions in the connector README to build the Docker image. Typically this will be something like `docker build . -t airbyte/source-<name>:<version>`.

From this point on your connector is a regular low-code CDK connector and can be distributed as a docker image and made part of the regular Airbyte connector catalog - you can find the [publish process on the overview page](/connector-development/#publishing-a-connector).

### Building the connector image

Follow the instructions in the connector README to build the Docker image. Typically this will be something like `docker build . -t airbyte/source-<name>:<version>`.

Once you've built the connector image, [follow these instructions](https://docs.airbyte.com/integrations/custom-connectors#adding-your-connectors-in-the-ui) to add your connector to your Airbyte instance.
