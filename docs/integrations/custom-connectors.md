---
description: Missing a connector?
---

# Custom or New Connector

If you'd like to **ask for a new connector,** you can request it directly [here](https://github.com/airbytehq/airbyte/discussions/new?category=new-connector-request).

If you'd like to build new connectors and **make them part of the pool of pre-built connectors on Airbyte,** first a big thank you. We invite you to check our [contributing guide on building connectors](/community/contributing-to-airbyte/).

If you'd like to build new connectors, or update existing ones, **for your own usage,** without contributing to the Airbyte codebase, read along.

## Developing your own connector

### You should probably use Connector Builder

If you need a connector for a data source that has an HTTP API, in 99% cases you should use the [Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview) to build a connector. You can choose to publish it to your workspace or contribute it to the Airbyte connector catalog.

You should only build and deploy your own connector in code (using Python or Java CDKs or any other language) when Builder does not support your data source or destination.

### Really need to build your own connector from scratch?

It's easy to build your own connectors for Airbyte. You can learn how to build new connectors using either our Connector Builder or our connector CDKs [here](/platform/connector-development/).

While the guides in the link above are specific to the languages used most frequently to write integrations, **Airbyte connectors can be written in any language**. Please reach out to us if you'd like help developing connectors in other languages.

:::caution
We strongly recommend creating new connectors using the [Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview) or one of the Airbyte CDKs.

While it is not recommended to build Docker images from scratch, it can be useful to build a custom Docker image if you cannot use the Connector Builder, and if you need to use a language other than Python or CDK.

See the following guides for more information on building custom Airbyte Docker images:

- [Using Custom Connectors](../platform/operator-guides/using-custom-connectors)
- [Airbyte Docker Protocol](../platform/understanding-airbyte/airbyte-protocol-docker)

:::

## Upgrading a connector

Follow these steps to upgrade a connector version.

1. In the navigaton bar, click **Workspace settings** > **Sources**/**Destinations**.

2. Find your connector in the list and click the edit button <svg fill="none" data-icon="pencil" role="img" viewBox="0 0 24 24" class="inline-svg"><path fill="currentColor" d="M22 7.24a1 1 0 0 0-.29-.71l-4.24-4.24a1 1 0 0 0-.71-.29 1 1 0 0 0-.71.29l-2.83 2.83L2.29 16.05a1 1 0 0 0-.29.71V21a1 1 0 0 0 1 1h4.24a1 1 0 0 0 .76-.29l10.87-10.93L21.71 8q.138-.146.22-.33.015-.12 0-.24a.7.7 0 0 0 0-.14zM6.83 20H4v-2.83l9.93-9.93 2.83 2.83zM18.17 8.66l-2.83-2.83 1.42-1.41 2.82 2.82z"></path></svg>.

3. In the dialog, update the Docker image tag to the new version.

To upgrade your connector version, go to the Settings in the left hand side of the UI and navigate to either Sources or Destinations. Find your connector in the list, and input the latest connector version.

![](/.gitbook/assets/upgrade-connector-version.png)
