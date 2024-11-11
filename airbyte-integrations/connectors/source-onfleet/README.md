# Onfleet
This directory contains the manifest-only connector for `source-onfleet`.

This is the Onfleet connector that ingests data from the Onfleet API.

Onfleet is the world&#39;s advanced logistics software that delights customers, scale operations, and boost efficiency https://onfleet.com/

In order to use this source you must first create an account on Onfleet. Once logged in, you can find the can create an API keys through the settings menu in the dashboard, by going into the API section.

You can find more information about the API here https://docs.onfleet.com/reference/setup-tutorial

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
This will create a dev image (`source-onfleet:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-onfleet build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-onfleet test
```

