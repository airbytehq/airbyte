# Zoho Invoice
This directory contains the manifest-only connector for `source-zoho-invoice`.

Zoho invoice is an invoicing software used by businesses.
With this connector we can extract data from various streams such as items , contacts and invoices streams.
Docs : https://www.zoho.com/invoice/api/v3/introduction/#overview

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
This will create a dev image (`source-zoho-invoice:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-zoho-invoice build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-zoho-invoice test
```

