# Firehydrant
This directory contains the manifest-only connector for `source-firehydrant`.

This is the Firehydrant source that ingests data from the Firehydrant API.

FireHydrant is with you throughout the entire incident lifecycle from first alert until you&#39;ve learned from the retrospective. Reduce alert fatigue, guide responders, reduce MTTR and run stress-less retrospectives - all in a single, unified platform https://firehydrant.com

To use this source you must first create an account. Once logged in, head over to settings and in the sidebar, under Integrations click on API Keys. Click on Create a New API Key and note it down. 
You can find more information about the API here https://developers.firehydrant.com/#/

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
This will create a dev image (`source-firehydrant:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-firehydrant build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-firehydrant test
```

