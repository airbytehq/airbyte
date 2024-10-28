# Shippo
This directory contains the manifest-only connector for `source-shippo`.

This is the Shippo source for ingesting data using the Shippo API.

Shippo is your one-stop solution for shipping labels. Whether you use our app to ship or API to power your logistics workflow, Shippo gives you scalable shipping tools, the best rates, and world-class support https://goshippo.com/

In order to use this source, you must first create a Shippo account. Once logged in, head over to Settings -&gt; Advanced -&gt; API and click on generate new token. You can learn more about the API here https://docs.goshippo.com/shippoapi/public-api/#tag/Overview 

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
This will create a dev image (`source-shippo:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-shippo build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-shippo test
```

