# Lightspeed Retail
This directory contains the manifest-only connector for `source-lightspeed-retail`.

Lightspeed Retail is a one-stop commerce platform empowering merchants around the world to simplify, scale and provide exceptional customer experiences. This source connector ingests data from the lightspeed retail API https://www.lightspeedhq.com/

In order to use this source, you must first create an account.
Note down the store url name as this will be needed for your subdomain name in the source. 
After logging in, you can create your personal token by navigating to Setup -&gt; Personal Token. You can learn more about the API here https://x-series-api.lightspeedhq.com/reference/listcustomers



 

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
This will create a dev image (`source-lightspeed-retail:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-lightspeed-retail build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-lightspeed-retail test
```

