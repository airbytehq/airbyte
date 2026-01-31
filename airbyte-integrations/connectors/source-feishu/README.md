# Feishu
This directory contains the manifest-only connector for `source-feishu`.

Extracts data from Feishu/Lark Bitable (Base). Supports authentication via App ID and App Secret.

**Prerequisites:**
1. A Feishu/Lark account.
2. A custom app created in the Feishu Open Platform with Bitable permissions enabled.
3. The App ID and App Secret.

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
You will need `airbyte-ci` installed. You can find the documentation [here](https://docs.airbyte.com/contributing-to-airbyte/airbyte-ci).

### Build
This will create a dev image (`source-feishu:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-feishu build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-feishu test
```

