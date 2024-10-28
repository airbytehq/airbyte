# Attio
This directory contains the manifest-only connector for `source-attio`.

The Attio Airbyte Connector enables seamless integration with Attio, a modern CRM platform. This connector allows you to easily extract, sync, and manage data from Attio, such as contacts, accounts, and interactions, directly into your preferred data destinations. With this integration, businesses can streamline workflows, perform advanced analytics, and create automated pipelines for their CRM data, ensuring data consistency and accessibility across tools.

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-attio:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-attio build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-attio test
```

