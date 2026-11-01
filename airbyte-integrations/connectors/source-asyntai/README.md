# Asyntai
This directory contains the manifest-only connector for `source-asyntai`.

Asyntai is an AI chat agent for websites. This source copies the chats it handles into your warehouse: every conversation, every message in it, the visitors who left an email address or a phone number, and the support tickets the agent raised.

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
This will create a dev image (`source-asyntai:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-asyntai build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-asyntai test
```

