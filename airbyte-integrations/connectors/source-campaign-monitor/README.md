# Campaign Monitor
This directory contains the manifest-only connector for `source-campaign-monitor`.

This is the setup guide for the Campaign Monitor source.

Campaign Monitor is an email marketing and services platform https://www.campaignmonitor.com/
This connector ingests a variety of endpoints from the Campaign Monitor API.
In order to use the API, you must first create an account. You can generate your API key in the account settings.
https://www.campaignmonitor.com/api/v3-3/getting-started/ 


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
This will create a dev image (`source-campaign-monitor:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-campaign-monitor build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-campaign-monitor test
```

