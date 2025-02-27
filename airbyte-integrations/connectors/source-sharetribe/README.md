# Sharetribe
This directory contains the manifest-only connector for `source-sharetribe`.

The Sharetribe source connector which ingests data from the sharetribe integrations API.
Sharetribe is a no code marketplace builder tool. The source supports a number of API changes.
For more information, checkout the website https://www.sharetribe.com/

This source uses the OAuth configuration for handling requests.
A client_ID and client_secret is required in order to setup a connection.
For more details about the API, check out https://www.sharetribe.com/api-reference/integration.html

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
This will create a dev image (`source-sharetribe:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-sharetribe build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-sharetribe test
```

