# Tempo.io
This directory contains the manifest-only connector for `source-tempo-io`.

This is the Tempo.io source connector that ingests data from the tempo.io API. 
Tempo is a flexible and modular portfolio management solutions for Jira. https://www.tempo.io/

In order to use this source, you must first create an account on Tempo.io and be a business plan user. Once logged in, you will have to add it to your Jira cloud account as an App. 

This source uses OAuth Bearer token for authentication. To obtain your token, head over to Tempo&gt;Settings, scroll down to Data Access and select API integration.
You can find more about the API here https://apidocs.tempo.io/

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
This will create a dev image (`source-tempo-io:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-tempo-io build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-tempo-io test
```

