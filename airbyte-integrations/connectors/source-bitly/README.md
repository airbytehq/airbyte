# Bitly
This directory contains the manifest-only connector for `source-bitly`.

Bitly is the most widely trusted link management platform in the world. By using the Bitly API, you will exercise the full power of your links through automated link customization, mobile deep linking, and click analytics.

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
This will create a dev image (`source-bitly:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-bitly build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-bitly test
```

