# DC Hub
This directory contains the manifest-only connector for `source-dc-hub`.

DC Hub (dchub.cloud): data center and energy intelligence. The Data Center Power Index (DCPI) scores 300+ markets daily on where data centers can get grid power. Also available as 94 MCP tools at https://dchub.cloud/mcp.

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
This will create a dev image (`source-dc-hub:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-dc-hub build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-dc-hub test
```

