# Katana
This directory contains the manifest-only connector for `source-katana`.

This is the Katana source connector that ingests data from the katana API.

Katana is a real-time cloud inventory platform to manage sales channels, products, and materials to always be ready to meet demands.  You can find more about it here https://katanamrp.com/

This source uses OAuth Bearer Token for authentication. In order to obtain your API token, you must first create an account on Katana and be on their Professional Plan. 

To generate a live API key: log in to your Katana account.  Go to Settings &gt; API. Select Add new API key. You can find more about the API here https://developer.katanamrp.com/reference/api-introduction

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
This will create a dev image (`source-katana:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-katana build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-katana test
```

