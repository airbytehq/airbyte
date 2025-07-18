# Concord
This directory contains the manifest-only connector for `source-concord`.

This is the setup for the Concord source which ingests data from the concord API.

Concord turns contract data into financial insights. Sign, store and search unlimited contracts https://www.concord.app/

In order to use this source, you must first create a concord account and log in. Then navigate to Automations -&gt; Integrations -&gt; Concord API -&gt; Generate New Key to obtain your API key.

The API is accessible from two environments, sandbox and production. You can learn more about the API here https://api.doc.concordnow.com/

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
This will create a dev image (`source-concord:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-concord build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-concord test
```

