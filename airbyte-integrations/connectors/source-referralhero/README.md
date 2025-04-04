# referralhero
[Referral Hero](https://referralhero.com) is a tool for creating, managing, and analyzing referral programs to boost customer acquisition and engagement.
With this connector, you can streamline the transfer of campaign-related data for better integration into your analytics, CRM, or marketing platforms.

Referral Hero Source Connector is a designed to sync referral data between your Referral Hero campaigns and your destination airbyte connectors.

This directory contains the manifest-only connector for `source-referralhero`airbyte connector developed using airbyte 1.0 UI Connector development

## Generate API Token
Please follow the instructions in the following [referralhero](https://support.referralhero.com/integrate/rest-api) page to generate the api token

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
This will create a dev image (`source-referralhero:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-referralhero build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-referralhero test
```

