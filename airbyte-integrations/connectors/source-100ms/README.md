# 100ms
This directory contains the manifest-only connector for `source-100ms`.

Website: https://dashboard.100ms.live/
API Reference: https://www.100ms.live/docs/server-side/v2/api-reference/Rooms/list-rooms

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
This will create a dev image (`source-100ms:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-100ms build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-100ms test
```

