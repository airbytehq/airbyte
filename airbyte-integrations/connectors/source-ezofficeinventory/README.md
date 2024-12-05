# EZOfficeInventory
This directory contains the manifest-only connector for `source-ezofficeinventory`.
https://ezo.io/ezofficeinventory/

## Documentation reference:
Visit https://ezo.io/ezofficeinventory/developers/ for API documentation

## Authentication setup
`source-ezofficeinventory` uses API Key authentication. <br />
API Access is disabled by default. <br /> 
Enable API Access in Settings > Integrations > API Integration and click on Update to generate a new access token

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
You will need `airbyte-ci` installed. You can find the documentation [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md).

### Build
This will create a dev image (`source-ezofficeinventory:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-ezofficeinventory build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-ezofficeinventory test
```

