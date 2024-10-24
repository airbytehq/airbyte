# Pinata
This directory contains the manifest-only connector for `source-pinata`.

This is the source connector for the Pinata API that ingests data from both Pinata files and IPFS files https://pinata.cloud/

This API uses bearer tokens for authentication, in order to generate your token create an account on pinata. Once logged in click on the API Keys button in the left sidebar, then click “New Key” in the top right.
Create a new key and copy the JWT token, this will be used in your bearer Auth  https://docs.pinata.cloud/quickstart

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
This will create a dev image (`source-pinata:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-pinata build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-pinata test
```

