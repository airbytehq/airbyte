# Shipstation
This directory contains the manifest-only connector for `source-shipstation`.

This page contains the setup guide and reference information for Shipstation source connector.

Documentation reference:
Visit https://www.shipstation.com/docs/api/ for API documentation

Authentication setup

To get your API key and secret in ShipStation:

↳ Go to Account Settings.

↳ Select Account from the side navigation, then choose API Settings.

↳ Click &quot;Generate New API Keys&quot; if no key and secret are listed yet.

** IMPORTANT **
↳If you&#39;ve already generated your API keys, the existing API keys will be displayed here and the button will read Regenerate API Keys.

If you already have API keys, do NOT generate new ones. Instead, copy your existing key and secret.

Copy your key and secret and paste them into the respective fields.


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
This will create a dev image (`source-shipstation:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-shipstation build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-shipstation test
```

