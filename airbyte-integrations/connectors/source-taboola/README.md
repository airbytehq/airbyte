# Taboola
This directory contains the manifest-only connector for `source-taboola`.

This is the Taboola source that ingests data from the Taboola API.

Taboola helps you reach customers that convert. Drive business results by reaching people genuinely, effectively at just the right moment https://www.taboola.com/

In order to use this source, you must first create an account. Once logged in you can contact Taboola support to provide you with a Client ID, Client Secret and Account ID. Once these credentials have been obtained, you can input them into the appropriate fields.

You can learn more about the API here https://developers.taboola.com/backstage-api/reference

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
This will create a dev image (`source-taboola:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-taboola build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-taboola test
```

