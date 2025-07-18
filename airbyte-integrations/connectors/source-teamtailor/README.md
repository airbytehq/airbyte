# Teamtailor
This directory contains the manifest-only connector for `source-teamtailor`.

This is the setup for the Teamtailor source that ingests data from the teamtailor API.

Teamtailor is a recruitment software, provding a new way to attract and hire top talent https://www.teamtailor.com/

In order to use this source, you must first create an account on teamtailor.

Navigate to your organisation settings -&gt; API Key to create the required API token. You must also specify a version number and can use today&#39;s date as X-Api-Version to always get the latest version of the API.

Make sure to have the add-ons installed in your account for using the `nps-response` and `job-offers` endpoints.

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
This will create a dev image (`source-teamtailor:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-teamtailor build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-teamtailor test
```

