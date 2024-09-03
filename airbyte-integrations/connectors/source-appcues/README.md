# Appcues
This directory contains the manifest-only connector for `source-appcues`.

New Source: AppCues
Account ID link: https://studio.appcues.com/settings/account
Docs link: https://api.appcues.com/v2/docs
API keys link: https://studio.appcues.com/settings/keys

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
This will create a dev image (`source-appcues:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-appcues build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-appcues test
```

