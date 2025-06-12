# Cloudbeds
This directory contains the manifest-only connector for `source-cloudbeds`.

This is Cloudbeds source that ingests data from the Cloudbeds API.

Cloudbeds is an unified hospitality platform https://cloudbeds.com

In order to use this source, you must first create a cloudbeds account. Once logged in, navigate to the API credentials page for your property by clicking Account &gt; Apps &amp; Marketplace in the upper right corner.  Use the menu on the top to navigate to the API Credentials Page. Click the New Credentials button, fill in the details and click on Create. This will create an application, then click on the API Key and provide all the required scopes as needed. 

You can learn more about the API here https://hotels.cloudbeds.com/api/v1.2/docs/

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
This will create a dev image (`source-cloudbeds:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-cloudbeds build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-cloudbeds test
```

